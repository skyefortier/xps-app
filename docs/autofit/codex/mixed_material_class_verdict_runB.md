OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f7e43-b83f-7601-a7b2-7a4bf9180a7c
--------
user
You are an adversarial reviewer for a new-feature commit in this repo (XPS
peak-fitting web app). Review commit 77bf3a8 ("feat(autofit): MIXED
material class -- relax C1s contamination width under differential
charging") on branch feature-autofit-stage2 -- `git show 77bf3a8`
gives the full diff. This lands right after a provenance audit that removed
every lab-derived reference value from this codebase (see
docs/autofit/PROGRESS.md's provenance-audit entries) -- treat this commit
as a direct test of whether that discipline held, not just a UI feature.

BACKGROUND -- what MIXED is supposed to be:

MaterialClass gains a 4th member, MIXED = "mixed", for analyte-in-matrix
samples (e.g. this lab's UCl4-in-graphite/B4C/BN samples). Analyte and
matrix can charge differently under X-ray illumination (differential
charging), which (a) broadens peaks (a distribution of local surface
potentials broadens the observed peak -- inhomogeneous broadening) and
(b) means a single charge reference calibrates the matrix's potential and
may not transfer to the analyte. C1sModule.build_candidates() relaxes the
contamination/adventitious FWHM ceiling (0.8-2.0 eV -> 0.8-15.0 eV) under
MIXED; every other constraint (position windows, linked offsets, every
other FWHM family) is untouched.

THE EXPLICIT DESIGN CONSTRAINT (read this before reviewing the diff): MIXED
must RELAX constraints, never ASSERT new ones. A cap widened to a number
derived from this lab's own mixed-phase spectra (e.g. "3.5 eV because
that's what our samples fit at") would be exactly the lab self-reference
the provenance audit removed, wearing a feature label instead of a tier
badge. The 15.0 eV ceiling is claimed to be a pure numeric guard reused
from fitting.py's own existing fwhm_max default (needed because
autofit/engine.py seeds the initial FWHM guess at the fwhm_range midpoint,
so an infinite bound would seed an infinite initial value) -- NOT a new
chemistry claim. Verify this claim doesn't secretly smuggle in a
lab-derived number under UNVERIFIED cover.

ADVERSARIAL QUESTIONS -- ATTACK THESE SPECIFICALLY (Skye's own framing):

(a) SELF-REFERENCE CHECK. Is the 15.0 eV ceiling ACTUALLY traceable to
    fitting.py's existing fwhm_max default (grep for it -- fitting.py's
    _make_peak_params, spec.get("fwhm_max", 15.0)), or is it coincidentally
    matching a number this lab's own spectra happen to fit at? Check
    docs/autofit/test_data/*.proj.zip and docs/autofit/adjudication-
    decisions.md for any number near 15.0 that could be the REAL source
    dressed up as a "numeric guard." Is there a smaller, equally-honest
    numeric-guard choice that would have been just as defensible (e.g. why
    15.0 and not some other pre-existing engine constant)?

(b) OPTIMIZER DEGENERACY. Relaxing a width ceiling from 2.0 to 15.0 eV
    opens real room for the optimizer to grow one component pathologically
    fat and absorb baseline or neighboring peaks -- especially in the
    "_linked" candidate families, where c1s.py's build_candidates() has ALL
    THREE contaminant slots (CO, C=O, OC=O) share ONE width parameter
    (_SHARED_CONTAM_FWHM) via shared_fwhm_params. Under MIXED that shared
    width's own range also widens to (0.8, 15.0) -- construct or reason
    through a concrete synthetic C 1s spectrum where a shared-width
    contaminant component under MIXED balloons wide enough to functionally
    absorb the aliphatic main or another contaminant's signal (the ~280-292
    eV C 1s contaminant span is only ~8-12 eV wide -- a 15 eV FWHM
    component can span or exceed the whole region). c1s.py's own MG-family
    comments already document an analogous overlap-degeneracy risk (see
    aliphatic_main_offset's linked-offset rationale) -- this is the same
    class of risk reached through width instead of position. If it
    materializes on a real or synthetic fit, is FWHM_MIXED_CEILING_NUMERIC_
    GUARD_EV = 15.0 too permissive, and would a MUCH lower numeric guard
    (still honestly labeled as a guard, not a chemistry claim) close it
    without reintroducing a new asserted value?

(c) BLAST RADIUS. Confirm build_candidates()'s change is read ONLY when
    phase.material_class is MaterialClass.MIXED -- run/reason through the
    non-MIXED path (conductor/semiconductor/insulator) and confirm the
    candidate pool, every fwhm_range, every BE window, every linked-offset
    range is IDENTICAL to before this commit (tests/autofit/
    test_c1s_mixed_material_class.py claims this structurally -- verify the
    tests actually cover it, and try to find a code path they miss). Also
    confirm no OTHER region module (u4f.py, b1s.py, etc.) reads
    material_class at all -- MIXED must be a no-op everywhere except C1s.

(d) USER-FACING NOTE ACCURACY. templates/index.html's FP_STRINGS.materials.
    mixed.hint is the ONLY user-visible description of what MIXED does.
    Read it literally: does it overstate (implying the app corrected for
    or measured the differential charging) or understate (failing to warn
    that reported positions are less trustworthy) what the feature
    actually does? The DECIDED constraint (Skye, 2026-07-17) is that MIXED
    "does not correct for that uncertainty; it only stops assuming there
    isn't any" -- does the shipped copy read that way to a chemist with no
    context, not just to someone who already knows the design intent?

(e) CHARGE-CORRECTION ISOLATION -- THE HARDEST REQUIREMENT, VERIFY BY
    DIFFING OUTPUT, NOT BY READING THE DIFF. Skye's explicit decision:
    "MIXED must not alter the charge-correction step in any way. Not
    suppressed, not adjusted, not conditionally applied." Trace
    app.py's _validate_analyze_request: material_class is parsed into
    `mclass` and passed ONLY into `Phase(material_class=mclass, ...)`;
    `corrected = energy - cc_shift` (the actual charge-correction
    arithmetic) has zero reference to `mclass`/`mc_raw` anywhere in its
    computation, textually or in control flow. Confirm this yourself by
    tracing the function, not by trusting this description. Then run (or
    reason precisely through) tests/test_api_analyze.py::
    test_material_class_does_not_affect_charge_correction and confirm it
    actually exercises the real code path (not a mock) and would fail if
    someone later added a material_class branch inside the cc_shift
    computation.

SCOPE CHECK: `git show --stat 77bf3a8` should show autofit/
grammar.py, autofit/regions/c1s.py, app.py (one docstring line), templates/
index.html, tests/test_api_analyze.py, tests/autofit/
test_c1s_mixed_material_class.py, tests/js/fp_material_mixed.test.js. Zero
diff in autofit/engine.py, autofit/methods/*.py, fitting.py, any OTHER
region module, or the charge-correction path in app.py beyond the one
enum-value addition to the docstring literal.

TESTS TO INTERROGATE: for each new/modified test, would it actually fail if
the corresponding behavior were removed or wrong? In particular:
test_mixed_relaxes_contamination_fwhm_ceiling (would it catch MIXED being
silently a no-op?), test_mixed_provenance_relaxation_record_asserts_no_new_
value (would it catch a record that snuck a bare number into `value`?),
and the FWHM_MIXED_CEILING_NUMERIC_GUARD_EV == provenance-record-value
cross-check (would it catch code and doc drifting apart?).

Deliver: a numbered findings list (severity BLOCKER/MAJOR/MINOR, each with
file/line and a concrete failure scenario), then a final line exactly
"VERDICT: GO" or "VERDICT: NO-GO".

codex
I’ll review this as a code-review pass against the specific commit, starting from the diff and then checking the surrounding implementation and tests for the provenance and charge-correction constraints.
exec
/bin/zsh -lc 'git show --stat --oneline 77bf3a8' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-5uGGppz8' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Xgzc9N4L' (errno=Operation not permitted)
77bf3a8 feat(autofit): MIXED material class -- relax C1s contamination width under differential charging
 app.py                                         |   2 +-
 autofit/grammar.py                             |  11 ++
 autofit/regions/c1s.py                         |  99 ++++++++++++-
 templates/index.html                           |  32 ++++-
 tests/autofit/test_c1s_mixed_material_class.py | 189 +++++++++++++++++++++++++
 tests/js/fp_material_mixed.test.js             |  54 +++++++
 tests/test_api_analyze.py                      |  62 +++++++-
 7 files changed, 439 insertions(+), 10 deletions(-)

exec
/bin/zsh -lc 'git status --short --branch' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Zllo4m2h' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4dvjIFvJ' (errno=Operation not permitted)
## feature-autofit-stage2...origin/feature-autofit-stage2
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json

exec
/bin/zsh -lc 'git show --find-renames --find-copies --stat --patch 77bf3a8' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-glcT2tAJ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-OPLANPtU' (errno=Operation not permitted)
commit 77bf3a813355b665fa80e72171f3df62455b0877
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Mon Jul 20 00:42:10 2026 -0600

    feat(autofit): MIXED material class -- relax C1s contamination width under differential charging
    
    Adds MaterialClass.MIXED for analyte-embedded-in-a-different-matrix
    samples (this lab's UCl4-in-graphite/B4C/BN samples are the motivating
    case, per the project context — but no number from those spectra appears
    anywhere in this commit; see the provenance-audit trap below).
    
    Physical rationale: analyte and matrix can charge differently under X-ray
    illumination (differential charging). A non-uniform spatial distribution
    of charging potentials broadens the observed peak (inhomogeneous
    broadening), and a single charge correction calibrates the matrix's
    potential — it does not necessarily transfer to the analyte. Baer,
    Artyushkova, Cohen, Easton, Engelhard, Gengenbach, Greczynski, Mack,
    Morgan, Roberts, "XPS Guide: Charge neutralization and binding energy
    referencing for insulating samples," J. Vac. Sci. Technol. A 38, 031204
    (2020), DOI 10.1116/6.0000057 (differential charging broadens peaks;
    internal referencing has "limited accuracy ... often including multiphase
    and other complex samples"); Greczynski & Hultman, "X-ray photoelectron
    spectroscopy: Towards reliable binding energy referencing," Prog. Mater.
    Sci. 107 (2020) 100591, DOI 10.1016/j.pmatsci.2019.100591.
    
    THE PROVENANCE-AUDIT TRAP THIS UNIT IS DESIGNED TO AVOID: the obvious way
    to implement MIXED is a cap/window derived from this lab's own mixed-phase
    spectra (e.g. "widen to 3.5 eV because that's what our samples fit at") —
    exactly the lab self-reference the provenance audit removed, wearing a
    feature label instead of a tier badge. So MIXED only RELAXES an existing
    constraint; it never asserts a new one. Withdrawing an assumption needs no
    citation (it is the removal of a claim); asserting a new numeric window
    does, and this feature has none.
    
    Concretely: autofit/regions/c1s.py's build_candidates() widens the
    contamination/adventitious FWHM ceiling (0.8-2.0 eV -> 0.8-15.0 eV) under
    MIXED, everywhere FWHM_RANGE_CONTAMINATION was used (aliphatic mains,
    plain/linked/offset-linked contaminant slots, the shared-width parameter
    for the "_linked" families). The floor is untouched — differential
    charging only broadens a peak, never narrows one. Position windows,
    linked-offset (contaminant center) ranges, and every other FWHM family
    (graphitic main, aromatic-polymer main, satellite) are untouched — the
    unit's own instructions name the adventitious cap as the one clear,
    in-scope case.
    
    The 15.0 eV ceiling is NOT a second chemistry-flavored magic number: a
    fully unconstrained (infinite) bound is not viable with the current engine
    (autofit/engine.py seeds the initial FWHM guess at the fwhm_range midpoint,
    so an infinite ceiling would seed an infinite initial value and break the
    optimizer outright). 15.0 eV is fitting.py's own pre-existing fwhm_max
    default — the ceiling the manual /api/fit path already applies to every
    peak, everywhere in this app — reused as a pure numeric guard for
    optimizer stability, not a physics claim. Labeled UNVERIFIED in
    provenance(), same footing as dsg_alpha_cap's existing "fitalg numeric
    guard" language. The relaxation itself is a separate CONDITIONAL
    provenance record whose `value` is a descriptive action ("relax the
    ceiling, assert no new value"), never a bare number — so the two claims
    (the withdrawal, which needs no citation, and the residual numeric guard,
    honestly labeled as a guard) can never be conflated.
    
    KNOWN RISK, flagged for Codex review rather than silently engineered
    around: the "_linked" families share ONE width parameter across all 3
    contaminant slots, so under MIXED that shared width also relaxes to the
    wide ceiling — a single fat shared-width component could in principle
    absorb signal across the whole ~280-292 eV C 1s contaminant span (an
    overlap-degeneracy failure mode analogous to the one c1s.py's own
    MG-family comments already document for a free aliphatic center).
    
    DECIDED (Skye, 2026-07-17): charge correction is out of scope. MIXED must
    not alter it — not suppressed, adjusted, or conditionally applied.
    app.py's material_class parses only into Phase.material_class, consumed
    by grammar resolution; the `corrected = energy - cc_shift` arithmetic has
    zero reference to it. Verified with a dedicated test
    (test_material_class_does_not_affect_charge_correction) that calls
    _validate_analyze_request directly and diffs its corrected x/y arrays
    across material classes, rather than trusting the code-path reasoning.
    
    Frontend: FP_STRINGS.materials.mixed gives the option a clear label
    ("mixed (analyte in matrix)") and an advisory hint — the charge reference
    may not apply to the analyte, reported positions carry additional
    unquantified uncertainty, and the note is explicit that this does NOT
    correct for that uncertainty. Rendering for the other 3 material classes
    is byte-identical (no FP_STRINGS.materials override exists for them — no
    title attribute, same bare-value label as before). Browser-verified via
    Playwright against a dev gunicorn on :5151: dropdown shows the new label,
    hint text updates correctly on selection and clears for the others, and a
    full Find Peaks run with material_class=mixed + region C 1s progresses
    normally through the real (widened) candidate families.
    
    Tests (TDD, red confirmed before each green): tests/autofit/
    test_c1s_mixed_material_class.py (11 tests) — non-regression for
    conductor/semiconductor/insulator (byte-identical fwhm_range, candidate
    names, BE windows, linked-offsets), MIXED actually widens the ceiling
    (not decorative), MIXED never touches position windows/offsets or
    unrelated FWHM families, both provenance records present and correctly
    shaped. tests/test_api_analyze.py — enum round-trips through /api/analyze/
    meta (fixed the one pre-existing pinned 3-value set), material_class=mixed
    accepted at /api/analyze (200) and /api/analyze/start (202 — corrected
    from this unit's brief, which said 200; the real contract returns 202 for
    an accepted async job), and the charge-correction isolation test above.
    tests/js/fp_material_mixed.test.js (3 tests) — FP_STRINGS content.
    
    Verification: parity gates (test_b1s_cl2p_parity_gates.py,
    test_c1s_parity_gate.py, test_u4f_parity_gate.py under
    RUN_AUTOFIT_GATE=1) all pass — these fit real expert spectra with
    non-MIXED phases and are structurally unaffected. Full suite: 696 passed,
    6 skipped, 0 failed. Scope: autofit/grammar.py, autofit/regions/c1s.py,
    app.py (one docstring line), templates/index.html, and 3 test files —
    zero changes to autofit/engine.py, autofit/methods/*.py, fitting.py, any
    other region module, or the charge-correction path beyond the docstring
    enum listing.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
---
 app.py                                         |   2 +-
 autofit/grammar.py                             |  11 ++
 autofit/regions/c1s.py                         |  99 ++++++++++++-
 templates/index.html                           |  32 ++++-
 tests/autofit/test_c1s_mixed_material_class.py | 189 +++++++++++++++++++++++++
 tests/js/fp_material_mixed.test.js             |  54 +++++++
 tests/test_api_analyze.py                      |  62 +++++++-
 7 files changed, 439 insertions(+), 10 deletions(-)

diff --git a/app.py b/app.py
index 3cd4ed4..2011f6c 100644
--- a/app.py
+++ b/app.py
@@ -894,7 +894,7 @@ def _register_routes(app: Flask) -> None:
           "session_id":     "...",
           "cc_shift":       0.0,          // frontend charge shift (corrected = raw − cc_shift)
           "roi":            {"be_min": ..., "be_max": ...},   // corrected frame
-          "material_class": "conductor" | "insulator" | "semiconductor",
+          "material_class": "conductor" | "insulator" | "semiconductor" | "mixed",
           "regions":        ["Cl 2p", ...],   // registered region names
           "phase":          {"id": "sample", "material": "graphite"},  // optional
           "method":         "ic_model_comparison" | "least_squares"
diff --git a/autofit/grammar.py b/autofit/grammar.py
index 677eef5..01ad401 100644
--- a/autofit/grammar.py
+++ b/autofit/grammar.py
@@ -78,6 +78,17 @@ class MaterialClass(Enum):
     CONDUCTOR = "conductor"
     SEMICONDUCTOR = "semiconductor"
     INSULATOR = "insulator"
+    # Analyte embedded in a different matrix (2026-07-20): differential
+    # charging between analyte and matrix is possible, which voids the
+    # single-species-homogeneity assumption behind some region modules'
+    # width ceilings. MIXED only RELAXES existing constraints (region
+    # modules opt in — see autofit.regions.c1s) — it asserts no new
+    # position or width value, and it must never reach charge-correction
+    # (that stays byte-identical to every other material class; see
+    # tests/test_api_analyze.py::test_material_class_does_not_affect_charge_correction).
+    # Appended LAST so the default dropdown/first-enum-member selection
+    # (conductor) is unchanged.
+    MIXED = "mixed"
 
 
 @dataclass(frozen=True)
diff --git a/autofit/regions/c1s.py b/autofit/regions/c1s.py
index 8d20f35..9e68678 100644
--- a/autofit/regions/c1s.py
+++ b/autofit/regions/c1s.py
@@ -29,6 +29,7 @@ from ..grammar import (
     CandidateModel,
     ComponentSlot,
     LineShape,
+    MaterialClass,
     Phase,
 )
 from . import register_region
@@ -80,6 +81,55 @@ FWHM_RANGE_SATELLITE = (1.0, 5.5)
 # is not expressible by construction — the cap is the ruling.
 FWHM_RANGE_CONTAMINATION = (0.8, 2.0)
 
+# MIXED material class (2026-07-20): FWHM_RANGE_CONTAMINATION's ceiling is
+# justified by a single, well-referenced HOMOGENEOUS surface. That
+# condition is not met for an analyte embedded in a different matrix —
+# analyte and matrix can charge differently under X-ray illumination
+# (differential charging), and a non-uniform spatial distribution of
+# charging potentials broadens the observed peak (inhomogeneous
+# broadening; see provenance() for the citations). Withdrawing that
+# homogeneity assumption needs no citation — it is the removal of a
+# claim, not a new one — so this widens the ceiling toward
+# "unconstrained" rather than asserting a second, chemistry-flavored
+# magic number (the provenance-audit trap this unit exists to avoid: a
+# cap derived from THIS LAB'S OWN mixed-phase spectra would be exactly
+# the self-reference the audit removed, wearing a feature label instead
+# of a tier badge). The floor is untouched: differential charging only
+# broadens a peak, it never narrows one.
+#
+# A fully unconstrained (infinite) ceiling is not viable with the current
+# engine: autofit/engine.py seeds the initial FWHM guess at the MIDPOINT
+# of fwhm_range, so an infinite upper bound would seed an infinite
+# initial value and break the optimizer outright. Some finite ceiling is
+# therefore unavoidable for numerical stability — so this reuses
+# fitting.py's OWN existing fwhm_max default (15.0 eV), the ceiling the
+# manual /api/fit path already applies to literally every peak, everywhere
+# in this app, rather than inventing a new number. Purely a numeric guard
+# for optimizer stability, not a chemistry or physics claim (same footing
+# as DSG_ALPHA_RANGE_GRAPHITIC's "fitalg numeric guard" below) — if a
+# fitted component pegs this ceiling under MIXED, that is the numerical
+# guard doing its job, not a measurement.
+#
+# KNOWN RISK (flag for review, do not silently paper over): the "_linked"
+# candidate families share ONE width parameter across all 3 contaminant
+# slots (see shared_decl below) — under MIXED that shared width relaxes
+# to this same wide ceiling, so a single fat shared-width component could
+# in principle absorb signal across the whole ~280-292 eV C 1s contaminant
+# span. c1s.py's own MG-family comments already document an analogous
+# overlap-degeneracy failure mode (see aliphatic_main_offset below); this
+# is the same class of risk, now reachable through a wider ceiling instead
+# of a free position. Should be adversarially fit-tested, not just read.
+FWHM_MIXED_CEILING_NUMERIC_GUARD_EV = 15.0
+
+
+def _contamination_fwhm_range(material_class: MaterialClass) -> tuple[float, float]:
+    """FWHM_RANGE_CONTAMINATION, widened under MIXED. See the constant
+    comment above — this relaxes a constraint, it never asserts a new one."""
+    if material_class is MaterialClass.MIXED:
+        return (FWHM_RANGE_CONTAMINATION[0], FWHM_MIXED_CEILING_NUMERIC_GUARD_EV)
+    return FWHM_RANGE_CONTAMINATION
+
+
 # DS+G Lorentzian HWHM fixed at the C 1s core-hole lifetime:
 # Campbell & Papp, At. Data Nucl. Data Tables 77 (2001) 1–56
 # (DOI 10.1006/adnd.2000.0848): Γ_K(C) ≈ 0.10 eV FWHM → 0.05 eV HWHM.
@@ -190,6 +240,42 @@ class C1sModule:
                        "284.5 vs aliphatic 284.8) and Biesinger's "
                        "adventitious C-C/C-H convention (284.8 vs "
                        "graphite 284.4, +0.4)"},
+            {"constant": "mixed_material_class_width_relaxation",
+             "value": "under MaterialClass.MIXED (analyte embedded in a "
+                      "different matrix), the contamination/adventitious "
+                      "FWHM ceiling's single-species-homogeneity "
+                      "assumption is withdrawn and the ceiling is relaxed "
+                      "toward unconstrained; no new position or width "
+                      "value is asserted — position windows and every "
+                      "other FWHM family are unchanged",
+             "status": "CONDITIONAL",
+             "source": "differential charging between analyte and matrix "
+                       "causes inhomogeneous broadening (Baer, "
+                       "Artyushkova, Cohen, Easton, Engelhard, Gengenbach, "
+                       "Greczynski, Mack, Morgan, Roberts, \"XPS Guide: "
+                       "Charge neutralization and binding energy "
+                       "referencing for insulating samples,\" J. Vac. Sci. "
+                       "Technol. A 38, 031204 (2020), DOI "
+                       "10.1116/6.0000057 — differential charging "
+                       "broadens peaks, and a single charge correction is "
+                       "insufficient once it is present; internal "
+                       "referencing has \"limited accuracy ... often "
+                       "including multiphase and other complex samples\"; "
+                       "Greczynski & Hultman, \"X-ray photoelectron "
+                       "spectroscopy: Towards reliable binding energy "
+                       "referencing,\" Prog. Mater. Sci. 107 (2020) "
+                       "100591, DOI 10.1016/j.pmatsci.2019.100591)"},
+            {"constant": "mixed_fwhm_ceiling_numeric_guard",
+             "value": FWHM_MIXED_CEILING_NUMERIC_GUARD_EV,
+             "status": "UNVERIFIED",
+             "source": "a fully unconstrained (infinite) ceiling breaks "
+                       "the engine's initial-value seeding (the FWHM "
+                       "guess is the fwhm_range midpoint); this reuses "
+                       "fitting.py's own existing fwhm_max default, the "
+                       "ceiling the manual /api/fit path already applies "
+                       "to every peak in this app — a numeric guard for "
+                       "optimizer stability, not a chemistry or physics "
+                       "claim (same footing as dsg_alpha_cap above)"},
         ]
 
     def build_candidates(
@@ -217,6 +303,7 @@ class C1sModule:
             )
         pid = phase.id
         main_fwhm = _MAIN_FWHM_BY_MATERIAL.get(phase.material, FWHM_RANGE_GRAPHITIC)
+        contam_fwhm = _contamination_fwhm_range(phase.material_class)
 
         def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
             return ComponentSlot(
@@ -241,7 +328,7 @@ class C1sModule:
 
         def aliphatic_main() -> ComponentSlot:
             return slot("main_aliphatic", C1S_WINDOWS["aliphatic"],
-                        LineShape.PSEUDO_VOIGT, FWHM_RANGE_CONTAMINATION)
+                        LineShape.PSEUDO_VOIGT, contam_fwhm)
 
         shake_up = slot(
             "satellite_pi", C1S_WINDOWS["shake_up_pi"], LineShape.PSEUDO_VOIGT,
@@ -250,7 +337,7 @@ class C1sModule:
         )
 
         def contam(key, linked_fwhm=None, offset=None,
-                   fwhm_range=FWHM_RANGE_CONTAMINATION) -> ComponentSlot:
+                   fwhm_range=None) -> ComponentSlot:
             kw = {}
             if linked_fwhm:
                 kw["fwhm_linked_to"] = linked_fwhm
@@ -259,10 +346,10 @@ class C1sModule:
                 kw["linked_to"] = "main_graphitic"
                 kw["linked_offset_range"] = (mid - hw, mid + hw)
             return slot(f"contamination_{key}", C1S_WINDOWS[key],
-                        LineShape.PSEUDO_VOIGT, fwhm_range, **kw)
+                        LineShape.PSEUDO_VOIGT,
+                        fwhm_range if fwhm_range is not None else contam_fwhm, **kw)
 
-        shared_decl = ((_SHARED_CONTAM_FWHM,
-                        FWHM_RANGE_CONTAMINATION[0], FWHM_RANGE_CONTAMINATION[1]),)
+        shared_decl = ((_SHARED_CONTAM_FWHM, contam_fwhm[0], contam_fwhm[1]),)
         keys = ["CO", "C=O", "OC=O"]
 
         candidates: list[CandidateModel] = []
@@ -328,7 +415,7 @@ class C1sModule:
         #     (+0.4).  UNVERIFIED-empirical (labeled-set + convention). ---
         def aliphatic_main_offset() -> ComponentSlot:
             return slot("main_aliphatic", C1S_WINDOWS["aliphatic"],
-                        LineShape.PSEUDO_VOIGT, FWHM_RANGE_CONTAMINATION,
+                        LineShape.PSEUDO_VOIGT, contam_fwhm,
                         linked_to="main_graphitic",
                         linked_offset_range=(0.2, 0.6))
 
diff --git a/templates/index.html b/templates/index.html
index 61ff8a7..2b2d3fa 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -12867,7 +12867,7 @@ document.addEventListener('mousedown', function(e) {
     <p id="fp-blurb" style="font-size:11px;color:var(--text2);line-height:1.5;margin:0 0 10px"></p>
     <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
       <label style="font-size:11px" id="fp-material-label">Material class
-        <select id="fp-material" class="btn" style="width:100%"></select>
+        <select id="fp-material" class="btn" style="width:100%" onchange="_fpMaterialChanged()"></select>
       </label>
       <label style="font-size:11px" id="fp-method-label">Method
         <select id="fp-method" class="btn" style="width:100%" onchange="_fpMethodChanged()"></select>
@@ -12884,6 +12884,7 @@ document.addEventListener('mousedown', function(e) {
         <div id="fp-regions-tier-note" style="font-size:9.5px;color:var(--text3);margin-top:3px;line-height:1.4"></div>
       </label>
       <div style="font-size:11px;grid-column:1 / -1">
+        <div id="fp-material-hint" style="color:var(--text3);font-size:10px;line-height:1.45;margin-bottom:6px"></div>
         <div id="fp-method-hint" style="color:var(--text3);font-size:10px;line-height:1.45;margin-bottom:6px"></div>
         <div id="fp-simple-options"></div>
         <details id="fp-advanced" style="margin-top:6px">
@@ -13018,6 +13019,22 @@ const FP_STRINGS = {
          'unless you add them.',
   applyNote: 'Adding replaces this tab’s current peak list with the ' +
              'suggested peaks. You can undo this (Ctrl+Z).',
+  // Label/hint override for one material-class dropdown option (2026-07-20).
+  // Only "mixed" gets an entry — conductor/semiconductor/insulator render
+  // exactly as before (bare backend value, no title attribute).
+  materials: {
+    mixed: {
+      label: 'mixed (analyte in matrix)',
+      hint: 'Your sample is an analyte embedded in a different matrix, ' +
+            'which can charge differently under x-rays than the matrix ' +
+            'does (differential charging). Peak width limits are relaxed ' +
+            'accordingly. The charge reference calibrates the MATRIX’s ' +
+            'potential — it may not apply to the analyte, so reported ' +
+            'positions carry additional, unquantified uncertainty. This ' +
+            'does not correct for that uncertainty; it only stops ' +
+            'assuming there isn’t any.',
+    },
+  },
   tips: {
     material: 'Conducting samples charge-correct differently from ' +
               'insulating ones, and the suggested peak shapes differ too. ' +
@@ -13410,7 +13427,12 @@ async function openFindPeaksModal() {
   document.getElementById('fp-regions-label').title = FP_STRINGS.tips.regions;
   const mat = document.getElementById('fp-material');
   mat.innerHTML = _fpMeta.material_classes
-    .map(m => `<option value="${_fpEsc(m)}">${_fpEsc(m)}</option>`).join('');
+    .map(m => {
+      const s = FP_STRINGS.materials[m] || {};
+      const title = s.hint ? ` title="${_fpEsc(s.hint)}"` : '';
+      return `<option value="${_fpEsc(m)}"${title}>${_fpEsc(s.label || m)}</option>`;
+    }).join('');
+  _fpMaterialChanged();
   document.getElementById('fp-regions-filter').value = '';
   _fpRegionsSelected = new Set();
   _fpExpandedElement = null;
@@ -13712,6 +13734,12 @@ function _fpSyncSelectionUI() {
   _fpRenderExpandedPanel();
 }
 
+function _fpMaterialChanged() {
+  const v = document.getElementById('fp-material').value;
+  const s = FP_STRINGS.materials[v] || {};
+  document.getElementById('fp-material-hint').textContent = s.hint || '';
+}
+
 function _fpMethodChanged() {
   const id = document.getElementById('fp-method').value;
   const m = (_fpMeta.methods || []).find(x => x.id === id);
diff --git a/tests/autofit/test_c1s_mixed_material_class.py b/tests/autofit/test_c1s_mixed_material_class.py
new file mode 100644
index 0000000..c827e62
--- /dev/null
+++ b/tests/autofit/test_c1s_mixed_material_class.py
@@ -0,0 +1,189 @@
+"""MIXED material class (2026-07-20 unit): analyte-in-matrix samples can
+show DIFFERENTIAL CHARGING between phases -- the sample charges
+non-uniformly under X-ray illumination, so a distribution of local surface
+potentials broadens observed peaks (inhomogeneous broadening). That
+broadening voids the single-species-homogeneity assumption behind the C 1s
+adventitious/contamination FWHM ceiling, so MIXED relaxes it.
+
+The provenance-audit trap this unit must NOT fall into: asserting a new
+numeric position/width value derived from this lab's own spectra (e.g.
+"MIXED widens the cap to 3.5 eV because that's what our UCl4-in-graphite
+samples do") would reintroduce exactly the self-reference the provenance
+audit removed -- wearing a feature label instead of a tier badge.
+Withdrawing an assumption needs no citation; asserting a new numeric
+window does, and this feature has none. So MIXED only RELAXES an existing
+constraint (widens toward the engine's own pre-existing numeric-stability
+ceiling) -- it never asserts a new position or width VALUE.
+
+Citations for the physical rationale (see also C1sModule.provenance()):
+Baer, Artyushkova, Cohen, Easton, Engelhard, Gengenbach, Greczynski, Mack,
+Morgan, Roberts, "XPS Guide: Charge neutralization and binding energy
+referencing for insulating samples," J. Vac. Sci. Technol. A 38, 031204
+(2020), DOI 10.1116/6.0000057 -- differential charging broadens peaks
+(examining the leading edge across analysis points/time "identif[ies]
+peak broadening as a result of differential charging"), and a single
+charge correction is insufficient once differential charging is present:
+internal referencing has "limited accuracy... often including multiphase
+and other complex samples." Greczynski & Hultman, "X-ray photoelectron
+spectroscopy: Towards reliable binding energy referencing," Prog. Mater.
+Sci. 107 (2020) 100591, DOI 10.1016/j.pmatsci.2019.100591 (referencing
+reliability, general).
+"""
+from __future__ import annotations
+
+import pytest
+
+from autofit.grammar import MaterialClass, Phase, resolve
+from autofit.regions.c1s import C1sModule, FWHM_RANGE_CONTAMINATION
+
+NON_MIXED = [MaterialClass.CONDUCTOR, MaterialClass.SEMICONDUCTOR,
+             MaterialClass.INSULATOR]
+
+
+def _by_constant(records, name):
+    hits = [r for r in records if r["constant"] == name]
+    assert len(hits) == 1, f"expected exactly one {name!r} record, got {len(hits)}"
+    return hits[0]
+
+
+def _resolve(material_class):
+    phase = Phase(id="sample", material_class=material_class, regions=("C 1s",))
+    return resolve([phase], "C 1s")
+
+
+def _contamination_slots(grammar):
+    """Every slot governed by FWHM_RANGE_CONTAMINATION under the DEFAULT
+    (non-MIXED) convention -- identified by its FLOOR, which MIXED never
+    changes, so this selector is stable across material classes."""
+    out = []
+    for c in grammar.candidates:
+        for s in c.slots:
+            if s.fwhm_range[0] == FWHM_RANGE_CONTAMINATION[0]:
+                out.append((c.name, s))
+    return out
+
+
+@pytest.mark.parametrize("material_class", NON_MIXED)
+def test_non_mixed_candidate_pool_unchanged(material_class):
+    """Non-regression, structural pin: conductor/semiconductor/insulator
+    must build EXACTLY the pre-MIXED contamination fwhm_range -- byte
+    (tuple) identical, not just close."""
+    g = _resolve(material_class)
+    slots = _contamination_slots(g)
+    assert slots, "fixture assumption: at least one contamination-governed slot"
+    for name, slot in slots:
+        assert slot.fwhm_range == FWHM_RANGE_CONTAMINATION, (
+            f"{name}/{slot.role}: fwhm_range changed for non-MIXED "
+            f"material_class {material_class}"
+        )
+
+
+@pytest.mark.parametrize("material_class", NON_MIXED)
+def test_non_mixed_candidate_names_unchanged(material_class):
+    """Non-regression at the coarsest level: the SET of candidate model
+    names build_candidates() produces must be identical across every
+    non-MIXED material class (it always was -- material_class was
+    previously read nowhere in this module)."""
+    names_conductor = {c.name for c in _resolve(MaterialClass.CONDUCTOR).candidates}
+    names_other = {c.name for c in _resolve(material_class).candidates}
+    assert names_conductor == names_other
+
+
+def test_mixed_relaxes_contamination_fwhm_ceiling():
+    """The one concrete, falsifiable claim: MIXED must actually widen the
+    contamination FWHM ceiling in the generated candidates -- otherwise
+    the feature is decorative. The FLOOR must NOT move: differential
+    charging only broadens a peak, it never narrows one, so there is no
+    physical basis to touch 0.8 eV."""
+    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
+    assert slots, "fixture assumption: at least one contamination-governed slot"
+    for name, slot in slots:
+        assert slot.fwhm_range[0] == FWHM_RANGE_CONTAMINATION[0], (
+            f"{name}/{slot.role}: MIXED changed the FLOOR -- no physical "
+            "justification for narrowing under differential charging"
+        )
+        assert slot.fwhm_range[1] > FWHM_RANGE_CONTAMINATION[1], (
+            f"{name}/{slot.role}: MIXED did not widen the ceiling -- decorative"
+        )
+
+
+def test_mixed_does_not_touch_position_windows_or_offsets():
+    """The provenance-audit trap, enforced structurally: MIXED relaxes
+    WIDTH only. Every BE window and every linked-offset (contaminant
+    center position, expressed relative to the graphitic main) must be
+    byte-identical to the conductor default -- tempting as it is to widen
+    a position window to admit an uncited differential-charging shift,
+    doing so would convert a known-unknown into a silently-permitted fit."""
+    g_conductor = _resolve(MaterialClass.CONDUCTOR)
+    g_mixed = _resolve(MaterialClass.MIXED)
+
+    windows = lambda g: {(c.name, s.role): s.be_window
+                         for c in g.candidates for s in c.slots}
+    assert windows(g_conductor) == windows(g_mixed), (
+        "MIXED must not alter any component's BE window"
+    )
+
+    offsets = lambda g: {(c.name, s.role): s.linked_offset_range
+                         for c in g.candidates for s in c.slots}
+    assert offsets(g_conductor) == offsets(g_mixed), (
+        "MIXED must not alter any linked-offset (contaminant center) range"
+    )
+
+
+def test_mixed_does_not_touch_unrelated_fwhm_families():
+    """Scope discipline: only the contamination/adventitious FWHM family
+    relaxes. The graphitic main, aromatic-polymer main, and satellite FWHM
+    ranges are untouched -- this unit's own instructions name the
+    adventitious cap as the one clear, in-scope case."""
+    g_conductor = _resolve(MaterialClass.CONDUCTOR)
+    g_mixed = _resolve(MaterialClass.MIXED)
+
+    def other_family_ranges(g):
+        return {(c.name, s.role): s.fwhm_range
+                for c in g.candidates for s in c.slots
+                if s.fwhm_range[0] != FWHM_RANGE_CONTAMINATION[0]}
+
+    assert other_family_ranges(g_conductor) == other_family_ranges(g_mixed)
+
+
+def test_mixed_provenance_relaxation_record_asserts_no_new_value():
+    """provenance() must document the relaxation itself: CONDITIONAL,
+    citing the differential-charging literature, and its `value` must
+    read as an ACTION (relax/remove a constraint) -- never a specific new
+    BE or width number. This is the literal test of the provenance-audit
+    design constraint: withdrawing an assumption needs no citation,
+    asserting a new numeric window does, and this record must not smuggle
+    one in under CONDITIONAL cover."""
+    records = C1sModule().provenance()
+    rec = _by_constant(records, "mixed_material_class_width_relaxation")
+    assert rec["status"] == "CONDITIONAL"
+    assert isinstance(rec["value"], str), (
+        "the relaxation record's value must be a descriptive action, not "
+        "a bare number that could read as a newly-asserted window"
+    )
+    assert "10.1116/6.0000057" in rec["source"], "Baer et al. 2020 DOI"
+    assert "baer" in rec["source"].lower()
+    assert "10.1016/j.pmatsci.2019.100591" in rec["source"], \
+        "Greczynski & Hultman 2020 DOI"
+    assert "greczynski" in rec["source"].lower()
+    assert "hultman" in rec["source"].lower()
+
+
+def test_mixed_provenance_numeric_guard_record_is_honestly_labeled():
+    """The residual finite ceiling (unavoidable -- the optimizer needs a
+    finite initial-value midpoint) must be labeled UNVERIFIED and
+    described as a numeric guard for fit stability, not a chemistry or
+    physics claim -- the same footing as dsg_alpha_cap's 'fitalg numeric
+    guard' language."""
+    records = C1sModule().provenance()
+    rec = _by_constant(records, "mixed_fwhm_ceiling_numeric_guard")
+    assert rec["status"] == "UNVERIFIED"
+    assert "numeric guard" in rec["source"].lower()
+    assert ("not a chemistry" in rec["source"].lower()
+            or "not a physical" in rec["source"].lower()
+            or "not a physics" in rec["source"].lower())
+    # the guard's own value must equal whatever ceiling build_candidates()
+    # actually uses under MIXED -- no drift between the doc and the code
+    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
+    actual_ceiling = slots[0][1].fwhm_range[1]
+    assert rec["value"] == actual_ceiling
diff --git a/tests/js/fp_material_mixed.test.js b/tests/js/fp_material_mixed.test.js
new file mode 100644
index 0000000..4397981
--- /dev/null
+++ b/tests/js/fp_material_mixed.test.js
@@ -0,0 +1,54 @@
+// MIXED material class (2026-07-20 unit) -- Find Peaks modal must offer a
+// clear label ("mixed (analyte in matrix)" reads better than bare "mixed")
+// and an advisory note: MIXED does not correct for differential charging,
+// it only stops ASSUMING there isn't any. Per the DECIDED scope
+// (Skye, 2026-07-17), the note must describe the charge reference as not
+// necessarily transferring to the analyte -- it must never imply the app
+// has corrected for anything.
+
+const { test } = require('node:test');
+const assert = require('node:assert');
+const fs = require('node:fs');
+const path = require('node:path');
+
+const html = fs.readFileSync(
+  path.join(__dirname, '../../templates/index.html'), 'utf8');
+
+function extract(re, name) {
+  const m = html.match(re);
+  assert.ok(m, name + ' not found in templates/index.html');
+  return m[0];
+}
+
+const FP_STRINGS = eval(
+  '(' + extract(/const FP_STRINGS = \{[\s\S]*?\n\};/, 'FP_STRINGS')
+    .replace(/^const FP_STRINGS = /, '').replace(/;$/, '') + ')');
+
+test('FP_STRINGS.materials.mixed has a clear, non-bare label', () => {
+  assert.ok(FP_STRINGS.materials && FP_STRINGS.materials.mixed,
+    'FP_STRINGS.materials.mixed must exist');
+  const label = FP_STRINGS.materials.mixed.label;
+  assert.match(label, /mixed/i);
+  assert.match(label, /analyte/i);
+  assert.notStrictEqual(label, 'mixed');
+});
+
+test('FP_STRINGS.materials.mixed hint is advisory, never claims correction', () => {
+  const hint = FP_STRINGS.materials.mixed.hint;
+  assert.match(hint, /charge reference/i);
+  assert.match(hint, /uncertain|not.*apply|may not/i);
+  // must not imply the app corrected for differential charging
+  assert.doesNotMatch(hint, /has been corrected/i);
+  assert.doesNotMatch(hint, /automatically adjust/i);
+  assert.doesNotMatch(hint, /we (have )?correct/i);
+});
+
+test('FP_STRINGS has no override entries for the other 3 material classes '
+     + '(dropdown rendering must stay byte-identical for them)', () => {
+  const materials = FP_STRINGS.materials || {};
+  for (const v of ['conductor', 'semiconductor', 'insulator']) {
+    assert.strictEqual(materials[v], undefined,
+      `${v} must not get an FP_STRINGS override -- non-MIXED rendering `
+      + 'must be unchanged');
+  }
+});
diff --git a/tests/test_api_analyze.py b/tests/test_api_analyze.py
index b1474d3..6c20510 100644
--- a/tests/test_api_analyze.py
+++ b/tests/test_api_analyze.py
@@ -51,7 +51,7 @@ def _upload_doublet(client, seed=7):
 def test_meta_menu(client):
     meta = client.get("/api/analyze/meta").get_json()
     assert set(meta["material_classes"]) == {"conductor", "insulator",
-                                             "semiconductor"}
+                                             "semiconductor", "mixed"}
     assert {"C 1s", "Cl 2p", "U 4f", "B 1s", "N 1s"} <= set(meta["regions"])
     methods = {m["id"]: m for m in meta["methods"]}
     assert set(methods) == {"least_squares", "ic_model_comparison",
@@ -172,6 +172,66 @@ def test_analyze_malformed_option_values_are_400s(client):
         assert "invalid option" in resp.get_json()["error"].lower()
 
 
+def test_analyze_material_class_mixed_accepted(client):
+    """MaterialClass.MIXED (2026-07-20 unit) round-trips through the
+    ordinary /api/analyze path exactly like any other material class --
+    Cl 2p's region module doesn't special-case it, so this is a plain
+    acceptance check, not a behavior check (that lives in
+    tests/autofit/test_c1s_mixed_material_class.py, against C 1s)."""
+    sid = _upload_doublet(client)
+    resp = client.post("/api/analyze", json={
+        "session_id": sid, "material_class": "mixed",
+        "regions": ["Cl 2p"], "method": "ic_model_comparison",
+        "roi": {"be_min": 192.0, "be_max": 205.0},
+        "options": {"n_refits": 2, "enable_proposal_pass": False},
+    })
+    assert resp.status_code == 200, resp.get_json()
+    assert resp.get_json()["success"] is True
+
+
+def test_analyze_start_material_class_mixed_accepted(client):
+    """Same acceptance check through the async /api/analyze/start path --
+    shares _validate_analyze_request with the sync route. Success here is
+    202 (job accepted), not 200 -- /api/analyze/start never returns the
+    result body directly; that comes from polling /api/analyze/progress."""
+    sid = _upload_doublet(client)
+    resp = client.post("/api/analyze/start", json={
+        "session_id": sid, "material_class": "mixed",
+        "regions": ["Cl 2p"], "method": "ic_model_comparison",
+        "roi": {"be_min": 192.0, "be_max": 205.0},
+        "options": {"n_refits": 2, "enable_proposal_pass": False},
+    })
+    assert resp.status_code == 202, resp.get_json()
+    assert "job_id" in resp.get_json()
+
+
+def test_material_class_does_not_affect_charge_correction(client):
+    """DECIDED (Skye, 2026-07-17): MIXED must not alter the charge-
+    correction step in any way -- not suppressed, not adjusted, not
+    conditionally applied. Verified at the mechanism, not just by reading
+    the diff: _validate_analyze_request's corrected/ROI-masked (x, y)
+    arrays -- the actual output of the cc_shift charge-correction step --
+    must be byte-identical regardless of material_class. material_class
+    only ever reaches Phase.material_class, consumed by grammar
+    resolution/candidate building, which happens strictly AFTER x/y are
+    already fixed."""
+    from app import _validate_analyze_request
+
+    sid = _upload_doublet(client)
+    upload_folder = client.application.config["UPLOAD_FOLDER"]
+    base = {
+        "session_id": sid, "regions": ["Cl 2p"],
+        "method": "ic_model_comparison", "cc_shift": 1.23,
+        "roi": {"be_min": 192.0, "be_max": 205.0},
+    }
+    ctx_conductor = _validate_analyze_request(
+        {**base, "material_class": "conductor"}, upload_folder)
+    ctx_mixed = _validate_analyze_request(
+        {**base, "material_class": "mixed"}, upload_folder)
+    assert np.array_equal(ctx_conductor.x, ctx_mixed.x)
+    assert np.array_equal(ctx_conductor.y, ctx_mixed.y)
+
+
 def test_json_sanitize_non_finite():
     """inf/NaN (degenerate-fit BIC values) must become null, not invalid
     JSON tokens browsers refuse to parse."""

codex
The diff scope matches the requested seven files. I’m going wider now: existing fitting defaults, prior provenance notes, region modules, and the test-data/adjudication trail, because the main risk here is a number or behavior justified outside the visible diff.
exec
/bin/zsh -lc "nl -ba app.py | sed -n '760,980p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'rg --files docs/autofit/test_data' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   760	              "center_max":   286.0,              // optional bound
   761	              "amplitude":    10000,
   762	              "amplitude_min": 0,                 // optional (default 0)
   763	              "fwhm":         1.5,
   764	              "fwhm_min":     0.2,                // optional
   765	              "fwhm_max":     3.0,                // optional
   766	              "gl_ratio":     0.3,                // Lorentzian fraction [0–1]
   767	              "fwhm_l":       1.5,                // asymmetric_gl only
   768	              "fwhm_r":       1.5,                // asymmetric_gl only
   769	              "alpha":        0.1,                // doniach_sunjic only
   770	              "constrain_to": null,               // id of master peak, or null
   771	              "splitting":    3.67,               // BE offset from master (eV)
   772	              "area_ratio":   0.75,               // amplitude = master × ratio
   773	              "fix_fwhm":     true                // lock FWHM to master
   774	            }
   775	          ]
   776	        }
   777	        """
   778	        body = request.get_json()
   779	        session_id = body.get("session_id", "")
   780	        _validate_session_id(session_id)
   781	
   782	        try:
   783	            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
   784	        except KeyError:
   785	            return _err(f"Session '{session_id}' not found", 404)
   786	
   787	        # Background config
   788	        bg_cfg = body.get("background", {})
   789	        bg_method = bg_cfg.get("method", "shirley")
   790	        bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
   791	        bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
   792	        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
   793	        try:
   794	            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
   795	        except (TypeError, ValueError):
   796	            return _err("endpoint_avg must be an integer")
   797	        manual_bg = bg_cfg.get("manual_bg")
   798	
   799	        # Peak specs
   800	        peak_specs = body.get("peaks", [])
   801	        if not peak_specs:
   802	            return _err("'peaks' list is empty – provide at least one peak")
   803	
   804	        # Validate peak ids are unique
   805	        ids = [p.get("id") for p in peak_specs]
   806	        if len(ids) != len(set(ids)):
   807	            return _err("Duplicate peak ids found – each peak must have a unique 'id'")
   808	
   809	        _ALLOWED_METHODS = {
   810	            "leastsq", "least_squares", "nelder",
   811	            "differential_evolution", "basinhopping",
   812	        }
   813	        fit_method = body.get("fit_method", "leastsq")
   814	        if fit_method not in _ALLOWED_METHODS:
   815	            return _err(f"Unknown fit_method '{fit_method}'")
   816	
   817	        # Bounded, type-checked n_perturb (audit F7; also covers the F9
   818	        # ValueError-on-bad-input case for this field). Reject out-of-range or
   819	        # non-integer values with a clean 400 instead of a 500 or a worker hang.
   820	        try:
   821	            n_perturb = int(body.get("n_perturb", 5))
   822	        except (TypeError, ValueError):
   823	            return _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
   824	        if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
   825	            return _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")
   826	
   827	        try:
   828	            result = fitting.run_fit(
   829	                energy=energy,
   830	                counts=counts,
   831	                peak_specs=peak_specs,
   832	                background_method=bg_method,
   833	                bg_start_idx=bg_start,
   834	                bg_end_idx=bg_end,
   835	                charge_shift_ev=0.0,
   836	                fit_kws={"method": fit_method},
   837	                manual_bg=manual_bg,
   838	                n_perturb=n_perturb,
   839	                endpoint_avg=endpoint_avg,
   840	            )
   841	        except ValueError as exc:
   842	            # Our own validation: unknown shape/method, self/circular constraint,
   843	            # "Master peak not found", bad numeric field, etc. (audit F10/F11).
   844	            return _err(str(exc))
   845	        except RuntimeError:
   846	            # Solver-internal failure (e.g. lmfit non-convergence). Log the
   847	            # detail; return a generic 422 that leaks no library internals.
   848	            app.logger.exception("Fit failed")
   849	            return _err("Fit failed — see server log for details.", 422)
   850	        except Exception:
   851	            app.logger.exception("Unexpected fitting error")
   852	            return _err("Internal fitting error — see server log.", 500)
   853	
   854	        return jsonify(result)
   855	
   856	    # ── Autofit analyze (opt-in Find Peaks; STRICTLY ADDITIVE — the manual
   857	    #    /api/fit path above is untouched) ──────────────────────────────────
   858	
   859	    @app.get("/api/analyze/meta")
   860	    def analyze_meta():
   861	        """Registered regions, material classes, the method menu with its
   862	        ADJUSTABLE defaults, and the full coverage-tier index (unit 3,
   863	        2026-07-11) — everything the opt-in Find Peaks UI needs to build
   864	        its form.  ``regions`` is UNCHANGED (still just the 5 curated
   865	        modules; existing consumers untouched); ``coverage`` is additive —
   866	        every selectable Z=1..96 region, tiered curated/machine/
   867	        structure_only, so the expanded selector can show real coverage
   868	        without ever presenting a fallback region as cited grammar."""
   869	        from autofit.coverage_index import region_coverage_index
   870	        from autofit.grammar import MaterialClass
   871	        from autofit.methods import available_methods
   872	        from autofit.regions import registered_regions
   873	
   874	        menu = [dict(m) for m in available_methods()
   875	                if m.get("id") in _ANALYZE_METHODS and m.get("implemented")]
   876	        for m in menu:
   877	            m["default_options"] = dict(_ANALYZE_METHODS[m["id"]])
   878	        return jsonify({
   879	            "regions": registered_regions(),
   880	            "coverage": region_coverage_index(),
   881	            "material_classes": [m.value for m in MaterialClass],
   882	            "methods": menu,
   883	        })
   884	
   885	    @app.post("/api/analyze")
   886	    @_require_json
   887	    def analyze():
   888	        """
   889	        Opt-in grammar-driven peak finding (spec §5A/§8).
   890	
   891	        Request body
   892	        ------------
   893	        {
   894	          "session_id":     "...",
   895	          "cc_shift":       0.0,          // frontend charge shift (corrected = raw − cc_shift)
   896	          "roi":            {"be_min": ..., "be_max": ...},   // corrected frame
   897	          "material_class": "conductor" | "insulator" | "semiconductor" | "mixed",
   898	          "regions":        ["Cl 2p", ...],   // registered region names
   899	          "phase":          {"id": "sample", "material": "graphite"},  // optional
   900	          "method":         "ic_model_comparison" | "least_squares"
   901	                            | "bayesian_exchange_mc" | "sparse_map",
   902	          "options":        {...},        // per-method; validated by the method
   903	          "peak_specs":     [...]         // least_squares only (manual baseline)
   904	        }
   905	
   906	        Returns the full MethodResult: candidate peaks with the per-peak
   907	        confidence vector, the analysis namespace (ambiguity flags, ranked
   908	        alternatives, constants provenance), diagnostics, and a review-gate
   909	        stub — results are candidates + honesty flags, not ground truth;
   910	        a NAMED human review is required before export (spec §8).
   911	
   912	        For a long analysis (60-240s), POST /api/analyze/start + poll
   913	        GET /api/analyze/progress/<job_id> instead — same validation, same
   914	        result shape, plus live sweep progress (Find Peaks UI, 2026-07-11).
   915	        This synchronous route is UNCHANGED: both now share
   916	        ``_validate_analyze_request``/``_run_analyze_method``/
   917	        ``_build_analyze_payload`` under the hood (a pure extract-method
   918	        refactor — tests/test_api_analyze.py pins the contract identical).
   919	        """
   920	        body = request.get_json(silent=True)
   921	        if not isinstance(body, dict):
   922	            return _err("request body must be a JSON object")
   923	        try:
   924	            ctx = _validate_analyze_request(body, app.config["UPLOAD_FOLDER"])
   925	            res = _run_analyze_method(ctx)
   926	        except _AnalyzeError as exc:
   927	            return _err(str(exc), exc.status)
   928	        payload = _build_analyze_payload(ctx, res)
   929	        return jsonify(_json_sanitize(payload))
   930	
   931	    @app.post("/api/analyze/start")
   932	    @_require_json
   933	    def analyze_start():
   934	        """
   935	        Async twin of POST /api/analyze for the Find Peaks progress
   936	        indicator (2026-07-11).  Same request body; same SYNCHRONOUS
   937	        validation (a malformed request is STILL an immediate 400, never
   938	        a spinner) — only the actual method execution (the genuinely
   939	        slow, honestly-long part) moves to a background thread.
   940	
   941	        Why a thread + a poll file, not SSE: production gunicorn runs the
   942	        default SYNC worker class (`--workers 4`, no gthread/gevent — see
   943	        the LaunchAgent plist), so a held-open SSE connection would tie up
   944	        an entire worker for the whole 60-240s analysis, on top of the
   945	        existing synchronous /api/analyze already doing exactly that for
   946	        ITS OWN request. A background thread returns the HTTP response
   947	        immediately (freeing the worker's request loop), and progress is
   948	        written to a small JSON file under the upload folder — file, not
   949	        an in-process dict, because gunicorn's workers are separate OS
   950	        processes and a poll can land on a different one (same reasoning
   951	        as the existing session .npz files: "no server-side memory state
   952	        ... compatible with multi-worker gunicorn").
   953	
   954	        Returns {"job_id": "..."} , 202.  Poll
   955	        GET /api/analyze/progress/<job_id> for {status, phase,
   956	        candidate_index, candidate_total, candidate_name, elapsed_sec,
   957	        message, result (once done), error (once errored)}.
   958	        """
   959	        body = request.get_json(silent=True)
   960	        if not isinstance(body, dict):
   961	            return _err("request body must be a JSON object")
   962	        upload_folder = app.config["UPLOAD_FOLDER"]
   963	        try:
   964	            ctx = _validate_analyze_request(body, upload_folder)
   965	        except _AnalyzeError as exc:
   966	            return _err(str(exc), exc.status)
   967	
   968	        job_id = str(uuid.uuid4())
   969	        _sweep_expired_jobs(upload_folder)
   970	        start_time = time.time()
   971	        _write_job_progress(job_id, upload_folder, {
   972	            "status": "running", "phase": "starting",
   973	            "candidate_index": None, "candidate_total": None,
   974	            "candidate_name": None, "elapsed_sec": 0.0,
   975	            "message": "starting analysis…",
   976	        })
   977	
   978	        def _progress_cb(evt: dict) -> None:
   979	            _write_job_progress(job_id, upload_folder, {
   980	                "status": "running",

 succeeded in 0ms:
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_8.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_8.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_8.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_8.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_4.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_4.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_5.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_5.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_7.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_7.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_6.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_6.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_2.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_2.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_3.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_3.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_1.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_1.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_0.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_0.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_6.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_6.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_5.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_5.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_1.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_1.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_0.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_0.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_2.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_2.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_3.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_3.xml
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json
docs/autofit/test_data/Project9_CasaXPS_newfit.proj.zip
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_8.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_8.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_6.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_6.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_5.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_5.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_1.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_1.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_0.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_0.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_2.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_2.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_3.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_3.xml
docs/autofit/test_data/4-GTA UCl4-BN.proj.zip
docs/autofit/test_data/UCl4_on_graphite.proj.zip
docs/autofit/test_data/B4C-UCl4.proj.zip
docs/autofit/test_data/Cl2p_projfit_test.proj.zip
docs/autofit/test_data/8-JT Graphite.proj.zip
docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.vgp
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_1.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_3.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_2.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_3.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_0.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_2.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_0.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_5.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_5.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_1.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_6.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_6.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_0.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_1.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_0.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_1.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_8.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_8.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_4.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_4.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_5.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_5.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_7.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_7.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_6.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_6.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_2.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_2.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_3.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_3.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_8.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_8.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A/XPS Survey.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A/XPS Survey.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A/C1s Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A/C1s Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A/U4f Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A/U4f Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A/Cl2p Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A/Cl2p Scan.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 E/U4f Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 E/XPS Survey.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 E/XPS Survey.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 E/C1s Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 E/C1s Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 E/U4f Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 C/XPS Survey.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 C/XPS Survey.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 C/C1s Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 C/C1s Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 C/U4f Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 C/U4f Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 C/Cl2p Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 C/Cl2p Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 D/C1s Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 D/U4f Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 D/U4f Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 D/XPS Survey.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 D/C1s Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 D/XPS Survey.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_7.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_7.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_4.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_6.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_6.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_3.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_5.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_4.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_5.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_1.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_1.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_2.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_2.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_0.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_0.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_3.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_3.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_8.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_8.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_0.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_2.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_2.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_3.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 F/U4f Scan.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 F/U4f Scan.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_1.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_0.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 F/C1s Scan.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_5.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_1.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_5.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 F/C1s Scan.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 F/XPS Survey.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 F/XPS Survey.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_6.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_6.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.VGD
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/XPS Survey.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/XPS Survey.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/C1s Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/C1s Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/U4f Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/U4f Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/Cl2p Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/Cl2p Scan.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_2.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_2.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_3.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_3.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_0.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_0.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_1.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_1.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_5.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_5.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_4.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_4.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_5.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_5.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_8.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_8.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_4.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_4.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_5.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_5.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_7.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_7.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_6.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_6.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_2.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_2.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_3.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_3.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_1.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_1.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_0.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_0.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_6.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_8.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_8.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_3.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_3.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_2.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_2.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_1.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_1.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/Cl2p Scan.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_6.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_0.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/Cl2p Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_0.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_4.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_0.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_0.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_1.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_1.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_3.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_3.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_2.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_2.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_5.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_5.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_4.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey_4.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/XPS Survey.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/Cl2p Scan_0.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/Cl2p Scan_0.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/Cl2p Scan_1.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/Cl2p Scan_1.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_3.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_3.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_2.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_2.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_0.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_0.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_1.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_1.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_5.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_5.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/U4f Scan_4.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_2.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_5.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_5.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_2.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_0.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_7.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_7.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_0.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_1.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_6.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_6.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_1.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_5.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_2.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_2.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_5.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_4.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_3.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_3.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_4.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_6.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_1.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_1.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_6.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_7.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_0.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_0.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_7.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_4.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_8.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_8.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_8.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_8.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_3.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_4.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/N1s Scan_4.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_0.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/U4f Scan_3.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_1.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_8.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_6.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_3.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_8.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.VGD
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_2.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_5.xml
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_7.xml

exec
/bin/zsh -lc "rg -n \"fwhm_max|15\\.0|15\\.00|15 eV|15eV|3\\.5|mixed|MIXED|differential|charging\" fitting.py autofit docs/autofit tests -S" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba autofit/regions/c1s.py | sed -n '70,470p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
   337	        )
   338	
   339	        def contam(key, linked_fwhm=None, offset=None,
   340	                   fwhm_range=None) -> ComponentSlot:
   341	            kw = {}
   342	            if linked_fwhm:
   343	                kw["fwhm_linked_to"] = linked_fwhm
   344	            if offset:
   345	                mid, hw = offset
   346	                kw["linked_to"] = "main_graphitic"
   347	                kw["linked_offset_range"] = (mid - hw, mid + hw)
   348	            return slot(f"contamination_{key}", C1S_WINDOWS[key],
   349	                        LineShape.PSEUDO_VOIGT,
   350	                        fwhm_range if fwhm_range is not None else contam_fwhm, **kw)
   351	
   352	        shared_decl = ((_SHARED_CONTAM_FWHM, contam_fwhm[0], contam_fwhm[1]),)
   353	        keys = ["CO", "C=O", "OC=O"]
   354	
   355	        candidates: list[CandidateModel] = []
   356	
   357	        def add(name, slots, shared=()):
   358	            candidates.append(CandidateModel(
   359	                name=name, background=BackgroundType.SHIRLEY,
   360	                slots=tuple(slots), shared_fwhm_params=tuple(shared),
   361	            ))
   362	
   363	        # --- A family: DS+G asymmetric main + satellite + contaminants ---
   364	        base_a = [graphitic_main_dsg(), shake_up]
   365	        plain = [contam(k) for k in keys]
   366	        add("A0_graphite_asym_satellite", base_a)
   367	        for n in (1, 2, 3):
   368	            add(f"A{n}_graphite_asym_sat_plus_{'_'.join(keys[:n])}",
   369	                base_a + plain[:n])
   370	
   371	        # --- A_linked: shared contamination width (Biesinger 2022) ---
   372	        linked = [contam(k, linked_fwhm=_SHARED_CONTAM_FWHM) for k in keys]
   373	        for n in (1, 2, 3):
   374	            add(f"A{n}_linked", base_a + linked[:n], shared_decl)
   375	
   376	        # --- A_linked_offset: + offset-parameterized contaminant centers ---
   377	        offset_linked = [
   378	            contam(k, linked_fwhm=_SHARED_CONTAM_FWHM, offset=CONTAM_OFFSETS[k])
   379	            for k in keys
   380	        ]
   381	        for n in (1, 2, 3):
   382	            add(f"A{n}_linked_offset", base_a + offset_linked[:n], shared_decl)
   383	
   384	        # --- AG family: asym-GL graphitic main (expert-fit parity family).
   385	        #     Contamination widths use the UNIFORM adjudicated cap — the
   386	        #     former split lab-practice (0.8, 3.5) convention was replaced
   387	        #     per adjudication #5; AG/MG now differ from A/M only in the
   388	        #     graphitic main lineshape. ---
   389	        base_ag = [graphitic_main_asymgl(), shake_up]
   390	        add("AG0_graphite_asymGL_satellite", base_ag)
   391	        for n in (1, 2, 3):
   392	            add(f"AG{n}_graphite_asymGL_sat_plus_{'_'.join(keys[:n])}",
   393	                base_ag + plain[:n])
   394	        for n in (1, 2, 3):
   395	            add(f"AG{n}_linked", base_ag + linked[:n], shared_decl)
   396	
   397	        # --- M family: mixed graphitic (DS+G) + aliphatic (PV) two mains ---
   398	        base_m = [graphitic_main_dsg(), aliphatic_main(), shake_up]
   399	        add("M0_graph_asym_aliph_sym_satellite", base_m)
   400	        for n in (1, 2, 3):
   401	            add(f"M{n}_graph_asym_aliph_sym_sat_{'_'.join(keys[:n])}",
   402	                base_m + plain[:n])
   403	
   404	        # --- MG family: the expert-practice STRUCTURE — asym-GL graphitic +
   405	        #     aliphatic + satellite + contaminants (uniform adjudicated
   406	        #     contamination cap).  The
   407	        #     reference C 1s fits are exactly MG2-shaped (graphitic asym-GL
   408	        #     284.5 + adventitious 284.8/285.9/287.6 + π→π* ~290.9).
   409	        #     The aliphatic center is OFFSET-LINKED to the graphitic main
   410	        #     (+0.2…+0.6 eV): with a free center the optimizer slides the
   411	        #     aliphatic into the graphitic flank and pegs the window floor
   412	        #     (overlap degeneracy, fitalg LIMITATIONS §9).  The offset window
   413	        #     brackets both the expert practice (+0.30: 284.8 vs 284.5) and
   414	        #     Biesinger's adventitious C-C/C-H at 284.8 vs graphite 284.4
   415	        #     (+0.4).  UNVERIFIED-empirical (labeled-set + convention). ---
   416	        def aliphatic_main_offset() -> ComponentSlot:
   417	            return slot("main_aliphatic", C1S_WINDOWS["aliphatic"],
   418	                        LineShape.PSEUDO_VOIGT, contam_fwhm,
   419	                        linked_to="main_graphitic",
   420	                        linked_offset_range=(0.2, 0.6))
   421	
   422	        base_mg = [graphitic_main_asymgl(), aliphatic_main_offset(), shake_up]
   423	        add("MG0_graphAsymGL_aliph_satellite", base_mg)
   424	        for n in (1, 2, 3):
   425	            add(f"MG{n}_graphAsymGL_aliph_sat_{'_'.join(keys[:n])}",
   426	                base_mg + plain[:n])
   427	
   428	        # --- B family: symmetric adventitious-carbon models (no satellite —
   429	        #     admissibility: shake-up requires an asymmetric sp² main) ---
   430	        aliph = aliphatic_main()
   431	        aliph_fwhm_param = "s_main_aliphatic_fwhm"
   432	        blinked = [contam(k, linked_fwhm=aliph_fwhm_param) for k in keys]
   433	        add("B2_linked", [aliph] + blinked[:2])
   434	        add("B3_linked", [aliph] + blinked[:3])
   435	        # plain-window symmetric variants (low-priority but admissible)
   436	        graph_sym = slot("main_graphitic", C1S_WINDOWS["graphitic"],
   437	                         LineShape.PSEUDO_VOIGT, main_fwhm)
   438	        add("B2_graphite_sym_CO_C=O", [graph_sym] + plain[:2])
   439	        add("B3_graphite_sym_CO_C=O_OC=O", [graph_sym] + plain[:3])
   440	
   441	        return candidates
   442	
   443	
   444	register_region(C1sModule())

 succeeded in 0ms:
fitting.py:722:    # Kernel half-width: ±3.5σ captures > 99.95% of the Gaussian. Use 3.5
fitting.py:724:    # `ceil(3.5σ)` doesn't coincide with integer m — that would put a
fitting.py:726:    # backwards compat with previously-saved (integer-m) fits. With 3.5
fitting.py:728:    half = max(1, int(np.ceil(3.5 * sigma_pts)))
fitting.py:821:    fwhm_max       : float – upper bound   (default 15.0)
fitting.py:867:             min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0))
fitting.py:916:         min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0),
docs/autofit/phase1-grammar-architecture-spec-v2.md:44:v1's pairwise `mixed{analyte, matrix}` **cannot** represent a 3-phase sample (BN/B4C/graphite) — three materials would fight over one reference/shift. Replaced with an explicit phase list.
docs/autofit/phase1-grammar-architecture-spec-v2.md:52:            shift_model } ]       # per-phase differential-charge shift
docs/autofit/phase1-grammar-architecture-spec-v2.md:55:- **Single-phase** (the general-use default) = a `phases` list of length 1; no differential-charging machinery instantiated.
docs/autofit/phase1-grammar-architecture-spec-v2.md:56:- **Composite** = length ≥ 2; the UI's `mixed` selection builds the list.
docs/autofit/phase1-grammar-architecture-spec-v2.md:80:**[Skye — simplified] Satellites and overlaps are modeled as peaks, one joint fit.** Confirmed against the literature: the U 4f asymmetry is multiplet/many-body in origin (not metallic screening), and an **LA-type asymmetric main line is documented best-fit practice**; the ~7–8 eV (and ~15 eV) satellites are **explicit components in the same fit**, not a separate step. **Oxidation-state *assignment* is out of scope (parked).** Two safeguards the engine keeps, reframed as general (not oxidation-state) logic: (i) **bound the asymmetry physically** (α within the U 4f lit range) so the tail cannot silently absorb a genuinely *separable* overlapping feature; (ii) the **residual/proposal pass flags unexplained tail structure** as a possible separate component for the analyst. Multi-element case: in U-in-BN, **N 1s (~398 eV) overlaps a U 4f satellite**, so the U 4f and N 1s grammars are composed and co-fit (§2).
docs/autofit/phase1-grammar-architecture-spec-v2.md:88:### 3.5 N 1s — the charge-reference exemplar
docs/autofit/phase1-grammar-architecture-spec-v2.md:96:- **Differential charging** in a composite is a **per-phase rigid shift** (`shift_model`), a fit parameter — never assumed away. Single-phase samples keep the current single-shift behavior.
autofit/reference.py:238:    ("C 1s", 270.0, 315.0),      # matches isC1sTab (index.html:6548)
autofit/reference.py:242:    ("U 4f", 370.0, 415.0),      # span ~35 eV so their midpoint lands ~387
tests/test_xps_reference.py:42:        "expected_region_ev": {"min": 203.5, "max": 214.0, "basis": "observed-reference-range"},
docs/autofit/inventory/sensitivity_sweeps.jsonl:81:{"anchor": "C1s_Scan_8", "constant": "<default+proposal_on>", "extra_opts": {"enable_proposal_pass": true}, "group": "proposal", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 167.8, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": null}
docs/autofit/inventory/sensitivity_sweeps.jsonl:82:{"anchor": "C1s_Scan_8", "constant": "PROPOSAL_FLAG_RATIO", "extra_opts": {"enable_proposal_pass": true}, "group": "proposal", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 169.8, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": 3.0}
docs/autofit/inventory/sensitivity_sweeps.jsonl:83:{"anchor": "C1s_Scan_8", "constant": "PROPOSAL_FLAG_RATIO", "extra_opts": {"enable_proposal_pass": true}, "group": "proposal", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 179.5, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": 8.0}
docs/autofit/inventory/sensitivity_sweeps.jsonl:84:{"anchor": "C1s_Scan_8", "constant": "DSG_ALPHA_RANGE_GRAPHITIC_upper", "group": "c1s_alpha", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 119.3, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": 0.2}
docs/autofit/inventory/sensitivity_sweeps.jsonl:85:{"anchor": "C1s_Scan_8", "constant": "DSG_ALPHA_RANGE_GRAPHITIC_upper", "group": "c1s_alpha", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 135.0, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": 0.5}
docs/autofit/inventory/sensitivity_sweeps.jsonl:86:{"anchor": "C1s_Scan_8", "constant": "<default>", "group": "options", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 105.3, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": null}
tests/test_api_analyze.py:54:                                             "semiconductor", "mixed"}
tests/test_api_analyze.py:175:def test_analyze_material_class_mixed_accepted(client):
tests/test_api_analyze.py:176:    """MaterialClass.MIXED (2026-07-20 unit) round-trips through the
tests/test_api_analyze.py:180:    tests/autofit/test_c1s_mixed_material_class.py, against C 1s)."""
tests/test_api_analyze.py:183:        "session_id": sid, "material_class": "mixed",
tests/test_api_analyze.py:192:def test_analyze_start_material_class_mixed_accepted(client):
tests/test_api_analyze.py:199:        "session_id": sid, "material_class": "mixed",
tests/test_api_analyze.py:209:    """DECIDED (Skye, 2026-07-17): MIXED must not alter the charge-
tests/test_api_analyze.py:229:    ctx_mixed = _validate_analyze_request(
tests/test_api_analyze.py:230:        {**base, "material_class": "mixed"}, upload_folder)
tests/test_api_analyze.py:231:    assert np.array_equal(ctx_conductor.x, ctx_mixed.x)
tests/test_api_analyze.py:232:    assert np.array_equal(ctx_conductor.y, ctx_mixed.y)
autofit/engine.py:107:# slots keep their own cited ranges (C 1s satellite 5.5, U 4f mains 3.5,
autofit/engine.py:158:PROPOSAL_MIN_FIT_BUDGET_SEC = 15.0
autofit/engine.py:760:    cap is grammar-sanctioned-broad (C 1s π→π* satellite 5.5, U 4f mains 3.5,
autofit/engine.py:2584:        # A future mixed-background grammar only affects DETECTION here —
autofit/grammar.py:16:``mixed{analyte, matrix}``.  Every :class:`ComponentSlot` carries a
autofit/grammar.py:81:    # Analyte embedded in a different matrix (2026-07-20): differential
autofit/grammar.py:82:    # charging between analyte and matrix is possible, which voids the
autofit/grammar.py:84:    # width ceilings. MIXED only RELAXES existing constraints (region
autofit/grammar.py:91:    MIXED = "mixed"
docs/autofit/inventory/reference_fits_inventory.json:600:     "amp": 11315.0,
docs/autofit/inventory/reference_fits_inventory.json:1351:     "amp": 1013.5,
docs/autofit/inventory/reference_fits_inventory.json:1431:     "fwhm": 3.575,
docs/autofit/inventory/reference_fits_inventory.json:1440:     "fwhm": 3.575,
docs/autofit/inventory/reference_fits_inventory.json:2744:     "fwhm": 3.527,
docs/autofit/inventory/reference_fits_inventory.json:3148:     "amp": 1803.5,
docs/autofit/inventory/reference_fits_inventory.json:3709:     "amp": 2853.5,
docs/autofit/inventory/reference_fits_inventory.json:4142:     "fwhm": 3.548,
docs/autofit/inventory/reference_fits_inventory.json:4507:     "fwhm": 3.595,
docs/autofit/inventory/reference_fits_inventory.json:4622:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:4634:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:5037:     "fwhm": 3.548,
docs/autofit/inventory/reference_fits_inventory.json:5402:     "fwhm": 3.595,
docs/autofit/inventory/reference_fits_inventory.json:5517:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:5529:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:5799:     "fwhm": 3.524,
autofit/confidence.py:7:  unavailable}``; kinds are NEVER mixed in one numeric field.  ``covariance``
tests/fixtures/curated_records_snapshot.json:486:      "curation_notes": "Curated: L3M4,5M4,5 (1G) — the principal Cu LMM line. Cu2O/CuO LMM kinetic energies (Wagner-plot values) were not recoverable from archived NIST pages — region floor is fallback to cover them; hand-check. NIST also tabulates M3VV (61 eV, PEJ82) and L2-series satellite offsets (SA- records, Scho72 et al.) — not curated in v1. Values recovered from NIST SRD 20 v3.5 via Internet Archive snapshot (2004)."
tests/fixtures/curated_records_snapshot.json:493:      "curation_notes": "Curated: 4f doublet + 4d family. Nominals are U METAL values, but real samples are almost always oxidized (UCl4, U4+/U6+ oxides) and sit several eV HIGHER — expected_region_ev bands are therefore widened upward through the common oxidation states (curator-directed, 2026-06) so orientation bands cover where actual sample peaks appear. U-4d3/2 nominal is DERIVED (4d5/2 + DS-4d median), not a direct NIST record — hand-check. UO2/U3O8/UO3 4f7/2 chemical-state values were NOT archive-recoverable (compound pages 2-5 unarchived) — uncurated; NIST v4.1 line list confirms 4f7/2,sat / 4f5/2,sat satellite records exist but their values were not recoverable — uncurated. Shallow lines (4s, 5d, 5p3/2, 6p, 6s) are curated from the complete 2004 NIST element page. 4p3/2 exists in NIST's v4.1 line list but no value was archive-recoverable — uncurated. U 5f is NOT tabulated as a line in NIST SRD 20 (valence character) — intentionally absent, not an omission. 5p1/2 is not in NIST's line list — 5p3/2 is curated unpaired (the DS-5p record, 63.6 eV FBWF74, is noted but unused). One NIST compound record (U3O7 4d3/2 = 105.3 eV) is a physically impossible data-entry artifact and was discarded. Asymmetric U 4f broadening in U(IV) compounds arises from 5f multiplet coupling — use multiplet models, not single DS peaks (see CLAUDE.md). Values recovered from NIST SRD 20 v3.5/v4.1 via Internet Archive snapshots (2004/2015/2016/2023)."
tests/fixtures/curated_records_snapshot.json:500:      "curation_notes": "Curated: 1s. NIST also tabulates a 1s surface core-level shift (SS-1s -0.95, Pate86) — not modeled. C KLL/KVV Auger values were not archive-recoverable — uncurated. Higher-BE chemical states (carbonates ~289.5+, fluorocarbons CF2/CF3) are NOT represented in the recovered NIST records — region top may need upward extension after hand-verification. Values recovered from NIST SRD 20 v3.5/v4.1 via Internet Archive snapshots (2004/2015/2016)."
tests/fixtures/curated_records_snapshot.json:507:      "curation_notes": "Curated: 2p doublet. The single archive-recoverable NIST elemental-page record (TPPF90) has an unidentified specimen (detail popup unarchived) — its 198.30 eV sits in metal-chloride territory; hand-check against live SRD 20. Chloride-compound 2p values were NOT archive-recoverable (the recovered compound page holds only Cl 1s records near 2815 eV from hard-X-ray work, beyond Al Ka reach) — region is fallback. Cl 2s not recovered — uncurated. In actinide chlorides (e.g. UCl4) the Cl 2p region overlaps U 5p3/2 — expect interference. Values recovered from NIST SRD 20 v4.1 via Internet Archive snapshots (2015/2016)."
tests/fixtures/curated_records_snapshot.json:514:      "curation_notes": "Curated: 2p doublet (LMM Auger lives in auger-lines.json). NIST also tabulates 3s (122.2-122.9), 3p3/2 (75.14, Seah89 NIST-evaluated), 2s (1096.4-1097.1), DS-3p (2.2-2.39) — not curated in v1. Cu2O/CuO/Cu(OH)2 chemical-state values and the Cu(II) shake-up satellites (~940-945 eV) were not recoverable from archived NIST pages — uncurated. Values recovered from NIST SRD 20 v3.5/v4.1 via Internet Archive snapshots (2004/2016)."
tests/fixtures/curated_records_snapshot.json:521:      "curation_notes": "Curated: 3d doublet. Nb-3d3/2 nominal is DERIVED (3d5/2 + DS-3d median), not a direct NIST record — the page holding direct 3d3/2 values was not archive-recoverable; hand-check. NIST also tabulates 3p3/2 (360.4-360.7), 3s (466.8-467.1), 4p3/2 (30.77, Powe95 NIST-evaluated), 4s (56.4), DS-3p (15.4-15.5), M5N23V Auger KE (167.6, NIST-evaluated) — not curated in v1. Oxide values (NbO/NbO2/Nb2O5) were not recoverable from archived NIST pages — region tops are fallback. Values recovered from NIST SRD 20 v3.5/v4.1 via Internet Archive snapshots (2004/2016)."
tests/fixtures/curated_records_snapshot.json:528:      "curation_notes": "O KLL Auger KE is NOT curated: NIST tabulates only Auger-parameter records (AP-1s,KVV 1041.5 / 1043.9, KKMP88) whose KE decomposition is ambiguous — needs hand-verification against live SRD 20. NIST 1s records (531.2-533.0) are compound/adsorbate-hosted; the lattice-oxide low end (~529-530.5) is not represented in archive-recoverable records, hence the conservative-fallback region. Values recovered from NIST SRD 20 v3.5/v4.1 via Internet Archive snapshots (2004/2016)."
tests/fixtures/curated_records_snapshot.json:1594:              "be_ev": 293.5,
tests/fixtures/curated_records_snapshot.json:1904:              "state": "U₃O₈ (mixed)",
docs/autofit/inventory/cwt_calibration.jsonl:217:{"key": "h0:0.05:5000:sigmoid:16", "section": "h0", "step": 0.05, "level": 5000.0, "bg": "sigmoid", "seed": 16, "max_prom_z": 3.5625, "n_ge_gate": 0}
docs/autofit/inventory/cwt_calibration.jsonl:431:{"key": "h0:0.1:500:sigmoid:5", "section": "h0", "step": 0.1, "level": 500.0, "bg": "sigmoid", "seed": 5, "max_prom_z": 3.5386, "n_ge_gate": 0}
docs/autofit/inventory/cwt_calibration.jsonl:498:{"key": "h0:0.1:5000:slope:22", "section": "h0", "step": 0.1, "level": 5000.0, "bg": "slope", "seed": 22, "max_prom_z": 3.5887, "n_ge_gate": 0}
docs/autofit/inventory/cwt_calibration.jsonl:566:{"key": "h0:0.1:50000:slope:15", "section": "h0", "step": 0.1, "level": 50000.0, "bg": "slope", "seed": 15, "max_prom_z": 3.5616, "n_ge_gate": 0}
docs/autofit/PROGRESS.md:30:| Multivariate MCR method (stretch #5) | DONE (synthetic-validated) | ✅ 8 tests | `methods/multivariate_mcr.py`: PCA scree rank estimate (variance_target 0.995 UNVERIFIED, user-overridable, scree always reported) + MCR-ALS (row-wise NNLS alternation, deterministic SVD init, non-negativity on C and S) on a multi-spectrum matrix; `build_matrix` interpolation helper for mixed-grid repeat scans. HONESTY: `peaks=[]` by design (chemical states, not fitted peaks); rotational ambiguity stated in the payload; negative intensities rejected loudly. Synthetic: rank recovered, pure-spectra corr >0.98 (permutation-free), concentration corr >0.99, deterministic. Real-data validation on the repeat-scan matrices = follow-up. Codex checkpoint pending. |
docs/autofit/PROGRESS.md:31:| Sparse/MAP method (stretch #4) | DONE (synthetic-validated) | ✅ 9 tests | `methods/sparse_map.py`: L1 Gaussian-atom dictionary on grammar slot windows (data-grid centers × log FWHM ladder), non-negative coordinate descent, geometric λ path, debiased NNLS refit, BIC (engine convention) model-size selection; cluster merge scaled to the resolved feature's width. Honesty: `uncertainty_kind='unavailable_post_selection'` (no fabricated σ), asymmetric slots flagged not-expressible, UNVERIFIED tunables in payload, limitations stated (decision-matrix entry 4: STAM:Methods 2024 DOI 10.1080/27660400.2024.2373046 + Tibshirani 1996). Synthetic ground truth: exact peak-count recovery, centers ≤0.15 eV, debiased amplitudes ≤15%, deterministic (no RNG). NOT validated on real anchors (its regime is few-separated-peaks; the real regions are overlap-heavy — documented). Codex checkpoint pending. |
docs/autofit/PROGRESS.md:432:2. **Lab-practice contamination width range** (0.8,3.5) for AG/MG families
docs/autofit/PROGRESS.md:582:- **BLOCKER** validation JSONL still a mixed append/resume record (28 stale
docs/autofit/PROGRESS.md:747:| Cl0rw_relaxed_freewidth | 1793.5 / 1.631 | 1812.7 / 2.686 | ratio@max AND fwhm_excess@min |
docs/autofit/PROGRESS.md:765:- *Residual localization (differential-charging check):* consistent on both
docs/autofit/PROGRESS.md:768:  −2.1…−4.8 eV (2.6–3.4σ). The low-BE surplus is where a lower-charging
docs/autofit/PROGRESS.md:770:  consistent with (not proof of) differential charging. The proposal pass
docs/autofit/PROGRESS.md:777:vs labeled-set 3.5 for AG/MG) with a uniform ~2.0 eV cap — "a cap, not a
docs/autofit/PROGRESS.md:862:   differential-charging residual evidence, and the Scan_8 parity
docs/autofit/PROGRESS.md:876:window, charging replica, asymmetric truth, background mismatch —
docs/autofit/PROGRESS.md:903:charging replica offset-0 (center-pegged true model not promoted by the
docs/autofit/PROGRESS.md:1280:mixed-sign pass-through match the documented policy. **The Tougaard
docs/autofit/PROGRESS.md:1358:with the exact expression the methods use) instead of a 400/500; mixed
docs/autofit/PROGRESS.md:1444:and API pins for the mixed deep+structural payload (structural_only
docs/autofit/PROGRESS.md:1460:mixed-API pin asserts actual derived record content (structure /
docs/autofit/PROGRESS.md:1966:  OWN cited ranges — C 1s satellite 5.5, U 4f mains 3.5 / sats 4.5, B 1s
docs/autofit/PROGRESS.md:2741:  the Cl 2p hypothesis-rejection + differential-charging residual
docs/autofit/PROGRESS.md:2979:fully; mixed curated+unassigned model branches per-slot; linked-slot
docs/autofit/PROGRESS.md:3147:The array-length fix was still wrong for a MIXED curated+structural
docs/autofit/PROGRESS.md:3149:stays non-empty (per `test_api_mixed_deep_plus_structural_runs_and_flags`)
docs/autofit/PROGRESS.md:3153:key at all, while every normal payload (success or failure, mixed or
docs/autofit/PROGRESS.md:3157:(an unrealistic fixture that let the new mixed-success test fail for
tests/test_browser_find_peaks_coverage.py:260:        assert 690.0 <= float(roi_min) <= 715.0    # Fe 2p3/2 neighborhood
tests/test_mixed_ds_lacx_e2e.py:89:print("OK — mixed DS + LACX recovered:")
tests/fixtures/xps_legacy_snapshot.json:323:    "be": 293.5,
tests/fixtures/xps_legacy_snapshot.json:491:    "state": "U₃O₈ (mixed)",
tests/fixtures/machine_records_snapshot.json:1248:    "max": 573.54,
tests/fixtures/machine_records_snapshot.json:1389:    "min": 243.5
tests/fixtures/machine_records_snapshot.json:1392:   "nominal_be_ev": 243.5,
docs/autofit/inventory/replicate_noise_survey.json:28:    "negative_intercept_clamped: a=-3.54e+04 -> 0",
docs/autofit/inventory/replicate_noise_survey.json:402:    "negative_intercept_clamped: a=-3.54e+04 -> 0",
docs/autofit/adjudication-decisions.md:27:- **Ruled out:** hydrolysis / second chloride species — the UCl₄ is **strictly anhydrous** (glovebox synthesis). If independent widths do *not* resolve it, check **differential charging** (insulator-in-conductor composite) and **beam damage** (ratio vs. scan number) — secondary only.
docs/autofit/adjudication-decisions.md:30:- **Adventitious / contamination C 1s components → cap FWHM at ~2.0 eV** (literature-reasonable upper bound; instrument/pass-energy-dependent — a *cap*, not a target). Replace the engine's split **1.6 / 3.5 eV** contamination caps with a **uniform ~2.0 eV.**
tests/js/fp_material_mixed.test.js:1:// MIXED material class (2026-07-20 unit) -- Find Peaks modal must offer a
tests/js/fp_material_mixed.test.js:2:// clear label ("mixed (analyte in matrix)" reads better than bare "mixed")
tests/js/fp_material_mixed.test.js:3:// and an advisory note: MIXED does not correct for differential charging,
tests/js/fp_material_mixed.test.js:27:test('FP_STRINGS.materials.mixed has a clear, non-bare label', () => {
tests/js/fp_material_mixed.test.js:28:  assert.ok(FP_STRINGS.materials && FP_STRINGS.materials.mixed,
tests/js/fp_material_mixed.test.js:29:    'FP_STRINGS.materials.mixed must exist');
tests/js/fp_material_mixed.test.js:30:  const label = FP_STRINGS.materials.mixed.label;
tests/js/fp_material_mixed.test.js:31:  assert.match(label, /mixed/i);
tests/js/fp_material_mixed.test.js:33:  assert.notStrictEqual(label, 'mixed');
tests/js/fp_material_mixed.test.js:36:test('FP_STRINGS.materials.mixed hint is advisory, never claims correction', () => {
tests/js/fp_material_mixed.test.js:37:  const hint = FP_STRINGS.materials.mixed.hint;
tests/js/fp_material_mixed.test.js:40:  // must not imply the app corrected for differential charging
tests/js/fp_material_mixed.test.js:51:      `${v} must not get an FP_STRINGS override -- non-MIXED rendering `
docs/autofit/inventory/bayesian_u4f_tuned_run.jsonl:1:{"anchor": "U4f_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 3274.113862379425, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.0932443063850315, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.0932443063850315, "min_effective_sample_size": 19.57108508725822, "n_components": 2, "n_posterior_samples": 2000, "name": "U0_mains", "posterior_weight": 2.0510286183062296e-218, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 573.6224509118443, "swap_acceptance": 0.583}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2826.7133119480504, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.6924659012925076, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.6924659012925076, "min_effective_sample_size": 15.011315092016366, "n_components": 4, "n_posterior_samples": 2000, "name": "U1_mains_satpair", "posterior_weight": 4.1263111460321444e-24, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 147.60795818246072, "swap_acceptance": 0.5014166666666666}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2801.11228799011, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.6678119437058285, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.6678119437058285, "min_effective_sample_size": 6.564437533639988, "n_components": 4, "n_posterior_samples": 2000, "name": "U1b_mains_satpair_freesep", "posterior_weight": 5.419327649621575e-13, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 136.5297064232104, "swap_acceptance": 0.49341666666666667}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2772.8686535390593, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 2.5158935620684133, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 2.5158935620684133, "min_effective_sample_size": 10.572444173558178, "n_components": 4, "n_posterior_samples": 2000, "name": "U2_mains_satfree", "posterior_weight": 0.999999999999458, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 123.76980566063898, "swap_acceptance": 0.49283333333333335}], "confidence": {"main_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 10.857960634534383, "ci_level": 0.68, "ci_low": 10.848031595158869, "ess": 74.10023929838128, "median": 10.85284414030929}, "ratio": {"ci_high": 0.6621946320074098, "ci_level": 0.68, "ci_low": 0.6573089625421653, "ess": 66.47974103792622, "median": 0.6598473953430019}}}}, "main_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 10.6 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"alpha": {"ci_high": 1.2377839105188733, "ci_level": 0.68, "ci_low": 1.1914786167002223, "ess": 18.545654282176088, "median": 1.207991578682303}, "amplitude": {"ci_high": 16128.390042255734, "ci_level": 0.68, "ci_low": 16050.667304065419, "ess": 10.572444173558178, "median": 16068.103592594733}, "beta": {"ci_high": 2.88725703769715, "ci_level": 0.68, "ci_low": 2.7386461819853074, "ess": 16.4062999417237, "median": 2.808763113800193}, "center": {"ci_high": 380.63292194454647, "ci_level": 0.68, "ci_low": 380.6234404645645, "ess": 27.81082842204054, "median": 380.62853648176514}, "fwhm": {"ci_high": 2.7173788725244896, "ci_level": 0.68, "ci_low": 2.598695462981316, "ess": 16.247127412703442, "median": 2.6539219203174924}, "m": {"ci_high": 6.859605882824331, "ci_level": 0.68, "ci_low": 5.7081801731179125, "ess": 14.11754650965665, "median": 6.381701994990381}}}}, "satellite_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2268.529577525702, "ci_level": 0.68, "ci_low": 2195.4939904315124, "ess": 75.41687892686828, "median": 2232.1972804245197}, "fwhm": {"ci_high": 2.5747560532934526, "ci_level": 0.68, "ci_low": 2.4729773313430443, "ess": 80.29533062885349, "median": 2.5241901879102784}, "gl_ratio": {"ci_high": 0.06457049982095478, "ci_level": 0.68, "ci_low": 0.0062847376945130845, "ess": 54.479102349422384, "median": 0.022923447360258774}, "offset": {"ci_high": 6.428304617579634, "ci_level": 0.68, "ci_low": 6.388760815240822, "ess": 273.43147855721935, "median": 6.409352959533626}}}}, "satellite_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 20.9 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2446.782916531736, "ci_level": 0.68, "ci_low": 2334.7252986024814, "ess": 27.315611807356188, "median": 2420.757152328541}, "fwhm": {"ci_high": 2.590673707643128, "ci_level": 0.68, "ci_low": 2.448327014125724, "ess": 32.50450267403081, "median": 2.517918287691745}, "gl_ratio": {"ci_high": 0.8704291822613868, "ci_level": 0.68, "ci_low": 0.6106182031892832, "ess": 20.94925624138724, "median": 0.7449538956814956}, "offset": {"ci_high": 6.083009691406851, "ci_level": 0.68, "ci_low": 6.041074004303911, "ess": 134.5219354156989, "median": 6.061859789293894}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 16, "n_sweeps": 4000}, "expert": {"chi_reduced": 1.7129708462685973, "peaks": [{"amplitude": 16166.479492182621, "center": 380.6179633862216, "fwhm": 2.737096332065471, "name": "U 4f7/2", "shape": "LACX"}, {"amplitude": 10508.211669918705, "center": 391.5179633862216, "fwhm": 2.737096332065471, "name": "U 4f5/2", "shape": "LACX"}, {"amplitude": 2214.057182779663, "center": 397.8977471164976, "fwhm": 2.556902102730025, "name": "Satellite 2", "shape": "Voigt"}, {"amplitude": 2436.210453422618, "center": 386.6877864274504, "fwhm": 2.512044323701672, "name": "Satellite 1", "shape": "Voigt"}]}, "method": "bayesian_exchange_mc", "peaks": [{"alpha": 1.207991578682303, "amplitude": 16068.103592594733, "beta": 2.808763113800193, "center": 380.62853648176514, "fwhm": 2.6539219203174924, "m": 6.381701994990381, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f72", "shape": "la_casaxps"}, {"alpha": 1.207991578682303, "amplitude": 10602.496303675165, "beta": 2.808763113800193, "center": 391.4813806220744, "fwhm": 2.6539219203174924, "m": 6.381701994990381, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f52", "shape": "la_casaxps"}, {"amplitude": 2420.757152328541, "center": 386.69039627105906, "fwhm": 2.517918287691745, "gl_ratio": 0.7449538956814956, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f72", "shape": "pseudo_voigt_gl"}, {"amplitude": 2232.1972804245197, "center": 397.89073358160806, "fwhm": 2.5241901879102784, "gl_ratio": 0.022923447360258774, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f52", "shape": "pseudo_voigt_gl"}], "runtime_s": 1088.1, "seed": 0, "selection_warning": null, "sigma_hat": 123.76980566063898, "success": true, "winner": "U2_mains_satfree"}
docs/autofit/bayesian-real-validation.md:81:| default | 1 | U2_mains_satfree | 6.4 | 3.5 | 129.3 | 0.45 | 3.8 | YES | YES | 312.0 |
autofit/methods/bayesian_exchange_mc.py:42:  mixed with 'covariance'/'stability_mad' numerics (spec §5 discipline).
autofit/methods/bayesian_exchange_mc.py:559:                # typed posterior kind — NEVER mixed with covariance /
tests/js/find_peaks_plain_message.test.js:116:test('_fpPlainMessage: a MIXED request that succeeded must NOT trigger the stub either (Codex-caught, round 2)', () => {
tests/js/find_peaks_plain_message.test.js:117:  // Regression: a mixed curated+structural request (e.g. regions
tests/js/find_peaks_plain_message.test.js:121:  // test_api_mixed_deep_plus_structural_runs_and_flags) — a bare
tests/js/find_peaks_plain_message.test.js:136:test('_fpPlainMessage: a MIXED request that failed for an unrelated reason must NOT trigger the stub', () => {
tests/js/find_peaks_plain_message.test.js:139:  // it could be an ordinary no-survivors failure in a mixed request.
tests/autofit/stress_cases.py:23:                   charging replica, wrong background); the method must
tests/autofit/stress_cases.py:260:# Regime 4 — differential-charging replica (truth outside the model space)
tests/autofit/stress_cases.py:263:def charging_tail_case(seed: int, with_replica_candidate: bool) -> StressCase:
tests/autofit/stress_cases.py:278:        name=("charging_with_replica_candidate" if with_replica_candidate
tests/autofit/stress_cases.py:279:              else "charging_no_replica_candidate"),
tests/autofit/stress_cases.py:280:        regime="charging_tail",
tests/autofit/stress_cases.py:286:        notes="25% replica at −0.8 eV (differential charging shape)",
tests/autofit/stress_cases.py:331:    structure — charging replica, asym tails, bg curvature — where
tests/autofit/stress_cases.py:482:        # charging replica
tests/autofit/stress_cases.py:483:        charging_tail_case(seed=41 + o, with_replica_candidate=False),
tests/autofit/stress_cases.py:484:        charging_tail_case(seed=42 + o, with_replica_candidate=True),
tests/autofit/test_bayesian_method.py:24:TRUE_SIGMA = 15.0
tests/autofit/test_bayesian_method.py:39:                                _slot("p2", (101.5, 103.5))))
tests/autofit/test_bayesian_method.py:42:                                  _slot("p2", (101.5, 103.5)),
tests/autofit/test_bayesian_method.py:256:                                   _slot("p2", (101.5, 103.5))))
tests/autofit/test_bayesian_method.py:259:                                   _slot("p2", (101.5, 103.5))))
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:17:{"anchor": "Cl2p_Scan_0", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1473.2304436039562, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.7395217912047656, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.7395217912047656, "min_effective_sample_size": 20.684374308336903, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 3.5319931601474715e-15, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 103.13100347901381, "swap_acceptance": 0.5817575757575758}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1439.9535295552473, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.7380618131642223, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.7380618131642223, "min_effective_sample_size": 7.225896048456788, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 0.9999999999999964, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 85.62223233675857, "swap_acceptance": 0.5392121212121213}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.579171561985343, "ci_level": 0.68, "ci_low": 1.55734096719466, "ess": 57.06850276569578, "median": 1.566558502041988}, "ratio": {"ci_high": 0.549764887343123, "ci_level": 0.68, "ci_low": 0.547425344373149, "ess": 85.41242944853359, "median": 0.5488246343977703}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 7.2 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5256.936097082505, "ci_level": 0.68, "ci_low": 5214.90820747329, "ess": 7.225896048456788, "median": 5232.142723619015}, "center": {"ci_high": 197.82256024913403, "ci_level": 0.68, "ci_low": 197.81026602969823, "ess": 48.21815233209739, "median": 197.81540534401904}, "fwhm": {"ci_high": 1.6795538831312302, "ci_level": 0.68, "ci_low": 1.6517718608974739, "ess": 9.576311654957737, "median": 1.6678516526121303}, "gl_ratio": {"ci_high": 0.2980319546544451, "ci_level": 0.68, "ci_low": 0.2468442811731639, "ess": 42.95543818806933, "median": 0.2730231345755179}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 1, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 4.938573321633435, "peaks": [{"amplitude": 5390.869523728373, "center": 197.82979333181197, "fwhm": 1.6722221137560755, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2695.4347618641864, "center": 199.42979333181196, "fwhm": 1.6722221137560755, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5232.142723619015, "center": 197.81540534401904, "fwhm": 1.6678516526121303, "gl_ratio": 0.2730231345755179, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 2871.5288174071597, "center": 199.38196384606104, "fwhm": 1.6678516526121303, "gl_ratio": 0.2730231345755179, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 27.4, "seed": 0, "selection_warning": null, "sigma_hat": 85.62223233675857, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:18:{"anchor": "Cl2p_Scan_0", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1474.0916166688653, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.8726461280788271, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.8726461280788271, "min_effective_sample_size": 7.5087253977162645, "n_components": 2, "n_posterior_samples": 1050, "name": "Cl0_doublet", "posterior_weight": 4.219158195969241e-15, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 102.98856786797472, "swap_acceptance": 0.5836363636363636}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1440.9924759024757, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.6862899360135089, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.6862899360135089, "min_effective_sample_size": 9.657876901994673, "n_components": 2, "n_posterior_samples": 1050, "name": "Cl0r_doublet_relaxed", "posterior_weight": 0.9999999999999958, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 85.54381716668294, "swap_acceptance": 0.5490909090909091}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.5807743744969904, "ci_level": 0.68, "ci_low": 1.5612023593760596, "ess": 70.22489291585961, "median": 1.5698005091057672}, "ratio": {"ci_high": 0.5498841460653824, "ci_level": 0.68, "ci_low": 0.5475559554521303, "ess": 119.9682443469296, "median": 0.5490102160872052}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 9.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5266.865029528373, "ci_level": 0.68, "ci_low": 5203.5535358185825, "ess": 9.657876901994673, "median": 5238.073549214881}, "center": {"ci_high": 197.8214415348672, "ci_level": 0.68, "ci_low": 197.81037491289882, "ess": 64.61390307045127, "median": 197.8151457097792}, "fwhm": {"ci_high": 1.6758560907062219, "ci_level": 0.68, "ci_low": 1.6535701148925581, "ess": 32.82466133655663, "median": 1.6638888732947288}, "gl_ratio": {"ci_high": 0.29281104905093885, "ci_level": 0.68, "ci_low": 0.24790402822172108, "ess": 53.729950239548636, "median": 0.2694077663965322}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.3, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 4.938573321633435, "peaks": [{"amplitude": 5390.869523728373, "center": 197.82979333181197, "fwhm": 1.6722221137560755, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2695.4347618641864, "center": 199.42979333181196, "fwhm": 1.6722221137560755, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5238.073549214881, "center": 197.8151457097792, "fwhm": 1.6638888732947288, "gl_ratio": 0.2694077663965322, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 2875.7558911351357, "center": 199.38494621888495, "fwhm": 1.6638888732947288, "gl_ratio": 0.2694077663965322, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 28.3, "seed": 0, "selection_warning": null, "sigma_hat": 85.54381716668294, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:19:{"anchor": "B1s_Scan", "candidates": [{"bic_star": 2015.5793171441512, "boundary_hits": [], "conditional": null, "name": "B1_low", "rank": 3, "reduced_chi_sq": 68.92400388089678}, {"bic_star": 2016.8478942186584, "boundary_hits": ["main_b_mid:center@min"], "conditional": null, "name": "B2_low_mid", "rank": null, "reduced_chi_sq": 63.82228280296653}, {"bic_star": 1704.6694232780123, "boundary_hits": [], "conditional": null, "name": "B2b_low_oxide", "rank": 2, "reduced_chi_sq": 7.994825977237744}, {"bic_star": 1366.483290435591, "boundary_hits": [], "conditional": null, "name": "B3_low_mid_oxide", "rank": 1, "reduced_chi_sq": 1.2588022557672092}], "conditional": null, "config": {"enable_proposal_pass": false, "n_refits": 4, "noise_floor": 1.0, "rng_seed": 0}, "expert": {"chi_reduced": 1.4265863110880088, "peaks": [{"amplitude": 1983.7464958794415, "center": 188.5451767387288, "fwhm": 1.8525484474576044, "name": "B-B", "shape": "GL"}, {"amplitude": 2300.416063771059, "center": 192.99838091823622, "fwhm": 1.6179616826553664, "name": "B-O", "shape": "Gaussian"}, {"amplitude": 7387.003496848665, "center": 187.16003377896104, "fwhm": 1.6686511208264643, "name": "B-C", "shape": "GL"}]}, "method": "ic_model_comparison", "peaks": [{"amplitude": 7688.133165498477, "center": 187.211409511551, "fwhm": 1.7271877467434202, "gl_ratio": 0.04453437321110043, "phase_id": "B4C", "region": "B 1s", "role": "main_b_low", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 46.39260955037003, "center": 0.010708750236042296, "fwhm": 0.018132815770626948, "gl_ratio": 0.015396272708934568}}, {"amplitude": 1300.1185615208988, "center": 188.7171124140521, "fwhm": 1.2602911020246341, "gl_ratio": 1.661853987755535e-11, "phase_id": "B4C", "region": "B 1s", "role": "main_b_mid", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 68.63650973371432, "center": 0.0425117037539577, "fwhm": 0.06574396588135549, "gl_ratio": 3.571703517565689}}, {"amplitude": 1938.0114030404895, "center": 192.98584606930964, "fwhm": 1.3421259794132938, "gl_ratio": 1.0697748242805005e-10, "phase_id": "B4C", "region": "B 1s", "role": "main_b_oxide", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 29.69451910033184, "center": 0.008563469426293834, "fwhm": 0.022941559398213685, "gl_ratio": 0.15860438165913027}}], "runtime_s": 4.6, "seed": 0, "success": true, "winner": "B3_low_mid_oxide"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:27:{"anchor": "B1s_Scan", "candidates": [{"ci_reliability_warning": null, "free_energy": 1413.5914176737938, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.009392260242407247, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.009392260242407247, "min_effective_sample_size": 53.097123072982306, "n_components": 1, "n_posterior_samples": 1050, "name": "B1_low", "posterior_weight": 2.22341956876447e-124, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 508.0376815326401, "swap_acceptance": 0.6445454545454545}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1411.1743369792453, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.22232719902876852, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.22232719902876852, "min_effective_sample_size": 17.333118818519388, "n_components": 2, "n_posterior_samples": 1050, "name": "B2_low_mid", "posterior_weight": 2.493137502891001e-123, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 487.7802620998975, "swap_acceptance": 0.6133333333333333}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1259.1300182709588, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.11730224526343136, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.11730224526343136, "min_effective_sample_size": 18.952576617230623, "n_components": 2, "n_posterior_samples": 1050, "name": "B2b_low_oxide", "posterior_weight": 2.683829061973386e-57, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 174.85975519924563, "swap_acceptance": 0.5596969696969697}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1128.86991249959, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 2.353747431324905, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 2.353747431324905, "min_effective_sample_size": 5.184530874642533, "n_components": 3, "n_posterior_samples": 1050, "name": "B3_low_mid_oxide", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 59.788007927502406, "swap_acceptance": 0.5181818181818182}], "confidence": {"main_b_low": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 7.1 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 7624.230833268837, "ci_level": 0.68, "ci_low": 7600.819292486143, "ess": 7.120691885466271, "median": 7620.02776201325}, "center": {"ci_high": 187.2012517885317, "ci_level": 0.68, "ci_low": 187.19477515464087, "ess": 16.510650041858643, "median": 187.1996358659438}, "fwhm": {"ci_high": 1.7307958504627785, "ci_level": 0.68, "ci_low": 1.7180968714290874, "ess": 22.160941553410016, "median": 1.7240005406135293}, "gl_ratio": {"ci_high": 0.030016574866597888, "ci_level": 0.68, "ci_low": 0.0057592061623693526, "ess": 33.58720561061282, "median": 0.016201929271977878}}}}, "main_b_mid": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 5.2 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1381.369605229491, "ci_level": 0.68, "ci_low": 1363.3365491609404, "ess": 5.184530874642533, "median": 1364.9890763916376}, "center": {"ci_high": 188.69458421691232, "ci_level": 0.68, "ci_low": 188.66118456709114, "ess": 24.036876190646577, "median": 188.67290251573925}, "fwhm": {"ci_high": 1.378300325638229, "ci_level": 0.68, "ci_low": 1.3206315383664249, "ess": 28.264869836868602, "median": 1.351245864587704}, "gl_ratio": {"ci_high": 0.058269066769517514, "ci_level": 0.68, "ci_low": 0.006299393459841925, "ess": 56.119119054489474, "median": 0.025128313712362647}}}}, "main_b_oxide": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 31.0 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1948.8523114223283, "ci_level": 0.68, "ci_low": 1908.813573068154, "ess": 31.005640546801597, "median": 1923.4348362315156}, "center": {"ci_high": 192.99248392965248, "ci_level": 0.68, "ci_low": 192.97763839644293, "ess": 85.12057391557299, "median": 192.9851493784654}, "fwhm": {"ci_high": 1.3780184432804041, "ci_level": 0.68, "ci_low": 1.3450004247362337, "ess": 90.54492494555609, "median": 1.3594343587187774}, "gl_ratio": {"ci_high": 0.021675723437439773, "ci_level": 0.68, "ci_low": 0.0020610736973662724, "ess": 106.77062474817896, "median": 0.0077218893169545555}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.3, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.4265863110880088, "peaks": [{"amplitude": 1983.7464958794415, "center": 188.5451767387288, "fwhm": 1.8525484474576044, "name": "B-B", "shape": "GL"}, {"amplitude": 2300.416063771059, "center": 192.99838091823622, "fwhm": 1.6179616826553664, "name": "B-O", "shape": "Gaussian"}, {"amplitude": 7387.003496848665, "center": 187.16003377896104, "fwhm": 1.6686511208264643, "name": "B-C", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 7620.02776201325, "center": 187.1996358659438, "fwhm": 1.7240005406135293, "gl_ratio": 0.016201929271977878, "phase_id": "B4C", "region": "B 1s", "role": "main_b_low", "shape": "pseudo_voigt_gl"}, {"amplitude": 1364.9890763916376, "center": 188.67290251573925, "fwhm": 1.351245864587704, "gl_ratio": 0.025128313712362647, "phase_id": "B4C", "region": "B 1s", "role": "main_b_mid", "shape": "pseudo_voigt_gl"}, {"amplitude": 1923.4348362315156, "center": 192.9851493784654, "fwhm": 1.3594343587187774, "gl_ratio": 0.0077218893169545555, "phase_id": "B4C", "region": "B 1s", "role": "main_b_oxide", "shape": "pseudo_voigt_gl"}], "runtime_s": 46.2, "seed": 0, "selection_warning": null, "sigma_hat": 59.788007927502406, "success": true, "winner": "B3_low_mid_oxide"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:30:{"anchor": "U4f_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 3275.8653945587066, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.14477112745930754, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.14477112745930754, "min_effective_sample_size": 19.28253695057585, "n_components": 2, "n_posterior_samples": 750, "name": "U0_mains", "posterior_weight": 2.464632247092009e-207, "posterior_weight_reliable": false, "rank": 4, "sigma_hat": 573.387468071737, "swap_acceptance": 0.4863636363636364}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2844.2086982208093, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.5815332846641468, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.5815332846641468, "min_effective_sample_size": 3.4385170487557475, "n_components": 4, "n_posterior_samples": 750, "name": "U1_mains_satpair", "posterior_weight": 7.208973392584402e-20, "posterior_weight_reliable": false, "rank": 3, "sigma_hat": 148.66479452995452, "swap_acceptance": 0.43787878787878787}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2806.5777928677244, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.7867632228535513, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.7867632228535513, "min_effective_sample_size": 2.983880808048932, "n_components": 4, "n_posterior_samples": 750, "name": "U1b_mains_satpair_freesep", "posterior_weight": 0.001587698251371118, "posterior_weight_reliable": false, "rank": 2, "sigma_hat": 136.5071227591875, "swap_acceptance": 0.4406060606060606}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2800.133911875463, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 3.5329734956487755, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 3.5329734956487755, "min_effective_sample_size": 3.754834800879, "n_components": 4, "n_posterior_samples": 750, "name": "U2_mains_satfree", "posterior_weight": 0.9984123017486289, "posterior_weight_reliable": false, "rank": 1, "sigma_hat": 129.25347086856078, "swap_acceptance": 0.4542424242424242}], "confidence": {"main_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 11.2 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 10.861757448200263, "ci_level": 0.68, "ci_low": 10.851773176667246, "ess": 48.94615768154585, "median": 10.85727194773624}, "ratio": {"ci_high": 0.6635838075418771, "ci_level": 0.68, "ci_low": 0.6584050540389826, "ess": 11.22488899035955, "median": 0.6605336818820506}}}}, "main_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 3.8 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"alpha": {"ci_high": 1.4216656540911476, "ci_level": 0.68, "ci_low": 1.3571740187030115, "ess": 9.18801526266417, "median": 1.374742342891894}, "amplitude": {"ci_high": 16121.875987554462, "ci_level": 0.68, "ci_low": 15981.63871482141, "ess": 3.754834800879, "median": 15981.63871482141}, "beta": {"ci_high": 3.3978832824587712, "ci_level": 0.68, "ci_low": 3.203817264799955, "ess": 4.502956189506384, "median": 3.2760712391362157}, "center": {"ci_high": 380.6392746735966, "ci_level": 0.68, "ci_low": 380.6157727918216, "ess": 5.589729730663764, "median": 380.6288831574634}, "fwhm": {"ci_high": 3.078861264390619, "ci_level": 0.68, "ci_low": 2.9387071399369615, "ess": 8.055666282099534, "median": 3.0077280400563975}, "m": {"ci_high": 5.754764950755495, "ci_level": 0.68, "ci_low": 2.4922951815072767, "ess": 4.200845794074715, "median": 4.179002142180813}}}}, "satellite_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 12.8 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2337.1020488056065, "ci_level": 0.68, "ci_low": 2213.794067767326, "ess": 12.75359891489697, "median": 2272.63776846611}, "fwhm": {"ci_high": 2.678006980740226, "ci_level": 0.68, "ci_low": 2.5322353720844704, "ess": 15.77355528722878, "median": 2.6127209229379984}, "gl_ratio": {"ci_high": 0.1267260573322226, "ci_level": 0.68, "ci_low": 0.02111169644924705, "ess": 88.20047812663083, "median": 0.057495623276168056}, "offset": {"ci_high": 6.417000799780815, "ci_level": 0.68, "ci_low": 6.373933033966472, "ess": 46.12968433352226, "median": 6.3964750597643185}}}}, "satellite_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 11.5 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2504.6958783249006, "ci_level": 0.68, "ci_low": 2464.1837781194417, "ess": 11.545264878618854, "median": 2470.604532690152}, "fwhm": {"ci_high": 2.7100130616120204, "ci_level": 0.68, "ci_low": 2.5790498070707066, "ess": 16.450150862408726, "median": 2.6470772568802916}, "gl_ratio": {"ci_high": 0.964886007002836, "ci_level": 0.68, "ci_low": 0.8355605759511769, "ess": 56.692207928860284, "median": 0.9178875257660675}, "offset": {"ci_high": 6.0571560657850165, "ci_level": 0.68, "ci_low": 6.005922631023874, "ess": 21.232672932441368, "median": 6.031726107250276}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.7129708462685973, "peaks": [{"amplitude": 16166.479492182621, "center": 380.6179633862216, "fwhm": 2.737096332065471, "name": "U 4f7/2", "shape": "LACX"}, {"amplitude": 10508.211669918705, "center": 391.5179633862216, "fwhm": 2.737096332065471, "name": "U 4f5/2", "shape": "LACX"}, {"amplitude": 2214.057182779663, "center": 397.8977471164976, "fwhm": 2.556902102730025, "name": "Satellite 2", "shape": "Voigt"}, {"amplitude": 2436.210453422618, "center": 386.6877864274504, "fwhm": 2.512044323701672, "name": "Satellite 1", "shape": "Voigt"}]}, "method": "bayesian_exchange_mc", "peaks": [{"alpha": 1.374742342891894, "amplitude": 15981.63871482141, "beta": 3.2760712391362157, "center": 380.6288831574634, "fwhm": 3.0077280400563975, "m": 4.179002142180813, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f72", "shape": "la_casaxps"}, {"alpha": 1.374742342891894, "amplitude": 10556.41066280971, "beta": 3.2760712391362157, "center": 391.48615510519966, "fwhm": 3.0077280400563975, "m": 4.179002142180813, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f52", "shape": "la_casaxps"}, {"amplitude": 2470.604532690152, "center": 386.6606092647137, "fwhm": 2.6470772568802916, "gl_ratio": 0.9178875257660675, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f72", "shape": "pseudo_voigt_gl"}, {"amplitude": 2272.63776846611, "center": 397.882630164964, "fwhm": 2.6127209229379984, "gl_ratio": 0.057495623276168056, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f52", "shape": "pseudo_voigt_gl"}], "runtime_s": 312.0, "seed": 1, "selection_warning": "UNRESOLVED model selection: top-2 \u0394F=6.4 is within 2\u00d7(MC errors 3.5+1.8; split-half (lower bound)) \u2014 increase n_sweeps/n_replicas or seed_replicates before trusting the winner", "sigma_hat": 129.25347086856078, "success": true, "winner": "U2_mains_satfree"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:31:{"anchor": "C1s_Scan_8", "candidates": [{"bic_star": 2163.8231648781107, "boundary_hits": ["satellite_pi:fwhm@min"], "conditional": null, "name": "A0_graphite_asym_satellite", "rank": 19, "reduced_chi_sq": 240.19194160113287}, {"bic_star": 2160.815299805517, "boundary_hits": ["contamination_CO:center@min", "contamination_CO:fwhm@max", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A1_graphite_asym_sat_plus_CO", "rank": 16, "reduced_chi_sq": 181.88951637848314}, {"bic_star": 2161.051121689465, "boundary_hits": ["contamination_CO:center@min", "contamination_CO:fwhm@max", "contamination_C=O:center@min", "contamination_C=O:fwhm@min", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A2_graphite_asym_sat_plus_CO_C=O", "rank": 17, "reduced_chi_sq": 187.39611578006767}, {"bic_star": 2161.0789397180533, "boundary_hits": ["contamination_CO:center@min", "contamination_CO:fwhm@max", "contamination_C=O:fwhm@min", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "rank": null, "reduced_chi_sq": 193.64161917230317}, {"bic_star": 2160.8152315307166, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A1_linked", "rank": 15, "reduced_chi_sq": 181.88941232293445}, {"bic_star": 2175.934967343506, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A2_linked", "rank": 20, "reduced_chi_sq": 186.10274165270138}, {"bic_star": 2175.9350957501024, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min", "contamination_OC=O:center@min", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A3_linked", "rank": 21, "reduced_chi_sq": 190.60538447543084}, {"bic_star": 2163.2109656964235, "boundary_hits": ["?:shared_contamination_fwhm@max", "satellite_pi:offset@min", "satellite_pi:fwhm@max", "contamination_CO:offset@min"], "conditional": null, "name": "A1_linked_offset", "rank": 18, "reduced_chi_sq": 178.85948534555155}, {"bic_star": 2163.553211914591, "boundary_hits": ["?:shared_contamination_fwhm@max", "satellite_pi:offset@min", "satellite_pi:fwhm@max", "contamination_CO:offset@min"], "conditional": null, "name": "A2_linked_offset", "rank": null, "reduced_chi_sq": 182.95020993312485}, {"bic_star": 2178.4289658127022, "boundary_hits": ["?:shared_contamination_fwhm@max", "satellite_pi:offset@min", "satellite_pi:fwhm@max", "contamination_CO:offset@min", "contamination_C=O:offset@min", "contamination_OC=O:offset@min"], "conditional": null, "name": "A3_linked_offset", "rank": 22, "reduced_chi_sq": 187.37614575574315}, {"bic_star": 1922.159197935138, "boundary_hits": ["satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "AG0_graphite_asymGL_satellite", "rank": 14, "reduced_chi_sq": 49.09198395188531}, {"bic_star": 1827.6972718306833, "boundary_hits": ["contamination_CO:center@min", "contamination_CO:fwhm@max"], "conditional": null, "name": "AG1_graphite_asymGL_sat_plus_CO", "rank": 4, "reduced_chi_sq": 30.67097468365853}, {"bic_star": 1857.2378471705656, "boundary_hits": ["contamination_C=O:center@min", "contamination_C=O:fwhm@max"], "conditional": null, "name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "rank": 9, "reduced_chi_sq": 34.77674005662118}, {"bic_star": 1866.4202137678092, "boundary_hits": ["contamination_CO:center@min"], "conditional": null, "name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "rank": 10, "reduced_chi_sq": 32.27014779205738}, {"bic_star": 1827.7348381771212, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min"], "conditional": null, "name": "AG1_linked", "rank": 6, "reduced_chi_sq": 30.670969061936145}, {"bic_star": 1827.7383651902487, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min", "contamination_C=O:center@max"], "conditional": null, "name": "AG2_linked", "rank": 7, "reduced_chi_sq": 31.401280684846206}, {"bic_star": 1827.698891160666, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min", "contamination_C=O:center@max", "contamination_OC=O:center@max"], "conditional": null, "name": "AG3_linked", "rank": 5, "reduced_chi_sq": 32.16709223938828}, {"bic_star": 1906.6151965335823, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@max"], "conditional": null, "name": "M0_graph_asym_aliph_sym_satellite", "rank": 13, "reduced_chi_sq": 51.026123997036166}, {"bic_star": 1852.892023570819, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@max"], "conditional": null, "name": "M1_graph_asym_aliph_sym_sat_CO", "rank": 8, "reduced_chi_sq": 33.249614334092435}, {"bic_star": 1876.4721336150988, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@max", "contamination_C=O:center@min"], "conditional": null, "name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "rank": 11, "reduced_chi_sq": 31.449919222263258}, {"bic_star": 1741.1828905801303, "boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min", "satellite_pi:offset@min"], "conditional": null, "name": "MG1_graphAsymGL_aliph_sat_CO", "rank": 3, "reduced_chi_sq": 12.39542802308734}, {"bic_star": 1723.5295130712864, "boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "conditional": null, "name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "rank": 1, "reduced_chi_sq": 9.040578699307785}, {"bic_star": 1739.4848904150426, "boundary_hits": ["contamination_CO:fwhm@min", "main_aliphatic:offset@min"], "conditional": null, "name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "rank": 2, "reduced_chi_sq": 8.963144376610053}, {"bic_star": 2273.9968677512966, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min"], "conditional": null, "name": "B2_linked", "rank": 23, "reduced_chi_sq": 195.26270825938678}, {"bic_star": 2287.4247672279807, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min", "contamination_OC=O:center@max"], "conditional": null, "name": "B3_linked", "rank": 24, "reduced_chi_sq": 191.20066833957887}, {"bic_star": 1894.6355482027723, "boundary_hits": ["contamination_CO:fwhm@max", "contamination_C=O:center@max", "contamination_C=O:fwhm@max"], "conditional": null, "name": "B2_graphite_sym_CO_C=O", "rank": 12, "reduced_chi_sq": 54.892341034848926}, {"bic_star": 1900.289299700932, "boundary_hits": [], "conditional": null, "name": "B3_graphite_sym_CO_C=O_OC=O", "rank": null, "reduced_chi_sq": 59.05393024039974}], "conditional": null, "config": {"enable_proposal_pass": false, "n_refits": 4, "noise_floor": 1.0, "rng_seed": 0}, "expert": {"chi_reduced": 1.2046857566409657, "peaks": [{"amplitude": 68687.50247254308, "center": 284.4998947390668, "fwhm": 0.666639931355077, "name": "Graphite", "shape": "asym-GL"}, {"amplitude": 6769.104782616617, "center": 284.84600000000006, "fwhm": 2.4362161470016317, "name": "Adventitious 1", "shape": "GL"}, {"amplitude": 980.2757090919454, "center": 286.6204483360466, "fwhm": 1.920204116987471, "name": "Adventitious 2", "shape": "GL"}, {"amplitude": 967.1178669586701, "center": 288.3459999999785, "fwhm": 3.7870918615811546, "name": "Adventitious 3", "shape": "GL"}, {"amplitude": 1039.5910934477724, "center": 291.21704604934337, "fwhm": 2.10582966510949, "name": "\u03c0\u2192\u03c0* satellite", "shape": "GL"}, {"amplitude": 3096.5394911174, "center": 283.45958350730706, "fwhm": 1.114128341337902, "name": "Unknown 1", "shape": "GL"}]}, "method": "ic_model_comparison", "peaks": [{"amplitude": 64934.51584247545, "asymmetry": 0.004564543290729389, "center": 284.5088393082103, "fwhm": 0.6743371621568794, "gl_ratio": 0.3478253485659817, "phase_id": "graphite", "region": "C 1s", "role": "main_graphitic", "shape": "asymmetric_gl"}, {"amplitude": 10638.980534673961, "center": 284.70883930821725, "fwhm": 2.557408591874607, "gl_ratio": 1.3836677359435612e-09, "phase_id": "graphite", "region": "C 1s", "role": "main_aliphatic", "shape": "pseudo_voigt_gl"}, {"amplitude": 1296.8516923145844, "center": 290.81708874220726, "fwhm": 2.7391088473614142, "gl_ratio": 2.95354034007822e-08, "phase_id": "graphite", "region": "C 1s", "role": "satellite_pi", "shape": "pseudo_voigt_gl"}, {"amplitude": 859.3391603349102, "center": 286.79999999924433, "fwhm": 0.9620619090767639, "gl_ratio": 2.5914003165539157e-09, "phase_id": "graphite", "region": "C 1s", "role": "contamination_CO", "shape": "pseudo_voigt_gl"}, {"amplitude": 1236.7569090879415, "center": 287.9541720087798, "fwhm": 1.9478282631295034, "gl_ratio": 1.3878992399796175e-10, "phase_id": "graphite", "region": "C 1s", "role": "contamination_C=O", "shape": "pseudo_voigt_gl"}], "runtime_s": 799.3, "seed": 0, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:32:{"anchor": "C1s_Scan_8", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1431.7384748727427, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 2.840805932549074, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 2.840805932549074, "min_effective_sample_size": 3.6378511930847868, "n_components": 4, "n_posterior_samples": 750, "name": "A2_linked", "posterior_weight": 9.34316052336157e-63, "posterior_weight_reliable": false, "rank": 4, "sigma_hat": 1591.1691144439912, "swap_acceptance": 0.59}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1291.695287428086, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.9735464150554662, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.9735464150554662, "min_effective_sample_size": 3.618167492044223, "n_components": 4, "n_posterior_samples": 750, "name": "AG2_linked", "posterior_weight": 0.06172730921141825, "posterior_weight_reliable": false, "rank": 2, "sigma_hat": 520.1780829088461, "swap_acceptance": 0.5654545454545454}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1288.973973252434, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.4610272658262602, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.4610272658262602, "min_effective_sample_size": 0.0, "n_components": 5, "n_posterior_samples": 750, "name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "posterior_weight": 0.9382726903971659, "posterior_weight_reliable": false, "rank": 1, "sigma_hat": 314.3142924012769, "swap_acceptance": 0.5427272727272727}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1310.5715093836916, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 2.959159662583147, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 2.959159662583147, "min_effective_sample_size": 0.0, "n_components": 6, "n_posterior_samples": 750, "name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "posterior_weight": 3.9141576285369144e-10, "posterior_weight_reliable": false, "rank": 3, "sigma_hat": 442.63466643193914, "swap_acceptance": 0.5648484848484848}], "confidence": {"contamination_C=O": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 4.5 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1413.8977807492288, "ci_level": 0.68, "ci_low": 1070.8289532804656, "ess": 4.49719611437458, "median": 1070.8289532804656}, "center": {"ci_high": 288.032722402536, "ci_level": 0.68, "ci_low": 287.70594780120274, "ess": 16.779000590905873, "median": 287.88346859207536}, "fwhm": {"ci_high": 2.0550491331827967, "ci_level": 0.68, "ci_low": 1.4346222838496572, "ess": 26.34233810365543, "median": 1.7966987440135327}, "gl_ratio": {"ci_high": 0.352846479858547, "ci_level": 0.68, "ci_low": 0.02824471383267556, "ess": 35.136567438855394, "median": 0.12565048346474644}}}}, "contamination_CO": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 7.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 763.5535401648384, "ci_level": 0.68, "ci_low": 429.2235408358105, "ess": 7.660437122561276, "median": 746.146872276544}, "center": {"ci_high": 286.7848965004658, "ci_level": 0.68, "ci_low": 286.6892224969777, "ess": 60.08554906935291, "median": 286.75295555811783}, "fwhm": {"ci_high": 1.0293830242196573, "ci_level": 0.68, "ci_low": 0.8170395331043406, "ess": 53.764117853639654, "median": 0.8829835082000135}, "gl_ratio": {"ci_high": 0.5761545619818959, "ci_level": 0.68, "ci_low": 0.052668552537415134, "ess": 13.713931350340532, "median": 0.20894908504740461}}}}, "main_aliphatic": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "stuck_chain", "reliability_note": "a sampled parameter never moved \u2014 intervals are meaningless; refit with larger steps/more sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 10591.011092574081, "ci_level": 0.68, "ci_low": 10591.011092574081, "ess": 0.0, "median": 10591.011092574081}, "fwhm": {"ci_high": 2.6486049720889735, "ci_level": 0.68, "ci_low": 2.610852203471151, "ess": 25.481737605006753, "median": 2.6306356976479814}, "gl_ratio": {"ci_high": 0.037139353550702615, "ci_level": 0.68, "ci_low": 0.005173505187192258, "ess": 44.32272219715784, "median": 0.014940168495951336}, "offset": {"ci_high": 0.20254970288043916, "ci_level": 0.68, "ci_low": 0.20056982358918704, "ess": 11.39453788515903, "median": 0.20133004996670265}}}}, "main_graphitic": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 2.8 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 65143.20439031434, "ci_level": 0.68, "ci_low": 64878.97252048374, "ess": 3.242813445025664, "median": 64878.97252048374}, "asymmetry": {"ci_high": 0.04527048451758119, "ci_level": 0.68, "ci_low": 0.028131929542454068, "ess": 3.573143648780697, "median": 0.03603303530979708}, "center": {"ci_high": 284.5065872710428, "ci_level": 0.68, "ci_low": 284.5040719145873, "ess": 2.8106927076404142, "median": 284.5040719145873}, "fwhm": {"ci_high": 0.6666833317825636, "ci_level": 0.68, "ci_low": 0.6629091741172232, "ess": 5.197830796670883, "median": 0.6647855925503354}, "gl_ratio": {"ci_high": 0.33356328407057734, "ci_level": 0.68, "ci_low": 0.3066350353457373, "ess": 29.222663581185778, "median": 0.31945250416635734}}}}, "satellite_pi": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 3.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1306.2409784416934, "ci_level": 0.68, "ci_low": 1138.072227140848, "ess": 3.67697265576572, "median": 1138.072227140848}, "fwhm": {"ci_high": 3.5493557774095663, "ci_level": 0.68, "ci_low": 2.632122835086131, "ess": 10.47322998773568, "median": 3.0904204438391005}, "gl_ratio": {"ci_high": 0.4028246074155279, "ci_level": 0.68, "ci_low": 0.048810734865377944, "ess": 33.65779476865091, "median": 0.16313646989546973}, "offset": {"ci_high": 6.385082154504203, "ci_level": 0.68, "ci_low": 6.034991605178216, "ess": 17.120604075459617, "median": 6.246191695477605}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.2046857566409657, "peaks": [{"amplitude": 68687.50247254308, "center": 284.4998947390668, "fwhm": 0.666639931355077, "name": "Graphite", "shape": "asym-GL"}, {"amplitude": 6769.104782616617, "center": 284.84600000000006, "fwhm": 2.4362161470016317, "name": "Adventitious 1", "shape": "GL"}, {"amplitude": 980.2757090919454, "center": 286.6204483360466, "fwhm": 1.920204116987471, "name": "Adventitious 2", "shape": "GL"}, {"amplitude": 967.1178669586701, "center": 288.3459999999785, "fwhm": 3.7870918615811546, "name": "Adventitious 3", "shape": "GL"}, {"amplitude": 1039.5910934477724, "center": 291.21704604934337, "fwhm": 2.10582966510949, "name": "\u03c0\u2192\u03c0* satellite", "shape": "GL"}, {"amplitude": 3096.5394911174, "center": 283.45958350730706, "fwhm": 1.114128341337902, "name": "Unknown 1", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 64878.97252048374, "asymmetry": 0.03603303530979708, "center": 284.5040719145873, "fwhm": 0.6647855925503354, "gl_ratio": 0.31945250416635734, "phase_id": "graphite", "region": "C 1s", "role": "main_graphitic", "shape": "asymmetric_gl"}, {"amplitude": 10591.011092574081, "center": 284.705401964554, "fwhm": 2.6306356976479814, "gl_ratio": 0.014940168495951336, "phase_id": "graphite", "region": "C 1s", "role": "main_aliphatic", "shape": "pseudo_voigt_gl"}, {"amplitude": 1138.072227140848, "center": 290.7502636100649, "fwhm": 3.0904204438391005, "gl_ratio": 0.16313646989546973, "phase_id": "graphite", "region": "C 1s", "role": "satellite_pi", "shape": "pseudo_voigt_gl"}, {"amplitude": 746.146872276544, "center": 286.75295555811783, "fwhm": 0.8829835082000135, "gl_ratio": 0.20894908504740461, "phase_id": "graphite", "region": "C 1s", "role": "contamination_CO", "shape": "pseudo_voigt_gl"}, {"amplitude": 1070.8289532804656, "center": 287.88346859207536, "fwhm": 1.7966987440135327, "gl_ratio": 0.12565048346474644, "phase_id": "graphite", "region": "C 1s", "role": "contamination_C=O", "shape": "pseudo_voigt_gl"}], "runtime_s": 351.9, "seed": 0, "selection_warning": "UNRESOLVED model selection: top-2 \u0394F=2.7 is within 2\u00d7(MC errors 1.5+2.0; split-half (lower bound)) \u2014 increase n_sweeps/n_replicas or seed_replicates before trusting the winner", "sigma_hat": 314.3142924012769, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O"}
docs/autofit/stress-test-report.md:9:0. **HEADLINE — filter-then-rank buried DECISIVE evidence; the engine now flags it at the RESULT level.** Three measured instances (gen-2): (a) `overlap_sep0.4_h9000` — P2 beats P1 by ΔBIC* 74–97 on EVERY noise draw and is stable, yet is plausibility-filtered every time; clean P1 emitted. (b) `overlap_sep0.7_h9000` offset 2000 — stable P2 buried at ΔBIC* +944. (c) `charging_with_replica_candidate` offset 0 — the center-pegged true candidate not promoted; `single_main` at ΔBIC* +801. DRIVEN ENGINE CHANGE (commit 8079188): a result-level `filtered_dominant_alternative` flag (diagnostics + analysis + message WARNING) whenever a filtered candidate's BIC* beats the winner's by the decisive threshold — THIS battery generation demonstrates it on every burial row (e.g. sep0.4@9000: P2 named, ΔBIC* 86.3, filter reason carried). The BIC/IC math review endorsed reporting-not-auto-promotion (raw BIC also RESCUES: it preferred a P3 overfit by margin 669 that filtering correctly rejected). Remaining recommendation: orphan-tolerant role matching for heavily-overlapped windows. (Contrast: `overlap_sep0.4_h900` is GENUINE parsimony — P1 wins the evidence by ΔBIC* 5–12 on every draw.)
docs/autofit/stress-test-report.md:15:6. **A-priori expectation labels were arbitrated by measurement** (in both directions): `weak_minor_0.03_h2000` ambiguous→recover (IC recovers on every draw; Bayes concurs with an honest budget warning; the minor's center wobbles ±0.16 eV, one draw exceeding the 0.15 eV PASS tolerance — reported as-is). `overlap_sep0.4_h9000` ambiguous→recover (the evidence decisively distinguishes; the pipeline currently fails it — finding 0). The current battery was REGENERATED under the corrected library labels (the superseded first generation lives in git history); the summarizer reads labels from the library at report time and annotates any future generation-label drift per row.
docs/autofit/stress-test-report.md:18:9. **Proposal-pass FP/FN characterization (run-brief item 3d)**: measured across the battery — ZERO false positives (0 accepted proposals on 66 rows whose model space covers the truth) and ZERO detections on the 18 distributed/overlapped truth-outside rows (charging replica at 0.8 eV inside the envelope, asymmetric tails, background curvature — those honesty cases surface via χ²ᵣ/autocorrelation/conditional instead), but RELIABLE detection in its designed regime: the isolated discrete missing peak (`isolated_missing_peak`, +5 eV) is proposed, accepted, and fitted at the true position on every noise draw. The pass is a conservative discrete-peak detector, not a general misspecification alarm — by design, now measured.
docs/autofit/stress-test-report.md:49:| ic_model_comparison | n_refits=12 | 2000 | PASS | asym_main | 3.50 | 0.000 | 1 |
docs/autofit/stress-test-report.md:52:| ic_model_comparison | n_refits=4 | 2000 | PASS | asym_main | 3.51 | 0.001 | 0 |
docs/autofit/stress-test-report.md:98:### charging_tail
docs/autofit/stress-test-report.md:100:**charging_no_replica_candidate** (expect: honesty; 25% replica at −0.8 eV (differential charging shape))
docs/autofit/stress-test-report.md:118:**charging_with_replica_candidate** (expect: recover; 25% replica at −0.8 eV (differential charging shape))
docs/autofit/stress-test-report.md:308:- `charging_with_replica_candidate` {"n_refits": 12} (expect: recover): winners flip across noise draws: ['main_plus_replica', 'single_main'] — recover FAILS on some noise draws — robustness deficiency, not ambiguity
docs/autofit/stress-test-report.md:309:- `charging_with_replica_candidate` {"n_refits": 4} (expect: recover): winners flip across noise draws: ['main_plus_replica', 'single_main'] — recover FAILS on some noise draws — robustness deficiency, not ambiguity
tests/autofit/test_cl2p_freewidth.py:183:def test_excess_area_link_rejects_mixed_shapes():
tests/js/ref_core.test.js:36:    states: [ { id:'si1', state: 'SiO2', be_ev: 103.5, ref: 'NIST', source:'legacy-embedded-dataset' } ] },
tests/js/ref_core.test.js:286:test('serializeRefCompoundMarkers: mixed valid+invalid → invalid be dropped, valid kept', () => {
autofit/regions/u4f.py:75:U4F_MAIN_FWHM_RANGE = (1.5, 3.5)
docs/autofit/codex/plain_english_pass_verdict_round2_runB.md:10:Note: this run did NOT catch run A's follow-on finding (mixed-success payloads with non-empty `structural_only` still misclassified). Per this project's "stricter verdict governs" convention, run A's NO-GO is the operative verdict for this round; see round 3 recheck for disposition.
tests/autofit/test_preseed_dominants.py:334:           + _pv(x, 9000.0 * 0.15, 203.5, 1.3, ETA))  # missing peak 2
tests/autofit/test_preseed_dominants.py:346:    assert fitted[1] == pytest.approx(203.5, abs=0.4)
docs/autofit/inventory/stress_battery_runs.jsonl:7:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3153.7565429787596, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 5.7809674050649695, "survived": true}, {"bic_star": 3118.2849367275676, "boundary_hits": ["main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 5.080109214935805, "survived": false}, {"bic_star": 2443.565329460894, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.75, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.4571079252480608, "survived": false}, {"bic_star": 3112.5811161689353, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2+bfix", "orphan_peaks": false, "reduced_chi_sq": 5.0627708242827145, "survived": true}], "case": "overlap_sep0.7_h9000", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2443.565329460894, "delta_bic_vs_winner": 669.0157867080411, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "name": "P3"}, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 16.52, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.3286, "d_fwhm_ev": 0.4075, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.3681, "d_fwhm_ev": 1.3, "matched_role": "main_b", "true_center": 198.04}], "truth_n": 2, "winner": "P2+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 5.0627708242827145, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:10:{"candidates": [{"free_energy": 1141.800413299352, "free_energy_mc_error": 1.9953657305029537, "free_energy_split_half_error": 1.9953657305029537, "min_effective_sample_size": 5.338290164277106, "name": "P1", "posterior_weight": 3.595354431773926e-61, "posterior_weight_reliable": true, "rank": 3}, {"free_energy": 1002.6223652032959, "free_energy_mc_error": 2.1753943273294567, "free_energy_split_half_error": 2.1753943273294567, "min_effective_sample_size": 3.6994767039440055, "name": "P2", "posterior_weight": 0.9999999999339444, "posterior_weight_reliable": true, "rank": 1}, {"free_energy": 1026.062888495648, "free_energy_mc_error": 8.073111284622996, "free_energy_split_half_error": 8.073111284622996, "min_effective_sample_size": 5.877342686762297, "name": "P3", "posterior_weight": 6.60556668404888e-11, "posterior_weight_reliable": true, "rank": 2}], "case": "overlap_sep0.7_h9000", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "recover", "method": "bayesian_exchange_mc", "n_emitted_components": 2, "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 10.52, "seed_offset": 0, "selection_warning": null, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0003, "d_fwhm_ev": 0.0067, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0041, "d_fwhm_ev": -0.0002, "matched_role": "main_b", "true_center": 198.04}], "truth_n": 2, "winner": "P2", "winner_is_true": true}
docs/autofit/inventory/stress_battery_runs.jsonl:20:{"candidates": [{"free_energy": 920.7742514192767, "free_energy_mc_error": 0.5246428357232844, "free_energy_split_half_error": 0.5246428357232844, "min_effective_sample_size": 27.071643772415026, "name": "P1", "posterior_weight": 0.9362378661594928, "posterior_weight_reliable": false, "rank": 1}, {"free_energy": 923.5071197457307, "free_energy_mc_error": 3.1363802582213225, "free_energy_split_half_error": 3.1363802582213225, "min_effective_sample_size": 4.459313814475639, "name": "P2", "posterior_weight": 0.06088587731601117, "posterior_weight_reliable": false, "rank": 2}, {"free_energy": 926.5596313632122, "free_energy_mc_error": 4.510421845794781, "free_energy_split_half_error": 4.510421845794781, "min_effective_sample_size": 4.466382055227123, "name": "P3", "posterior_weight": 0.0028762565244962015, "posterior_weight_reliable": false, "rank": 3}], "case": "overlap_sep0.4_h900", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "ambiguous", "method": "bayesian_exchange_mc", "n_emitted_components": 1, "notes": "separation 0.4\u00d7FWHM, heights 900/630", "regime": "heavy_overlap", "runtime_s": 10.5, "seed_offset": 0, "selection_warning": "UNRESOLVED model selection: top-2 \u0394F=2.7 is within 2\u00d7(MC errors 0.5+3.1; split-half (lower bound)) \u2014 increase n_sweeps/n_replicas or seed_replicates before trusting the winner", "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.2003, "d_fwhm_ev": 0.1891, "matched_role": "main_a", "true_center": 197.2}, null], "truth_n": 2, "winner": "P1", "winner_is_true": false}
docs/autofit/inventory/stress_battery_runs.jsonl:23:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3925.4525458362814, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 90.48023620943462, "survived": true}, {"bic_star": 3299.6471607179587, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 14.069527634570445, "survived": true}, {"bic_star": 3332.149559856226, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.25, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 14.204328337416305, "survived": false}], "case": "weak_minor_0.03_h90000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 3.59, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.004, "d_fwhm_ev": 0.0114, "matched_role": "main_a", "true_center": 197.0}, {"d_center_ev": -0.0523, "d_fwhm_ev": 0.1539, "matched_role": "main_b", "true_center": 198.8}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 14.069527634570445, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:41:{"case": "charging_no_replica_candidate", "chi_reduced": 2.11933018079081, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.0397, "d_fwhm_ev": 0.0591, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": -0.1661, "d_fwhm_ev": -0.1165, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:42:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3061.2254608577414, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.962869989958203, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.03, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1451, "d_fwhm_ev": 0.2452, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 6.962869989958203, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:43:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3061.225259358099, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.96286998990333, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.07, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1451, "d_fwhm_ev": 0.2452, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 6.96286998990333, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:44:{"case": "charging_no_replica_candidate", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 3.54, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1405, "d_fwhm_ev": 0.1802, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:45:{"candidates": [{"free_energy": 1164.4119461114783, "free_energy_mc_error": 3.3940131980712067, "free_energy_split_half_error": 3.3940131980712067, "min_effective_sample_size": 3.485445192889438, "name": "single_main", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1}], "case": "charging_no_replica_candidate", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "honesty", "method": "bayesian_exchange_mc", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 1.02, "seed_offset": 0, "selection_warning": null, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1473, "d_fwhm_ev": 0.2454, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_is_true": false}
docs/autofit/inventory/stress_battery_runs.jsonl:46:{"case": "charging_with_replica_candidate", "chi_reduced": 1.747290088264468, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 0, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0655, "d_fwhm_ev": -0.1281, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.4835, "d_fwhm_ev": 0.3695, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:47:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3069.7110277472125, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.691644167392703, "survived": true}, {"bic_star": 2268.771804830489, "boundary_hits": ["replica:center@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['replica:center@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.7702846538141737, "survived": false}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2268.771804830489, "delta_bic_vs_winner": 800.9392229167233, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['replica:center@max'], unphysical_widths=[], orphan_peaks=False)", "name": "main_plus_replica"}, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.23, "seed_offset": 0, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.1434, "d_fwhm_ev": 0.2462, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 6.691644167392703, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:48:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3069.711389067813, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.691644167338099, "survived": true}, {"bic_star": 2268.7718011018105, "boundary_hits": ["replica:center@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['replica:center@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.77028465381276, "survived": false}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2268.7718011018105, "delta_bic_vs_winner": 800.9395879660024, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['replica:center@max'], unphysical_widths=[], orphan_peaks=False)", "name": "main_plus_replica"}, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.64, "seed_offset": 0, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.1434, "d_fwhm_ev": 0.2462, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 6.691644167338099, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:49:{"case": "charging_with_replica_candidate", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 6.85, "seed_offset": 0, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.1364, "d_fwhm_ev": 0.1886, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:50:{"candidates": [{"free_energy": 1159.9673901900233, "free_energy_mc_error": 4.331402015625713, "free_energy_split_half_error": 4.331402015625713, "min_effective_sample_size": 11.257203545526906, "name": "single_main", "posterior_weight": 2.125021944800329e-66, "posterior_weight_reliable": true, "rank": 2}, {"free_energy": 1008.7505561817042, "free_energy_mc_error": 1.4515628189728886, "free_energy_split_half_error": 1.4515628189728886, "min_effective_sample_size": 2.6292565194409003, "name": "main_plus_replica", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1}], "case": "charging_with_replica_candidate", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "recover", "method": "bayesian_exchange_mc", "n_emitted_components": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 4.14, "seed_offset": 0, "selection_warning": null, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0287, "d_fwhm_ev": -0.0147, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": 0.3687, "d_fwhm_ev": 0.3699, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2, "winner": "main_plus_replica", "winner_is_true": true}
docs/autofit/inventory/stress_battery_runs.jsonl:60:{"candidates": [{"free_energy": 1178.806932312742, "free_energy_mc_error": 0.6377158821167086, "free_energy_split_half_error": 0.6377158821167086, "min_effective_sample_size": 15.016747625284404, "name": "sym_main", "posterior_weight": 6.192750338903466e-32, "posterior_weight_reliable": true, "rank": 2}, {"free_energy": 1106.9475886446419, "free_energy_mc_error": 1.639656788828006, "free_energy_split_half_error": 1.639656788828006, "min_effective_sample_size": 4.744365796408424, "name": "asym_main", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1}], "case": "asym_truth_with_asym_candidate", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "recover", "method": "bayesian_exchange_mc", "n_emitted_components": 1, "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 2.86, "seed_offset": 0, "selection_warning": null, "success": true, "true_candidates": ["asym_main"], "truth_match": [{"d_center_ev": -0.0111, "d_fwhm_ev": -0.0842, "matched_role": "main_a", "true_center": 197.8}], "truth_n": 1, "winner": "asym_main", "winner_is_true": true}
docs/autofit/inventory/stress_battery_runs.jsonl:67:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4146.61792120331, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 126.30873391628948, "survived": false}, {"bic_star": 2433.522542110988, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.2355887929329685, "survived": true}, {"bic_star": 2464.9017984747015, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.2209246366731366, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 1.17, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0012, "d_fwhm_ev": 0.0114, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0018, "d_fwhm_ev": 0.0065, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.2355887929329685, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:68:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4146.6177847728, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 126.30873391534688, "survived": false}, {"bic_star": 2433.5225504652817, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.2355887929327787, "survived": true}, {"bic_star": 2464.9017984747015, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 0.9166666666666666, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.2209246366731366, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 2.72, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0012, "d_fwhm_ev": 0.0114, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0018, "d_fwhm_ev": 0.0065, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.2355887929327787, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:80:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 2529.846397250423, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 2.5011103545460256, "survived": true}, {"bic_star": 2455.712579641171, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.7885560493966415, "survived": false}, {"bic_star": 2483.5388447920755, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.6828315384857104, "survived": false}], "case": "overlap_sep0.4_h9000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2455.712579641171, "delta_bic_vs_winner": 74.13381760925176, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "name": "P2"}, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "separation 0.4\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 1.71, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1959, "d_fwhm_ev": 0.1589, "matched_role": "main_a", "true_center": 197.2}, null], "truth_n": 2, "winner": "P1", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 2.5011103545460256, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:81:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 2529.8466347049653, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 2.5011103545447106, "survived": true}, {"bic_star": 2455.712732678833, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.7885560493888828, "survived": false}, {"bic_star": 2483.5279471733843, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 0.75, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.6828315306538362, "survived": false}], "case": "overlap_sep0.4_h9000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2455.712732678833, "delta_bic_vs_winner": 74.13390202613209, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "name": "P2"}, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "separation 0.4\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 16.9, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1959, "d_fwhm_ev": 0.1589, "matched_role": "main_a", "true_center": 197.2}, null], "truth_n": 2, "winner": "P1", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 2.5011103545447106, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:96:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4283.283653905022, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 376.30958977610044, "survived": true}, {"bic_star": 2361.291874772842, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.7784581293646837, "survived": true}, {"bic_star": 2403.521344864318, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.75, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.7637353959087687, "survived": false}, {"bic_star": 2426.315290961152, "boundary_hits": ["main_d:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_d:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.0, "name": "P4", "orphan_peaks": true, "reduced_chi_sq": 1.7885768993239026, "survived": false}, {"bic_star": 2449.1314060187674, "boundary_hits": ["main_d:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_d:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.0, "name": "P5", "orphan_peaks": true, "reduced_chi_sq": 1.8141280641936752, "survived": false}], "case": "overspecified_2true_5max", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "prune", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "truth 2 well-separated peaks; menu offers up to 5", "regime": "overspecified", "runtime_s": 4.33, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0001, "d_fwhm_ev": 0.0147, "matched_role": "main_a", "true_center": 196.8}, {"d_center_ev": -0.0055, "d_fwhm_ev": 0.0299, "matched_role": "main_b", "true_center": 199.4}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.7784581293646837, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:103:{"case": "charging_no_replica_candidate", "chi_reduced": 3.2617136636412978, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.06, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0196, "d_fwhm_ev": -0.1273, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.5088, "d_fwhm_ev": 0.4886, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:104:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3094.9892829615083, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 9.091478360741299, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.03, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1421, "d_fwhm_ev": 0.2625, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 9.091478360741299, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:105:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3094.9892829615083, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 9.091478360741299, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.08, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1421, "d_fwhm_ev": 0.2625, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 9.091478360741299, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:106:{"case": "charging_no_replica_candidate", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 3.73, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1127, "d_fwhm_ev": 0.1378, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:107:{"case": "charging_with_replica_candidate", "chi_reduced": 1.8653919775457, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.0239, "d_fwhm_ev": 0.0419, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": -0.0889, "d_fwhm_ev": -0.0014, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:108:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3050.7264501784407, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.699517650214303, "survived": true}, {"bic_star": 2268.1535058762415, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.865391977506154, "survived": true}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.16, "seed_offset": 1000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.0239, "d_fwhm_ev": 0.0419, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": -0.0889, "d_fwhm_ev": -0.0014, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2, "winner": "main_plus_replica", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.865391977506154, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:109:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3050.7260572120103, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.69951765015872, "survived": true}, {"bic_star": 2268.1535654108015, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.8653919773281642, "survived": true}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.39, "seed_offset": 1000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.0239, "d_fwhm_ev": 0.0419, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": -0.0889, "d_fwhm_ev": -0.0014, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2, "winner": "main_plus_replica", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.8653919773281642, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:110:{"case": "charging_with_replica_candidate", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 7.37, "seed_offset": 1000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.141, "d_fwhm_ev": 0.1856, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:134:{"case": "overlap_sep0.7_h9000", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 5, "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 13.54, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.3741, "d_fwhm_ev": 0.2657, "matched_role": "main_a#3", "true_center": 197.2}, {"d_center_ev": -1.29, "d_fwhm_ev": -0.6, "matched_role": "main_a#2", "true_center": 198.04}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:159:{"case": "charging_no_replica_candidate", "chi_reduced": 1.7521780523190802, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0528, "d_fwhm_ev": -0.0962, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.4595, "d_fwhm_ev": 0.4025, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:160:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3077.8924377887674, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 7.273306463854169, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.03, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1416, "d_fwhm_ev": 0.2499, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 7.273306463854169, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:161:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3077.892007835877, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 7.273306463794299, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.07, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1416, "d_fwhm_ev": 0.2499, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 7.273306463794299, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:162:{"case": "charging_no_replica_candidate", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 3.59, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1085, "d_fwhm_ev": 0.1491, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:163:{"case": "charging_with_replica_candidate", "chi_reduced": 1.0564952083796528, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0319, "d_fwhm_ev": -0.0126, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.1501, "d_fwhm_ev": 0.1416, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:164:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3054.3526555265244, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 5.584627880499543, "survived": true}, {"bic_star": 2250.0786978167107, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.0564952055324386, "survived": true}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.16, "seed_offset": 2000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0319, "d_fwhm_ev": -0.0126, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": 0.1501, "d_fwhm_ev": 0.1416, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2, "winner": "main_plus_replica", "winner_absent_slots": [], "winner_autocorr_flag": false, "winner_boundary_hits": [], "winner_chi_reduced": 1.0564952055324386, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:165:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3054.3531150263357, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 5.584627880407254, "survived": true}, {"bic_star": 2250.0820292977264, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.0564952032164714, "survived": true}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.45, "seed_offset": 2000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0319, "d_fwhm_ev": -0.0126, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": 0.1502, "d_fwhm_ev": 0.1416, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2, "winner": "main_plus_replica", "winner_absent_slots": [], "winner_autocorr_flag": false, "winner_boundary_hits": [], "winner_chi_reduced": 1.0564952032164714, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:166:{"case": "charging_with_replica_candidate", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": true, "n_selected": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 6.89, "seed_offset": 2000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.1001, "d_fwhm_ev": 0.1878, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": -1.6, "d_fwhm_ev": 1.3, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:172:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 2811.9160721377707, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "sym_main", "orphan_peaks": false, "reduced_chi_sq": 6.339402041039051, "survived": true}, {"bic_star": 2502.999969437228, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "asym_main", "orphan_peaks": false, "reduced_chi_sq": 3.5054533590976438, "survived": true}], "case": "asym_truth_with_asym_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 0.09, "seed_offset": 2000, "success": true, "true_candidates": ["asym_main"], "truth_match": [{"d_center_ev": -0.0006, "d_fwhm_ev": -0.065, "matched_role": "main_a", "true_center": 197.8}], "truth_n": 1, "winner": "asym_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 3.5054533590976438, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/peak-fit-methods-decision-matrix.md:32:- **Oxidation state is read from the shake-up satellite separation, not the main-peak BE** (main-line shifts are small vs. linewidth). Diagnostic satellite-to-main separations: **U(IV) ≈ 6.8–7.1 eV, U(V) ≈ 8 eV, U(VI) ≈ 3.5–4 and ~10 eV.** [Ilton & Bagus 2011; Schindler 2009]
docs/autofit/peak-fit-methods-decision-matrix.md:64:- **Differential charging invalidates any method** — fix it before fitting, don't fit through it.
docs/autofit/peak-fit-methods-decision-matrix.md:83:**Actinide / weak components:** Ilton & Bagus, *SIA* 43, 1549 (2011), 10.1002/sia.3836 · Bagus et al. (heavy-element multiplets), *Surf. Sci.* 643, 142 (2016), 10.1016/j.susc.2015.06.002 · Ilton et al. (shallow core level), *PCCP* 19, 30473 (2017), 10.1039/C7CP05805E · Schindler et al. (U 4f uranyl), *GCA* 73, 2488 (2009), 10.1016/j.gca.2009.02.008 · Kvashnina et al. (HERFD-XANES), *PRL* 111, 253002 (2013) · Shard (quantitative XPS), *JVST A* 38, 041201 (2020), 10.1116/1.5141395 · Hill/Faradzhev/Powell (detection limit), *SIA* 49, 1187 (2017), 10.1002/sia.6285 · Shard (ISO 19668), *SIA* 50, 906 (2018), 10.1002/sia.6339.
tests/autofit/test_structural_fallback.py:346:def test_api_mixed_deep_plus_structural_runs_and_flags(client):
autofit/regions/n1s.py:8:(charge-reference exemplar, spec §3.5) is a later unit.
tests/autofit/test_noise_model.py:85:    """Replicates whose truth is BE-shifted (charging drift): the gradient
tests/autofit/test_cwt_detector.py:74:    x = np.arange(274.4, 293.5, 0.1)[:191]
tests/autofit/test_cwt_detector.py:126:        sig = _pv(x, 30000.0, 197.5, 3.5, ETA)
docs/autofit/codex/phaseD_unit3_verdict_runA.md:7:   Failure scenario: `resolve([Phase(..., regions=("Cu 2p",))], "Cu 2p", allow_structural_fallback=True)` returns `candidates == []`, but provenance includes `nominal_be_ev`, `be_window_ev`, and `spin_orbit.splitting_ev` for `Cu-2p1/2` and `Cu-2p3/2`. Fe/Mg/Rh/Au/Zn also expose nominal BEs and BE windows. `/api/analyze` returns these in `structure_report` and mixed-method payloads under `analysis.constants_provenance`. This violates the rail that fallback must never create a BE window, splitting, or other fit-enabling number.
autofit/regions/cl2p.py:29:positive low-BE shoulders at −2…−4.8 eV — differential-charging candidate,
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:392:-     "fwhm": 3.5752402300579225,
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:396:+     "fwhm": 3.5752402300533492,
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:403:-     "fwhm": 3.5752402300579225,
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:407:+     "fwhm": 3.5752402300533492,
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:1300:autofit/engine.py:2584:        # A future mixed-background grammar only affects DETECTION here —
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:1394:tests/autofit/stress_cases.py:23:                   charging replica, wrong background); the method must
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:1481:tests/test_mixed_ds_lacx_e2e.py:54:    background_method='none',
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:1791:   238	    ("C 1s", 270.0, 315.0),      # matches isC1sTab (index.html:6548)
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:1795:   242	    ("U 4f", 370.0, 415.0),      # span ~35 eV so their midpoint lands ~387
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:2222:   438	     "fwhm": 3.5752402300533492,
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:2229:   445	     "fwhm": 3.5752402300533492,
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:2567:tests/test_mixed_ds_lacx_e2e.py:50:result = run_fit(
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:2733:   765	              "fwhm_max":     3.0,                // optional
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md:2779:   811	            "differential_evolution", "basinhopping",
docs/autofit/codex/stage5_recheck2_verdict.md:12:   JSONL was still not fully regenerated — mixed append/resume output: 28
docs/autofit/codex/stage4_cookbook_review_prompt.txt:1:Adversarial review of the region-cookbook stage of the XPS autofit engine, branch feature-autofit-stage2, commit 0154efd (git show 0154efd; context git diff main...HEAD). Spec: docs/autofit/phase1-grammar-architecture-spec-v2.md §3.3–§3.5, §7, §9; run log docs/autofit/PROGRESS.md.
autofit/regions/c1s.py:77:# A/M/B families vs a 3.5 labeled-set-calibrated ceiling for the AG/MG
autofit/regions/c1s.py:84:# MIXED material class (2026-07-20): FWHM_RANGE_CONTAMINATION's ceiling is
autofit/regions/c1s.py:88:# (differential charging), and a non-uniform spatial distribution of
autofit/regions/c1s.py:89:# charging potentials broadens the observed peak (inhomogeneous
autofit/regions/c1s.py:95:# cap derived from THIS LAB'S OWN mixed-phase spectra would be exactly
autofit/regions/c1s.py:97:# of a tier badge). The floor is untouched: differential charging only
autofit/regions/c1s.py:105:# fitting.py's OWN existing fwhm_max default (15.0 eV), the ceiling the
autofit/regions/c1s.py:110:# fitted component pegs this ceiling under MIXED, that is the numerical
autofit/regions/c1s.py:115:# slots (see shared_decl below) — under MIXED that shared width relaxes
autofit/regions/c1s.py:122:FWHM_MIXED_CEILING_NUMERIC_GUARD_EV = 15.0
autofit/regions/c1s.py:126:    """FWHM_RANGE_CONTAMINATION, widened under MIXED. See the constant
autofit/regions/c1s.py:128:    if material_class is MaterialClass.MIXED:
autofit/regions/c1s.py:129:        return (FWHM_RANGE_CONTAMINATION[0], FWHM_MIXED_CEILING_NUMERIC_GUARD_EV)
autofit/regions/c1s.py:209:                       "a target; replaces the prior split 1.6/3.5 caps"},
autofit/regions/c1s.py:243:            {"constant": "mixed_material_class_width_relaxation",
autofit/regions/c1s.py:244:             "value": "under MaterialClass.MIXED (analyte embedded in a "
autofit/regions/c1s.py:252:             "source": "differential charging between analyte and matrix "
autofit/regions/c1s.py:259:                       "10.1116/6.0000057 — differential charging "
autofit/regions/c1s.py:268:            {"constant": "mixed_fwhm_ceiling_numeric_guard",
autofit/regions/c1s.py:269:             "value": FWHM_MIXED_CEILING_NUMERIC_GUARD_EV,
autofit/regions/c1s.py:274:                       "fitting.py's own existing fwhm_max default, the "
autofit/regions/c1s.py:293:        - M0–M3:  mixed graphitic (DS+G) + aliphatic (PV) two-main models
autofit/regions/c1s.py:386:        #     former split lab-practice (0.8, 3.5) convention was replaced
autofit/regions/c1s.py:397:        # --- M family: mixed graphitic (DS+G) + aliphatic (PV) two mains ---
tests/autofit/test_resolver.py:36:    # families present: DS+G asymmetric, expert-parity asym-GL, mixed, symmetric
docs/autofit/codex/adjudication_unit_verdict.md:20:   and mixed-shape rejection pinned in `test_cl2p_freewidth.py`.
tests/autofit/test_engine_doublet.py:96:                                  noise_floor=15.0, n_refits=6, rng_seed=0)
tests/autofit/test_candidate_pool.py:105:    x = np.arange(274.4, 293.5, 0.1)[:191]             # real grid geometry
tests/autofit/test_candidate_pool.py:166:        ys.append(_noisy(_pv(x, 30000.0, 197.5, 3.5, ETA), 300.0, 920 + seed))
tests/autofit/test_candidate_pool.py:361:    x = np.arange(274.4, 293.5, 0.1)[:191]
docs/autofit/codex/stress_suite_review_prompt.txt:6:  specified menu, differential-charging replica, asymmetric truth,
tests/autofit/test_multivariate_mcr.py:163:def test_build_matrix_interpolates_mixed_grids():
docs/autofit/codex/phaseD_unit3_recheck_prompt.txt:57:2. API pins: mixed deep+structural request → deep fit runs,
docs/autofit/codex/fwhm_cap_review_prompt.txt:27:   satellite 5.5, U 4f mains 3.5, B 1s 2.5, Cl 2p 2.2-3.0, N 1s 2.5) are
docs/autofit/codex/fwhm_cap_review_prompt.txt:41:     satellite); a U 4f main at 3.0 (declared 3.5) is NOT flagged; a
docs/autofit/codex/tougaard_bg_fixes_unit2_verdict_runB.md:730:  2584	        # A future mixed-background grammar only affects DETECTION here —
docs/autofit/codex/tougaard_bg_fixes_unit2_verdict_runB.md:1781:   811	            "differential_evolution", "basinhopping",
tests/autofit/test_fit_full_window_option.py:147:def test_full_window_mixed_model_branches_per_slot_not_per_region():
docs/autofit/codex/plain_english_pass_verdict_round3_runB.md:4:Prompt: docs/autofit/codex/plain_english_pass_recheck2_prompt.txt (recheck of round 2's mixed-payload finding)
tests/autofit/test_c1s_mixed_material_class.py:1:"""MIXED material class (2026-07-20 unit): analyte-in-matrix samples can
tests/autofit/test_c1s_mixed_material_class.py:6:adventitious/contamination FWHM ceiling, so MIXED relaxes it.
tests/autofit/test_c1s_mixed_material_class.py:10:"MIXED widens the cap to 3.5 eV because that's what our UCl4-in-graphite
tests/autofit/test_c1s_mixed_material_class.py:14:window does, and this feature has none. So MIXED only RELAXES an existing
tests/autofit/test_c1s_mixed_material_class.py:22:(2020), DOI 10.1116/6.0000057 -- differential charging broadens peaks
tests/autofit/test_c1s_mixed_material_class.py:24:peak broadening as a result of differential charging"), and a single
tests/autofit/test_c1s_mixed_material_class.py:25:charge correction is insufficient once differential charging is present:
tests/autofit/test_c1s_mixed_material_class.py:39:NON_MIXED = [MaterialClass.CONDUCTOR, MaterialClass.SEMICONDUCTOR,
tests/autofit/test_c1s_mixed_material_class.py:56:    (non-MIXED) convention -- identified by its FLOOR, which MIXED never
tests/autofit/test_c1s_mixed_material_class.py:66:@pytest.mark.parametrize("material_class", NON_MIXED)
tests/autofit/test_c1s_mixed_material_class.py:67:def test_non_mixed_candidate_pool_unchanged(material_class):
tests/autofit/test_c1s_mixed_material_class.py:69:    must build EXACTLY the pre-MIXED contamination fwhm_range -- byte
tests/autofit/test_c1s_mixed_material_class.py:76:            f"{name}/{slot.role}: fwhm_range changed for non-MIXED "
tests/autofit/test_c1s_mixed_material_class.py:81:@pytest.mark.parametrize("material_class", NON_MIXED)
tests/autofit/test_c1s_mixed_material_class.py:82:def test_non_mixed_candidate_names_unchanged(material_class):
tests/autofit/test_c1s_mixed_material_class.py:85:    non-MIXED material class (it always was -- material_class was
tests/autofit/test_c1s_mixed_material_class.py:92:def test_mixed_relaxes_contamination_fwhm_ceiling():
tests/autofit/test_c1s_mixed_material_class.py:93:    """The one concrete, falsifiable claim: MIXED must actually widen the
tests/autofit/test_c1s_mixed_material_class.py:95:    the feature is decorative. The FLOOR must NOT move: differential
tests/autofit/test_c1s_mixed_material_class.py:96:    charging only broadens a peak, it never narrows one, so there is no
tests/autofit/test_c1s_mixed_material_class.py:98:    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
tests/autofit/test_c1s_mixed_material_class.py:102:            f"{name}/{slot.role}: MIXED changed the FLOOR -- no physical "
tests/autofit/test_c1s_mixed_material_class.py:103:            "justification for narrowing under differential charging"
tests/autofit/test_c1s_mixed_material_class.py:106:            f"{name}/{slot.role}: MIXED did not widen the ceiling -- decorative"
tests/autofit/test_c1s_mixed_material_class.py:110:def test_mixed_does_not_touch_position_windows_or_offsets():
tests/autofit/test_c1s_mixed_material_class.py:111:    """The provenance-audit trap, enforced structurally: MIXED relaxes
tests/autofit/test_c1s_mixed_material_class.py:115:    a position window to admit an uncited differential-charging shift,
tests/autofit/test_c1s_mixed_material_class.py:118:    g_mixed = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:122:    assert windows(g_conductor) == windows(g_mixed), (
tests/autofit/test_c1s_mixed_material_class.py:123:        "MIXED must not alter any component's BE window"
tests/autofit/test_c1s_mixed_material_class.py:128:    assert offsets(g_conductor) == offsets(g_mixed), (
tests/autofit/test_c1s_mixed_material_class.py:129:        "MIXED must not alter any linked-offset (contaminant center) range"
tests/autofit/test_c1s_mixed_material_class.py:133:def test_mixed_does_not_touch_unrelated_fwhm_families():
tests/autofit/test_c1s_mixed_material_class.py:139:    g_mixed = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:146:    assert other_family_ranges(g_conductor) == other_family_ranges(g_mixed)
tests/autofit/test_c1s_mixed_material_class.py:149:def test_mixed_provenance_relaxation_record_asserts_no_new_value():
tests/autofit/test_c1s_mixed_material_class.py:151:    citing the differential-charging literature, and its `value` must
tests/autofit/test_c1s_mixed_material_class.py:158:    rec = _by_constant(records, "mixed_material_class_width_relaxation")
tests/autofit/test_c1s_mixed_material_class.py:172:def test_mixed_provenance_numeric_guard_record_is_honestly_labeled():
tests/autofit/test_c1s_mixed_material_class.py:179:    rec = _by_constant(records, "mixed_fwhm_ceiling_numeric_guard")
tests/autofit/test_c1s_mixed_material_class.py:186:    # actually uses under MIXED -- no drift between the doc and the code
tests/autofit/test_c1s_mixed_material_class.py:187:    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
tests/autofit/test_candidate_pool_wiring.py:181:    """NO-HALLUCINATION e2e: a peakless smooth step (charging-artifact
tests/autofit/fixtures/c1s_battery_expected.json:473:     "amplitude": 11315.069946209393,
tests/autofit/fixtures/c1s_battery_expected.json:715:     "area": -6413.5377101421445,
tests/autofit/fixtures/c1s_battery_expected.json:795:     "amplitude": 4263.598578409354,
tests/autofit/fixtures/c1s_battery_expected.json:877:     "area": -30803.582396212227,
tests/autofit/fixtures/c1s_battery_expected.json:930:     "fwhm": 3.526877294520959,
tests/autofit/fixtures/c1s_battery_expected.json:1090:     "fwhm": 3.524208219321252,
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:1200:./tests/test_mixed_ds_lacx_e2e.py:4:same code path as /api/fit, and assert each peak's parameters recover
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:1366:./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:27:I could not run pytest because the read-only sandbox has no usable temp directory, but I executed the extracted `tougaard_background` body directly and confirmed `[100,0,0,0] -> [0,0,0,0]`. I also checked the mixed-sign cancellation edge: it returns a signed unanchored correlation, consistent with the “negative counts pass through signed; no clamping” policy.
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:2803:docs/autofit/PROGRESS.md:1280:mixed-sign pass-through match the documented policy. **The Tougaard
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:2883:docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:27:I could not run pytest because the read-only sandbox has no usable temp directory, but I executed the extracted `tougaard_background` body directly and confirmed `[100,0,0,0] -> [0,0,0,0]`. I also checked the mixed-sign cancellation edge: it returns a signed unanchored correlation, consistent with the “negative counts pass through signed; no clamping” policy.
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:2890:uploads/3ee1dcee-2f3a-4c83-a33e-ce349f9dd4e8.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 21.9, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.5000049005795, "fwhm": 0.8000022727809339, "amplitude": 5999.985762735916, "gl_ratio": 8.555378627761456e-13, "stderr": {"center": 1.962102350870924e-06, "amplitude": 0.04162189670815025, "fwhm": 4.680060151954143e-06, "gl_ratio": 3.7802776622909907e-06}}], "confidence": {"main_aliphatic": {"sigma_stat": {"uncertainty_kind": "covariance", "values": {"center": 1.962102350870924e-06, "fwhm": 4.680060151954143e-06, "amplitude": 0.04162189670815025}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 2.7853275241795927e-12, "fwhm_mad": 4.9372728128105337e-11, "amplitude_mad": 2.594129000499379e-07}, "detectability": {"amplitude": 5999.985762735916, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:fwhm@min"], "max_cross_correlation": 0.6776994710374912}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "AG0_graphite_asymGL_satellite", "n_components": 2, "reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "bic_raw": -1732.2640251122796, "bic_weighted": 52.64466679288834, "n_eff_lag1": 366.3534125802044, "survived": true, "rank": 3, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['satellite_pi:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 3.186674785301061e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["satellite_pi:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_linked", "n_components": 3, "reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "bic_raw": -1721.6806443935482, "bic_weighted": 58.4939949414036, "n_eff_lag1": 363.28017154566334, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:fwhm@min', 'contamination_CO:center@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 5.19904519042311e-12}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.186864808391868e-11}], "proposed_peaks": [{"role": "proposed_peak_0", "accepted": false, "fitted_center": 284.0562, "fitted_fwhm": 0.5, "width_capped": false, "rejection_reason": "amplitude 1.0 \u2264 noise_floor 1.0", "near_roi_endpoint": false}], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_graphite_sym_CO_C=O", "n_components": 3, "reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "bic_raw": -1709.979884899033, "bic_weighted": 70.19264450130285, "n_eff_lag1": 363.28024523651777, "survived": true, "rank": 2, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_C=O:fwhm@max'], unphysical_widths=['contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)'], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.1271782252075944e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.382268211640556e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": ["contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)"], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["contamination_CO:center@max", "contamination_C=O:fwhm@max"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "bic_raw": -1708.8655954986962, "bic_weighted": 76.0419659126833, "n_eff_lag1": 366.35338688232457, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 7.909867801039288e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["main_aliphatic:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_linked", "n_components": 3, "reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "bic_raw": -1708.8655820330348, "bic_weighted": 76.04196591267502, "n_eff_lag1": 366.3533885732838, "survived": true, "rank": 5, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.4061902357893664e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 1.3408724708678914e-14}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "n_components": 3, "reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "bic_raw": -1708.8655817728024, "bic_weighted": 76.04196591267494, "n_eff_lag1": 366.3533923770929, "survived": true, "rank": 4, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.628908028198292e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.753864998110036e-16}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}], "non_converged": [], "ambiguous_pairs": [["B2_linked", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.12); structural difference: {'main_graphitic', 'main_aliphatic', 'contamination_CO', 'contamination_C=O', 'satellite_pi'}"], ["B2_graphite_sym_CO_C=O", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.11); structural difference: {'contamination_C=O', 'satellite_pi', 'contamination_CO'}"], ["AG0_graphite_asymGL_satellite", "AG1_graphite_asymGL_sat_plus_CO", "Indistinguishable on fit quality and BIC* (\u0394BIC*=0.00); structural difference: {'contamination_CO'}"]], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max", "residual_gap"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8, "residual_gap": {"n_attempts": 1, "n_accepted": 0}}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 2356.1031279564713, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 2379.5009607446636, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 2402.898356672834, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 2426.2955913250544, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 2379.5009606895596, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 2397.0489719191914, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 2414.5969365032793, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 2379.500437560467, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 2397.0484483372284, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 2414.596388869996, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": -1732.2628630458792, "selected": true}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": -1708.8655817728024, "selected": true}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": -1685.4717428556983, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": -1662.0718740907616, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": -1708.8655820330348, "selected": true}, {"name": "AG2_linked", "converged": true, "bic": -1691.3175603688178, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": -1673.7697813731577, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2379.5009857340206, "selected": false}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2402.8983010024053, "selected": false}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2426.29571673858, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2449.693448965505, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": -1708.8655888943526, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": -1685.4680086668614, "selected": false}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": -1662.0707790890274, "selected": false}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": -690.5033612735614, "selected": false}, {"name": "B2_linked", "converged": true, "bic": -1721.6789198318845, "selected": true}, {"name": "B3_linked", "converged": true, "bic": -1704.1305018737503, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": -1709.9798453429748, "selected": true}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": -1686.5824714043713, "selected": false}], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"AG0_graphite_asymGL_satellite": {"reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "aicc": -1766.373823502721, "n_params": 9, "n_params_adjusted": 5, "n_components": 2}, "B2_linked": {"reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "aicc": -1759.519130288255, "n_params": 10, "n_params_adjusted": 4, "n_components": 3}, "B2_graphite_sym_CO_C=O": {"reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "aicc": -1755.2376505218683, "n_params": 12, "n_params_adjusted": 4, "n_components": 3}, "MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "aicc": -1757.8137245449122, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "AG1_linked": {"reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "aicc": -1757.8137110792509, "n_params": 13, "n_params_adjusted": 6, "n_components": 3}, "AG1_graphite_asymGL_sat_plus_CO": {"reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "aicc": -1757.8137108190185, "n_params": 13, "n_params_adjusted": 5, "n_components": 3}}, "top_by_bic_star": "B2_linked", "top_by_aicc": "AG0_graphite_asymGL_satellite", "bic_ambiguous": true, "criteria_conflict": true, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "B2_linked", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "preseeded_features": [], "n_survivors": 5, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner B2_linked has constraint violations ['main_aliphatic:fwhm@min', 'contamination_CO:center@min'] (see analysis.candidates). ", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:2891:uploads/58ef8f7c-8e65-4581-a1d5-b342298d1425.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 60.5, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_graphitic", "region": "C 1s", "phase_id": "sample", "shape": "ds_g", "center": 284.40862660161633, "fwhm": 0.6625927514639813, "amplitude": 3312.068644701938, "alpha": 4.6264159170306125e-12, "beta": 0.05, "m_gauss": 0.6625927514639813}, {"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.60000000001236, "fwhm": 0.8000000000185057, "amplitude": 2954.930348377461, "gl_ratio": 1.5421386390102043e-11}], "confidence": {"main_graphitic": {"sigma_stat": {"uncertainty_kind": "stability_mad", "values": {"center": 0.04460548852011925, "fwhm": 0.02629222009172294, "amplitude": 1333.794922536627}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 0.04460548852011925, "fwhm_mad": 0.02629222009172294, "amplitude_mad": 1333.794922536627}, "detectability": {"amplitude": 3312.068644701938, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": [], "max_cross_correlation": null}}, "main_aliphatic": {"sigma_stat": {"uncertainty_kind": "stability_mad", "values": {"center": 1.1368683772161603e-13, "fwhm": 0.0, "amplitude": 0.01636871560003783}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 0.75, "position_mad": 1.1368683772161603e-13, "fwhm_mad": 0.0, "amplitude_mad": 0.01636871560003783}, "detectability": {"amplitude": 2954.930348377461, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min"], "max_cross_correlation": null}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866390594288e-06, "bic_star": -1732.2629233085559, "bic_raw": -1708.8656241887684, "bic_weighted": 76.04196591268362, "n_eff_lag1": 366.3533853562398, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.732479228417388e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 4}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "n_components": 4, "reduced_chi_sq": 2.2538587778357373e-06, "bic_star": -1732.262137328864, "bic_raw": -1685.467539089289, "bic_weighted": 99.4392650324933, "n_eff_lag1": 366.353460351388, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:offset@max', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.4702538358659414e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.515142706037034e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["contamination_CO:fwhm@min", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:offset@max", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 4}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "n_components": 5, "reduced_chi_sq": 2.2815134764749067e-06, "bic_star": -1732.262147660311, "bic_raw": -1662.0702503009486, "bic_weighted": 122.83656415227738, "n_eff_lag1": 366.3534720499048, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_C=O:center@max', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.5356066679308465e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.3563402013254895e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 6.937798106689261e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.25, "boundary_hits": ["contamination_C=O:center@max", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 3}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "n_components": 6, "reduced_chi_sq": 2.1990369814617878e-06, "bic_star": -1762.164200824285, "bic_raw": -1668.5750043451353, "bic_weighted": 146.2338275885795, "n_eff_lag1": 401.06051089289645, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 2.889000740966408e-10}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.084367297735124e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 3.3135447554575374e-11}, {"role": "contamination_OC=O", "persistence": 0.0, "area_fraction": 5.868305324176354e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.25, "boundary_hits": ["contamination_CO:center@max", "contamination_CO:fwhm@min", "contamination_C=O:fwhm@min", "contamination_OC=O:fwhm@min", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 1}, {"name": "M0_graph_asym_aliph_sym_satellite", "n_components": 3, "reduced_chi_sq": 0.5445546916051832, "bic_star": 2199.204211199102, "bic_raw": 2222.6015103188893, "bic_weighted": 252.6177190470987, "n_eff_lag1": 4.371020551972791, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:center@min', 'main_aliphatic:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 1.1139261674936666e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": true, "min_active_persistence": 0.25, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 1}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "n_components": 4, "reduced_chi_sq": 0.5511354169322392, "bic_star": 2199.1834191338194, "bic_raw": 2245.9780173733943, "bic_weighted": 276.01501948372095, "n_eff_lag1": 4.3708990513348684, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:center@min', 'main_aliphatic:fwhm@min', 'contamination_CO:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.2370351534164325e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.487697359241712e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": true, "min_active_persistence": 0.75, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min", "contamination_CO:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 2}], "non_converged": [], "ambiguous_pairs": [], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 3753.6915569887074, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 3777.0797675518816, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 3800.4736710871393, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 3823.878033686888, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 3777.0797675518816, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 3794.6107745192317, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 3812.179292646422, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 3777.07751804941, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 3794.603988962943, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 3812.1648087337817, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": 3203.092457785431, "selected": false}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": 3226.4895926311533, "selected": false}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": 3249.886864603099, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 3273.2841770393084, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": 3226.4896031446615, "selected": false}, {"name": "AG2_linked", "converged": true, "bic": 3244.0434203132595, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": 3261.5855136976834, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2263.1271879845717, "selected": true}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2286.5244671115156, "selected": true}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2309.921556825529, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2333.3190793743943, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": 1953.573584264419, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": 1976.9708924404435, "selected": true}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": 2000.3681945376777, "selected": true}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": 2023.7655196301753, "selected": true}, {"name": "B2_linked", "converged": true, "bic": 3807.15449535746, "selected": false}, {"name": "B3_linked", "converged": true, "bic": 3824.7024555091207, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": 3813.7161299169506, "selected": false}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": 3837.514037613595, "selected": false}], "filtered_dominant_alternative": {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "bic_star": -1762.164200824285, "delta_bic_vs_winner": 3961.3476199581046, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)"}, "weighted_ic_disagreement": null, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866390594288e-06, "bic_star": -1732.2629233085559, "aicc": -1757.8137532349845, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "MG1_graphAsymGL_aliph_sat_CO": {"reduced_chi_sq": 2.2538587778357373e-06, "bic_star": -1732.262137328864, "aicc": -1749.045877977565, "n_params": 17, "n_params_adjusted": 9, "n_components": 4}, "MG2_graphAsymGL_aliph_sat_CO_C=O": {"reduced_chi_sq": 2.2815134764749067e-06, "bic_star": -1732.262147660311, "aicc": -1740.0629937567558, "n_params": 21, "n_params_adjusted": 9, "n_components": 5}, "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O": {"reduced_chi_sq": 2.1990369814617878e-06, "bic_star": -1762.164200824285, "aicc": -1760.7582796070465, "n_params": 25, "n_params_adjusted": 9, "n_components": 6}, "M0_graph_asym_aliph_sym_satellite": {"reduced_chi_sq": 0.5445546916051832, "bic_star": 2199.204211199102, "aicc": 2177.343744696054, "n_params": 12, "n_params_adjusted": 8, "n_components": 3}, "M1_graph_asym_aliph_sym_sat_CO": {"reduced_chi_sq": 0.5511354169322392, "bic_star": 2199.1834191338194, "aicc": 2186.037305742729, "n_params": 16, "n_params_adjusted": 8, "n_components": 4}}, "top_by_bic_star": "M1_graph_asym_aliph_sym_sat_CO", "top_by_aicc": "M1_graph_asym_aliph_sym_sat_CO", "bic_ambiguous": false, "criteria_conflict": false, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "M1_graph_asym_aliph_sym_sat_CO", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min", "contamination_CO:fwhm@min", "satellite_pi:fwhm@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "bic_star": -1762.164200824285, "delta_bic_vs_winner": 3961.3476199581046, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)"}, "weighted_ic_disagreement": null, "preseeded_features": [], "n_survivors": 1, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner M1_graph_asym_aliph_sym_sat_CO has constraint violations ['main_aliphatic:center@min', 'main_aliphatic:fwhm@min', 'contamination_CO:fwhm@min', 'satellite_pi:fwhm@min'] (see analysis.candidates).  WARNING: filtered candidate MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O beats this winner by \u0394BIC* 3961.3 but did not survive filtering (plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True))", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:2892:uploads/a0499bc7-9313-4388-8408-d6e42386862c.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 22.5, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.5000049005795, "fwhm": 0.8000022727809339, "amplitude": 5999.985762735916, "gl_ratio": 8.555378627761456e-13, "stderr": {"center": 1.962102350870924e-06, "amplitude": 0.04162189670815025, "fwhm": 4.680060151954143e-06, "gl_ratio": 3.7802776622909907e-06}}], "confidence": {"main_aliphatic": {"sigma_stat": {"uncertainty_kind": "covariance", "values": {"center": 1.962102350870924e-06, "fwhm": 4.680060151954143e-06, "amplitude": 0.04162189670815025}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 2.7853275241795927e-12, "fwhm_mad": 4.9372728128105337e-11, "amplitude_mad": 2.594129000499379e-07}, "detectability": {"amplitude": 5999.985762735916, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:fwhm@min"], "max_cross_correlation": 0.6776994710374912}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "AG0_graphite_asymGL_satellite", "n_components": 2, "reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "bic_raw": -1732.2640251122796, "bic_weighted": 52.64466679288834, "n_eff_lag1": 366.3534125802044, "survived": true, "rank": 3, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['satellite_pi:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 3.186674785301061e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["satellite_pi:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_linked", "n_components": 3, "reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "bic_raw": -1721.6806443935482, "bic_weighted": 58.4939949414036, "n_eff_lag1": 363.28017154566334, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:fwhm@min', 'contamination_CO:center@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 5.19904519042311e-12}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.186864808391868e-11}], "proposed_peaks": [{"role": "proposed_peak_0", "accepted": false, "fitted_center": 284.0562, "fitted_fwhm": 0.5, "width_capped": false, "rejection_reason": "amplitude 1.0 \u2264 noise_floor 1.0", "near_roi_endpoint": false}], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_graphite_sym_CO_C=O", "n_components": 3, "reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "bic_raw": -1709.979884899033, "bic_weighted": 70.19264450130285, "n_eff_lag1": 363.28024523651777, "survived": true, "rank": 2, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_C=O:fwhm@max'], unphysical_widths=['contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)'], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.1271782252075944e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.382268211640556e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": ["contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)"], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["contamination_CO:center@max", "contamination_C=O:fwhm@max"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "bic_raw": -1708.8655954986962, "bic_weighted": 76.0419659126833, "n_eff_lag1": 366.35338688232457, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 7.909867801039288e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["main_aliphatic:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_linked", "n_components": 3, "reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "bic_raw": -1708.8655820330348, "bic_weighted": 76.04196591267502, "n_eff_lag1": 366.3533885732838, "survived": true, "rank": 5, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.4061902357893664e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 1.3408724708678914e-14}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "n_components": 3, "reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "bic_raw": -1708.8655817728024, "bic_weighted": 76.04196591267494, "n_eff_lag1": 366.3533923770929, "survived": true, "rank": 4, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.628908028198292e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.753864998110036e-16}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}], "non_converged": [], "ambiguous_pairs": [["B2_linked", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.12); structural difference: {'main_graphitic', 'main_aliphatic', 'contamination_CO', 'contamination_C=O', 'satellite_pi'}"], ["B2_graphite_sym_CO_C=O", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.11); structural difference: {'contamination_C=O', 'satellite_pi', 'contamination_CO'}"], ["AG0_graphite_asymGL_satellite", "AG1_graphite_asymGL_sat_plus_CO", "Indistinguishable on fit quality and BIC* (\u0394BIC*=0.00); structural difference: {'contamination_CO'}"]], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max", "residual_gap"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8, "residual_gap": {"n_attempts": 1, "n_accepted": 0}}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 2356.1031279564713, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 2379.5009607446636, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 2402.898356672834, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 2426.2955913250544, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 2379.5009606895596, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 2397.0489719191914, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 2414.5969365032793, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 2379.500437560467, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 2397.0484483372284, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 2414.596388869996, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": -1732.2628630458792, "selected": true}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": -1708.8655817728024, "selected": true}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": -1685.4717428556983, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": -1662.0718740907616, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": -1708.8655820330348, "selected": true}, {"name": "AG2_linked", "converged": true, "bic": -1691.3175603688178, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": -1673.7697813731577, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2379.5009857340206, "selected": false}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2402.8983010024053, "selected": false}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2426.29571673858, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2449.693448965505, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": -1708.8655888943526, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": -1685.4680086668614, "selected": false}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": -1662.0707790890274, "selected": false}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": -690.5033612735614, "selected": false}, {"name": "B2_linked", "converged": true, "bic": -1721.6789198318845, "selected": true}, {"name": "B3_linked", "converged": true, "bic": -1704.1305018737503, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": -1709.9798453429748, "selected": true}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": -1686.5824714043713, "selected": false}], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"AG0_graphite_asymGL_satellite": {"reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "aicc": -1766.373823502721, "n_params": 9, "n_params_adjusted": 5, "n_components": 2}, "B2_linked": {"reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "aicc": -1759.519130288255, "n_params": 10, "n_params_adjusted": 4, "n_components": 3}, "B2_graphite_sym_CO_C=O": {"reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "aicc": -1755.2376505218683, "n_params": 12, "n_params_adjusted": 4, "n_components": 3}, "MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "aicc": -1757.8137245449122, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "AG1_linked": {"reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "aicc": -1757.8137110792509, "n_params": 13, "n_params_adjusted": 6, "n_components": 3}, "AG1_graphite_asymGL_sat_plus_CO": {"reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "aicc": -1757.8137108190185, "n_params": 13, "n_params_adjusted": 5, "n_components": 3}}, "top_by_bic_star": "B2_linked", "top_by_aicc": "AG0_graphite_asymGL_satellite", "bic_ambiguous": true, "criteria_conflict": true, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "B2_linked", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "preseeded_features": [], "n_survivors": 5, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner B2_linked has constraint violations ['main_aliphatic:fwhm@min', 'contamination_CO:center@min'] (see analysis.candidates). ", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:3724:bg 0,191.3,390.5,596.5,807.6,1022.3,1013.5,1006.8,1002.3,1000,1000 min 0 max 1022.3289246060109
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:3725:overshoot idx 1:191.3>0 2:390.5>0 3:596.5>0 4:807.6>0 6:1013.5>0 7:1006.8>0 8:1002.3>0 9:1000.0>0
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:3727:bg 400,494.2,563.5,605.3,617.3,597.4,753.6,874.7,957.8,1000,1000 min 400 max 1000
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:3728:overshoot idx 1:494.2>350 2:563.5>300 3:605.3>250 4:617.3>200 6:753.6>150 7:874.7>100 8:957.8>50 9:1000.0>25
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:3879:   765	              "fwhm_max":     3.0,                // optional
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md:3983:   811	            "differential_evolution", "basinhopping",
tests/autofit/fixtures/b1s_battery_expected.json:8:     "area": -42343.509473059705,
docs/autofit/codex/phaseD_unit3_recheck_verdict_runA.md:14:Run B minor 2: **CLOSED.** The API pins at [tests/autofit/test_structural_fallback.py](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:306) and [tests/autofit/test_structural_fallback.py](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:325) would fail for the guarded regressions: missing mixed `structural_only`, wiped deep fit, missing structural provenance in `analysis.constants_provenance`, or `least_squares` entering structural degradation.
tests/autofit/fixtures/u4f_battery_expected.json:206:     "amplitude": 1193.5114013746593,
tests/autofit/fixtures/u4f_battery_expected.json:438:     "fwhm": 3.5752402300533492,
tests/autofit/fixtures/u4f_battery_expected.json:445:     "fwhm": 3.5752402300533492,
docs/autofit/codex/plain_english_pass_recheck2_prompt.txt:42:- a MIXED-SUCCESS case (`structural_only: ['Fe 2p']`, `success: true`,
docs/autofit/codex/plain_english_pass_recheck2_prompt.txt:46:- a MIXED-FAILURE case (`structural_only: ['Fe 2p']`, `success: false`,
docs/autofit/codex/plain_english_pass_recheck2_prompt.txt:51:has one) — this is WHY the mixed-success test initially failed for the
docs/autofit/codex/plain_english_pass_recheck2_prompt.txt:54:realistic mixed-success payload shape.
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runB.md:920:fitting.py:706:    # backwards compat with previously-saved (integer-m) fits. With 3.5
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runB.md:979:templates/index.html:1903:          <button class="save-dropdown-item" id="auto-fit-c1s-menu-item" onclick="runAutoFitC1sGraphite()" title="Available only on C1s spectra (ROI midpoint 270–315 eV)"><span class="dd-icon">&#128293;</span><div>Auto-Fit C1s Graphite<small>One-click fit + charge correction</small></div></button>
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runB.md:2539:  1231	    6033.509405194101,
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runB.md:2670:tests/test_mixed_ds_lacx_e2e.py
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runB.md:2697:[Clang 17.0.0 (clang-1700.0.13.5)]
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runB.md:3241:/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import numpy as np\\ndef tb(x,y,C=1643.0,force_desc=True,old_f1=False):\\n    B=2866.0; n=len(x)\\n    if n<2: return np.zeros_like(y,dtype=float)\\n    xa=np.asarray(x,dtype=float); ya=np.asarray(y,dtype=float); flipped=False\\n    if force_desc:\\n        flipped=bool(xa[0]<xa[-1])\\n        if flipped: xa,ya=xa[::-1].copy(),ya[::-1].copy()\\n    dx=float(abs(xa[1]-xa[0])); diffs=np.diff(xa); uniform=bool(dx>0.0 and np.max(np.abs(diffs-diffs[0]))<=1e-6*dx)\\n    if old_f1:\\n        net=ya; c0=0.0\\n    else:\\n        c0=float(ya[-1]); net=ya-c0\\n    if uniform:\\n        m=np.arange(n,dtype=float); T=m*dx; k=(B*T)/(C+T*T)**2; bg=np.convolve(net,k[::-1])[n-1:]*dx\\n    else:\\n        w=np.abs(np.gradient(xa)); bg=np.zeros(n)\\n        for i in range(n):\\n            T=np.abs(xa[i:]-xa[i]); kernel=(B*T)/(C+T*T)**2; bg[i]=float(np.sum(kernel*net[i:]*w[i:]))\\n    if old_f1:\\n        out=bg*float(ya[0]) if bg[0]==0.0 else bg*(float(ya[0])/bg[0])\\n    else:\\n        out=np.full(n,c0) if bg[0]==0.0 else c0+bg*((float(ya[0])-c0)/bg[0])\\n    return out[::-1] if (force_desc and flipped) else out\\n# C-squared pin\\nx=np.linspace(100.0,0.0,1001); y=np.full_like(x,1e-9); y[0]=2e-9; y[800]=1e6\\nfor C in (1643.0,1643.0**2):\\n    bg=tb(x,y,C=C); peak_x=x[:800][np.argmax(bg[:800])]; print(\"C\",C,\"peak_x\",peak_x,\"passes\",abs(peak_x-(20+np.sqrt(1643.0/3.0)))<=0.25)\\n# order pin under no normalization\\nxd=np.linspace(295.0,280.0,151); yd=100.0+5000.0*np.exp(-0.5*((xd-287.0)/0.8)**2)+400.0/(1.0+np.exp(-(287.0-xd)))\\nprint(\"ascending_without_normalization_maxdiff\",float(np.max(np.abs(tb(xd,yd)-tb(xd[::-1].copy(),yd[::-1].copy(),force_desc=False)[::-1]))))\\n# F1 old behavior against nonzero C0 pins\\nxflat=np.linspace(740.0,700.0,200); yflat=np.full_like(xflat,500.0); print(\"old_f1_flat_net_max\",float(np.max(np.abs(yflat-tb(xflat,yflat,old_f1=True)))))\\nxw=np.linspace(740.0,700.0,600); pk=6000.0*np.exp(-0.5*((xw-710.9)/1.6)**2)+3000.0*np.exp(-0.5*((xw-724.5)/1.9)**2); baseline=4000.0+3000.0*np.cumsum(pk[::-1])[::-1]/np.sum(pk); yw=pk+baseline; bgold=tb(xw,yw,old_f1=True); print(\"old_f1_wide_low_edge\",bgold[-1],\"want\",yw[-1],\"diff\",bgold[-1]-yw[-1])\\n# negative scale scenario\\nxn=np.linspace(295.0,280.0,151); yn=500.0-400.0*(xn-280.0)/15.0; bg=tb(xn,yn); print(\"negative_scale_endpoint_delta\",yn[0]-yn[-1],\"bg_edges\",bg[0],bg[-1],\"minmax\",float(bg.min()),float(bg.max()))'" in /Users/skyefortier/xps-verify
docs/autofit/codex/mixed_material_class_review_prompt.txt:2:peak-fitting web app). Review commit 77bf3a8 ("feat(autofit): MIXED
docs/autofit/codex/mixed_material_class_review_prompt.txt:3:material class -- relax C1s contamination width under differential
docs/autofit/codex/mixed_material_class_review_prompt.txt:4:charging") on branch feature-autofit-stage2 -- `git show 77bf3a8`
docs/autofit/codex/mixed_material_class_review_prompt.txt:10:BACKGROUND -- what MIXED is supposed to be:
docs/autofit/codex/mixed_material_class_review_prompt.txt:12:MaterialClass gains a 4th member, MIXED = "mixed", for analyte-in-matrix
docs/autofit/codex/mixed_material_class_review_prompt.txt:14:matrix can charge differently under X-ray illumination (differential
docs/autofit/codex/mixed_material_class_review_prompt.txt:15:charging), which (a) broadens peaks (a distribution of local surface
docs/autofit/codex/mixed_material_class_review_prompt.txt:19:contamination/adventitious FWHM ceiling (0.8-2.0 eV -> 0.8-15.0 eV) under
docs/autofit/codex/mixed_material_class_review_prompt.txt:20:MIXED; every other constraint (position windows, linked offsets, every
docs/autofit/codex/mixed_material_class_review_prompt.txt:23:THE EXPLICIT DESIGN CONSTRAINT (read this before reviewing the diff): MIXED
docs/autofit/codex/mixed_material_class_review_prompt.txt:25:derived from this lab's own mixed-phase spectra (e.g. "3.5 eV because
docs/autofit/codex/mixed_material_class_review_prompt.txt:28:badge. The 15.0 eV ceiling is claimed to be a pure numeric guard reused
docs/autofit/codex/mixed_material_class_review_prompt.txt:29:from fitting.py's own existing fwhm_max default (needed because
docs/autofit/codex/mixed_material_class_review_prompt.txt:37:(a) SELF-REFERENCE CHECK. Is the 15.0 eV ceiling ACTUALLY traceable to
docs/autofit/codex/mixed_material_class_review_prompt.txt:38:    fitting.py's existing fwhm_max default (grep for it -- fitting.py's
docs/autofit/codex/mixed_material_class_review_prompt.txt:39:    _make_peak_params, spec.get("fwhm_max", 15.0)), or is it coincidentally
docs/autofit/codex/mixed_material_class_review_prompt.txt:42:    decisions.md for any number near 15.0 that could be the REAL source
docs/autofit/codex/mixed_material_class_review_prompt.txt:45:    15.0 and not some other pre-existing engine constant)?
docs/autofit/codex/mixed_material_class_review_prompt.txt:47:(b) OPTIMIZER DEGENERACY. Relaxing a width ceiling from 2.0 to 15.0 eV
docs/autofit/codex/mixed_material_class_review_prompt.txt:52:    (_SHARED_CONTAM_FWHM) via shared_fwhm_params. Under MIXED that shared
docs/autofit/codex/mixed_material_class_review_prompt.txt:53:    width's own range also widens to (0.8, 15.0) -- construct or reason
docs/autofit/codex/mixed_material_class_review_prompt.txt:55:    contaminant component under MIXED balloons wide enough to functionally
docs/autofit/codex/mixed_material_class_review_prompt.txt:57:    eV C 1s contaminant span is only ~8-12 eV wide -- a 15 eV FWHM
docs/autofit/codex/mixed_material_class_review_prompt.txt:62:    materializes on a real or synthetic fit, is FWHM_MIXED_CEILING_NUMERIC_
docs/autofit/codex/mixed_material_class_review_prompt.txt:63:    GUARD_EV = 15.0 too permissive, and would a MUCH lower numeric guard
docs/autofit/codex/mixed_material_class_review_prompt.txt:68:    phase.material_class is MaterialClass.MIXED -- run/reason through the
docs/autofit/codex/mixed_material_class_review_prompt.txt:69:    non-MIXED path (conductor/semiconductor/insulator) and confirm the
docs/autofit/codex/mixed_material_class_review_prompt.txt:72:    test_c1s_mixed_material_class.py claims this structurally -- verify the
docs/autofit/codex/mixed_material_class_review_prompt.txt:75:    material_class at all -- MIXED must be a no-op everywhere except C1s.
docs/autofit/codex/mixed_material_class_review_prompt.txt:78:    mixed.hint is the ONLY user-visible description of what MIXED does.
docs/autofit/codex/mixed_material_class_review_prompt.txt:80:    or measured the differential charging) or understate (failing to warn
docs/autofit/codex/mixed_material_class_review_prompt.txt:82:    actually does? The DECIDED constraint (Skye, 2026-07-17) is that MIXED
docs/autofit/codex/mixed_material_class_review_prompt.txt:89:    "MIXED must not alter the charge-correction step in any way. Not
docs/autofit/codex/mixed_material_class_review_prompt.txt:106:test_c1s_mixed_material_class.py, tests/js/fp_material_mixed.test.js. Zero
docs/autofit/codex/mixed_material_class_review_prompt.txt:113:test_mixed_relaxes_contamination_fwhm_ceiling (would it catch MIXED being
docs/autofit/codex/mixed_material_class_review_prompt.txt:114:silently a no-op?), test_mixed_provenance_relaxation_record_asserts_no_new_
docs/autofit/codex/mixed_material_class_review_prompt.txt:116:and the FWHM_MIXED_CEILING_NUMERIC_GUARD_EV == provenance-record-value
docs/autofit/fit-physics-coverage-report.md:56:| Te-3d5/2 | 573.03 | Powe95 | 572.1–573.54 | stage9-dual | — | dual |
docs/autofit/fit-physics-coverage-report.md:72:| W-4d5/2 | 243.5 | Powe95 | 243.5–244 | expansion | 20040919030310 | ✓ |
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:23:- For adversarial mixed-sign exact cancellation, the guard does not edge-match or clamp; it returns a signed, unanchored shape scaled through the `denom = 1` fallback. The “all zeros in practice” wording is accurate for the documented nonnegative no-loss case, not a universal mixed-sign claim.
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json:3:  "timestamp": "2026-04-27T04:32:03.507Z",
docs/autofit/codex/stage5_recheck3_prompt.txt:5:1. (BLOCKER) mixed-schema/duplicated validation JSONL → the artifact
docs/autofit/codex/c1s_multienv_fix_review_prompt.txt:50:     modules are single-background)? Flag if a mixed-background grammar
docs/autofit/codex/c1s_multienv_fix_recheck_prompt.txt:35:- new constant PROPOSAL_MIN_FIT_BUDGET_SEC = 15.0; a guard at the top of
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:56:guard, where bg[0] could in principle be exactly -0/0 with mixed-sign
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:793:tests/autofit/stress_cases.py:23:                   charging replica, wrong background); the method must
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:837:tests/test_mixed_ds_lacx_e2e.py:54:    background_method='none',
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:885:tests/autofit/stress_cases.py:23:                   charging replica, wrong background); the method must
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:2102:docs/autofit/inventory/stress_battery_runs.jsonl:41:{"case": "charging_no_replica_candidate", "chi_reduced": 2.11933018079081, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.0397, "d_fwhm_ev": 0.0591, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": -0.1661, "d_fwhm_ev": -0.1165, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:2103:docs/autofit/inventory/stress_battery_runs.jsonl:46:{"case": "charging_with_replica_candidate", "chi_reduced": 1.747290088264468, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 0, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0655, "d_fwhm_ev": -0.1281, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.4835, "d_fwhm_ev": 0.3695, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:2112:docs/autofit/inventory/stress_battery_runs.jsonl:67:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4146.61792120331, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 126.30873391628948, "survived": false}, {"bic_star": 2433.522542110988, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.2355887929329685, "survived": true}, {"bic_star": 2464.9017984747015, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.2209246366731366, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 1.17, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0012, "d_fwhm_ev": 0.0114, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0018, "d_fwhm_ev": 0.0065, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.2355887929329685, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:2113:docs/autofit/inventory/stress_battery_runs.jsonl:68:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4146.6177847728, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 126.30873391534688, "survived": false}, {"bic_star": 2433.5225504652817, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.2355887929327787, "survived": true}, {"bic_star": 2464.9017984747015, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 0.9166666666666666, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.2209246366731366, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 2.72, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0012, "d_fwhm_ev": 0.0114, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0018, "d_fwhm_ev": 0.0065, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.2355887929327787, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:2124:docs/autofit/inventory/stress_battery_runs.jsonl:103:{"case": "charging_no_replica_candidate", "chi_reduced": 3.2617136636412978, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.06, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0196, "d_fwhm_ev": -0.1273, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.5088, "d_fwhm_ev": 0.4886, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:2125:docs/autofit/inventory/stress_battery_runs.jsonl:107:{"case": "charging_with_replica_candidate", "chi_reduced": 1.8653919775457, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.0239, "d_fwhm_ev": 0.0419, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": -0.0889, "d_fwhm_ev": -0.0014, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:2144:docs/autofit/inventory/stress_battery_runs.jsonl:159:{"case": "charging_no_replica_candidate", "chi_reduced": 1.7521780523190802, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0528, "d_fwhm_ev": -0.0962, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.4595, "d_fwhm_ev": 0.4025, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:2145:docs/autofit/inventory/stress_battery_runs.jsonl:163:{"case": "charging_with_replica_candidate", "chi_reduced": 1.0564952083796528, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0319, "d_fwhm_ev": -0.0126, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.1501, "d_fwhm_ev": 0.1416, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:2159:uploads/a0499bc7-9313-4388-8408-d6e42386862c.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 22.5, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.5000049005795, "fwhm": 0.8000022727809339, "amplitude": 5999.985762735916, "gl_ratio": 8.555378627761456e-13, "stderr": {"center": 1.962102350870924e-06, "amplitude": 0.04162189670815025, "fwhm": 4.680060151954143e-06, "gl_ratio": 3.7802776622909907e-06}}], "confidence": {"main_aliphatic": {"sigma_stat": {"uncertainty_kind": "covariance", "values": {"center": 1.962102350870924e-06, "fwhm": 4.680060151954143e-06, "amplitude": 0.04162189670815025}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 2.7853275241795927e-12, "fwhm_mad": 4.9372728128105337e-11, "amplitude_mad": 2.594129000499379e-07}, "detectability": {"amplitude": 5999.985762735916, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:fwhm@min"], "max_cross_correlation": 0.6776994710374912}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "AG0_graphite_asymGL_satellite", "n_components": 2, "reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "bic_raw": -1732.2640251122796, "bic_weighted": 52.64466679288834, "n_eff_lag1": 366.3534125802044, "survived": true, "rank": 3, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['satellite_pi:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 3.186674785301061e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["satellite_pi:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_linked", "n_components": 3, "reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "bic_raw": -1721.6806443935482, "bic_weighted": 58.4939949414036, "n_eff_lag1": 363.28017154566334, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:fwhm@min', 'contamination_CO:center@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 5.19904519042311e-12}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.186864808391868e-11}], "proposed_peaks": [{"role": "proposed_peak_0", "accepted": false, "fitted_center": 284.0562, "fitted_fwhm": 0.5, "width_capped": false, "rejection_reason": "amplitude 1.0 \u2264 noise_floor 1.0", "near_roi_endpoint": false}], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_graphite_sym_CO_C=O", "n_components": 3, "reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "bic_raw": -1709.979884899033, "bic_weighted": 70.19264450130285, "n_eff_lag1": 363.28024523651777, "survived": true, "rank": 2, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_C=O:fwhm@max'], unphysical_widths=['contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)'], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.1271782252075944e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.382268211640556e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": ["contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)"], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["contamination_CO:center@max", "contamination_C=O:fwhm@max"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "bic_raw": -1708.8655954986962, "bic_weighted": 76.0419659126833, "n_eff_lag1": 366.35338688232457, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 7.909867801039288e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["main_aliphatic:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_linked", "n_components": 3, "reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "bic_raw": -1708.8655820330348, "bic_weighted": 76.04196591267502, "n_eff_lag1": 366.3533885732838, "survived": true, "rank": 5, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.4061902357893664e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 1.3408724708678914e-14}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "n_components": 3, "reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "bic_raw": -1708.8655817728024, "bic_weighted": 76.04196591267494, "n_eff_lag1": 366.3533923770929, "survived": true, "rank": 4, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.628908028198292e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.753864998110036e-16}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}], "non_converged": [], "ambiguous_pairs": [["B2_linked", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.12); structural difference: {'main_graphitic', 'main_aliphatic', 'contamination_CO', 'contamination_C=O', 'satellite_pi'}"], ["B2_graphite_sym_CO_C=O", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.11); structural difference: {'contamination_C=O', 'satellite_pi', 'contamination_CO'}"], ["AG0_graphite_asymGL_satellite", "AG1_graphite_asymGL_sat_plus_CO", "Indistinguishable on fit quality and BIC* (\u0394BIC*=0.00); structural difference: {'contamination_CO'}"]], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max", "residual_gap"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8, "residual_gap": {"n_attempts": 1, "n_accepted": 0}}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 2356.1031279564713, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 2379.5009607446636, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 2402.898356672834, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 2426.2955913250544, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 2379.5009606895596, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 2397.0489719191914, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 2414.5969365032793, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 2379.500437560467, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 2397.0484483372284, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 2414.596388869996, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": -1732.2628630458792, "selected": true}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": -1708.8655817728024, "selected": true}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": -1685.4717428556983, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": -1662.0718740907616, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": -1708.8655820330348, "selected": true}, {"name": "AG2_linked", "converged": true, "bic": -1691.3175603688178, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": -1673.7697813731577, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2379.5009857340206, "selected": false}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2402.8983010024053, "selected": false}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2426.29571673858, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2449.693448965505, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": -1708.8655888943526, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": -1685.4680086668614, "selected": false}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": -1662.0707790890274, "selected": false}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": -690.5033612735614, "selected": false}, {"name": "B2_linked", "converged": true, "bic": -1721.6789198318845, "selected": true}, {"name": "B3_linked", "converged": true, "bic": -1704.1305018737503, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": -1709.9798453429748, "selected": true}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": -1686.5824714043713, "selected": false}], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"AG0_graphite_asymGL_satellite": {"reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "aicc": -1766.373823502721, "n_params": 9, "n_params_adjusted": 5, "n_components": 2}, "B2_linked": {"reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "aicc": -1759.519130288255, "n_params": 10, "n_params_adjusted": 4, "n_components": 3}, "B2_graphite_sym_CO_C=O": {"reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "aicc": -1755.2376505218683, "n_params": 12, "n_params_adjusted": 4, "n_components": 3}, "MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "aicc": -1757.8137245449122, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "AG1_linked": {"reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "aicc": -1757.8137110792509, "n_params": 13, "n_params_adjusted": 6, "n_components": 3}, "AG1_graphite_asymGL_sat_plus_CO": {"reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "aicc": -1757.8137108190185, "n_params": 13, "n_params_adjusted": 5, "n_components": 3}}, "top_by_bic_star": "B2_linked", "top_by_aicc": "AG0_graphite_asymGL_satellite", "bic_ambiguous": true, "criteria_conflict": true, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "B2_linked", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "preseeded_features": [], "n_survivors": 5, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner B2_linked has constraint violations ['main_aliphatic:fwhm@min', 'contamination_CO:center@min'] (see analysis.candidates). ", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:2160:uploads/58ef8f7c-8e65-4581-a1d5-b342298d1425.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 60.5, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_graphitic", "region": "C 1s", "phase_id": "sample", "shape": "ds_g", "center": 284.40862660161633, "fwhm": 0.6625927514639813, "amplitude": 3312.068644701938, "alpha": 4.6264159170306125e-12, "beta": 0.05, "m_gauss": 0.6625927514639813}, {"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.60000000001236, "fwhm": 0.8000000000185057, "amplitude": 2954.930348377461, "gl_ratio": 1.5421386390102043e-11}], "confidence": {"main_graphitic": {"sigma_stat": {"uncertainty_kind": "stability_mad", "values": {"center": 0.04460548852011925, "fwhm": 0.02629222009172294, "amplitude": 1333.794922536627}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 0.04460548852011925, "fwhm_mad": 0.02629222009172294, "amplitude_mad": 1333.794922536627}, "detectability": {"amplitude": 3312.068644701938, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": [], "max_cross_correlation": null}}, "main_aliphatic": {"sigma_stat": {"uncertainty_kind": "stability_mad", "values": {"center": 1.1368683772161603e-13, "fwhm": 0.0, "amplitude": 0.01636871560003783}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 0.75, "position_mad": 1.1368683772161603e-13, "fwhm_mad": 0.0, "amplitude_mad": 0.01636871560003783}, "detectability": {"amplitude": 2954.930348377461, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min"], "max_cross_correlation": null}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866390594288e-06, "bic_star": -1732.2629233085559, "bic_raw": -1708.8656241887684, "bic_weighted": 76.04196591268362, "n_eff_lag1": 366.3533853562398, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.732479228417388e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 4}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "n_components": 4, "reduced_chi_sq": 2.2538587778357373e-06, "bic_star": -1732.262137328864, "bic_raw": -1685.467539089289, "bic_weighted": 99.4392650324933, "n_eff_lag1": 366.353460351388, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:offset@max', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.4702538358659414e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.515142706037034e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["contamination_CO:fwhm@min", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:offset@max", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 4}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "n_components": 5, "reduced_chi_sq": 2.2815134764749067e-06, "bic_star": -1732.262147660311, "bic_raw": -1662.0702503009486, "bic_weighted": 122.83656415227738, "n_eff_lag1": 366.3534720499048, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_C=O:center@max', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.5356066679308465e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.3563402013254895e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 6.937798106689261e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.25, "boundary_hits": ["contamination_C=O:center@max", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 3}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "n_components": 6, "reduced_chi_sq": 2.1990369814617878e-06, "bic_star": -1762.164200824285, "bic_raw": -1668.5750043451353, "bic_weighted": 146.2338275885795, "n_eff_lag1": 401.06051089289645, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 2.889000740966408e-10}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.084367297735124e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 3.3135447554575374e-11}, {"role": "contamination_OC=O", "persistence": 0.0, "area_fraction": 5.868305324176354e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.25, "boundary_hits": ["contamination_CO:center@max", "contamination_CO:fwhm@min", "contamination_C=O:fwhm@min", "contamination_OC=O:fwhm@min", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 1}, {"name": "M0_graph_asym_aliph_sym_satellite", "n_components": 3, "reduced_chi_sq": 0.5445546916051832, "bic_star": 2199.204211199102, "bic_raw": 2222.6015103188893, "bic_weighted": 252.6177190470987, "n_eff_lag1": 4.371020551972791, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:center@min', 'main_aliphatic:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 1.1139261674936666e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": true, "min_active_persistence": 0.25, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 1}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "n_components": 4, "reduced_chi_sq": 0.5511354169322392, "bic_star": 2199.1834191338194, "bic_raw": 2245.9780173733943, "bic_weighted": 276.01501948372095, "n_eff_lag1": 4.3708990513348684, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:center@min', 'main_aliphatic:fwhm@min', 'contamination_CO:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.2370351534164325e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.487697359241712e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": true, "min_active_persistence": 0.75, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min", "contamination_CO:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 2}], "non_converged": [], "ambiguous_pairs": [], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 3753.6915569887074, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 3777.0797675518816, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 3800.4736710871393, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 3823.878033686888, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 3777.0797675518816, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 3794.6107745192317, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 3812.179292646422, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 3777.07751804941, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 3794.603988962943, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 3812.1648087337817, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": 3203.092457785431, "selected": false}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": 3226.4895926311533, "selected": false}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": 3249.886864603099, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 3273.2841770393084, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": 3226.4896031446615, "selected": false}, {"name": "AG2_linked", "converged": true, "bic": 3244.0434203132595, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": 3261.5855136976834, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2263.1271879845717, "selected": true}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2286.5244671115156, "selected": true}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2309.921556825529, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2333.3190793743943, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": 1953.573584264419, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": 1976.9708924404435, "selected": true}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": 2000.3681945376777, "selected": true}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": 2023.7655196301753, "selected": true}, {"name": "B2_linked", "converged": true, "bic": 3807.15449535746, "selected": false}, {"name": "B3_linked", "converged": true, "bic": 3824.7024555091207, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": 3813.7161299169506, "selected": false}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": 3837.514037613595, "selected": false}], "filtered_dominant_alternative": {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "bic_star": -1762.164200824285, "delta_bic_vs_winner": 3961.3476199581046, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)"}, "weighted_ic_disagreement": null, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866390594288e-06, "bic_star": -1732.2629233085559, "aicc": -1757.8137532349845, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "MG1_graphAsymGL_aliph_sat_CO": {"reduced_chi_sq": 2.2538587778357373e-06, "bic_star": -1732.262137328864, "aicc": -1749.045877977565, "n_params": 17, "n_params_adjusted": 9, "n_components": 4}, "MG2_graphAsymGL_aliph_sat_CO_C=O": {"reduced_chi_sq": 2.2815134764749067e-06, "bic_star": -1732.262147660311, "aicc": -1740.0629937567558, "n_params": 21, "n_params_adjusted": 9, "n_components": 5}, "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O": {"reduced_chi_sq": 2.1990369814617878e-06, "bic_star": -1762.164200824285, "aicc": -1760.7582796070465, "n_params": 25, "n_params_adjusted": 9, "n_components": 6}, "M0_graph_asym_aliph_sym_satellite": {"reduced_chi_sq": 0.5445546916051832, "bic_star": 2199.204211199102, "aicc": 2177.343744696054, "n_params": 12, "n_params_adjusted": 8, "n_components": 3}, "M1_graph_asym_aliph_sym_sat_CO": {"reduced_chi_sq": 0.5511354169322392, "bic_star": 2199.1834191338194, "aicc": 2186.037305742729, "n_params": 16, "n_params_adjusted": 8, "n_components": 4}}, "top_by_bic_star": "M1_graph_asym_aliph_sym_sat_CO", "top_by_aicc": "M1_graph_asym_aliph_sym_sat_CO", "bic_ambiguous": false, "criteria_conflict": false, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "M1_graph_asym_aliph_sym_sat_CO", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min", "contamination_CO:fwhm@min", "satellite_pi:fwhm@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "bic_star": -1762.164200824285, "delta_bic_vs_winner": 3961.3476199581046, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)"}, "weighted_ic_disagreement": null, "preseeded_features": [], "n_survivors": 1, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner M1_graph_asym_aliph_sym_sat_CO has constraint violations ['main_aliphatic:center@min', 'main_aliphatic:fwhm@min', 'contamination_CO:fwhm@min', 'satellite_pi:fwhm@min'] (see analysis.candidates).  WARNING: filtered candidate MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O beats this winner by \u0394BIC* 3961.3 but did not survive filtering (plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True))", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md:2161:uploads/3ee1dcee-2f3a-4c83-a33e-ce349f9dd4e8.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 21.9, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.5000049005795, "fwhm": 0.8000022727809339, "amplitude": 5999.985762735916, "gl_ratio": 8.555378627761456e-13, "stderr": {"center": 1.962102350870924e-06, "amplitude": 0.04162189670815025, "fwhm": 4.680060151954143e-06, "gl_ratio": 3.7802776622909907e-06}}], "confidence": {"main_aliphatic": {"sigma_stat": {"uncertainty_kind": "covariance", "values": {"center": 1.962102350870924e-06, "fwhm": 4.680060151954143e-06, "amplitude": 0.04162189670815025}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 2.7853275241795927e-12, "fwhm_mad": 4.9372728128105337e-11, "amplitude_mad": 2.594129000499379e-07}, "detectability": {"amplitude": 5999.985762735916, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:fwhm@min"], "max_cross_correlation": 0.6776994710374912}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "AG0_graphite_asymGL_satellite", "n_components": 2, "reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "bic_raw": -1732.2640251122796, "bic_weighted": 52.64466679288834, "n_eff_lag1": 366.3534125802044, "survived": true, "rank": 3, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['satellite_pi:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 3.186674785301061e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["satellite_pi:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_linked", "n_components": 3, "reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "bic_raw": -1721.6806443935482, "bic_weighted": 58.4939949414036, "n_eff_lag1": 363.28017154566334, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:fwhm@min', 'contamination_CO:center@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 5.19904519042311e-12}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.186864808391868e-11}], "proposed_peaks": [{"role": "proposed_peak_0", "accepted": false, "fitted_center": 284.0562, "fitted_fwhm": 0.5, "width_capped": false, "rejection_reason": "amplitude 1.0 \u2264 noise_floor 1.0", "near_roi_endpoint": false}], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_graphite_sym_CO_C=O", "n_components": 3, "reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "bic_raw": -1709.979884899033, "bic_weighted": 70.19264450130285, "n_eff_lag1": 363.28024523651777, "survived": true, "rank": 2, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_C=O:fwhm@max'], unphysical_widths=['contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)'], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.1271782252075944e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.382268211640556e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": ["contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)"], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["contamination_CO:center@max", "contamination_C=O:fwhm@max"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "bic_raw": -1708.8655954986962, "bic_weighted": 76.0419659126833, "n_eff_lag1": 366.35338688232457, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 7.909867801039288e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["main_aliphatic:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_linked", "n_components": 3, "reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "bic_raw": -1708.8655820330348, "bic_weighted": 76.04196591267502, "n_eff_lag1": 366.3533885732838, "survived": true, "rank": 5, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.4061902357893664e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 1.3408724708678914e-14}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "n_components": 3, "reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "bic_raw": -1708.8655817728024, "bic_weighted": 76.04196591267494, "n_eff_lag1": 366.3533923770929, "survived": true, "rank": 4, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.628908028198292e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.753864998110036e-16}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}], "non_converged": [], "ambiguous_pairs": [["B2_linked", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.12); structural difference: {'main_graphitic', 'main_aliphatic', 'contamination_CO', 'contamination_C=O', 'satellite_pi'}"], ["B2_graphite_sym_CO_C=O", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.11); structural difference: {'contamination_C=O', 'satellite_pi', 'contamination_CO'}"], ["AG0_graphite_asymGL_satellite", "AG1_graphite_asymGL_sat_plus_CO", "Indistinguishable on fit quality and BIC* (\u0394BIC*=0.00); structural difference: {'contamination_CO'}"]], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max", "residual_gap"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8, "residual_gap": {"n_attempts": 1, "n_accepted": 0}}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 2356.1031279564713, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 2379.5009607446636, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 2402.898356672834, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 2426.2955913250544, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 2379.5009606895596, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 2397.0489719191914, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 2414.5969365032793, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 2379.500437560467, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 2397.0484483372284, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 2414.596388869996, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": -1732.2628630458792, "selected": true}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": -1708.8655817728024, "selected": true}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": -1685.4717428556983, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": -1662.0718740907616, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": -1708.8655820330348, "selected": true}, {"name": "AG2_linked", "converged": true, "bic": -1691.3175603688178, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": -1673.7697813731577, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2379.5009857340206, "selected": false}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2402.8983010024053, "selected": false}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2426.29571673858, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2449.693448965505, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": -1708.8655888943526, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": -1685.4680086668614, "selected": false}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": -1662.0707790890274, "selected": false}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": -690.5033612735614, "selected": false}, {"name": "B2_linked", "converged": true, "bic": -1721.6789198318845, "selected": true}, {"name": "B3_linked", "converged": true, "bic": -1704.1305018737503, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": -1709.9798453429748, "selected": true}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": -1686.5824714043713, "selected": false}], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"AG0_graphite_asymGL_satellite": {"reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "aicc": -1766.373823502721, "n_params": 9, "n_params_adjusted": 5, "n_components": 2}, "B2_linked": {"reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "aicc": -1759.519130288255, "n_params": 10, "n_params_adjusted": 4, "n_components": 3}, "B2_graphite_sym_CO_C=O": {"reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "aicc": -1755.2376505218683, "n_params": 12, "n_params_adjusted": 4, "n_components": 3}, "MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "aicc": -1757.8137245449122, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "AG1_linked": {"reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "aicc": -1757.8137110792509, "n_params": 13, "n_params_adjusted": 6, "n_components": 3}, "AG1_graphite_asymGL_sat_plus_CO": {"reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "aicc": -1757.8137108190185, "n_params": 13, "n_params_adjusted": 5, "n_components": 3}}, "top_by_bic_star": "B2_linked", "top_by_aicc": "AG0_graphite_asymGL_satellite", "bic_ambiguous": true, "criteria_conflict": true, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "B2_linked", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "preseeded_features": [], "n_survivors": 5, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner B2_linked has constraint violations ['main_aliphatic:fwhm@min', 'contamination_CO:center@min'] (see analysis.candidates). ", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}
docs/autofit/codex/tougaard_bg_fixes_unit2_verdict_runA.md:804:        # A future mixed-background grammar only affects DETECTION here —
docs/autofit/codex/tougaard_bg_fixes_unit2_verdict_runA.md:898:              "fwhm_max":     3.0,                // optional
docs/autofit/codex/tougaard_bg_fixes_unit2_verdict_runA.md:944:            "differential_evolution", "basinhopping",
docs/autofit/codex/tougaard_bg_fixes_unit2_verdict_runA.md:2347:``mixed{analyte, matrix}``.  Every :class:`ComponentSlot` carries a
docs/autofit/codex/stage2_review_prompt.txt:14:- Typed uncertainty kinds never mixed; no quadrature of sigma_stat with reference_sensitivity_range.
docs/autofit/codex/phaseD_unit3_recheck_verdict_runB.md:12:- API pins: **PARTIAL**. Static path is correct: mixed non-`least_squares` resolves fallback, deep candidates run, and method analysis deep-copies `grammar.provenance`; `least_squares` keeps `grammar=None`. I could not execute Flask API tests because the read-only sandbox has no usable temp dir and app import hits `dill/tempfile`.
docs/autofit/codex/phaseD_unit3_recheck_verdict_runB.md:17:- **MINOR** [tests/autofit/test_structural_fallback.py](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:321): the mixed API pin asserts only that `"Fe 2p"` exists in `analysis.constants_provenance`, not that derived structural records are present. Failure scenario: API/method returns `"Fe 2p": []` or fit-physics-only records; the test still passes.
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runB.md:1103:./docs/autofit/PROGRESS.md:1280:mixed-sign pass-through match the documented policy. **The Tougaard
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runB.md:1266:./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:27:I could not run pytest because the read-only sandbox has no usable temp directory, but I executed the extracted `tougaard_background` body directly and confirmed `[100,0,0,0] -> [0,0,0,0]`. I also checked the mixed-sign cancellation edge: it returns a signed unanchored correlation, consistent with the “negative counts pass through signed; no clamping” policy.
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runB.md:2945:tests/test_mixed_ds_lacx_e2e.py:54:    background_method='none',
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runB.md:2949:tests/autofit/stress_cases.py:23:                   charging replica, wrong background); the method must
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runB.md:3073:tests/autofit/stress_cases.py:23:                   charging replica, wrong background); the method must
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/Cl2p Scan.xml:3:    <Series Name="PeakTableAnnotations" Legend="Legend1" XValueType="Double" YValueType="Double" ChartType="Point" ChartArea="ChartArea1" MarkerSize="0" CustomProperties="YAxis_ScalingMode=Auto, CustomYAxis_Max=39693.556952872, CustomYAxis_Min=7514.74846956409, Type=PeakTableAnnotations" IsVisibleInLegend="False">
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/Cl2p Scan.xml:34:      <AxisY IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="39693.556952872" Minimum="7522.79116101205" Enabled="False">
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/Cl2p Scan.xml:70:      <AxisY2 IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="39693.556952872" Minimum="7514.7484695640851" Enabled="True">
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml:3:    <Series Name="PeakTableAnnotations" Legend="Legend1" XValueType="Double" YValueType="Double" ChartType="Point" ChartArea="ChartArea1" MarkerSize="0" CustomProperties="YAxis_ScalingMode=Auto, CustomYAxis_Max=26753.5614030376, CustomYAxis_Min=12835.5139178607, Type=PeakTableAnnotations" IsVisibleInLegend="False">
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml:34:      <AxisY IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="26753.5614030376" Minimum="12838.9925600714" Enabled="False">
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml:76:      <AxisY2 IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="26753.5614030376" Minimum="12835.513917860659" Enabled="True">
docs/autofit/codex/phaseD_unit3_verdict_runB.md:8:2. MINOR [tests/autofit/test_structural_fallback.py:188](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:188): API tests cover structure-only and unparseable paths, but do not pin mixed deep+structural or the `least_squares` grammar-`None` path. Current code is statically correct at [app.py:703](/Users/skyefortier/xps-app/app.py:703) and [app.py:761](/Users/skyefortier/xps-app/app.py:761). Failure scenario: omitting `structural_only` from a mixed method payload, or accidentally resolving fallback for `least_squares`, would not be caught by the current API tests.
docs/autofit/codex/plain_english_pass_verdict_round3_runA.md:4:Prompt: docs/autofit/codex/plain_english_pass_recheck2_prompt.txt (recheck of round 2's mixed-payload finding)
docs/autofit/codex/plain_english_pass_verdict_round3_runA.md:10:The original stub test and both new mixed-payload regressions are present and pass (`node --test tests/js/find_peaks_plain_message.test.js` — 20/20). The mixed-success fixture is realistic: non-empty `structural_only`, real peak data, `analysis` present — aligns with tests/autofit/test_structural_fallback.py's own assertions.
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:379:-     "fwhm": 3.5752402300579225,
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:383:+     "fwhm": 3.5752402300533492,
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:390:-     "fwhm": 3.5752402300579225,
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:394:+     "fwhm": 3.5752402300533492,
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:2179:   238	    ("C 1s", 270.0, 315.0),      # matches isC1sTab (index.html:6548)
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:2183:   242	    ("U 4f", 370.0, 415.0),      # span ~35 eV so their midpoint lands ~387
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:2320:   rel=1.27913941127e-12 abs=4.57323068304e-12 field=/peaks/3/fwhm old=3.5752402300579225 new=3.5752402300533492
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:2321:   rel=1.27913941127e-12 abs=4.57323068304e-12 field=/peaks/2/fwhm old=3.5752402300579225 new=3.5752402300533492
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:3120:   364	        # Phase D: regions that resolved structure-only in a MIXED
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:3286:   765	              "fwhm_max":     3.0,                // optional
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:3332:   811	            "differential_evolution", "basinhopping",
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md:3413:   467	    "Co 2p":  {"splitting": 15.0,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:27:I could not run pytest because the read-only sandbox has no usable temp directory, but I executed the extracted `tougaard_background` body directly and confirmed `[100,0,0,0] -> [0,0,0,0]`. I also checked the mixed-sign cancellation edge: it returns a signed unanchored correlation, consistent with the “negative counts pass through signed; no clamping” policy.
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_2.xml:3:    <Series Name="PeakTableAnnotations" Legend="Legend1" XValueType="Double" YValueType="Double" ChartType="Point" ChartArea="ChartArea1" MarkerSize="0" CustomProperties="YAxis_ScalingMode=Auto, CustomYAxis_Max=436583.544612424, CustomYAxis_Min=-109.145886153106, Type=PeakTableAnnotations" IsVisibleInLegend="False">
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_2.xml:34:      <AxisY IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="436583.544612424" Minimum="0" Enabled="False">
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan_2.xml:71:      <AxisY2 IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="436583.544612424" Minimum="-109.145886153106" Enabled="True">
docs/autofit/codex/stress_suite_recheck_prompt.txt:11:   truth centers within 0.15 eV; count-only outcomes are labeled
docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.xml:34:      <AxisY IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="27170.2898893307" Minimum="12363.5903440752" Enabled="False">
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.xml:3:    <Series Name="PeakTableAnnotations" Legend="Legend1" XValueType="Double" YValueType="Double" ChartType="Point" ChartArea="ChartArea1" MarkerSize="0" CustomProperties="YAxis_ScalingMode=Auto, CustomYAxis_Max=4042.69815604396, CustomYAxis_Min=1043.58444488508, Type=PeakTableAnnotations" IsVisibleInLegend="False">
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_7.xml:71:      <AxisY2 IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="4042.69815604396" Minimum="1043.5844448850778" Enabled="True">
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 D/C1s Scan.xml:3:    <Series Name="PeakTableAnnotations" Legend="Legend1" XValueType="Double" YValueType="Double" ChartType="Point" ChartArea="ChartArea1" MarkerSize="0" CustomProperties="YAxis_ScalingMode=Auto, CustomYAxis_Max=436583.544612424, CustomYAxis_Min=-109.145886153106, Type=PeakTableAnnotations" IsVisibleInLegend="False">
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 D/C1s Scan.xml:34:      <AxisY IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="436583.544612424" Minimum="0" Enabled="False">
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 D/C1s Scan.xml:71:      <AxisY2 IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="436583.544612424" Minimum="-109.145886153106" Enabled="True">
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/Cl2p Scan_1.xml:3:    <Series Name="PeakTableAnnotations" Legend="Legend1" XValueType="Double" YValueType="Double" ChartType="Point" ChartArea="ChartArea1" MarkerSize="0" CustomProperties="YAxis_ScalingMode=Auto, CustomYAxis_Max=39693.556952872, CustomYAxis_Min=7514.74846956409, Type=PeakTableAnnotations" IsVisibleInLegend="False">
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/Cl2p Scan_1.xml:34:      <AxisY IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="39693.556952872" Minimum="7522.79116101205" Enabled="False">
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/Cl2p Scan_1.xml:70:      <AxisY2 IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="39693.556952872" Minimum="7514.7484695640851" Enabled="True">
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.xml:3:    <Series Name="PeakTableAnnotations" Legend="Legend1" XValueType="Double" YValueType="Double" ChartType="Point" ChartArea="ChartArea1" MarkerSize="0" CustomProperties="YAxis_ScalingMode=Auto, CustomYAxis_Max=1164303.54624454, CustomYAxis_Min=-291.075886561135, Type=PeakTableAnnotations" IsVisibleInLegend="False">
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.xml:34:      <AxisY IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="1164303.54624454" Minimum="0" Enabled="False">
docs/autofit/test_data/1 UCl4-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/XPS Survey_8.xml:78:      <AxisY2 IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="1164303.54624454" Minimum="-291.075886561135" Enabled="True">
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.xml:3:    <Series Name="PeakTableAnnotations" Legend="Legend1" XValueType="Double" YValueType="Double" ChartType="Point" ChartArea="ChartArea1" MarkerSize="0" CustomProperties="YAxis_ScalingMode=Auto, CustomYAxis_Max=60312.0190357783, CustomYAxis_Min=-15.0780047589446, Type=PeakTableAnnotations" IsVisibleInLegend="False">
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/B1s Scan_4.xml:78:      <AxisY2 IsLabelAutoFit="False" LabelAutoFitStyle="StaggeredLabels" Title="Counts / s" TitleFont="Arial, 10pt" IsStartedFromZero="False" IsMarginVisible="False" Maximum="60312.0190357783" Minimum="-15.078004758944576" Enabled="True">

exec
/bin/zsh -lc 'rg -n "material_class|MaterialClass" autofit/regions autofit/engine.py autofit/methods app.py tests -S' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
app.py:222:    from autofit.grammar import (MaterialClass, Phase,
app.py:243:    mc_raw = body.get("material_class", "")
app.py:245:        mclass = MaterialClass(mc_raw)
app.py:247:        raise _AnalyzeError(f"Unknown material_class '{mc_raw}'")
app.py:289:                      material_class=mclass,
app.py:870:        from autofit.grammar import MaterialClass
app.py:881:            "material_classes": [m.value for m in MaterialClass],
app.py:897:          "material_class": "conductor" | "insulator" | "semiconductor" | "mixed",
tests/test_api_analyze_progress.py:60:    "session_id": sid, "material_class": "insulator",
tests/test_api_analyze_progress.py:164:    """Cheap, request-shape validation (session/region/roi/material_class)
tests/test_api_analyze_progress.py:168:        "session_id": "not-a-uuid", "material_class": "insulator",
autofit/regions/c1s.py:32:    MaterialClass,
autofit/regions/c1s.py:125:def _contamination_fwhm_range(material_class: MaterialClass) -> tuple[float, float]:
autofit/regions/c1s.py:128:    if material_class is MaterialClass.MIXED:
autofit/regions/c1s.py:243:            {"constant": "mixed_material_class_width_relaxation",
autofit/regions/c1s.py:244:             "value": "under MaterialClass.MIXED (analyte embedded in a "
autofit/regions/c1s.py:306:        contam_fwhm = _contamination_fwhm_range(phase.material_class)
tests/test_api_analyze_coverage.py:81:        "session_id": sid, "material_class": "conductor",
tests/test_api_analyze_coverage.py:102:        "session_id": sid, "material_class": "insulator",
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
tests/autofit/test_stage2_rereview_findings.py:26:from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_stage2_rereview_findings.py:94:    pa = Phase(id="B-4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:96:    pb = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:103:    pa = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_stage2_rereview_findings.py:105:    pb = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:124:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/test_api_fit_full_window_option.py:60:        "session_id": sid, "material_class": "insulator",
tests/test_api_fit_full_window_option.py:75:        "session_id": sid, "material_class": "insulator",
tests/autofit/test_reference_bridge.py:31:from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_reference_bridge.py:271:    phase = Phase(id="s", material_class=MaterialClass("conductor"),
tests/autofit/test_reference_bridge.py:289:    phase2 = Phase(id="s", material_class=MaterialClass("conductor"),
tests/autofit/test_c1s_parity_gate.py:50:from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_c1s_parity_gate.py:95:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_u4f_parity_gate.py:23:from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_u4f_parity_gate.py:30:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_u4f_parity_gate.py:32:BN = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_methods_seam.py:6:from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_methods_seam.py:9:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_candidate_pool_real_gate.py:85:    from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_candidate_pool_real_gate.py:86:    phase = Phase(id="sample", material_class=MaterialClass("conductor"),
tests/autofit/test_candidate_pool_real_gate.py:223:    from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_candidate_pool_real_gate.py:226:    phase = Phase(id="sample", material_class=MaterialClass("conductor"),
tests/autofit/test_structural_fallback.py:26:    MaterialClass,
tests/autofit/test_structural_fallback.py:34:    return Phase(id="sample", material_class=MaterialClass(mc),
tests/autofit/test_structural_fallback.py:227:    p1 = Phase(id="a", material_class=MaterialClass("conductor"),
tests/autofit/test_structural_fallback.py:229:    p2 = Phase(id="b", material_class=MaterialClass("conductor"),
tests/autofit/test_structural_fallback.py:280:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:304:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:322:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:351:        "session_id": sid, "material_class": "insulator",
tests/autofit/test_structural_fallback.py:374:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_b1s_cl2p_parity_gates.py:26:from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_b1s_cl2p_parity_gates.py:36:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_b1s_cl2p_parity_gates.py:38:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_cl2p_freewidth.py:31:    MaterialClass,
tests/autofit/test_cl2p_freewidth.py:41:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_c1s_mixed_material_class.py:36:from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_c1s_mixed_material_class.py:39:NON_MIXED = [MaterialClass.CONDUCTOR, MaterialClass.SEMICONDUCTOR,
tests/autofit/test_c1s_mixed_material_class.py:40:             MaterialClass.INSULATOR]
tests/autofit/test_c1s_mixed_material_class.py:49:def _resolve(material_class):
tests/autofit/test_c1s_mixed_material_class.py:50:    phase = Phase(id="sample", material_class=material_class, regions=("C 1s",))
tests/autofit/test_c1s_mixed_material_class.py:66:@pytest.mark.parametrize("material_class", NON_MIXED)
tests/autofit/test_c1s_mixed_material_class.py:67:def test_non_mixed_candidate_pool_unchanged(material_class):
tests/autofit/test_c1s_mixed_material_class.py:71:    g = _resolve(material_class)
tests/autofit/test_c1s_mixed_material_class.py:77:            f"material_class {material_class}"
tests/autofit/test_c1s_mixed_material_class.py:81:@pytest.mark.parametrize("material_class", NON_MIXED)
tests/autofit/test_c1s_mixed_material_class.py:82:def test_non_mixed_candidate_names_unchanged(material_class):
tests/autofit/test_c1s_mixed_material_class.py:85:    non-MIXED material class (it always was -- material_class was
tests/autofit/test_c1s_mixed_material_class.py:87:    names_conductor = {c.name for c in _resolve(MaterialClass.CONDUCTOR).candidates}
tests/autofit/test_c1s_mixed_material_class.py:88:    names_other = {c.name for c in _resolve(material_class).candidates}
tests/autofit/test_c1s_mixed_material_class.py:98:    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
tests/autofit/test_c1s_mixed_material_class.py:117:    g_conductor = _resolve(MaterialClass.CONDUCTOR)
tests/autofit/test_c1s_mixed_material_class.py:118:    g_mixed = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:138:    g_conductor = _resolve(MaterialClass.CONDUCTOR)
tests/autofit/test_c1s_mixed_material_class.py:139:    g_mixed = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:158:    rec = _by_constant(records, "mixed_material_class_width_relaxation")
tests/autofit/test_c1s_mixed_material_class.py:187:    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
tests/autofit/test_coverage_structure.py:140:    allotrope/compound caveat. Uses the grammar's MaterialClass vocabulary."""
tests/autofit/test_fit_physics_wiring.py:13:from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_fit_physics_wiring.py:15:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_fit_physics_wiring.py:17:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_bayesian_real_gate.py:30:from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_bayesian_real_gate.py:37:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_resolver.py:10:    MaterialClass,
tests/autofit/test_resolver.py:18:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_resolver.py:20:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_resolver.py:22:BN = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_resolver.py:84:        xe = Phase(id="x", material_class=MaterialClass.CONDUCTOR, regions=("Xe 3d",))
tests/autofit/test_resolver.py:131:    both = Phase(id="mix", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_resolver.py:158:    p1 = Phase(id="ph1", material_class=MaterialClass.INSULATOR, regions=("Fk 2p",))
tests/autofit/test_resolver.py:159:    p2 = Phase(id="ph2", material_class=MaterialClass.SEMICONDUCTOR, regions=("Fk 2p",))
tests/autofit/test_resolver.py:183:    p1 = Phase(id="ph1", material_class=MaterialClass.INSULATOR, regions=("Fk 2p",))
tests/autofit/test_bayesian_u4f_unresolved_gate.py:30:from autofit.grammar import MaterialClass, Phase, resolve
tests/autofit/test_bayesian_u4f_unresolved_gate.py:37:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,

codex
So far the code path is narrow: only `autofit/regions/c1s.py` reads `MaterialClass.MIXED`, and `app.py` parses the enum before charge correction but does not feed it into the arithmetic. The weak spots I’m checking next are whether the tests pin the linked shared-width parameter directly and whether the 15.0 value has any trail in the lab/test-data artifacts.
exec
/bin/zsh -lc "nl -ba app.py | sed -n '200,320p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   200	
   201	
   202	class _AnalyzeContext:
   203	    """Everything _run_analyze_method / _build_analyze_payload need,
   204	    assembled once by _validate_analyze_request."""
   205	
   206	    __slots__ = ("x", "y", "method_id", "opts", "peak_specs", "grammar")
   207	
   208	    def __init__(self, x, y, method_id, opts, peak_specs, grammar):
   209	        self.x = x
   210	        self.y = y
   211	        self.method_id = method_id
   212	        self.opts = opts
   213	        self.peak_specs = peak_specs
   214	        self.grammar = grammar
   215	
   216	
   217	def _validate_analyze_request(body: dict, upload_folder: str) -> _AnalyzeContext:
   218	    """ALL the synchronous, cheap validation /api/analyze has always done
   219	    (session lookup through grammar resolution) — pure extract-method
   220	    refactor, byte-identical checks/messages/order, raising
   221	    ``_AnalyzeError`` in place of the old inline ``return _err(...)``."""
   222	    from autofit.grammar import (MaterialClass, Phase,
   223	                                 PhaseAmbiguityError, UnknownRegionError,
   224	                                 resolve)
   225	
   226	    session_id = body.get("session_id", "")
   227	    _validate_session_id(session_id)
   228	    try:
   229	        energy, counts = _load_session(session_id, upload_folder)
   230	    except KeyError:
   231	        raise _AnalyzeError(f"Session '{session_id}' not found", 404)
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
   295	            grammar = resolve(
   296	                [phase], regions if len(regions) > 1 else regions[0],
   297	                allow_structural_fallback=True)
   298	        except (UnknownRegionError, PhaseAmbiguityError, ValueError) as exc:
   299	            raise _AnalyzeError(str(exc))
   300	
   301	    return _AnalyzeContext(x, y, method_id, opts, peak_specs, grammar)
   302	
   303	
   304	def _run_analyze_method(ctx: _AnalyzeContext, progress_cb=None):
   305	    """The one genuinely slow/unpredictable step — the ONLY part that
   306	    runs on a background thread for the async job path.  ``progress_cb``
   307	    is None for the synchronous /api/analyze route (no poller to feed)."""
   308	    from autofit.methods import get_method
   309	
   310	    try:
   311	        return get_method(ctx.method_id).run(
   312	            ctx.x, ctx.y, grammar=ctx.grammar, peak_specs=ctx.peak_specs,
   313	            options=ctx.opts, progress_cb=progress_cb)
   314	    except (ValueError, TypeError) as exc:
   315	        # the method's own option/spec validation — TypeError included:
   316	        # a malformed option VALUE (e.g. n_refits: []) raises TypeError
   317	        # from the methods' numeric casts (Codex re-check blocker)
   318	        raise _AnalyzeError(f"invalid option or spec: {exc}")
   319	    except Exception:
   320	        logging.getLogger(__name__).exception("analyze failed")

exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '810,925p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   810	
   811	    Spec keys
   812	    ---------
   813	    shape          : str   – one of AVAILABLE_SHAPES
   814	    center         : float – initial centre (eV)
   815	    center_min     : float – lower bound   (optional)
   816	    center_max     : float – upper bound   (optional)
   817	    amplitude      : float – peak maximum counts
   818	    amplitude_min  : float – lower bound   (default 0)
   819	    fwhm           : float – full width at half max (eV)
   820	    fwhm_min       : float – lower bound   (default 0.1)
   821	    fwhm_max       : float – upper bound   (default 15.0)
   822	    gl_ratio       : float – Lorentzian fraction for *_gl shapes  [0–1]
   823	    asymmetry      : float – high-BE broadening factor for asymmetric_gl [0–1]
   824	    alpha          : float – DS asymmetry index
   825	    constrain_to   : str   – id of master peak (spin‑orbit slave)
   826	    splitting      : float – centre offset from master (eV)
   827	    area_ratio     : float – amplitude = master_amplitude × area_ratio
   828	    fix_fwhm       : bool  – if True, lock FWHM to master value
   829	    """
   830	    shape = spec["shape"]
   831	    p = model.make_params()
   832	
   833	    center = spec.get("center", 285.0)
   834	    amp = spec.get("amplitude", 1000.0)
   835	    fwhm = spec.get("fwhm", 1.5)
   836	    asymmetry = spec.get("asymmetry", 0.0)
   837	
   838	    def _set(name, value, min_=None, max_=None, expr=None, vary=True):
   839	        full = prefix + name
   840	        if full not in p:
   841	            return
   842	        p[full].set(value=value)
   843	        if expr is not None:
   844	            p[full].expr = expr
   845	            p[full].vary = False
   846	        else:
   847	            if min_ is not None:
   848	                p[full].min = min_
   849	            if max_ is not None:
   850	                p[full].max = max_
   851	            p[full].vary = vary
   852	
   853	    # Constrain to a master peak (spin‑orbit doublet)?
   854	    master_id = spec.get("constrain_to")
   855	    if master_id is not None:
   856	        # Find the master spec to get its prefix
   857	        master_spec = next((s for s in all_specs if s["id"] == master_id), None)
   858	        if master_spec is None:
   859	            raise ValueError(f"Master peak '{master_id}' not found for spin‑orbit constraint")
   860	        m_prefix = f"p{master_spec['id']}_"
   861	        splitting = float(spec.get("splitting", 0.0))
   862	        area_ratio = float(spec.get("area_ratio", 1.0))
   863	
   864	        _set("center", center, expr=f"{m_prefix}center + {splitting}")
   865	        _set("amplitude", amp, expr=f"{m_prefix}amplitude * {area_ratio}")
   866	        _set("fwhm", fwhm, expr=f"{m_prefix}fwhm" if spec.get("fix_fwhm", True) else None,
   867	             min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0))
   868	        if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
   869	            _set("gl_ratio", spec.get("gl_ratio", 0.3),
   870	                 expr=f"{m_prefix}gl_ratio" if spec.get("fix_fwhm", True) else None,
   871	                 min_=0.0, max_=1.0)
   872	        if shape == "asymmetric_gl":
   873	            _set("asymmetry", asymmetry,
   874	                 expr=f"{m_prefix}asymmetry" if spec.get("fix_fwhm", True) else None,
   875	                 min_=spec.get("asymmetry_min", 0.0),
   876	                 max_=spec.get("asymmetry_max", 1.0))
   877	        if shape == "doniach_sunjic":
   878	            _set("alpha", spec.get("alpha", 0.1),
   879	                 expr=f"{m_prefix}alpha" if spec.get("fix_fwhm", True) else None,
   880	                 min_=0.0, max_=0.5)
   881	            _set("gamma_asym", spec.get("gamma_asym", 0.0),
   882	                 expr=f"{m_prefix}gamma_asym" if spec.get("fix_fwhm", True) else None,
   883	                 min_=0.0, max_=1.0)
   884	        if shape == "ds_g":
   885	            fix = spec.get("fix_fwhm", True)
   886	            _set("alpha",   spec.get("alpha",   0.10), expr=f"{m_prefix}alpha"   if fix else None, min_=0.0,  max_=0.49)
   887	            _set("beta",    spec.get("beta",    0.3),  expr=f"{m_prefix}beta"    if fix else None, min_=0.05, max_=2.0)
   888	            _set("m_gauss", spec.get("m_gauss", 0.4),  expr=f"{m_prefix}m_gauss" if fix else None, min_=0.0,  max_=4.0)
   889	        if shape == "la_casaxps":
   890	            fix = spec.get("fix_fwhm", True)
   891	            _set("alpha", spec.get("alpha", 1.0),
   892	                 expr=f"{m_prefix}alpha" if fix else None,
   893	                 min_=0.1, max_=5.0)
   894	            _set("beta",  spec.get("beta",  1.0),
   895	                 expr=f"{m_prefix}beta" if fix else None,
   896	                 min_=0.1, max_=5.0)
   897	            _set("m",     spec.get("m",    50.0),
   898	                 expr=f"{m_prefix}m" if fix else None,
   899	                 min_=0.0, max_=499.0)
   900	        return p
   901	
   902	    # Free (master or unconstrained) peak
   903	    # Non-DS+G peaks (satellites, etc.) get a default ±2 eV constraint to prevent
   904	    # the optimizer from drifting to physically unreasonable positions.
   905	    c_min = spec.get("center_min")
   906	    c_max = spec.get("center_max")
   907	    if shape != "ds_g" and c_min is None:
   908	        c_min = center - 2.0
   909	    if shape != "ds_g" and c_max is None:
   910	        c_max = center + 2.0
   911	    _set("center", center, min_=c_min, max_=c_max, vary=not spec.get("fix_center", False))
   912	    _set("amplitude", amp,
   913	         min_=spec.get("amplitude_min", 0.0), max_=spec.get("amplitude_max"),
   914	         vary=not spec.get("fix_amplitude", False))
   915	    _set("fwhm", fwhm,
   916	         min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0),
   917	         vary=not spec.get("fix_fwhm", False))
   918	
   919	    if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
   920	        _set("gl_ratio", spec.get("gl_ratio", 0.3), min_=0.0, max_=1.0,
   921	             vary=not spec.get("fix_gl_ratio", False))
   922	    if shape == "asymmetric_gl":
   923	        _set("asymmetry", asymmetry,
   924	             min_=spec.get("asymmetry_min", 0.0),
   925	             max_=spec.get("asymmetry_max", 1.0),

exec
/bin/zsh -lc "nl -ba tests/autofit/test_c1s_mixed_material_class.py | sed -n '1,220p'" in /Users/skyefortier/xps-verify
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
   164	    assert "10.1116/6.0000057" in rec["source"], "Baer et al. 2020 DOI"
   165	    assert "baer" in rec["source"].lower()
   166	    assert "10.1016/j.pmatsci.2019.100591" in rec["source"], \
   167	        "Greczynski & Hultman 2020 DOI"
   168	    assert "greczynski" in rec["source"].lower()
   169	    assert "hultman" in rec["source"].lower()
   170	
   171	
   172	def test_mixed_provenance_numeric_guard_record_is_honestly_labeled():
   173	    """The residual finite ceiling (unavoidable -- the optimizer needs a
   174	    finite initial-value midpoint) must be labeled UNVERIFIED and
   175	    described as a numeric guard for fit stability, not a chemistry or
   176	    physics claim -- the same footing as dsg_alpha_cap's 'fitalg numeric
   177	    guard' language."""
   178	    records = C1sModule().provenance()
   179	    rec = _by_constant(records, "mixed_fwhm_ceiling_numeric_guard")
   180	    assert rec["status"] == "UNVERIFIED"
   181	    assert "numeric guard" in rec["source"].lower()
   182	    assert ("not a chemistry" in rec["source"].lower()
   183	            or "not a physical" in rec["source"].lower()
   184	            or "not a physics" in rec["source"].lower())
   185	    # the guard's own value must equal whatever ceiling build_candidates()
   186	    # actually uses under MIXED -- no drift between the doc and the code
   187	    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
   188	    actual_ceiling = slots[0][1].fwhm_range[1]
   189	    assert rec["value"] == actual_ceiling

exec
/bin/zsh -lc 'rg -n "midpoint|fwhm_range|fwhm.*guess|shared_fwhm_params|fwhm_linked_to|init|initial" autofit/engine.py -S' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
164:                                 # finite fit (measured need: ~33 evals;
347:# Default (init, lo, hi) for each shape's extra parameters.  Slot-level
355:    # DS+G: fitalg convention — slot.fwhm_range bounds m_gauss (the Gaussian
362:# Which parameter carries the slot's fwhm_range for each shape.
368:    p: Parameters, prefix: str, slot: ComponentSlot, fwhm_init: float,
372:    flo, fhi = slot.fwhm_range
392:        if wname in shared or wname in fixed or slot.fwhm_linked_to is not None:
410:    elif slot.fwhm_linked_to is not None:
411:        p.add(f"{prefix}{wname}", value=float(np.clip(fwhm_init, flo, fhi)),
412:              expr=slot.fwhm_linked_to)
415:        p.add(f"{prefix}{wname}", value=float(np.clip(fwhm_init, wlo, whi)),
418:    for name, init, lo, hi in _SHAPE_PARAM_DEFAULTS[slot.line_shape]:
426:        p.add(f"{prefix}{name}", value=float(np.clip(init, plo, phi)), min=plo, max=phi)
483:    """Slot midpoints as starting values, slot bounds as hard constraints.
494:    for name, lo_b, hi_b in model.shared_fwhm_params:
504:            init = _peak_estimate_in_window(x, y_net, window)
505:            return init, max(2.0 * y_peak, 10.0 * init, 1.0)
517:        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])
518:        amp_init, amp_max = _amp_bounds(slot.be_window)
521:        p.add(f"{prefix}amplitude", value=amp_init, min=0.0, max=amp_max)
551:        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])
577:            rinit = slot.area_ratio if slot.area_ratio is not None else 0.5 * (rlo + rhi)
578:            p.add(f"{prefix}ratio", value=float(np.clip(rinit, rlo, rhi)),
585:            amp_init, amp_max = _amp_bounds(slot.be_window)
586:            p.add(f"{prefix}amplitude", value=amp_init, min=0.0, max=amp_max)
704:    """Varying params within 1% of a finite bound → 'role:param@min|max'."""
713:        if not (np.isfinite(lo) and np.isfinite(hi)) or hi <= lo:
759:    A slot whose grammar-declared ``fwhm_range`` maximum EXCEEDS the ordinary
772:    ranges = {s.role: s.fwhm_range for s in model.slots}
843:    initial_params: Optional[Parameters] = None,
869:    params = initial_params if initial_params is not None else \
878:                and np.isfinite(result.chisqr)):
887:            # χ²).  Fires ONLY on a failed-but-finite fit, so converging
936:def perturb_initial_params(
960:        lo = par.min if np.isfinite(par.min) else -np.inf
961:        hi = par.max if np.isfinite(par.max) else np.inf
1042:                and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
1182:    # Data-informed perturbation seeds (see perturb_initial_params): reuse
1202:        init = perturb_initial_params(model, seed=seed, x=x, y_net=y_net,
1208:                if pname in init:
1209:                    init[pname].set(value=float(val), vary=False)
1210:        outcome = fit_candidate(x, y, weights, model, initial_params=init)
1433:    proposed_center_init: float
1434:    proposed_fwhm_init: float
1435:    proposed_amplitude_init: float
1529:        if n <= 0 or not np.isfinite(chi):
1692:                  and np.isfinite(r.bic_adjusted)]
1736:    center_init: float
1737:    fwhm_init: float
1749:            "center_be": round(float(self.center_init), 3),
1753:            "fwhm_init": round(float(self.fwhm_init), 2),
1777:    """Mean main-FWHM midpoint across the candidate set × the proposal
1781:    mids = [_main_slot_fwhm_midpoint(c) for c in candidates] or [1.0]
1816:    # margin: mean main-FWHM midpoint across the candidate set × the
1852:        fwhm_init = float(np.clip(fwhh if fwhh > 0 else PROPOSAL_FWHM_MIN,
1855:            role="", center_init=center, fwhm_init=fwhm_init,
1866:        if any(abs(s.center_init - a.center_init) < PRESEED_MIN_SEPARATION_BE
1870:    accepted.sort(key=lambda s: s.center_init)
1871:    return [PreseedSpec(role=f"preseed_dominant_{i}", center_init=s.center_init,
1872:                        fwhm_init=s.fwhm_init, amplitude_net=s.amplitude_net,
1891:            be_window=(s.center_init - 0.75, s.center_init + 0.75),
1893:            fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
1901:        shared_fwhm_params=base.shared_fwhm_params,
1915:    center_init: float
1916:    fwhm_init: float
1917:    amplitude_init: float
1934:def _main_slot_fwhm_midpoint(model: CandidateModel) -> float:
1935:    mids = [0.5 * (s.fwhm_range[0] + s.fwhm_range[1])
2053:        fwhm_init = float(np.clip(fwhh if fwhh > 0 else PROPOSAL_FWHM_MIN,
2062:            center_init=center, fwhm_init=fwhm_init,
2063:            amplitude_init=max(r_at, 1.0),
2100:        be_window=(spec.center_init - 0.75, spec.center_init + 0.75),
2102:        fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
2108:        shared_fwhm_params=base.shared_fwhm_params,
2112:def _initial_params_for_augmented(
2126:            lo = params[pname].min if np.isfinite(params[pname].min) else -np.inf
2127:            hi = params[pname].max if np.isfinite(params[pname].max) else np.inf
2131:    pc.set(value=float(np.clip(spec.center_init, pc.min, pc.max)))
2133:    pa.set(value=float(np.clip(spec.amplitude_init, pa.min, pa.max)))
2136:        pf.set(value=float(np.clip(spec.fwhm_init, pf.min, pf.max)))
2164:        proposed_center_init=spec.center_init, proposed_fwhm_init=spec.fwhm_init,
2165:        proposed_amplitude_init=spec.amplitude_init, roi_bounds=roi,
2184:        init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
2187:        return _fast(f"init_params_error: {exc}")
2189:    primary = fit_candidate(x, y, weights, aug_model, initial_params=init)
2269:    # wall the initial fit did not touch (Codex fwhm-cap review, run B
2334:                             else pr.proposed_center_init)}
2414:    outcome = fit_candidate(x, y, weights, report.model, initial_params=params)
2551:    Threaded through every place a candidate's initial/refit parameters
2630:                    role=s.role, center_init=s.center_be,
2631:                    fwhm_init=s.fwhm_init, amplitude_net=s.amplitude_net,
2637:        preseed_specs.sort(key=lambda s: s.center_init)
2643:                [round(s.center_init, 2) for s in preseed_specs],
2652:            # detected structure in one cheap, well-initialized model.
2659:            augment_specs.sort(key=lambda s: s.center_init)
2686:                    # cheapest, best-initialized candidate, and the screen
2944:                            else pr.proposed_center_init),

exec
/bin/zsh -lc "nl -ba tests/test_api_analyze.py | sed -n '35,245p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    35	    x = np.arange(192.0, 205.0, 0.05)
    36	
    37	    def pv(h, c, w, eta=0.3):
    38	        g = np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
    39	        lo = (w / 2) ** 2 / ((x - c) ** 2 + (w / 2) ** 2)
    40	        return h * ((1 - eta) * g + eta * lo)
    41	
    42	    y = rng.poisson(300.0 + pv(9000.0, 197.9, 1.65)
    43	                    + pv(4950.0, 199.5, 1.65)).astype(float)
    44	    csv = "\n".join(f"{a:.3f},{b:.1f}" for a, b in zip(x, y))
    45	    resp = client.post("/api/upload", data={
    46	        "file": (io.BytesIO(csv.encode()), "doublet.csv")})
    47	    assert resp.status_code == 200, resp.get_json()
    48	    return resp.get_json()["session_id"]
    49	
    50	
    51	def test_meta_menu(client):
    52	    meta = client.get("/api/analyze/meta").get_json()
    53	    assert set(meta["material_classes"]) == {"conductor", "insulator",
    54	                                             "semiconductor", "mixed"}
    55	    assert {"C 1s", "Cl 2p", "U 4f", "B 1s", "N 1s"} <= set(meta["regions"])
    56	    methods = {m["id"]: m for m in meta["methods"]}
    57	    assert set(methods) == {"least_squares", "ic_model_comparison",
    58	                            "bayesian_exchange_mc", "sparse_map"}
    59	    assert methods["ic_model_comparison"]["default_options"]["n_refits"] == 4
    60	
    61	
    62	def test_analyze_ic_end_to_end(client):
    63	    sid = _upload_doublet(client)
    64	    resp = client.post("/api/analyze", json={
    65	        "session_id": sid, "material_class": "insulator",
    66	        "regions": ["Cl 2p"], "method": "ic_model_comparison",
    67	        "roi": {"be_min": 192.0, "be_max": 205.0},
    68	        "options": {"n_refits": 2, "enable_proposal_pass": False},
    69	    })
    70	    assert resp.status_code == 200, resp.get_json()
    71	    body = resp.get_json()
    72	    assert body["success"] is True
    73	    assert body["diagnostics"]["winner"]
    74	    assert len(body["peaks"]) == 2
    75	    roles = {p["role"] for p in body["peaks"]}
    76	    assert roles == {"main_cl2p32", "main_cl2p12"}
    77	    # per-peak confidence vector present
    78	    assert set(body["confidence"]) == roles
    79	    # ambiguity/alternatives surface: ranked candidate table + flags
    80	    names = [c["name"] for c in body["analysis"]["candidates"]]
    81	    assert "Cl0_doublet" in names
    82	    assert "conditional_tier" in body["analysis"]
    83	    # constants provenance flows through, incl. the fit-physics exposure
    84	    prov_keys = {p["constant"]
    85	                 for p in body["analysis"]["constants_provenance"]["Cl 2p"]}
    86	    assert "fit_physics:Cl-2p3/2" in prov_keys
    87	    # the named-review gate (spec §8): nothing is pre-approved
    88	    assert body["review_gate"]["reviewed_by"] is None
    89	    # payload is pure JSON (no numpy leakage)
    90	    json.dumps(body)
    91	
    92	
    93	def test_analyze_least_squares_baseline(client):
    94	    sid = _upload_doublet(client)
    95	    resp = client.post("/api/analyze", json={
    96	        "session_id": sid, "material_class": "insulator",
    97	        "regions": ["Cl 2p"], "method": "least_squares",
    98	        "peak_specs": [
    99	            {"id": "1", "shape": "pseudo_voigt_gl", "center": 197.9,
   100	             "amplitude": 9000, "fwhm": 1.6, "glMix": 30},
   101	            {"id": "2", "shape": "pseudo_voigt_gl", "center": 199.5,
   102	             "amplitude": 5000, "fwhm": 1.6, "glMix": 30},
   103	        ],
   104	        "options": {"background_method": "linear"},
   105	    })
   106	    assert resp.status_code == 200, resp.get_json()
   107	    body = resp.get_json()
   108	    assert body["success"] is True
   109	    centers = sorted(p["center"] for p in body["peaks"])
   110	    assert centers[0] == pytest.approx(197.9, abs=0.1)
   111	    assert centers[1] == pytest.approx(199.5, abs=0.1)
   112	
   113	
   114	@pytest.mark.parametrize("payload,fragment", [
   115	    ({"method": "nonexistent"}, "Unknown analyze method"),
   116	    ({"material_class": "plasma"}, "material_class"),
   117	    ({"regions": []}, "regions"),
   118	    ({"regions": ["Xx 9z"]}, "region"),
   119	    ({"method": "least_squares"}, "peak_specs"),
   120	    ({"options": {"bogus_option": 1}}, "unknown"),
   121	    ({"roi": {"be_min": 197.0, "be_max": 197.2}}, "20 points"),
   122	    ({"cc_shift": "lots"}, "cc_shift"),
   123	])
   124	def test_analyze_validation_400s(client, payload, fragment):
   125	    sid = _upload_doublet(client)
   126	    base = {"session_id": sid, "material_class": "insulator",
   127	            "regions": ["Cl 2p"], "method": "ic_model_comparison",
   128	            "options": {"n_refits": 2, "enable_proposal_pass": False}}
   129	    base.update(payload)
   130	    resp = client.post("/api/analyze", json=base)
   131	    assert resp.status_code == 400, resp.get_json()
   132	    assert fragment.lower() in resp.get_json()["error"].lower()
   133	
   134	
   135	def test_analyze_unknown_session_404(client):
   136	    resp = client.post("/api/analyze", json={
   137	        "session_id": "0" * 32, "material_class": "insulator",
   138	        "regions": ["Cl 2p"]})
   139	    assert resp.status_code == 404
   140	
   141	
   142	def test_analyze_non_object_bodies_are_clean_400s(client):
   143	    """Codex analyze review blocker: a JSON array/string/null body (or
   144	    non-object roi/phase) must be a clean 400, never a 500."""
   145	    sid = _upload_doublet(client)
   146	    for body in (["not", "an", "object"], "string", 42):
   147	        resp = client.post("/api/analyze", json=body)
   148	        assert resp.status_code == 400, (body, resp.status_code)
   149	        assert "JSON object" in resp.get_json()["error"]
   150	    base = {"session_id": sid, "material_class": "insulator",
   151	            "regions": ["Cl 2p"], "method": "ic_model_comparison"}
   152	    # truthy AND falsy non-objects: `or {}` used to swallow [] / "" / false
   153	    for bad in (["bad"], [], "", False):
   154	        for field, frag in (("roi", "'roi'"), ("phase", "'phase'"),
   155	                            ("options", "'options'")):
   156	            resp = client.post("/api/analyze", json={**base, field: bad})
   157	            assert resp.status_code == 400, (field, bad, resp.status_code)
   158	            assert frag in resp.get_json()["error"]
   159	
   160	
   161	def test_analyze_malformed_option_values_are_400s(client):
   162	    """A well-formed options OBJECT with a malformed VALUE (TypeError from
   163	    the method's numeric casts) must be a clean 400, never a 500."""
   164	    sid = _upload_doublet(client)
   165	    for bad_opts in ({"n_refits": []}, {"n_refits": {"a": 1}},
   166	                     {"rng_seed": [1, 2]}):
   167	        resp = client.post("/api/analyze", json={
   168	            "session_id": sid, "material_class": "insulator",
   169	            "regions": ["Cl 2p"], "method": "ic_model_comparison",
   170	            "options": bad_opts})
   171	        assert resp.status_code == 400, (bad_opts, resp.status_code)
   172	        assert "invalid option" in resp.get_json()["error"].lower()
   173	
   174	
   175	def test_analyze_material_class_mixed_accepted(client):
   176	    """MaterialClass.MIXED (2026-07-20 unit) round-trips through the
   177	    ordinary /api/analyze path exactly like any other material class --
   178	    Cl 2p's region module doesn't special-case it, so this is a plain
   179	    acceptance check, not a behavior check (that lives in
   180	    tests/autofit/test_c1s_mixed_material_class.py, against C 1s)."""
   181	    sid = _upload_doublet(client)
   182	    resp = client.post("/api/analyze", json={
   183	        "session_id": sid, "material_class": "mixed",
   184	        "regions": ["Cl 2p"], "method": "ic_model_comparison",
   185	        "roi": {"be_min": 192.0, "be_max": 205.0},
   186	        "options": {"n_refits": 2, "enable_proposal_pass": False},
   187	    })
   188	    assert resp.status_code == 200, resp.get_json()
   189	    assert resp.get_json()["success"] is True
   190	
   191	
   192	def test_analyze_start_material_class_mixed_accepted(client):
   193	    """Same acceptance check through the async /api/analyze/start path --
   194	    shares _validate_analyze_request with the sync route. Success here is
   195	    202 (job accepted), not 200 -- /api/analyze/start never returns the
   196	    result body directly; that comes from polling /api/analyze/progress."""
   197	    sid = _upload_doublet(client)
   198	    resp = client.post("/api/analyze/start", json={
   199	        "session_id": sid, "material_class": "mixed",
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
   241	                          "d": np.float64("inf"), "e": 2.5})
   242	    assert out == {"a": None, "b": None, "c": [1.0, None],
   243	                   "d": None, "e": 2.5}
   244	    json.dumps(out, allow_nan=False)

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '360,430p'" in /Users/skyefortier/xps-verify
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
   426	        p.add(f"{prefix}{name}", value=float(np.clip(init, plo, phi)), min=plo, max=phi)
   427	
   428	
   429	def _full_window_bound_overrides(
   430	    model: CandidateModel, x: Optional[np.ndarray],

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '480,565p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   480	    y_net: Optional[np.ndarray] = None,
   481	    fit_full_window: bool = False,
   482	) -> Parameters:
   483	    """Slot midpoints as starting values, slot bounds as hard constraints.
   484	
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
   506	        return 1000.0, 1.0e5
   507	
   508	    bound_overrides = (_full_window_bound_overrides(model, x)
   509	                       if fit_full_window else {})
   510	
   511	    # Pass 1: primary (non-linked) slots
   512	    for slot in model.slots:
   513	        if slot.linked_to is not None:
   514	            continue
   515	        prefix = _slot_prefix(slot.role)
   516	        cmid = 0.5 * (slot.be_window[0] + slot.be_window[1])
   517	        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])
   518	        amp_init, amp_max = _amp_bounds(slot.be_window)
   519	        bound = bound_overrides.get(slot.role, slot.be_window)
   520	        p.add(f"{prefix}center", value=cmid, min=bound[0], max=bound[1])
   521	        p.add(f"{prefix}amplitude", value=amp_init, min=0.0, max=amp_max)
   522	        _add_shape_params(p, prefix, slot, fmid)
   523	
   524	    # Pass 2: linked slots (satellites, chemically-shifted contaminants,
   525	    # spin-orbit partners) — center via offset expression; amplitude either
   526	    # free (satellite) or ratio-linked (doublet).  Processed in dependency
   527	    # order so a chain (main ← sat7/2 ← sat5/2) resolves: lmfit exprs may
   528	    # not reference parameters that do not exist yet.
   529	    done_roles = {s.role for s in model.slots if s.linked_to is None}
   530	    pending = [s for s in model.slots if s.linked_to is not None]
   531	    ordered: list[ComponentSlot] = []
   532	    while pending:
   533	        ready = [s for s in pending if s.linked_to in done_roles]
   534	        if not ready:
   535	            raise ValueError(
   536	                f"unresolvable linkage chain among {[s.role for s in pending]} "
   537	                "(missing parent or cycle)"
   538	            )
   539	        for s in ready:
   540	            ordered.append(s)
   541	            done_roles.add(s.role)
   542	            pending.remove(s)
   543	
   544	    for slot in ordered:
   545	        prefix = _slot_prefix(slot.role)
   546	        parent = model.slot_by_role(slot.linked_to)
   547	        if parent is None:
   548	            raise ValueError(f"Slot {slot.role!r} linked to unknown role {slot.linked_to!r}")
   549	        parent_prefix = _slot_prefix(parent.role)
   550	        offs_lo, offs_hi = slot.linked_offset_range or (0.0, 0.0)
   551	        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])
   552	
   553	        if offs_hi > offs_lo:
   554	            p.add(f"{prefix}offset", value=0.5 * (offs_lo + offs_hi),
   555	                  min=offs_lo, max=offs_hi)
   556	            p.add(f"{prefix}center", value=0.0,
   557	                  expr=f"{parent_prefix}center + {prefix}offset")
   558	        else:
   559	            # Degenerate range = fixed offset
   560	            p.add(f"{prefix}center", value=0.0,
   561	                  expr=f"{parent_prefix}center + {offs_lo}")
   562	
   563	        # Shape params (incl. the width) BEFORE the amplitude: the width-
   564	        # aware area-ratio expression below references this slot's width.
   565	        _add_shape_params(p, prefix, slot, fmid, parent_prefix=parent_prefix)

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '565,625p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   565	        _add_shape_params(p, prefix, slot, fmid, parent_prefix=parent_prefix)
   566	
   567	        # ``area_ratio`` is an AREA statement (2j+1 statistical intensity).
   568	        # With a shared width, height ratio == area ratio and the plain
   569	        # height link is exact.  Under width-inequality linkage
   570	        # (fwhm_excess_range) the height link must carry the width
   571	        # correction: same-shape peaks have area ∝ amplitude × width (the
   572	        # lineshape factor cancels only when the mixing params are shared —
   573	        # guarded in _add_shape_params/_validate below).
   574	        ratio_expr: Optional[str] = None
   575	        if slot.area_ratio_range is not None:
   576	            rlo, rhi = slot.area_ratio_range
   577	            rinit = slot.area_ratio if slot.area_ratio is not None else 0.5 * (rlo + rhi)
   578	            p.add(f"{prefix}ratio", value=float(np.clip(rinit, rlo, rhi)),
   579	                  min=rlo, max=rhi)
   580	            ratio_expr = f"{prefix}ratio"
   581	        elif slot.area_ratio is not None:
   582	            ratio_expr = repr(float(slot.area_ratio))
   583	
   584	        if ratio_expr is None:
   585	            amp_init, amp_max = _amp_bounds(slot.be_window)
   586	            p.add(f"{prefix}amplitude", value=amp_init, min=0.0, max=amp_max)
   587	        elif slot.fwhm_excess_range is not None:
   588	            # Area-ratio linkage under independent widths is implemented
   589	            # ONLY for the pseudo-Voigt with a shared mixing parameter —
   590	            # the one case where area ∝ height × width with a cancelling
   591	            # shape factor.  Other shapes (asym-GL asymmetry, DS α/γ,
   592	            # DS+G's m_gauss-only width, LACX α/β/m) do NOT scale that way;
   593	            # a shape-specific area factor is FUTURE WORK, and silently
   594	            # emitting the height×width link there would enforce a wrong
   595	            # area ratio (Codex adjudication-unit review, both runs).
   596	            if parent.line_shape is not slot.line_shape:
   597	                raise ValueError(
   598	                    f"slot {slot.role!r}: area-ratio linkage under "
   599	                    "fwhm_excess_range requires the parent to share the "
   600	                    "line shape (area ∝ amplitude × width only holds "
   601	                    "within one shape family)"
   602	                )
   603	            if slot.line_shape is not LineShape.PSEUDO_VOIGT:
   604	                raise ValueError(
   605	                    f"slot {slot.role!r}: area-ratio linkage under "
   606	                    "fwhm_excess_range is implemented only for "
   607	                    "PSEUDO_VOIGT (shape-specific area factors for other "
   608	                    "shapes are future work)"
   609	                )
   610	            if "gl_ratio" not in slot.share_parent_params:
   611	                raise ValueError(
   612	                    f"slot {slot.role!r}: area-ratio linkage under "
   613	                    "fwhm_excess_range requires gl_ratio in "
   614	                    "share_parent_params (the pseudo-Voigt area factor "
   615	                    "must cancel in the ratio)"
   616	                )
   617	            wname = _width_param(slot.line_shape)
   618	            p.add(f"{prefix}amplitude", value=0.0,
   619	                  expr=(f"{parent_prefix}amplitude * {ratio_expr} * "
   620	                        f"{parent_prefix}{wname} / {prefix}{wname}"))
   621	        else:
   622	            p.add(f"{prefix}amplitude", value=0.0,
   623	                  expr=f"{parent_prefix}amplitude * {ratio_expr}")
   624	
   625	    return p

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '13010,13040p'" in /Users/skyefortier/xps-verify
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
 13030	            'does (differential charging). Peak width limits are relaxed ' +
 13031	            'accordingly. The charge reference calibrates the MATRIX’s ' +
 13032	            'potential — it may not apply to the analyte, so reported ' +
 13033	            'positions carry additional, unquantified uncertainty. This ' +
 13034	            'does not correct for that uncertainty; it only stops ' +
 13035	            'assuming there isn’t any.',
 13036	    },
 13037	  },
 13038	  tips: {
 13039	    material: 'Conducting samples charge-correct differently from ' +
 13040	              'insulating ones, and the suggested peak shapes differ too. ' +

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '13420,13745p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
 13420	  // all wording from FP_STRINGS; server strings escaped even though
 13421	  // currently code-controlled (a future registered label must never
 13422	  // become an injection point)
 13423	  document.getElementById('fp-blurb').innerHTML = FP_STRINGS.blurb;
 13424	  document.getElementById('fp-apply-note').textContent = FP_STRINGS.applyNote;
 13425	  document.getElementById('fp-material-label').title = FP_STRINGS.tips.material;
 13426	  document.getElementById('fp-method-label').title = FP_STRINGS.tips.method;
 13427	  document.getElementById('fp-regions-label').title = FP_STRINGS.tips.regions;
 13428	  const mat = document.getElementById('fp-material');
 13429	  mat.innerHTML = _fpMeta.material_classes
 13430	    .map(m => {
 13431	      const s = FP_STRINGS.materials[m] || {};
 13432	      const title = s.hint ? ` title="${_fpEsc(s.hint)}"` : '';
 13433	      return `<option value="${_fpEsc(m)}"${title}>${_fpEsc(s.label || m)}</option>`;
 13434	    }).join('');
 13435	  _fpMaterialChanged();
 13436	  document.getElementById('fp-regions-filter').value = '';
 13437	  _fpRegionsSelected = new Set();
 13438	  _fpExpandedElement = null;
 13439	  _fpRenderLegend();
 13440	  _fpRenderPtGrid('');
 13441	  _fpRenderSearchDropdown('');
 13442	  _fpRenderExpandedPanel();
 13443	  document.getElementById('fp-regions-tier-note').textContent = '';
 13444	  const meth = document.getElementById('fp-method');
 13445	  meth.innerHTML = _fpMeta.methods
 13446	    .map(m => {
 13447	      const s = FP_STRINGS.methods[m.id] || {};
 13448	      // hovering an option (even before selecting it) shows the SAME
 13449	      // plain-English explanation as the hint box below the dropdown —
 13450	      // no jargon, and no need to select first just to learn what an
 13451	      // option does. Previously showed the raw backend label here
 13452	      // (e.g. "Auto — model comparison (IC)"), which read as vague/
 13453	      // jargon-y "the tooltip" per the 2026-07-14 bug report.
 13454	      return `<option value="${_fpEsc(m.id)}" title="${_fpEsc(s.hint || s.label || m.label || m.id)}">${_fpEsc(s.label || m.label || m.id)}</option>`;
 13455	    }).join('');
 13456	  meth.value = 'ic_model_comparison';
 13457	  _fpMethodChanged();
 13458	  document.getElementById('fp-results').style.display = 'none';
 13459	  document.getElementById('fp-status').textContent = '';
 13460	  _fpResetModalPosition();
 13461	  document.getElementById('find-peaks-overlay').classList.add('open');
 13462	}
 13463	
 13464	function closeFindPeaksModal() {
 13465	  document.getElementById('find-peaks-overlay').classList.remove('open');
 13466	}
 13467	
 13468	// ── Draggable modal (2026-07-11) ────────────────────────────────────────
 13469	// Same technique as the Reference palette's _refPaletteDragStart/Move/End
 13470	// (static/js/ref_identify_core.js RefCore.clampToViewport is the shared,
 13471	// tested clamp math) — but scoped to ONLY the Find Peaks modal: every
 13472	// other .xps-modal in the app stays centered/non-draggable.
 13473	
 13474	let _fpModalDrag = null;
 13475	
 13476	// True for the close button (or any future control placed in the header)
 13477	// — those must still work; only the bare header background starts a drag.
 13478	// (`instanceof Element` guard: a text-node event target lacks .closest —
 13479	// see CLAUDE.md Known Issues re: the same class of bug elsewhere.)
 13480	function _fpIsDragBlockingTarget(target) {
 13481	  return !!(target instanceof Element && target.closest('button, select, input, a, textarea'));
 13482	}
 13483	
 13484	function _fpClampModal(left, top) {
 13485	  const el = document.getElementById('find-peaks-modal-box');
 13486	  const w = el ? el.offsetWidth : 680, h = el ? el.offsetHeight : 400;
 13487	  return RefCore.clampToViewport(left, top, w, h, window.innerWidth, window.innerHeight, 8);
 13488	}
 13489	
 13490	function _fpModalDragStart(e) {
 13491	  if (_fpIsDragBlockingTarget(e.target)) return;
 13492	  const el = document.getElementById('find-peaks-modal-box');
 13493	  if (!el) return;
 13494	  const r = el.getBoundingClientRect();
 13495	  // First drag: switch from flex-centered to absolutely positioned,
 13496	  // pinned at its CURRENT visual spot so there is no jump.
 13497	  el.style.position = 'fixed';
 13498	  el.style.left = r.left + 'px'; el.style.top = r.top + 'px';
 13499	  el.style.margin = '0';
 13500	  _fpModalDrag = { dx: e.clientX - r.left, dy: e.clientY - r.top };
 13501	  el.classList.add('dragging');
 13502	  document.addEventListener('mousemove', _fpModalDragMove, true);
 13503	  document.addEventListener('mouseup', _fpModalDragEnd, true);
 13504	  e.preventDefault();
 13505	}
 13506	function _fpModalDragMove(e) {
 13507	  if (!_fpModalDrag) return;
 13508	  const el = document.getElementById('find-peaks-modal-box');
 13509	  if (!el) return;
 13510	  const c = _fpClampModal(e.clientX - _fpModalDrag.dx, e.clientY - _fpModalDrag.dy);
 13511	  el.style.left = c.left + 'px'; el.style.top = c.top + 'px';
 13512	}
 13513	function _fpModalDragEnd() {
 13514	  const el = document.getElementById('find-peaks-modal-box');
 13515	  if (el) el.classList.remove('dragging');
 13516	  _fpModalDrag = null;
 13517	  document.removeEventListener('mousemove', _fpModalDragMove, true);
 13518	  document.removeEventListener('mouseup', _fpModalDragEnd, true);
 13519	}
 13520	// Re-clamp an open, already-dragged modal when the viewport changes
 13521	// (mirrors the Reference palette's resize guard). A never-dragged modal
 13522	// is still flex-centered — CSS handles that case with no JS needed.
 13523	window.addEventListener('resize', () => {
 13524	  const overlay = document.getElementById('find-peaks-overlay');
 13525	  const el = document.getElementById('find-peaks-modal-box');
 13526	  if (!overlay || !overlay.classList.contains('open') || !el) return;
 13527	  if (el.style.position !== 'fixed') return;
 13528	  const c = _fpClampModal(parseFloat(el.style.left), parseFloat(el.style.top));
 13529	  el.style.left = c.left + 'px'; el.style.top = c.top + 'px';
 13530	});
 13531	// Every fresh open starts centered — a drag is a "move it out of the way
 13532	// for now" convenience, not a permanent relocation.
 13533	function _fpResetModalPosition() {
 13534	  const el = document.getElementById('find-peaks-modal-box');
 13535	  if (!el) return;
 13536	  el.style.position = ''; el.style.left = ''; el.style.top = ''; el.style.margin = '';
 13537	  el.classList.remove('dragging');
 13538	}
 13539	
 13540	// Preserve a selection across a filter-driven rebuild — a previously
 13541	// picked region (e.g. one member of a ctrl-click co-fit pair) stays
 13542	// selected even when a later keystroke filters it out of view.
 13543	let _fpRegionsSelected = new Set();
 13544	
 13545	// The element symbol currently expanded to show its level chips below the
 13546	// grid (unit 2, 2026-07-13 periodic-table picker), or null.
 13547	let _fpExpandedElement = null;
 13548	
 13549	const FP_TIER_RANK = { curated: 3, machine: 2, structure_only: 1 };
 13550	
 13551	// One element symbol -> its PRACTICAL coverage entries only (backend
 13552	// `practical` flag, autofit/coverage_index.py — never invents a BE, just
 13553	// hides valence/too-deep levels a bench chemist would not try to fit).
 13554	function _fpElementCoverage(sym) {
 13555	  return ((_fpMeta && _fpMeta.coverage) || []).filter(
 13556	    e => e.symbol === sym && e.practical);
 13557	}
 13558	
 13559	function _fpBestTier(entries) {
 13560	  let best = null;
 13561	  for (const e of entries) {
 13562	    if (!best || FP_TIER_RANK[e.tier] > FP_TIER_RANK[best]) best = e.tier;
 13563	  }
 13564	  return best;
 13565	}
 13566	
 13567	// Static-ish legend (rebuilt on modal open, from the SAME FP_TIER_META
 13568	// single source the grid/chips read — never a second copy of the colors).
 13569	function _fpRenderLegend() {
 13570	  const el = document.getElementById('fp-legend');
 13571	  if (!el) return;
 13572	  const items = ['curated', 'machine', 'structure_only'].map(t => {
 13573	    const meta = FP_TIER_META[t];
 13574	    return `<span><span class="fp-legend-dot" style="--tier-c:${meta.color}"></span>${_fpEsc(meta.label)}</span>`;
 13575	  });
 13576	  items.push('<span><span class="fp-legend-dot disabled"></span>No coverage</span>');
 13577	  el.innerHTML = items.join('');
 13578	}
 13579	
 13580	// The periodic-table grid: one cell per element (REF_PT_LAYOUT — the same
 13581	// 18-column layout the Reference panel's #ref-pt-grid uses). Cell color =
 13582	// the BEST tier among that element's practical regions (curated > machine
 13583	// > structure_only); an element with none is disabled/greyed — never
 13584	// invented coverage. A search query dims (not hides — a co-fit pick stays
 13585	// visible even if filtered out) non-matching cells.
 13586	function _fpRenderPtGrid(query) {
 13587	  const grid = document.getElementById('fp-pt-grid');
 13588	  if (!grid) return;
 13589	  const q = String(query == null ? '' : query).trim();
 13590	  const ql = q.toLowerCase();
 13591	  let cells = '';
 13592	  for (const el of REF_PT_LAYOUT) {
 13593	    const entries = _fpElementCoverage(el.sym);
 13594	    const clickable = entries.length > 0;
 13595	    const bestTier = _fpBestTier(entries);
 13596	    const meta = bestTier ? (FP_TIER_META[bestTier] || FP_TIER_META.structure_only) : null;
 13597	    const matchesQuery = !q || entries.some(e => _fpRegionMatchesFilter(e, q)) ||
 13598	      el.sym.toLowerCase().includes(ql);
 13599	    const hasSelection = entries.some(e => _fpRegionsSelected.has(e.region));
 13600	    const isExpanded = _fpExpandedElement === el.sym;
 13601	    const cls = 'fp-pt-cell' +
 13602	      (clickable ? ' selectable' : '') +
 13603	      (isExpanded ? ' expanded' : '') +
 13604	      (hasSelection ? ' has-selection' : '') +
 13605	      (q && !matchesQuery ? ' dimmed' : '');
 13606	    const style = `grid-column:${el.col};grid-row:${el.row}` +
 13607	      (meta ? `;--tier-c:${meta.color}` : '');
 13608	    const title = clickable
 13609	      ? `${el.sym} (Z=${el.z}) — ${meta.label}: click to see available core levels`
 13610	      : `${el.sym} (Z=${el.z}) — no practical Find Peaks coverage`;
 13611	    cells += `<div class="${_fpEsc(cls)}" style="${style}"` +
 13612	      (clickable
 13613	        ? ` tabindex="0" role="button" aria-expanded="${isExpanded}" onclick="_fpToggleElementExpand('${el.sym}')"` +
 13614	          ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpToggleElementExpand('${el.sym}')}"`
 13615	        : '') +
 13616	      ` title="${_fpEsc(title)}">${el.sym}</div>`;
 13617	  }
 13618	  cells += '<div class="fp-pt-cell fmarker" style="grid-column:3;grid-row:6" title="Lanthanides — detached row below">57–71</div>';
 13619	  cells += '<div class="fp-pt-cell fmarker" style="grid-column:3;grid-row:7" title="Actinides — detached row below">89–103</div>';
 13620	  grid.innerHTML = cells;
 13621	}
 13622	
 13623	function _fpToggleElementExpand(sym) {
 13624	  _fpExpandedElement = (_fpExpandedElement === sym) ? null : sym;
 13625	  _fpRenderPtGrid(document.getElementById('fp-regions-filter').value);
 13626	  _fpRenderExpandedPanel();
 13627	}
 13628	
 13629	// The currently-expanded element's practical levels, as clickable chips —
 13630	// each independently colored/tagged by ITS OWN tier (a curated + machine
 13631	// level can coexist on one element).
 13632	function _fpRenderExpandedPanel() {
 13633	  const panel = document.getElementById('fp-expanded-panel');
 13634	  if (!panel) return;
 13635	  if (!_fpExpandedElement) {
 13636	    panel.innerHTML = '<div class="fp-expanded-empty">Click an element above to see its available core levels, or search by element, name, or level.</div>';
 13637	    return;
 13638	  }
 13639	  const entries = _fpElementCoverage(_fpExpandedElement)
 13640	    .sort((a, b) => (FP_TIER_RANK[b.tier] - FP_TIER_RANK[a.tier]) || a.level.localeCompare(b.level));
 13641	  if (!entries.length) {
 13642	    panel.innerHTML = `<div class="fp-expanded-empty">${_fpEsc(_fpExpandedElement)} — no practical Find Peaks coverage.</div>`;
 13643	    return;
 13644	  }
 13645	  const name = entries[0].name;
 13646	  const chips = entries.map(e => {
 13647	    const meta = FP_TIER_META[e.tier] || FP_TIER_META.structure_only;
 13648	    const isSel = _fpRegionsSelected.has(e.region);
 13649	    return `<div class="fp-level-chip${isSel ? ' selected' : ''}" style="--tier-c:${meta.color}"` +
 13650	      ` tabindex="0" role="button" aria-pressed="${isSel}"` +
 13651	      ` onclick="_fpToggleRegion('${_fpEsc(e.region)}', event.ctrlKey||event.metaKey)"` +
 13652	      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpToggleRegion('${_fpEsc(e.region)}', event.ctrlKey||event.metaKey)}"` +
 13653	      ` title="${_fpEsc(meta.label + ': ' + e.note)}">${meta.tag} ${_fpEsc(e.level)}</div>`;
 13654	  }).join('');
 13655	  panel.innerHTML = `<div class="fp-expanded-title">${_fpEsc(name)} (Z=${entries[0].z}) — click a level` +
 13656	    ` <small style="color:var(--text3)">(ctrl/⌘-click to add a second region)</small></div>` +
 13657	    `<div class="fp-level-chips">${chips}</div>`;
 13658	}
 13659	
 13660	// Up to 8 direct region matches while typing — a fast alternative to
 13661	// clicking through the grid (goal: type-ahead search alongside the grid).
 13662	function _fpRenderSearchDropdown(query) {
 13663	  const box = document.getElementById('fp-search-dropdown');
 13664	  if (!box) return;
 13665	  const q = String(query == null ? '' : query).trim();
 13666	  if (!q) { box.innerHTML = ''; return; }
 13667	  const coverage = ((_fpMeta && _fpMeta.coverage) || []).filter(e => e.practical);
 13668	  const opts = _fpBuildRegionOptions(coverage, q).slice(0, 8);
 13669	  if (!opts.length) { box.innerHTML = ''; return; }
 13670	  const rows = opts.map(o => {
 13671	    const meta = FP_TIER_META[o.tier] || FP_TIER_META.structure_only;
 13672	    const entry = coverage.find(e => e.region === o.value);
 13673	    return `<div class="fp-search-dropdown-item" style="--tier-c:${meta.color}"` +
 13674	      ` tabindex="0" role="button"` +
 13675	      ` onclick="_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)"` +
 13676	      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)}">` +
 13677	      `<span>${meta.tag} ${_fpEsc(o.value)}</span>` +
 13678	      `<span class="fp-sdi-name">${_fpEsc(entry ? entry.name : '')}</span></div>`;
 13679	  }).join('');
 13680	  box.innerHTML = `<div class="fp-search-dropdown">${rows}</div>`;
 13681	}
 13682	
 13683	function _fpPickFromSearch(region, additive) {
 13684	  const coverage = (_fpMeta && _fpMeta.coverage) || [];
 13685	  const entry = coverage.find(e => e.region === region);
 13686	  if (entry) _fpExpandedElement = entry.symbol;
 13687	  _fpToggleRegion(region, additive);
 13688	  const box = document.getElementById('fp-search-dropdown');
 13689	  if (box) box.innerHTML = '';
 13690	}
 13691	
 13692	function _fpFilterRegions(query) {
 13693	  _fpRenderPtGrid(query);
 13694	  _fpRenderSearchDropdown(query);
 13695	}
 13696	
 13697	// Pure selection-set logic (DOM-free, unit-testable): a plain click
 13698	// REPLACES the selection with just that region (matches how a single
 13699	// click reads); ctrl/cmd-click toggles membership without disturbing the
 13700	// rest (goal: "preserve the existing multi-region selection (ctrl-click
 13701	// to fit two together)"). Returns a NEW Set — never mutates `current`.
 13702	function _fpNextSelection(current, region, additive) {
 13703	  if (additive) {
 13704	    const next = new Set(current);
 13705	    if (next.has(region)) next.delete(region);
 13706	    else next.add(region);
 13707	    return next;
 13708	  }
 13709	  if (current.size === 1 && current.has(region)) return current;
 13710	  return new Set([region]);
 13711	}
 13712	
 13713	function _fpToggleRegion(region, additive) {
 13714	  _fpRegionsSelected = _fpNextSelection(_fpRegionsSelected, region, additive);
 13715	  _fpSyncSelectionUI();
 13716	}
 13717	
 13718	function _fpSyncSelectionUI() {
 13719	  const values = Array.from(_fpRegionsSelected);
 13720	  const coverage = (_fpMeta && _fpMeta.coverage) || [];
 13721	  const entries = values.map(v => coverage.find(e => e.region === v))
 13722	    .filter(Boolean);
 13723	  document.getElementById('fp-regions-tier-note').textContent =
 13724	    _fpTierNoteFor(entries);
 13725	  // ROI auto-fill: only for an UNAMBIGUOUS single-region pick with a real
 13726	  // hint — a co-fit selection (2 regions) has no single "right" window,
 13727	  // and a structure_only region honestly has no hint to offer (goal:
 13728	  // never invent a window; the note above says so, ROI is left alone).
 13729	  if (entries.length === 1 && entries[0].roi) {
 13730	    document.getElementById('roi-min').value = entries[0].roi.be_min;
 13731	    document.getElementById('roi-max').value = entries[0].roi.be_max;
 13732	  }
 13733	  _fpRenderPtGrid(document.getElementById('fp-regions-filter').value);
 13734	  _fpRenderExpandedPanel();
 13735	}
 13736	
 13737	function _fpMaterialChanged() {
 13738	  const v = document.getElementById('fp-material').value;
 13739	  const s = FP_STRINGS.materials[v] || {};
 13740	  document.getElementById('fp-material-hint').textContent = s.hint || '';
 13741	}
 13742	
 13743	function _fpMethodChanged() {
 13744	  const id = document.getElementById('fp-method').value;
 13745	  const m = (_fpMeta.methods || []).find(x => x.id === id);

codex
The implementation does widen both per-slot contamination ranges and the shared-width declaration in the linked families. One notable test gap: the new structural tests inspect slot `fwhm_range`s but not `CandidateModel.shared_fwhm_params`, which is the actual parameter bound for the linked shared-width families.
exec
/bin/zsh -lc "nl -ba docs/autofit/PROGRESS.md | sed -n '400,455p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   400	  case) + one 2×Voigt fit (cc=0, χ²ᵣ 1.83).
   401	- **N 1s**: NOT present as a dedicated region scan in the fitted projects; N 1s signal
   402	  appears inside U 4f windows (UCl4-BN 5-peak fits incl. asym-GL N-region peak) — the
   403	  co-fit exemplar. Raw `3 BN-graphite ... .DATA` has N1s scans (unfitted).
   404	- **RSF-tag bugs to lint** (goal mentioned 'Zr 3d' on a boron peak): confirmed stray tags
   405	  seen so far: 'K 2p' on a C 1s π→π* satellite (1-GTA), 'N 1s' on a U 4f satellite
   406	  (UCl4_on_graphite — may be intentional: that satellite sits at ~397 eV).
   407	  Zr-3d-on-B1s to be confirmed when B 1s parity work starts.
   408	- Standalone `U4f_5_Scan1_...fit.json`: `.fit.json` export (version 1) with
   409	  `_backendParams` incl. bounds — useful for LACX param cross-checks.
   410	
   411	### Tab JSON schema (observed, v3)
   412	Top-level: `id,name,color,isSurvey,rawBE,rawIntensity,ccShift,chargeVerified,peaks,nextId,
   413	fitResult{chi,chiReduced,rmse,fittedY,be,bgIntensity,bgSubtracted,roiRange},notes,
   414	manualAnchors,lineWidth,ui{bgType,bgStart,bgEnd,shirleyIter,endpointAvg,roiMin,roiMax,
   415	ccMethod,ccObs,ccLit,bgSubtractedView}`.
   416	
   417	### Decisions made
   418	- Bg for parity/battery fits comes from each tab's persisted `ui.bgType` (observed:
   419	  'smart' on U 4f anchors) — reproduce with `fitting.py` equivalents.
   420	- New engine lives in a new `autofit/` package; tests in `tests/autofit/`;
   421	  nothing imports it from the existing request path (strictly additive).
   422	
   423	## Parity-gate calibration log (2026-07-03)
   424	
   425	Iterating the C 1s gate on 3 real anchors exposed four issues; each fix is a
   426	documented methodological decision (Codex should adversarially review all):
   427	
   428	1. **Satellite FWHM cap recalibrated** (1.0,3.0)→(1.0,5.5): fitalg UNVERIFIED
   429	   tunable; 44 labeled expert fits span 1.9–5.0 eV (median 4.17, both
   430	   analysts). With 3.0, every candidate pegged `satellite_pi:fwhm@max` → zero
   431	   survivors on all anchors.
   432	2. **Lab-practice contamination width range** (0.8,3.5) for AG/MG families
   433	   only (labeled set: median 2.08, 70% >1.6); A/M/B keep the Biesinger
   434	   (0.8,1.6) convention so model comparison arbitrates. Discrepancy #5.
   435	3. **Best-minimum promotion** (engine improvement over fitalg): the report
   436	   now uses the best converged fit found across primary + stability refits,
   437	   not unconditionally the primary. Before: two anchors reported graphitic
   438	   main exactly at the 284.400 init (window midpoint) while refits had found
   439	   deeper minima; after: Scan_6 main lands 284.512 (Δ12 meV vs expert 284.50).
   440	4. **Two-tier rank_and_filter** (departure from fitalg, documented in code):
   441	   when NO candidate passes plausibility cleanly, stable-but-boundary-limited
   442	   candidates are ranked as a CONDITIONAL tier (`conditional=True`, violations
   443	   preserved and surfaced). fitalg's absolutist filter returned zero survivors
   444	   on 2/3 real composite anchors — routine data, not pathology. Stability
   445	   failures are never promoted.
   446	5. **MG family added** (asym-GL graphitic + aliphatic + satellite +
   447	   contaminants = the expert model's exact structure; χ²ᵣ 3.8–7.1 vs AG's
   448	   31–94 on the anchors) with the aliphatic center OFFSET-LINKED to the
   449	   graphitic main (+0.2…+0.6 eV) — a free aliphatic slides into the graphitic
   450	   flank and pegs the window floor (overlap degeneracy, fitalg LIMITATIONS §9).
   451	
   452	Engine winners vs expert (post-fix, reduced 4-candidate gate, n_refits=4):
   453	main Δ 12–100 meV; satellite Δ 0.2–0.3 eV; envelope R-factor (≥284 eV domain)
   454	0.014–0.053. The low-BE 'Unknown' (~283.4) is intentionally out of gate scope
   455	(proposal-pass territory, discrepancy #6).

exec
/bin/zsh -lc "nl -ba docs/autofit/PROGRESS.md | sed -n '740,775p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   740	
   741	**Measured outcome on the real anchors (both corrected Cl2p tabs):** the
   742	data REJECTS the Coster-Kronig hypothesis —
   743	
   744	| candidate | Scan bic*/χ²ᵣ | Scan_0 bic*/χ²ᵣ | boundary pegs |
   745	|---|---|---|---|
   746	| Cl0r_doublet_relaxed+bfix (winner, unchanged) | 1782.9 / 1.614 | 1802.1 / 2.658 | — (ratio bound-fixed 0.55) |
   747	| Cl0rw_relaxed_freewidth | 1793.5 / 1.631 | 1812.7 / 2.686 | ratio@max AND fwhm_excess@min |
   748	| Cl0_doublet (shared width, 0.5) | 1894.2 / 2.399 | 1880.0 / 3.253 | — |
   749	| Cl0w_freewidth (0.5 area ratio) | 1899.5 / 2.411 | 1885.3 / 3.270 | fwhm_excess@min |
   750	
   751	Width freedom buys NOTHING at the statistical ratio (χ²ᵣ 2.41 vs 2.40 /
   752	3.27 vs 3.25) and the relaxed ratio still pegs 0.55 WITH width freedom.
   753	The ratio anomaly is not a shared-FWHM artifact. **Δso/ratio therefore
   754	REMAIN CONDITIONAL** (the adjudicated lift was contingent on ratio → ~0.5,
   755	which did not occur).
   756	
   757	**Secondary diagnostics run per the ruling's fallback (for Skye):**
   758	- *Beam damage (ratio vs scan order):* interior area ratio 0.607 (Scan) vs
   759	  0.596 (Scan_0) with a wide-ratio diagnostic — no monotonic trend across
   760	  the two usable scans (Scan_1 is the documented uncorrected tab, excluded
   761	  by construction). No damage signal, but n=2.
   762	- *Identifiability:* on Scan the free-width wide-ratio diagnostic finds a
   763	  shallow ratio↔excess valley — (ratio 0.65, excess 0.073 eV, χ²ᵣ 1.282)
   764	  vs (0.607, 0, 1.309): the two knobs partially degenerate on this data.
   765	- *Residual localization (differential-charging check):* consistent on both
   766	  scans — a −/+ dipole in the doublet valley (deficit at +0.5 eV, surplus
   767	  at +1.1–1.2 eV from the 2p3/2) plus POSITIVE low-BE shoulders at
   768	  −2.1…−4.8 eV (2.6–3.4σ). The low-BE surplus is where a lower-charging
   769	  replica of the doublet would sit in an insulator-in-conductor composite —
   770	  consistent with (not proof of) differential charging. The proposal pass
   771	  does not fire (structure is distributed, not a discrete missing peak). No
   772	  grammar change (no uncited species invention).
   773	
   774	### #5 C 1s adventitious width — uniform 2.0 eV cap IMPLEMENTED
   775	

exec
/bin/zsh -lc "nl -ba docs/autofit/adjudication-decisions.md | sed -n '1,220p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	# Adjudication Decisions — PROGRESS.md discrepancies
     2	
     3	**Ruled by:** Skye (domain expert), 2026-07-03 (Fri evening), with Claude.
     4	**Purpose:** dispositions for the Monday session and for Fable to execute. Nothing here re-litigated.
     5	
     6	---
     7	
     8	## Data / tagging bugs — confirmed, lint-and-fix (no science)
     9	- **#1 `Zr 3d` RSF tags** (B4C-UCl₄, B 1s B–B/B–C) and **#2 `K 2p` RSF tags** (all 44 C 1s π→π\* satellites): **confirmed erroneous — no Zr or K in any sample.** Re-tag correctly and add the quantification lint (spec §8) to catch the pattern. **Do NOT alter the source data files.**
    10	- The **`N 1s` RSF tag on the ~397 eV U 4f satellite: LEAVE it** — that satellite genuinely sits in N 1s territory; the tag may be deliberate.
    11	
    12	## Reference-data exclusions — confirmed
    13	- **#3 4-GTA UCl₄-BN B 1s fits** (χ²ᵣ up to ~10⁵): erroneous one-offs (never a real fit) → **exclude as anchors.** Confirmed.
    14	- **#4 internally inconsistent C 1s tab** (`UCl4_on_graphite / C1s Scan_4`, `fittedY` 143 pts vs `be` 142): **exclude.** Confirmed.
    15	
    16	## Resolved by domain knowledge — no engine change
    17	- **#6 low-BE ~283.4 eV "Unknown":** a graphite **surface species, removed by vacuum-degassing the graphite immediately before use** — not intrinsic chemistry, not a U artifact. The proposal-pass flagging it is *correct behavior*; no grammar change. Origin recorded.
    18	- **#8 B 1s label swap** (B–C / B–B between the two expert sources): **manual-assignment mix-up** — positions identical, only the chemistry labels differ. The engine's **position-neutral roles (low/mid/oxide) are the correct handling.** Non-issue.
    19	- **U 4f satellite decoupling** (separation ~11.2 ≠ Δso 10.9; intensity ratio ~0.91 ≠ 0.75): **not concerning** — multifactorial and not straightforward, per Skye. No action; the **U2 (independent satellites) default stands.**
    20	
    21	## Engine changes to make (Fable / Monday)
    22	
    23	### Cl 2p 2:1-ratio rejection (#7) — resolved as a LINESHAPE fix, not chemistry
    24	- **Cause:** artifact of the **shared-FWHM** doublet constraint. The 2p₁/₂ is intrinsically broader than 2p₃/₂ (Coster-Kronig), so forcing equal widths mis-partitions area and pushes the apparent ratio above 0.5.
    25	- **ACTION:** allow the Cl 2p doublet components **independent widths** (2p₁/₂ ≥ 2p₃/₂). Expect the area ratio to return to ~0.5.
    26	- **Then:** Cl 2p Δso/ratio can **leave CONDITIONAL** status (spec §9).
    27	- **Ruled out:** hydrolysis / second chloride species — the UCl₄ is **strictly anhydrous** (glovebox synthesis). If independent widths do *not* resolve it, check **differential charging** (insulator-in-conductor composite) and **beam damage** (ratio vs. scan number) — secondary only.
    28	
    29	### Width convention (#5)
    30	- **Adventitious / contamination C 1s components → cap FWHM at ~2.0 eV** (literature-reasonable upper bound; instrument/pass-energy-dependent — a *cap*, not a target). Replace the engine's split **1.6 / 3.5 eV** contamination caps with a **uniform ~2.0 eV.**
    31	- **Satellites (π→π\*, etc.) → NO change.** Broad satellites are a known/expected occurrence. Fable already recalibrated the satellite FWHM cap to **(1.0, 5.5) eV** to match the 44 expert fits (span 1.9–5.0 eV). Keep.
    32	
    33	---
    34	
    35	## Net for Monday / Fable
    36	1. Re-tag the RSF mis-tags (#1/#2) + add the quantification lint; leave the U-satellite `N 1s` tag.
    37	2. Cl 2p: **independent doublet widths** → ratio ~0.5 → constants off CONDITIONAL.
    38	3. Adventitious-C FWHM cap → **~2.0 eV uniform**; satellite cap stays 5.5 eV.
    39	4. No engine change for #3, #4, #6, #8, or the U 4f satellite gaps.

exec
/bin/zsh -lc "find docs/autofit/test_data -maxdepth 1 -name '*.proj.zip' -print" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
docs/autofit/test_data/Cl2p_projfit_test.proj.zip
docs/autofit/test_data/B4C-UCl4.proj.zip
docs/autofit/test_data/UCl4_on_graphite.proj.zip
docs/autofit/test_data/4-GTA UCl4-BN.proj.zip
docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
docs/autofit/test_data/8-JT Graphite.proj.zip
docs/autofit/test_data/Project9_CasaXPS_newfit.proj.zip

exec
/bin/zsh -lc "zipgrep -n -i \"15\\.0\\|15\\.00\\|fwhm\\|FWHM\\|width\\|3\\.5\\|3\\.50\\|3\\.575\\|5\\.46\" docs/autofit/test_data/*.proj.zip" in /Users/skyefortier/xps-verify
 exited 2 in 0ms:
caution: filename not matched:  docs/autofit/test_data/4-GTA UCl4-BN.proj.zip
caution: filename not matched:  docs/autofit/test_data/8-JT Graphite.proj.zip
caution: filename not matched:  docs/autofit/test_data/B4C-UCl4.proj.zip
caution: filename not matched:  docs/autofit/test_data/Cl2p_projfit_test.proj.zip
caution: filename not matched:  docs/autofit/test_data/Project9_CasaXPS_newfit.proj.zip
caution: filename not matched:  docs/autofit/test_data/UCl4_on_graphite.proj.zip
/usr/bin/zipgrep: line 97: test: -eq: unary operator expected
/usr/bin/zipgrep: line 100: test: : integer expression expected

codex
The visible adjudication trail contains the old removed 3.5 eV lab-practice cap and the current 2.0 eV ruling, but I don’t see a 15.0 eV C 1s contamination-width value in the decision file. The previous `zipgrep` command tripped over the zip paths with spaces, so I’m rerunning that inspection one archive at a time via `find -exec`.
exec
/bin/zsh -lc "rg -n \"15\\.0|15\\.00|15 eV|fwhm.*15|FWHM.*15|3\\.5|5\\.46|differential|mixed\" docs/autofit/adjudication-decisions.md docs/autofit/PROGRESS.md docs/autofit/inventory/reference_fits_inventory.json docs/autofit/inventory -S" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
docs/autofit/adjudication-decisions.md:27:- **Ruled out:** hydrolysis / second chloride species — the UCl₄ is **strictly anhydrous** (glovebox synthesis). If independent widths do *not* resolve it, check **differential charging** (insulator-in-conductor composite) and **beam damage** (ratio vs. scan number) — secondary only.
docs/autofit/adjudication-decisions.md:30:- **Adventitious / contamination C 1s components → cap FWHM at ~2.0 eV** (literature-reasonable upper bound; instrument/pass-energy-dependent — a *cap*, not a target). Replace the engine's split **1.6 / 3.5 eV** contamination caps with a **uniform ~2.0 eV.**
docs/autofit/inventory/reference_fits_inventory.json:388:     "fwhm": 1.152,
docs/autofit/inventory/reference_fits_inventory.json:514:     "fwhm": 1.15,
docs/autofit/inventory/reference_fits_inventory.json:600:     "amp": 11315.0,
docs/autofit/inventory/reference_fits_inventory.json:1351:     "amp": 1013.5,
docs/autofit/inventory/reference_fits_inventory.json:1431:     "fwhm": 3.575,
docs/autofit/inventory/reference_fits_inventory.json:1440:     "fwhm": 3.575,
docs/autofit/inventory/reference_fits_inventory.json:2510:     "fwhm": 5.462,
docs/autofit/inventory/reference_fits_inventory.json:2744:     "fwhm": 3.527,
docs/autofit/inventory/reference_fits_inventory.json:3148:     "amp": 1803.5,
docs/autofit/inventory/reference_fits_inventory.json:3709:     "amp": 2853.5,
docs/autofit/inventory/reference_fits_inventory.json:4142:     "fwhm": 3.548,
docs/autofit/inventory/reference_fits_inventory.json:4507:     "fwhm": 3.595,
docs/autofit/inventory/reference_fits_inventory.json:4622:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:4634:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:5037:     "fwhm": 3.548,
docs/autofit/inventory/reference_fits_inventory.json:5402:     "fwhm": 3.595,
docs/autofit/inventory/reference_fits_inventory.json:5517:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:5529:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:5789:     "fwhm": 1.915,
docs/autofit/inventory/reference_fits_inventory.json:5799:     "fwhm": 3.524,
docs/autofit/PROGRESS.md:30:| Multivariate MCR method (stretch #5) | DONE (synthetic-validated) | ✅ 8 tests | `methods/multivariate_mcr.py`: PCA scree rank estimate (variance_target 0.995 UNVERIFIED, user-overridable, scree always reported) + MCR-ALS (row-wise NNLS alternation, deterministic SVD init, non-negativity on C and S) on a multi-spectrum matrix; `build_matrix` interpolation helper for mixed-grid repeat scans. HONESTY: `peaks=[]` by design (chemical states, not fitted peaks); rotational ambiguity stated in the payload; negative intensities rejected loudly. Synthetic: rank recovered, pure-spectra corr >0.98 (permutation-free), concentration corr >0.99, deterministic. Real-data validation on the repeat-scan matrices = follow-up. Codex checkpoint pending. |
docs/autofit/PROGRESS.md:31:| Sparse/MAP method (stretch #4) | DONE (synthetic-validated) | ✅ 9 tests | `methods/sparse_map.py`: L1 Gaussian-atom dictionary on grammar slot windows (data-grid centers × log FWHM ladder), non-negative coordinate descent, geometric λ path, debiased NNLS refit, BIC (engine convention) model-size selection; cluster merge scaled to the resolved feature's width. Honesty: `uncertainty_kind='unavailable_post_selection'` (no fabricated σ), asymmetric slots flagged not-expressible, UNVERIFIED tunables in payload, limitations stated (decision-matrix entry 4: STAM:Methods 2024 DOI 10.1080/27660400.2024.2373046 + Tibshirani 1996). Synthetic ground truth: exact peak-count recovery, centers ≤0.15 eV, debiased amplitudes ≤15%, deterministic (no RNG). NOT validated on real anchors (its regime is few-separated-peaks; the real regions are overlap-heavy — documented). Codex checkpoint pending. |
docs/autofit/PROGRESS.md:432:2. **Lab-practice contamination width range** (0.8,3.5) for AG/MG families
docs/autofit/PROGRESS.md:582:- **BLOCKER** validation JSONL still a mixed append/resume record (28 stale
docs/autofit/PROGRESS.md:747:| Cl0rw_relaxed_freewidth | 1793.5 / 1.631 | 1812.7 / 2.686 | ratio@max AND fwhm_excess@min |
docs/autofit/PROGRESS.md:765:- *Residual localization (differential-charging check):* consistent on both
docs/autofit/PROGRESS.md:770:  consistent with (not proof of) differential charging. The proposal pass
docs/autofit/PROGRESS.md:777:vs labeled-set 3.5 for AG/MG) with a uniform ~2.0 eV cap — "a cap, not a
docs/autofit/PROGRESS.md:862:   differential-charging residual evidence, and the Scan_8 parity
docs/autofit/PROGRESS.md:1280:mixed-sign pass-through match the documented policy. **The Tougaard
docs/autofit/PROGRESS.md:1358:with the exact expression the methods use) instead of a 400/500; mixed
docs/autofit/PROGRESS.md:1444:and API pins for the mixed deep+structural payload (structural_only
docs/autofit/PROGRESS.md:1460:mixed-API pin asserts actual derived record content (structure /
docs/autofit/PROGRESS.md:1966:  OWN cited ranges — C 1s satellite 5.5, U 4f mains 3.5 / sats 4.5, B 1s
docs/autofit/PROGRESS.md:2741:  the Cl 2p hypothesis-rejection + differential-charging residual
docs/autofit/PROGRESS.md:2979:fully; mixed curated+unassigned model branches per-slot; linked-slot
docs/autofit/PROGRESS.md:3149:stays non-empty (per `test_api_mixed_deep_plus_structural_runs_and_flags`)
docs/autofit/PROGRESS.md:3153:key at all, while every normal payload (success or failure, mixed or
docs/autofit/PROGRESS.md:3157:(an unrealistic fixture that let the new mixed-success test fail for
docs/autofit/inventory/sensitivity_sweeps.jsonl:77:{"anchor": "Cl2p_Scan_0", "constant": "CL2P_RATIO_RANGE_upper", "group": "cl2p", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "decisive_override", "peaks": {"main_cl2p12": {"amplitude": 3102.12, "center": 199.3491, "fwhm": 1.6261}, "main_cl2p32": {"amplitude": 5170.2, "center": 197.7948, "fwhm": 1.6261}}, "runtime_s": 0.3, "success": true, "winner": "Cl0r_doublet_relaxed+bfix", "winner_absent_slots": [], "winner_bic_star": 1752.6524977155975, "winner_boundary_hits": [], "winner_chi_r": 2.4174788049471307}, "value": 0.6}
docs/autofit/inventory/sensitivity_sweeps.jsonl:80:{"anchor": "Cl2p_Scan_0", "constant": "CL2P_SPLITTING_RANGE", "group": "cl2p", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "decisive_override", "peaks": {"main_cl2p12": {"amplitude": 2894.65, "center": 199.384, "fwhm": 1.6524}, "main_cl2p32": {"amplitude": 5263.0, "center": 197.819, "fwhm": 1.6524}}, "runtime_s": 0.3, "success": true, "winner": "Cl0r_doublet_relaxed+bfix", "winner_absent_slots": [], "winner_bic_star": 1802.0561540808153, "winner_boundary_hits": [], "winner_chi_r": 2.6581192426982265}, "value": [1.5, 1.7]}
docs/autofit/inventory/sensitivity_sweeps.jsonl:81:{"anchor": "C1s_Scan_8", "constant": "<default+proposal_on>", "extra_opts": {"enable_proposal_pass": true}, "group": "proposal", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 167.8, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": null}
docs/autofit/inventory/sensitivity_sweeps.jsonl:82:{"anchor": "C1s_Scan_8", "constant": "PROPOSAL_FLAG_RATIO", "extra_opts": {"enable_proposal_pass": true}, "group": "proposal", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 169.8, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": 3.0}
docs/autofit/inventory/sensitivity_sweeps.jsonl:83:{"anchor": "C1s_Scan_8", "constant": "PROPOSAL_FLAG_RATIO", "extra_opts": {"enable_proposal_pass": true}, "group": "proposal", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 179.5, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": 8.0}
docs/autofit/inventory/sensitivity_sweeps.jsonl:84:{"anchor": "C1s_Scan_8", "constant": "DSG_ALPHA_RANGE_GRAPHITIC_upper", "group": "c1s_alpha", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 119.3, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": 0.2}
docs/autofit/inventory/sensitivity_sweeps.jsonl:85:{"anchor": "C1s_Scan_8", "constant": "DSG_ALPHA_RANGE_GRAPHITIC_upper", "group": "c1s_alpha", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 135.0, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": 0.5}
docs/autofit/inventory/sensitivity_sweeps.jsonl:86:{"anchor": "C1s_Scan_8", "constant": "<default>", "group": "options", "result": {"ambiguous_pairs": [], "conditional": true, "conditional_reason": "no_clean_survivor", "peaks": {"contamination_C=O": {"amplitude": 1236.76, "center": 287.9542, "fwhm": 1.9478}, "contamination_CO": {"amplitude": 859.34, "center": 286.8, "fwhm": 0.9621}, "main_aliphatic": {"amplitude": 10638.98, "center": 284.7088, "fwhm": 2.5574}, "main_graphitic": {"amplitude": 64934.52, "center": 284.5088, "fwhm": 0.6743}, "satellite_pi": {"amplitude": 1296.85, "center": 290.8171, "fwhm": 2.7391}}, "runtime_s": 105.3, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O", "winner_absent_slots": [], "winner_bic_star": 1723.5295130712864, "winner_boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "winner_chi_r": 9.040578699307785}, "value": null}
docs/autofit/inventory/reference_fits_inventory.json:388:     "fwhm": 1.152,
docs/autofit/inventory/reference_fits_inventory.json:514:     "fwhm": 1.15,
docs/autofit/inventory/reference_fits_inventory.json:600:     "amp": 11315.0,
docs/autofit/inventory/reference_fits_inventory.json:1351:     "amp": 1013.5,
docs/autofit/inventory/reference_fits_inventory.json:1431:     "fwhm": 3.575,
docs/autofit/inventory/reference_fits_inventory.json:1440:     "fwhm": 3.575,
docs/autofit/inventory/reference_fits_inventory.json:2510:     "fwhm": 5.462,
docs/autofit/inventory/reference_fits_inventory.json:2744:     "fwhm": 3.527,
docs/autofit/inventory/reference_fits_inventory.json:3148:     "amp": 1803.5,
docs/autofit/inventory/reference_fits_inventory.json:3709:     "amp": 2853.5,
docs/autofit/inventory/reference_fits_inventory.json:4142:     "fwhm": 3.548,
docs/autofit/inventory/reference_fits_inventory.json:4507:     "fwhm": 3.595,
docs/autofit/inventory/reference_fits_inventory.json:4622:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:4634:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:5037:     "fwhm": 3.548,
docs/autofit/inventory/reference_fits_inventory.json:5402:     "fwhm": 3.595,
docs/autofit/inventory/reference_fits_inventory.json:5517:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:5529:     "caBeta": 3.561697521889929,
docs/autofit/inventory/reference_fits_inventory.json:5789:     "fwhm": 1.915,
docs/autofit/inventory/reference_fits_inventory.json:5799:     "fwhm": 3.524,
docs/autofit/inventory/cwt_calibration.jsonl:217:{"key": "h0:0.05:5000:sigmoid:16", "section": "h0", "step": 0.05, "level": 5000.0, "bg": "sigmoid", "seed": 16, "max_prom_z": 3.5625, "n_ge_gate": 0}
docs/autofit/inventory/cwt_calibration.jsonl:429:{"key": "h0:0.1:500:sigmoid:3", "section": "h0", "step": 0.1, "level": 500.0, "bg": "sigmoid", "seed": 3, "max_prom_z": 5.4671, "n_ge_gate": 0}
docs/autofit/inventory/cwt_calibration.jsonl:431:{"key": "h0:0.1:500:sigmoid:5", "section": "h0", "step": 0.1, "level": 500.0, "bg": "sigmoid", "seed": 5, "max_prom_z": 3.5386, "n_ge_gate": 0}
docs/autofit/inventory/cwt_calibration.jsonl:498:{"key": "h0:0.1:5000:slope:22", "section": "h0", "step": 0.1, "level": 5000.0, "bg": "slope", "seed": 22, "max_prom_z": 3.5887, "n_ge_gate": 0}
docs/autofit/inventory/cwt_calibration.jsonl:566:{"key": "h0:0.1:50000:slope:15", "section": "h0", "step": 0.1, "level": 50000.0, "bg": "slope", "seed": 15, "max_prom_z": 3.5616, "n_ge_gate": 0}
docs/autofit/inventory/cwt_calibration.jsonl:606:{"key": "sh:40000:0.5:0.15:0", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.5, "ratio": 0.15, "seed": 0, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:607:{"key": "sh:40000:0.5:0.15:1", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.5, "ratio": 0.15, "seed": 1, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:608:{"key": "sh:40000:0.5:0.15:2", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.5, "ratio": 0.15, "seed": 2, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:609:{"key": "sh:40000:0.5:0.15:3", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.5, "ratio": 0.15, "seed": 3, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:610:{"key": "sh:40000:0.5:0.15:4", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.5, "ratio": 0.15, "seed": 4, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:631:{"key": "sh:40000:0.7:0.15:0", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.7, "ratio": 0.15, "seed": 0, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:632:{"key": "sh:40000:0.7:0.15:1", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.7, "ratio": 0.15, "seed": 1, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:633:{"key": "sh:40000:0.7:0.15:2", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.7, "ratio": 0.15, "seed": 2, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:634:{"key": "sh:40000:0.7:0.15:3", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.7, "ratio": 0.15, "seed": 3, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:635:{"key": "sh:40000:0.7:0.15:4", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.7, "ratio": 0.15, "seed": 4, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:656:{"key": "sh:40000:0.9:0.15:0", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.9, "ratio": 0.15, "seed": 0, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:657:{"key": "sh:40000:0.9:0.15:1", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.9, "ratio": 0.15, "seed": 1, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:658:{"key": "sh:40000:0.9:0.15:2", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.9, "ratio": 0.15, "seed": 2, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:659:{"key": "sh:40000:0.9:0.15:3", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.9, "ratio": 0.15, "seed": 3, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:660:{"key": "sh:40000:0.9:0.15:4", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.9, "ratio": 0.15, "seed": 4, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:669:{"key": "sh:40000:0.9:0.3:3", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 0.9, "ratio": 0.3, "seed": 3, "composite_has_local_max": false, "detected": true, "prom_z": 29.1155}
docs/autofit/inventory/cwt_calibration.jsonl:681:{"key": "sh:40000:1.1:0.15:0", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.1, "ratio": 0.15, "seed": 0, "composite_has_local_max": false, "detected": true, "prom_z": 16.2763}
docs/autofit/inventory/cwt_calibration.jsonl:682:{"key": "sh:40000:1.1:0.15:1", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.1, "ratio": 0.15, "seed": 1, "composite_has_local_max": false, "detected": true, "prom_z": 18.3324}
docs/autofit/inventory/cwt_calibration.jsonl:683:{"key": "sh:40000:1.1:0.15:2", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.1, "ratio": 0.15, "seed": 2, "composite_has_local_max": false, "detected": true, "prom_z": 21.1057}
docs/autofit/inventory/cwt_calibration.jsonl:684:{"key": "sh:40000:1.1:0.15:3", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.1, "ratio": 0.15, "seed": 3, "composite_has_local_max": false, "detected": true, "prom_z": 20.1881}
docs/autofit/inventory/cwt_calibration.jsonl:685:{"key": "sh:40000:1.1:0.15:4", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.1, "ratio": 0.15, "seed": 4, "composite_has_local_max": false, "detected": true, "prom_z": 19.4729}
docs/autofit/inventory/cwt_calibration.jsonl:696:{"key": "sh:40000:1.1:0.5:0", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.1, "ratio": 0.5, "seed": 0, "composite_has_local_max": true, "detected": true, "prom_z": 156.6418}
docs/autofit/inventory/cwt_calibration.jsonl:697:{"key": "sh:40000:1.1:0.5:1", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.1, "ratio": 0.5, "seed": 1, "composite_has_local_max": true, "detected": true, "prom_z": 158.0813}
docs/autofit/inventory/cwt_calibration.jsonl:698:{"key": "sh:40000:1.1:0.5:2", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.1, "ratio": 0.5, "seed": 2, "composite_has_local_max": true, "detected": true, "prom_z": 158.4114}
docs/autofit/inventory/cwt_calibration.jsonl:699:{"key": "sh:40000:1.1:0.5:3", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.1, "ratio": 0.5, "seed": 3, "composite_has_local_max": true, "detected": true, "prom_z": 157.6683}
docs/autofit/inventory/cwt_calibration.jsonl:700:{"key": "sh:40000:1.1:0.5:4", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.1, "ratio": 0.5, "seed": 4, "composite_has_local_max": true, "detected": true, "prom_z": 156.451}
docs/autofit/inventory/cwt_calibration.jsonl:706:{"key": "sh:40000:1.3:0.15:0", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.3, "ratio": 0.15, "seed": 0, "composite_has_local_max": false, "detected": true, "prom_z": 59.1385}
docs/autofit/inventory/cwt_calibration.jsonl:707:{"key": "sh:40000:1.3:0.15:1", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.3, "ratio": 0.15, "seed": 1, "composite_has_local_max": false, "detected": true, "prom_z": 58.3723}
docs/autofit/inventory/cwt_calibration.jsonl:708:{"key": "sh:40000:1.3:0.15:2", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.3, "ratio": 0.15, "seed": 2, "composite_has_local_max": false, "detected": true, "prom_z": 61.0447}
docs/autofit/inventory/cwt_calibration.jsonl:709:{"key": "sh:40000:1.3:0.15:3", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.3, "ratio": 0.15, "seed": 3, "composite_has_local_max": false, "detected": true, "prom_z": 60.5103}
docs/autofit/inventory/cwt_calibration.jsonl:710:{"key": "sh:40000:1.3:0.15:4", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.3, "ratio": 0.15, "seed": 4, "composite_has_local_max": false, "detected": true, "prom_z": 56.1285}
docs/autofit/inventory/cwt_calibration.jsonl:717:{"key": "sh:40000:1.3:0.3:1", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.3, "ratio": 0.3, "seed": 1, "composite_has_local_max": true, "detected": true, "prom_z": 158.9245}
docs/autofit/inventory/cwt_calibration.jsonl:718:{"key": "sh:40000:1.3:0.3:2", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.3, "ratio": 0.3, "seed": 2, "composite_has_local_max": true, "detected": true, "prom_z": 160.1577}
docs/autofit/inventory/cwt_calibration.jsonl:720:{"key": "sh:40000:1.3:0.3:4", "section": "shoulder", "height": 40000.0, "sep_xfwhm": 1.3, "ratio": 0.3, "seed": 4, "composite_has_local_max": true, "detected": true, "prom_z": 157.3355}
docs/autofit/inventory/cwt_calibration.jsonl:731:{"key": "sh:2000:0.5:0.15:0", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.5, "ratio": 0.15, "seed": 0, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:732:{"key": "sh:2000:0.5:0.15:1", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.5, "ratio": 0.15, "seed": 1, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:733:{"key": "sh:2000:0.5:0.15:2", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.5, "ratio": 0.15, "seed": 2, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:734:{"key": "sh:2000:0.5:0.15:3", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.5, "ratio": 0.15, "seed": 3, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:735:{"key": "sh:2000:0.5:0.15:4", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.5, "ratio": 0.15, "seed": 4, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:756:{"key": "sh:2000:0.7:0.15:0", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.7, "ratio": 0.15, "seed": 0, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:757:{"key": "sh:2000:0.7:0.15:1", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.7, "ratio": 0.15, "seed": 1, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:758:{"key": "sh:2000:0.7:0.15:2", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.7, "ratio": 0.15, "seed": 2, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:759:{"key": "sh:2000:0.7:0.15:3", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.7, "ratio": 0.15, "seed": 3, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:760:{"key": "sh:2000:0.7:0.15:4", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.7, "ratio": 0.15, "seed": 4, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:781:{"key": "sh:2000:0.9:0.15:0", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.9, "ratio": 0.15, "seed": 0, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:782:{"key": "sh:2000:0.9:0.15:1", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.9, "ratio": 0.15, "seed": 1, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:783:{"key": "sh:2000:0.9:0.15:2", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.9, "ratio": 0.15, "seed": 2, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:784:{"key": "sh:2000:0.9:0.15:3", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.9, "ratio": 0.15, "seed": 3, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:785:{"key": "sh:2000:0.9:0.15:4", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 0.9, "ratio": 0.15, "seed": 4, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:806:{"key": "sh:2000:1.1:0.15:0", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.1, "ratio": 0.15, "seed": 0, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:807:{"key": "sh:2000:1.1:0.15:1", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.1, "ratio": 0.15, "seed": 1, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:808:{"key": "sh:2000:1.1:0.15:2", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.1, "ratio": 0.15, "seed": 2, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:809:{"key": "sh:2000:1.1:0.15:3", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.1, "ratio": 0.15, "seed": 3, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:810:{"key": "sh:2000:1.1:0.15:4", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.1, "ratio": 0.15, "seed": 4, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:817:{"key": "sh:2000:1.1:0.3:1", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.1, "ratio": 0.3, "seed": 1, "composite_has_local_max": false, "detected": true, "prom_z": 15.9893}
docs/autofit/inventory/cwt_calibration.jsonl:831:{"key": "sh:2000:1.3:0.15:0", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.3, "ratio": 0.15, "seed": 0, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:832:{"key": "sh:2000:1.3:0.15:1", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.3, "ratio": 0.15, "seed": 1, "composite_has_local_max": false, "detected": true, "prom_z": 8.448}
docs/autofit/inventory/cwt_calibration.jsonl:833:{"key": "sh:2000:1.3:0.15:2", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.3, "ratio": 0.15, "seed": 2, "composite_has_local_max": false, "detected": true, "prom_z": 10.6812}
docs/autofit/inventory/cwt_calibration.jsonl:834:{"key": "sh:2000:1.3:0.15:3", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.3, "ratio": 0.15, "seed": 3, "composite_has_local_max": false, "detected": true, "prom_z": 10.1691}
docs/autofit/inventory/cwt_calibration.jsonl:835:{"key": "sh:2000:1.3:0.15:4", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.3, "ratio": 0.15, "seed": 4, "composite_has_local_max": false, "detected": false, "prom_z": null}
docs/autofit/inventory/cwt_calibration.jsonl:837:{"key": "sh:2000:1.3:0.2:1", "section": "shoulder", "height": 2000.0, "sep_xfwhm": 1.3, "ratio": 0.2, "seed": 1, "composite_has_local_max": false, "detected": true, "prom_z": 13.1152}
docs/autofit/inventory/replicate_noise_survey.json:28:    "negative_intercept_clamped: a=-3.54e+04 -> 0",
docs/autofit/inventory/replicate_noise_survey.json:402:    "negative_intercept_clamped: a=-3.54e+04 -> 0",
docs/autofit/inventory/bayesian_u4f_tuned_run.jsonl:1:{"anchor": "U4f_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 3274.113862379425, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.0932443063850315, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.0932443063850315, "min_effective_sample_size": 19.57108508725822, "n_components": 2, "n_posterior_samples": 2000, "name": "U0_mains", "posterior_weight": 2.0510286183062296e-218, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 573.6224509118443, "swap_acceptance": 0.583}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2826.7133119480504, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.6924659012925076, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.6924659012925076, "min_effective_sample_size": 15.011315092016366, "n_components": 4, "n_posterior_samples": 2000, "name": "U1_mains_satpair", "posterior_weight": 4.1263111460321444e-24, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 147.60795818246072, "swap_acceptance": 0.5014166666666666}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2801.11228799011, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.6678119437058285, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.6678119437058285, "min_effective_sample_size": 6.564437533639988, "n_components": 4, "n_posterior_samples": 2000, "name": "U1b_mains_satpair_freesep", "posterior_weight": 5.419327649621575e-13, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 136.5297064232104, "swap_acceptance": 0.49341666666666667}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2772.8686535390593, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 2.5158935620684133, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 2.5158935620684133, "min_effective_sample_size": 10.572444173558178, "n_components": 4, "n_posterior_samples": 2000, "name": "U2_mains_satfree", "posterior_weight": 0.999999999999458, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 123.76980566063898, "swap_acceptance": 0.49283333333333335}], "confidence": {"main_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 10.857960634534383, "ci_level": 0.68, "ci_low": 10.848031595158869, "ess": 74.10023929838128, "median": 10.85284414030929}, "ratio": {"ci_high": 0.6621946320074098, "ci_level": 0.68, "ci_low": 0.6573089625421653, "ess": 66.47974103792622, "median": 0.6598473953430019}}}}, "main_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 10.6 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"alpha": {"ci_high": 1.2377839105188733, "ci_level": 0.68, "ci_low": 1.1914786167002223, "ess": 18.545654282176088, "median": 1.207991578682303}, "amplitude": {"ci_high": 16128.390042255734, "ci_level": 0.68, "ci_low": 16050.667304065419, "ess": 10.572444173558178, "median": 16068.103592594733}, "beta": {"ci_high": 2.88725703769715, "ci_level": 0.68, "ci_low": 2.7386461819853074, "ess": 16.4062999417237, "median": 2.808763113800193}, "center": {"ci_high": 380.63292194454647, "ci_level": 0.68, "ci_low": 380.6234404645645, "ess": 27.81082842204054, "median": 380.62853648176514}, "fwhm": {"ci_high": 2.7173788725244896, "ci_level": 0.68, "ci_low": 2.598695462981316, "ess": 16.247127412703442, "median": 2.6539219203174924}, "m": {"ci_high": 6.859605882824331, "ci_level": 0.68, "ci_low": 5.7081801731179125, "ess": 14.11754650965665, "median": 6.381701994990381}}}}, "satellite_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2268.529577525702, "ci_level": 0.68, "ci_low": 2195.4939904315124, "ess": 75.41687892686828, "median": 2232.1972804245197}, "fwhm": {"ci_high": 2.5747560532934526, "ci_level": 0.68, "ci_low": 2.4729773313430443, "ess": 80.29533062885349, "median": 2.5241901879102784}, "gl_ratio": {"ci_high": 0.06457049982095478, "ci_level": 0.68, "ci_low": 0.0062847376945130845, "ess": 54.479102349422384, "median": 0.022923447360258774}, "offset": {"ci_high": 6.428304617579634, "ci_level": 0.68, "ci_low": 6.388760815240822, "ess": 273.43147855721935, "median": 6.409352959533626}}}}, "satellite_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 20.9 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2446.782916531736, "ci_level": 0.68, "ci_low": 2334.7252986024814, "ess": 27.315611807356188, "median": 2420.757152328541}, "fwhm": {"ci_high": 2.590673707643128, "ci_level": 0.68, "ci_low": 2.448327014125724, "ess": 32.50450267403081, "median": 2.517918287691745}, "gl_ratio": {"ci_high": 0.8704291822613868, "ci_level": 0.68, "ci_low": 0.6106182031892832, "ess": 20.94925624138724, "median": 0.7449538956814956}, "offset": {"ci_high": 6.083009691406851, "ci_level": 0.68, "ci_low": 6.041074004303911, "ess": 134.5219354156989, "median": 6.061859789293894}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 16, "n_sweeps": 4000}, "expert": {"chi_reduced": 1.7129708462685973, "peaks": [{"amplitude": 16166.479492182621, "center": 380.6179633862216, "fwhm": 2.737096332065471, "name": "U 4f7/2", "shape": "LACX"}, {"amplitude": 10508.211669918705, "center": 391.5179633862216, "fwhm": 2.737096332065471, "name": "U 4f5/2", "shape": "LACX"}, {"amplitude": 2214.057182779663, "center": 397.8977471164976, "fwhm": 2.556902102730025, "name": "Satellite 2", "shape": "Voigt"}, {"amplitude": 2436.210453422618, "center": 386.6877864274504, "fwhm": 2.512044323701672, "name": "Satellite 1", "shape": "Voigt"}]}, "method": "bayesian_exchange_mc", "peaks": [{"alpha": 1.207991578682303, "amplitude": 16068.103592594733, "beta": 2.808763113800193, "center": 380.62853648176514, "fwhm": 2.6539219203174924, "m": 6.381701994990381, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f72", "shape": "la_casaxps"}, {"alpha": 1.207991578682303, "amplitude": 10602.496303675165, "beta": 2.808763113800193, "center": 391.4813806220744, "fwhm": 2.6539219203174924, "m": 6.381701994990381, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f52", "shape": "la_casaxps"}, {"amplitude": 2420.757152328541, "center": 386.69039627105906, "fwhm": 2.517918287691745, "gl_ratio": 0.7449538956814956, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f72", "shape": "pseudo_voigt_gl"}, {"amplitude": 2232.1972804245197, "center": 397.89073358160806, "fwhm": 2.5241901879102784, "gl_ratio": 0.022923447360258774, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f52", "shape": "pseudo_voigt_gl"}], "runtime_s": 1088.1, "seed": 0, "selection_warning": null, "sigma_hat": 123.76980566063898, "success": true, "winner": "U2_mains_satfree"}
docs/autofit/inventory/bayesian_u4f_tuned_run.jsonl:2:{"anchor": "U4f_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2800.601460195511, "free_energy_is_replicate_mean": true, "free_energy_mc_error": 1.6678119437058285, "free_energy_replicate_spread": 0.5108277945985265, "free_energy_replicates": [2801.11228799011, 2800.090632400913], "free_energy_split_half_error": 1.6678119437058285, "min_effective_sample_size": 6.564437533639988, "n_components": 4, "n_posterior_samples": 2000, "name": "U1b_mains_satpair_freesep", "posterior_weight": 1.076619850178737e-12, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 136.5297064232104, "swap_acceptance": 0.49341666666666667}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2773.0442654443987, "free_energy_is_replicate_mean": true, "free_energy_mc_error": 2.5158935620684133, "free_energy_replicate_spread": 0.17561190533933768, "free_energy_replicates": [2772.8686535390593, 2773.219877349738], "free_energy_split_half_error": 2.5158935620684133, "min_effective_sample_size": 10.572444173558178, "n_components": 4, "n_posterior_samples": 2000, "name": "U2_mains_satfree", "posterior_weight": 0.9999999999989233, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 123.76980566063898, "swap_acceptance": 0.49283333333333335}], "confidence": {"main_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 10.857960634534383, "ci_level": 0.68, "ci_low": 10.848031595158869, "ess": 74.10023929838128, "median": 10.85284414030929}, "ratio": {"ci_high": 0.6621946320074098, "ci_level": 0.68, "ci_low": 0.6573089625421653, "ess": 66.47974103792622, "median": 0.6598473953430019}}}}, "main_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 10.6 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"alpha": {"ci_high": 1.2377839105188733, "ci_level": 0.68, "ci_low": 1.1914786167002223, "ess": 18.545654282176088, "median": 1.207991578682303}, "amplitude": {"ci_high": 16128.390042255734, "ci_level": 0.68, "ci_low": 16050.667304065419, "ess": 10.572444173558178, "median": 16068.103592594733}, "beta": {"ci_high": 2.88725703769715, "ci_level": 0.68, "ci_low": 2.7386461819853074, "ess": 16.4062999417237, "median": 2.808763113800193}, "center": {"ci_high": 380.63292194454647, "ci_level": 0.68, "ci_low": 380.6234404645645, "ess": 27.81082842204054, "median": 380.62853648176514}, "fwhm": {"ci_high": 2.7173788725244896, "ci_level": 0.68, "ci_low": 2.598695462981316, "ess": 16.247127412703442, "median": 2.6539219203174924}, "m": {"ci_high": 6.859605882824331, "ci_level": 0.68, "ci_low": 5.7081801731179125, "ess": 14.11754650965665, "median": 6.381701994990381}}}}, "satellite_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2268.529577525702, "ci_level": 0.68, "ci_low": 2195.4939904315124, "ess": 75.41687892686828, "median": 2232.1972804245197}, "fwhm": {"ci_high": 2.5747560532934526, "ci_level": 0.68, "ci_low": 2.4729773313430443, "ess": 80.29533062885349, "median": 2.5241901879102784}, "gl_ratio": {"ci_high": 0.06457049982095478, "ci_level": 0.68, "ci_low": 0.0062847376945130845, "ess": 54.479102349422384, "median": 0.022923447360258774}, "offset": {"ci_high": 6.428304617579634, "ci_level": 0.68, "ci_low": 6.388760815240822, "ess": 273.43147855721935, "median": 6.409352959533626}}}}, "satellite_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 20.9 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2446.782916531736, "ci_level": 0.68, "ci_low": 2334.7252986024814, "ess": 27.315611807356188, "median": 2420.757152328541}, "fwhm": {"ci_high": 2.590673707643128, "ci_level": 0.68, "ci_low": 2.448327014125724, "ess": 32.50450267403081, "median": 2.517918287691745}, "gl_ratio": {"ci_high": 0.8704291822613868, "ci_level": 0.68, "ci_low": 0.6106182031892832, "ess": 20.94925624138724, "median": 0.7449538956814956}, "offset": {"ci_high": 6.083009691406851, "ci_level": 0.68, "ci_low": 6.041074004303911, "ess": 134.5219354156989, "median": 6.061859789293894}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "candidate_filter": ["U1b_mains_satpair_freesep", "U2_mains_satfree"], "exchange_every": 5, "n_replicas": 16, "n_sweeps": 4000, "seed_replicates": 2}, "expert": {"chi_reduced": 1.7129708462685973, "peaks": [{"amplitude": 16166.479492182621, "center": 380.6179633862216, "fwhm": 2.737096332065471, "name": "U 4f7/2", "shape": "LACX"}, {"amplitude": 10508.211669918705, "center": 391.5179633862216, "fwhm": 2.737096332065471, "name": "U 4f5/2", "shape": "LACX"}, {"amplitude": 2214.057182779663, "center": 397.8977471164976, "fwhm": 2.556902102730025, "name": "Satellite 2", "shape": "Voigt"}, {"amplitude": 2436.210453422618, "center": 386.6877864274504, "fwhm": 2.512044323701672, "name": "Satellite 1", "shape": "Voigt"}]}, "method": "bayesian_exchange_mc", "peaks": [{"alpha": 1.207991578682303, "amplitude": 16068.103592594733, "beta": 2.808763113800193, "center": 380.62853648176514, "fwhm": 2.6539219203174924, "m": 6.381701994990381, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f72", "shape": "la_casaxps"}, {"alpha": 1.207991578682303, "amplitude": 10602.496303675165, "beta": 2.808763113800193, "center": 391.4813806220744, "fwhm": 2.6539219203174924, "m": 6.381701994990381, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f52", "shape": "la_casaxps"}, {"amplitude": 2420.757152328541, "center": 386.69039627105906, "fwhm": 2.517918287691745, "gl_ratio": 0.7449538956814956, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f72", "shape": "pseudo_voigt_gl"}, {"amplitude": 2232.1972804245197, "center": 397.89073358160806, "fwhm": 2.5241901879102784, "gl_ratio": 0.022923447360258774, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f52", "shape": "pseudo_voigt_gl"}], "runtime_s": 1239.3, "seed": 0, "selection_warning": null, "sigma_hat": 123.76980566063898, "success": true, "winner": "U2_mains_satfree"}
docs/autofit/inventory/stress_battery_runs.jsonl:6:{"case": "overlap_sep0.7_h9000", "chi_reduced": 1.5809299088896689, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0184, "d_fwhm_ev": 0.0082, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": -0.04, "d_fwhm_ev": 0.0615, "matched_role": "2", "true_center": 198.04}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:7:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3153.7565429787596, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 5.7809674050649695, "survived": true}, {"bic_star": 3118.2849367275676, "boundary_hits": ["main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 5.080109214935805, "survived": false}, {"bic_star": 2443.565329460894, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.75, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.4571079252480608, "survived": false}, {"bic_star": 3112.5811161689353, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2+bfix", "orphan_peaks": false, "reduced_chi_sq": 5.0627708242827145, "survived": true}], "case": "overlap_sep0.7_h9000", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2443.565329460894, "delta_bic_vs_winner": 669.0157867080411, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "name": "P3"}, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 16.52, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.3286, "d_fwhm_ev": 0.4075, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.3681, "d_fwhm_ev": 1.3, "matched_role": "main_b", "true_center": 198.04}], "truth_n": 2, "winner": "P2+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 5.0627708242827145, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:8:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3153.756440767745, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 5.780967405052238, "survived": true}, {"bic_star": 2373.026332173199, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 0.9166666666666666, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.5809299084372963, "survived": true}, {"bic_star": 2444.11377063316, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.4166666666666667, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.4571074609826968, "survived": false}], "case": "overlap_sep0.7_h9000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 23.06, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0184, "d_fwhm_ev": 0.0082, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.04, "d_fwhm_ev": 0.0615, "matched_role": "main_b", "true_center": 198.04}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.5809299084372963, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:10:{"candidates": [{"free_energy": 1141.800413299352, "free_energy_mc_error": 1.9953657305029537, "free_energy_split_half_error": 1.9953657305029537, "min_effective_sample_size": 5.338290164277106, "name": "P1", "posterior_weight": 3.595354431773926e-61, "posterior_weight_reliable": true, "rank": 3}, {"free_energy": 1002.6223652032959, "free_energy_mc_error": 2.1753943273294567, "free_energy_split_half_error": 2.1753943273294567, "min_effective_sample_size": 3.6994767039440055, "name": "P2", "posterior_weight": 0.9999999999339444, "posterior_weight_reliable": true, "rank": 1}, {"free_energy": 1026.062888495648, "free_energy_mc_error": 8.073111284622996, "free_energy_split_half_error": 8.073111284622996, "min_effective_sample_size": 5.877342686762297, "name": "P3", "posterior_weight": 6.60556668404888e-11, "posterior_weight_reliable": true, "rank": 2}], "case": "overlap_sep0.7_h9000", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "recover", "method": "bayesian_exchange_mc", "n_emitted_components": 2, "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 10.52, "seed_offset": 0, "selection_warning": null, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0003, "d_fwhm_ev": 0.0067, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0041, "d_fwhm_ev": -0.0002, "matched_role": "main_b", "true_center": 198.04}], "truth_n": 2, "winner": "P2", "winner_is_true": true}
docs/autofit/inventory/stress_battery_runs.jsonl:16:{"case": "overlap_sep0.4_h900", "chi_reduced": 1.3658889942098313, "config": {"background_method": "linear"}, "expectation": "ambiguous", "method": "least_squares", "notes": "separation 0.4\u00d7FWHM, heights 900/630", "regime": "heavy_overlap", "runtime_s": 0.02, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1657, "d_fwhm_ev": 0.1563, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.2259, "d_fwhm_ev": 0.1642, "matched_role": "2", "true_center": 197.67999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:20:{"candidates": [{"free_energy": 920.7742514192767, "free_energy_mc_error": 0.5246428357232844, "free_energy_split_half_error": 0.5246428357232844, "min_effective_sample_size": 27.071643772415026, "name": "P1", "posterior_weight": 0.9362378661594928, "posterior_weight_reliable": false, "rank": 1}, {"free_energy": 923.5071197457307, "free_energy_mc_error": 3.1363802582213225, "free_energy_split_half_error": 3.1363802582213225, "min_effective_sample_size": 4.459313814475639, "name": "P2", "posterior_weight": 0.06088587731601117, "posterior_weight_reliable": false, "rank": 2}, {"free_energy": 926.5596313632122, "free_energy_mc_error": 4.510421845794781, "free_energy_split_half_error": 4.510421845794781, "min_effective_sample_size": 4.466382055227123, "name": "P3", "posterior_weight": 0.0028762565244962015, "posterior_weight_reliable": false, "rank": 3}], "case": "overlap_sep0.4_h900", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "ambiguous", "method": "bayesian_exchange_mc", "n_emitted_components": 1, "notes": "separation 0.4\u00d7FWHM, heights 900/630", "regime": "heavy_overlap", "runtime_s": 10.5, "seed_offset": 0, "selection_warning": "UNRESOLVED model selection: top-2 \u0394F=2.7 is within 2\u00d7(MC errors 0.5+3.1; split-half (lower bound)) \u2014 increase n_sweeps/n_replicas or seed_replicates before trusting the winner", "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.2003, "d_fwhm_ev": 0.1891, "matched_role": "main_a", "true_center": 197.2}, null], "truth_n": 2, "winner": "P1", "winner_is_true": false}
docs/autofit/inventory/stress_battery_runs.jsonl:21:{"case": "weak_minor_0.03_h90000", "chi_reduced": 14.06952772490919, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 0.02, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.004, "d_fwhm_ev": 0.0114, "matched_role": "1", "true_center": 197.0}, {"d_center_ev": -0.0523, "d_fwhm_ev": 0.154, "matched_role": "2", "true_center": 198.8}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:22:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3925.455110822625, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 90.4802362095952, "survived": true}, {"bic_star": 3299.65035074613, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 14.069527648179847, "survived": true}, {"bic_star": 3332.178961848933, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.25, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 14.204331885607486, "survived": false}], "case": "weak_minor_0.03_h90000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 1.53, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.004, "d_fwhm_ev": 0.0114, "matched_role": "main_a", "true_center": 197.0}, {"d_center_ev": -0.0523, "d_fwhm_ev": 0.1539, "matched_role": "main_b", "true_center": 198.8}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 14.069527648179847, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:23:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3925.4525458362814, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 90.48023620943462, "survived": true}, {"bic_star": 3299.6471607179587, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 14.069527634570445, "survived": true}, {"bic_star": 3332.149559856226, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.25, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 14.204328337416305, "survived": false}], "case": "weak_minor_0.03_h90000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 3.59, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.004, "d_fwhm_ev": 0.0114, "matched_role": "main_a", "true_center": 197.0}, {"d_center_ev": -0.0523, "d_fwhm_ev": 0.1539, "matched_role": "main_b", "true_center": 198.8}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 14.069527634570445, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:25:{"candidates": [{"free_energy": 1553.4947306054514, "free_energy_mc_error": 2.859961886769838, "free_energy_split_half_error": 2.859961886769838, "min_effective_sample_size": 4.57119058146634, "name": "P1", "posterior_weight": 1.3621071805739707e-109, "posterior_weight_reliable": false, "rank": 3}, {"free_energy": 1302.8219883771847, "free_energy_mc_error": 1.3633267718126945, "free_energy_split_half_error": 1.3633267718126945, "min_effective_sample_size": 3.210200708634454, "name": "P2", "posterior_weight": 0.999999990066741, "posterior_weight_reliable": false, "rank": 1}, {"free_energy": 1321.249365584245, "free_energy_mc_error": 14.083383273103436, "free_energy_split_half_error": 14.083383273103436, "min_effective_sample_size": 2.888035483466519, "name": "P3", "posterior_weight": 9.933258983700135e-09, "posterior_weight_reliable": false, "rank": 2}], "case": "weak_minor_0.03_h90000", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "recover", "method": "bayesian_exchange_mc", "n_emitted_components": 2, "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 10.75, "seed_offset": 0, "selection_warning": "UNRESOLVED model selection: top-2 \u0394F=18.4 is within 2\u00d7(MC errors 1.4+14.1; split-half (lower bound)) \u2014 increase n_sweeps/n_replicas or seed_replicates before trusting the winner", "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0093, "d_fwhm_ev": 0.0057, "matched_role": "main_a", "true_center": 197.0}, {"d_center_ev": -0.1154, "d_fwhm_ev": 0.2394, "matched_role": "main_b", "true_center": 198.8}], "truth_n": 2, "winner": "P2", "winner_is_true": true}
docs/autofit/inventory/stress_battery_runs.jsonl:26:{"case": "weak_minor_0.03_h2000", "chi_reduced": 2.3608518137434937, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 0.09, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0068, "d_fwhm_ev": 0.0266, "matched_role": "1", "true_center": 197.0}, {"d_center_ev": -0.1594, "d_fwhm_ev": -0.2592, "matched_role": "2", "true_center": 198.8}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:27:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 2102.557719007429, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 2.7993481757742953, "survived": true}, {"bic_star": 2078.7286227120576, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 2.360851619136528, "survived": true}, {"bic_star": 2101.5420595462733, "boundary_hits": [], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.0, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 2.3936412299500076, "survived": false}], "case": "weak_minor_0.03_h2000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 2.79, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0068, "d_fwhm_ev": 0.0266, "matched_role": "main_a", "true_center": 197.0}, {"d_center_ev": -0.1594, "d_fwhm_ev": -0.2593, "matched_role": "main_b", "true_center": 198.8}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 2.360851619136528, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:28:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 2102.557719007429, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 2.7993481757742953, "survived": true}, {"bic_star": 2078.7286227120576, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 0.9166666666666666, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 2.360851619136528, "survived": true}, {"bic_star": 2101.5420595462733, "boundary_hits": [], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.0, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 2.3936412299500076, "survived": false}], "case": "weak_minor_0.03_h2000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 4.78, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0068, "d_fwhm_ev": 0.0266, "matched_role": "main_a", "true_center": 197.0}, {"d_center_ev": -0.1594, "d_fwhm_ev": -0.2593, "matched_role": "main_b", "true_center": 198.8}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 2.360851619136528, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:30:{"candidates": [{"free_energy": 1029.178477685529, "free_energy_mc_error": 4.062204706042621, "free_energy_split_half_error": 4.062204706042621, "min_effective_sample_size": 3.767194698678288, "name": "P1", "posterior_weight": 1.6884782198725294e-08, "posterior_weight_reliable": false, "rank": 3}, {"free_energy": 1011.28162640352, "free_energy_mc_error": 2.7576240812794595, "free_energy_split_half_error": 2.7576240812794595, "min_effective_sample_size": 4.635829870215257, "name": "P2", "posterior_weight": 0.9999981997202898, "posterior_weight_reliable": false, "rank": 1}, {"free_energy": 1024.5186163505064, "free_energy_mc_error": 8.712822275283372, "free_energy_split_half_error": 8.712822275283372, "min_effective_sample_size": 4.771130829524421, "name": "P3", "posterior_weight": 1.7833949279783068e-06, "posterior_weight_reliable": false, "rank": 2}], "case": "weak_minor_0.03_h2000", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "recover", "method": "bayesian_exchange_mc", "n_emitted_components": 2, "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 10.51, "seed_offset": 0, "selection_warning": "UNRESOLVED model selection: top-2 \u0394F=13.2 is within 2\u00d7(MC errors 2.8+8.7; split-half (lower bound)) \u2014 increase n_sweeps/n_replicas or seed_replicates before trusting the winner", "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0123, "d_fwhm_ev": 0.0265, "matched_role": "main_a", "true_center": 197.0}, {"d_center_ev": -0.2155, "d_fwhm_ev": -0.22, "matched_role": "main_b", "true_center": 198.8}], "truth_n": 2, "winner": "P2", "winner_is_true": true}
docs/autofit/inventory/stress_battery_runs.jsonl:40:{"candidates": [{"free_energy": 1756.5069574278016, "free_energy_mc_error": 1.4214486231550154, "free_energy_split_half_error": 1.4214486231550154, "min_effective_sample_size": 13.85806958636207, "name": "P1", "posterior_weight": 0.0, "posterior_weight_reliable": true, "rank": 3}, {"free_energy": 929.5115600365787, "free_energy_mc_error": 1.9583859250482192, "free_energy_split_half_error": 1.9583859250482192, "min_effective_sample_size": 2.7960039955570357, "name": "P2", "posterior_weight": 0.999999999999887, "posterior_weight_reliable": true, "rank": 1}, {"free_energy": 959.3221983742337, "free_energy_mc_error": 11.501787779683127, "free_energy_split_half_error": 11.501787779683127, "min_effective_sample_size": 2.61540653853434, "name": "P3_decoy", "posterior_weight": 1.1308480876480209e-13, "posterior_weight_reliable": true, "rank": 2}], "case": "overspecified_inroi_decoy", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "prune", "method": "bayesian_exchange_mc", "n_emitted_components": 2, "notes": "decoy 'shoulder' window between the true peaks (real tail intensity present) \u2014 must be pruned, not populated", "regime": "overspecified", "runtime_s": 11.16, "seed_offset": 0, "selection_warning": null, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0014, "d_fwhm_ev": 0.0022, "matched_role": "main_a", "true_center": 196.8}, {"d_center_ev": 0.0002, "d_fwhm_ev": 0.0156, "matched_role": "main_b", "true_center": 199.4}], "truth_n": 2, "winner": "P2", "winner_is_true": true}
docs/autofit/inventory/stress_battery_runs.jsonl:41:{"case": "charging_no_replica_candidate", "chi_reduced": 2.11933018079081, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.0397, "d_fwhm_ev": 0.0591, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": -0.1661, "d_fwhm_ev": -0.1165, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:42:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3061.2254608577414, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.962869989958203, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.03, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1451, "d_fwhm_ev": 0.2452, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 6.962869989958203, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:43:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3061.225259358099, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.96286998990333, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.07, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1451, "d_fwhm_ev": 0.2452, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 6.96286998990333, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:44:{"case": "charging_no_replica_candidate", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 3.54, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1405, "d_fwhm_ev": 0.1802, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:45:{"candidates": [{"free_energy": 1164.4119461114783, "free_energy_mc_error": 3.3940131980712067, "free_energy_split_half_error": 3.3940131980712067, "min_effective_sample_size": 3.485445192889438, "name": "single_main", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1}], "case": "charging_no_replica_candidate", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "honesty", "method": "bayesian_exchange_mc", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 1.02, "seed_offset": 0, "selection_warning": null, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1473, "d_fwhm_ev": 0.2454, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_is_true": false}
docs/autofit/inventory/stress_battery_runs.jsonl:46:{"case": "charging_with_replica_candidate", "chi_reduced": 1.747290088264468, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 0, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0655, "d_fwhm_ev": -0.1281, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.4835, "d_fwhm_ev": 0.3695, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:47:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3069.7110277472125, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.691644167392703, "survived": true}, {"bic_star": 2268.771804830489, "boundary_hits": ["replica:center@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['replica:center@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.7702846538141737, "survived": false}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2268.771804830489, "delta_bic_vs_winner": 800.9392229167233, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['replica:center@max'], unphysical_widths=[], orphan_peaks=False)", "name": "main_plus_replica"}, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.23, "seed_offset": 0, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.1434, "d_fwhm_ev": 0.2462, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 6.691644167392703, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:48:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3069.711389067813, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.691644167338099, "survived": true}, {"bic_star": 2268.7718011018105, "boundary_hits": ["replica:center@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['replica:center@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.77028465381276, "survived": false}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2268.7718011018105, "delta_bic_vs_winner": 800.9395879660024, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['replica:center@max'], unphysical_widths=[], orphan_peaks=False)", "name": "main_plus_replica"}, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.64, "seed_offset": 0, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.1434, "d_fwhm_ev": 0.2462, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 6.691644167338099, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:49:{"case": "charging_with_replica_candidate", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 6.85, "seed_offset": 0, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.1364, "d_fwhm_ev": 0.1886, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:50:{"candidates": [{"free_energy": 1159.9673901900233, "free_energy_mc_error": 4.331402015625713, "free_energy_split_half_error": 4.331402015625713, "min_effective_sample_size": 11.257203545526906, "name": "single_main", "posterior_weight": 2.125021944800329e-66, "posterior_weight_reliable": true, "rank": 2}, {"free_energy": 1008.7505561817042, "free_energy_mc_error": 1.4515628189728886, "free_energy_split_half_error": 1.4515628189728886, "min_effective_sample_size": 2.6292565194409003, "name": "main_plus_replica", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1}], "case": "charging_with_replica_candidate", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "recover", "method": "bayesian_exchange_mc", "n_emitted_components": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 4.14, "seed_offset": 0, "selection_warning": null, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0287, "d_fwhm_ev": -0.0147, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": 0.3687, "d_fwhm_ev": 0.3699, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2, "winner": "main_plus_replica", "winner_is_true": true}
docs/autofit/inventory/stress_battery_runs.jsonl:60:{"candidates": [{"free_energy": 1178.806932312742, "free_energy_mc_error": 0.6377158821167086, "free_energy_split_half_error": 0.6377158821167086, "min_effective_sample_size": 15.016747625284404, "name": "sym_main", "posterior_weight": 6.192750338903466e-32, "posterior_weight_reliable": true, "rank": 2}, {"free_energy": 1106.9475886446419, "free_energy_mc_error": 1.639656788828006, "free_energy_split_half_error": 1.639656788828006, "min_effective_sample_size": 4.744365796408424, "name": "asym_main", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1}], "case": "asym_truth_with_asym_candidate", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "recover", "method": "bayesian_exchange_mc", "n_emitted_components": 1, "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 2.86, "seed_offset": 0, "selection_warning": null, "success": true, "true_candidates": ["asym_main"], "truth_match": [{"d_center_ev": -0.0111, "d_fwhm_ev": -0.0842, "matched_role": "main_a", "true_center": 197.8}], "truth_n": 1, "winner": "asym_main", "winner_is_true": true}
docs/autofit/inventory/stress_battery_runs.jsonl:61:{"case": "bg_shirley_truth_linear_fit", "chi_reduced": 1.3111668357842798, "config": {"background_method": "shirley"}, "expectation": "honesty", "method": "least_squares", "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0019, "d_fwhm_ev": 0.0058, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": -0.0015, "d_fwhm_ev": 0.0102, "matched_role": "2", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:62:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4271.54858425193, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 468.6838552678528, "survived": false}, {"bic_star": 3801.4114042480733, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 308.7466180222082, "survived": true}, {"bic_star": 3648.466236534472, "boundary_hits": ["main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 284.1218885924425, "survived": false}, {"bic_star": 3642.7622641369885, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P3+bfix", "orphan_peaks": false, "reduced_chi_sq": 283.1387414386821, "survived": true}], "case": "bg_shirley_truth_linear_fit", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 10.22, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0151, "d_fwhm_ev": -0.1716, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0174, "d_fwhm_ev": 0.2873, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 283.1387414386821, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:63:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4271.544614789273, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 468.68383163083354, "survived": false}, {"bic_star": 3801.406217540362, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 308.74661569462177, "survived": true}, {"bic_star": 3648.489127912308, "boundary_hits": ["main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 284.1217320570383, "survived": false}, {"bic_star": 3642.785345422898, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P3+bfix", "orphan_peaks": false, "reduced_chi_sq": 283.1386118748553, "survived": true}], "case": "bg_shirley_truth_linear_fit", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 32.82, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0151, "d_fwhm_ev": -0.1716, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0172, "d_fwhm_ev": 0.2878, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 283.1386118748553, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:67:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4146.61792120331, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 126.30873391628948, "survived": false}, {"bic_star": 2433.522542110988, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.2355887929329685, "survived": true}, {"bic_star": 2464.9017984747015, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.2209246366731366, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 1.17, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0012, "d_fwhm_ev": 0.0114, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0018, "d_fwhm_ev": 0.0065, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.2355887929329685, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:68:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4146.6177847728, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 126.30873391534688, "survived": false}, {"bic_star": 2433.5225504652817, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.2355887929327787, "survived": true}, {"bic_star": 2464.9017984747015, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 0.9166666666666666, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.2209246366731366, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 2.72, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0012, "d_fwhm_ev": 0.0114, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0018, "d_fwhm_ev": 0.0065, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.2355887929327787, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:74:{"case": "overlap_sep1_h9000", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": true, "n_selected": 2, "notes": "separation 1.0\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 14.57, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.4529, "d_fwhm_ev": 0.1592, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 2.9893, "d_fwhm_ev": 0.5758, "matched_role": "main_c", "true_center": 198.39999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:77:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3200.9378373045492, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 6.5504025251323394, "survived": true}, {"bic_star": 2319.827660084753, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.200247215973865, "survived": true}, {"bic_star": 2355.5001097772392, "boundary_hits": ["main_c:center@min", "main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min', 'main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 0.8333333333333334, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.1867198051966428, "survived": false}], "case": "overlap_sep0.7_h9000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 24.96, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0116, "d_fwhm_ev": -0.0012, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0124, "d_fwhm_ev": 0.0279, "matched_role": "main_b", "true_center": 198.04}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.200247215973865, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:80:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 2529.846397250423, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 2.5011103545460256, "survived": true}, {"bic_star": 2455.712579641171, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.7885560493966415, "survived": false}, {"bic_star": 2483.5388447920755, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.6828315384857104, "survived": false}], "case": "overlap_sep0.4_h9000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2455.712579641171, "delta_bic_vs_winner": 74.13381760925176, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "name": "P2"}, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "separation 0.4\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 1.71, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1959, "d_fwhm_ev": 0.1589, "matched_role": "main_a", "true_center": 197.2}, null], "truth_n": 2, "winner": "P1", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 2.5011103545460256, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:81:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 2529.8466347049653, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 2.5011103545447106, "survived": true}, {"bic_star": 2455.712732678833, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.7885560493888828, "survived": false}, {"bic_star": 2483.5279471733843, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 0.75, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.6828315306538362, "survived": false}], "case": "overlap_sep0.4_h9000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2455.712732678833, "delta_bic_vs_winner": 74.13390202613209, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "name": "P2"}, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "separation 0.4\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 16.9, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1959, "d_fwhm_ev": 0.1589, "matched_role": "main_a", "true_center": 197.2}, null], "truth_n": 2, "winner": "P1", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 2.5011103545447106, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:84:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 1914.159255338055, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 1.120242810299788, "survived": true}, {"bic_star": 1919.418597413299, "boundary_hits": ["main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.0874072276093152, "survived": false}], "case": "overlap_sep0.4_h900", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "ambiguous", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "separation 0.4\u00d7FWHM, heights 900/630", "regime": "heavy_overlap", "runtime_s": 4.61, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1934, "d_fwhm_ev": 0.1445, "matched_role": "main_a", "true_center": 197.2}, null], "truth_n": 2, "winner": "P1", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.120242810299788, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:85:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 1914.1592317847628, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 1.1202428102997057, "survived": true}, {"bic_star": 1919.418597413299, "boundary_hits": ["main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.0874072276093152, "survived": false}], "case": "overlap_sep0.4_h900", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "ambiguous", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "separation 0.4\u00d7FWHM, heights 900/630", "regime": "heavy_overlap", "runtime_s": 5.49, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1934, "d_fwhm_ev": 0.1445, "matched_role": "main_a", "true_center": 197.2}, null], "truth_n": 2, "winner": "P1", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.1202428102997057, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:96:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4283.283653905022, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 376.30958977610044, "survived": true}, {"bic_star": 2361.291874772842, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.7784581293646837, "survived": true}, {"bic_star": 2403.521344864318, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.75, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.7637353959087687, "survived": false}, {"bic_star": 2426.315290961152, "boundary_hits": ["main_d:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_d:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.0, "name": "P4", "orphan_peaks": true, "reduced_chi_sq": 1.7885768993239026, "survived": false}, {"bic_star": 2449.1314060187674, "boundary_hits": ["main_d:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_d:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.0, "name": "P5", "orphan_peaks": true, "reduced_chi_sq": 1.8141280641936752, "survived": false}], "case": "overspecified_2true_5max", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "prune", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "truth 2 well-separated peaks; menu offers up to 5", "regime": "overspecified", "runtime_s": 4.33, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0001, "d_fwhm_ev": 0.0147, "matched_role": "main_a", "true_center": 196.8}, {"d_center_ev": -0.0055, "d_fwhm_ev": 0.0299, "matched_role": "main_b", "true_center": 199.4}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.7784581293646837, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:101:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4283.1413352187155, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 376.0028803012931, "survived": true}, {"bic_star": 2307.7060700154566, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 2.225654104915598, "survived": true}, {"bic_star": 2322.1946419152873, "boundary_hits": ["decoy_mid:center@min", "decoy_mid:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['decoy_mid:center@min', 'decoy_mid:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 0.9166666666666666, "name": "P3_decoy", "orphan_peaks": false, "reduced_chi_sq": 2.171338789921752, "survived": false}], "case": "overspecified_inroi_decoy", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "prune", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "decoy 'shoulder' window between the true peaks (real tail intensity present) \u2014 must be pruned, not populated", "regime": "overspecified", "runtime_s": 3.25, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0014, "d_fwhm_ev": 0.0238, "matched_role": "main_a", "true_center": 196.8}, {"d_center_ev": -0.005, "d_fwhm_ev": 0.0192, "matched_role": "main_b", "true_center": 199.4}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 2.225654104915598, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:103:{"case": "charging_no_replica_candidate", "chi_reduced": 3.2617136636412978, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.06, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0196, "d_fwhm_ev": -0.1273, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.5088, "d_fwhm_ev": 0.4886, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:104:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3094.9892829615083, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 9.091478360741299, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.03, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1421, "d_fwhm_ev": 0.2625, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 9.091478360741299, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:105:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3094.9892829615083, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 9.091478360741299, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.08, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1421, "d_fwhm_ev": 0.2625, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 9.091478360741299, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:106:{"case": "charging_no_replica_candidate", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 3.73, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1127, "d_fwhm_ev": 0.1378, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:107:{"case": "charging_with_replica_candidate", "chi_reduced": 1.8653919775457, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.0239, "d_fwhm_ev": 0.0419, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": -0.0889, "d_fwhm_ev": -0.0014, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:108:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3050.7264501784407, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.699517650214303, "survived": true}, {"bic_star": 2268.1535058762415, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.865391977506154, "survived": true}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.16, "seed_offset": 1000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.0239, "d_fwhm_ev": 0.0419, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": -0.0889, "d_fwhm_ev": -0.0014, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2, "winner": "main_plus_replica", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.865391977506154, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:109:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3050.7260572120103, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 6.69951765015872, "survived": true}, {"bic_star": 2268.1535654108015, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.8653919773281642, "survived": true}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.39, "seed_offset": 1000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.0239, "d_fwhm_ev": 0.0419, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": -0.0889, "d_fwhm_ev": -0.0014, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2, "winner": "main_plus_replica", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.8653919773281642, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:110:{"case": "charging_with_replica_candidate", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 7.37, "seed_offset": 1000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.141, "d_fwhm_ev": 0.1856, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:111:{"case": "asym_truth_symmetric_only", "chi_reduced": 5.468264131068512, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.0028, "d_fwhm_ev": -0.088, "matched_role": "1", "true_center": 197.8}], "truth_n": 1}
docs/autofit/inventory/stress_battery_runs.jsonl:114:{"case": "asym_truth_symmetric_only", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 2, "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 4.63, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.0697, "d_fwhm_ev": 0.1536, "matched_role": "main_a", "true_center": 197.8}], "truth_n": 1}
docs/autofit/inventory/stress_battery_runs.jsonl:116:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 2794.5375948416445, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "sym_main", "orphan_peaks": false, "reduced_chi_sq": 7.7961602387375155, "survived": true}, {"bic_star": 2560.945632953749, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "asym_main", "orphan_peaks": false, "reduced_chi_sq": 4.020125924382515, "survived": true}], "case": "asym_truth_with_asym_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 0.09, "seed_offset": 1000, "success": true, "true_candidates": ["asym_main"], "truth_match": [{"d_center_ev": -0.022, "d_fwhm_ev": -0.1065, "matched_role": "main_a", "true_center": 197.8}], "truth_n": 1, "winner": "asym_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 4.020125924382515, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:120:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4276.13751211553, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 485.82886930696975, "survived": false}, {"bic_star": 3798.867786537885, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 323.0957615487757, "survived": true}, {"bic_star": 3657.6171964795, "boundary_hits": ["main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 300.2440732654479, "survived": false}, {"bic_star": 3651.9134139931, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P3+bfix", "orphan_peaks": false, "reduced_chi_sq": 299.2051664358594, "survived": true}], "case": "bg_shirley_truth_linear_fit", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 9.05, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.015, "d_fwhm_ev": -0.1739, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0129, "d_fwhm_ev": 0.2661, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 299.2051664358594, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:121:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4276.137336465737, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 485.8288419015945, "survived": false}, {"bic_star": 3798.867786537885, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 323.0957615487757, "survived": true}, {"bic_star": 3657.5852867891253, "boundary_hits": ["main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 300.24406294190317, "survived": false}, {"bic_star": 3651.8815042352185, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P3+bfix", "orphan_peaks": false, "reduced_chi_sq": 299.20515613836733, "survived": true}], "case": "bg_shirley_truth_linear_fit", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 31.2, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0151, "d_fwhm_ev": -0.1737, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0127, "d_fwhm_ev": 0.2658, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 299.20515613836733, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:122:{"case": "bg_shirley_truth_linear_fit", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": true, "n_selected": 2, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 16.13, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.8014, "d_fwhm_ev": 0.1565, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 2.9, "d_fwhm_ev": 1.3, "matched_role": "main_c", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:124:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4149.40180690114, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 127.16094575159921, "survived": false}, {"bic_star": 2513.9500119745444, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.606179086709936, "survived": true}, {"bic_star": 2547.2588045334355, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.75, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.5585186839073915, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 1.38, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0031, "d_fwhm_ev": 0.0033, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0, "d_fwhm_ev": 0.01, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.606179086709936, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:125:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4149.401849051055, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 127.1609457367891, "survived": false}, {"bic_star": 2513.9499633731625, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.606179086709871, "survived": true}, {"bic_star": 2547.2588045334355, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.6666666666666666, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.5585186839073915, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 2.41, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0031, "d_fwhm_ev": 0.0033, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0, "d_fwhm_ev": 0.01, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.606179086709871, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:127:{"case": "overlap_sep1_h9000", "chi_reduced": 1.858992418320096, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 1.0\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.01, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0005, "d_fwhm_ev": 0.0151, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.0068, "d_fwhm_ev": 0.0052, "matched_role": "2", "true_center": 198.39999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:128:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3731.089416941838, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 36.73277568852025, "survived": true}, {"bic_star": 2374.741012556063, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.8589924180833206, "survived": true}, {"bic_star": 2412.6029367699443, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.25, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.8585964629846135, "survived": false}], "case": "overlap_sep1_h9000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "separation 1.0\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.44, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0005, "d_fwhm_ev": 0.0151, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0068, "d_fwhm_ev": 0.0052, "matched_role": "main_b", "true_center": 198.39999999999998}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.8589924180833206, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:129:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3731.0863685545824, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 36.73277568702825, "survived": true}, {"bic_star": 2374.7409523003485, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.8589924179132822, "survived": true}, {"bic_star": 2412.6068768598, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.4166666666666667, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.8585964564896011, "survived": false}], "case": "overlap_sep1_h9000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "separation 1.0\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 1.37, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0005, "d_fwhm_ev": 0.0151, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0068, "d_fwhm_ev": 0.0052, "matched_role": "main_b", "true_center": 198.39999999999998}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.8589924179132822, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:130:{"case": "overlap_sep1_h9000", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": true, "n_selected": 2, "notes": "separation 1.0\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 14.12, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.4735, "d_fwhm_ev": 0.1508, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 3.1078, "d_fwhm_ev": 0.429, "matched_role": "main_c", "true_center": 198.39999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:131:{"case": "overlap_sep0.7_h9000", "chi_reduced": 1.0584987881714802, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.01, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0012, "d_fwhm_ev": 0.0219, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.0064, "d_fwhm_ev": 0.0153, "matched_role": "2", "true_center": 198.04}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:132:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3174.490421997974, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 5.964964587858943, "survived": true}, {"bic_star": 2230.673291475814, "boundary_hits": [], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.75, "name": "P2", "orphan_peaks": true, "reduced_chi_sq": 1.058498788135691, "survived": false}, {"bic_star": 2257.1968735839887, "boundary_hits": ["main_c:fwhm@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.5, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.0567452737290672, "survived": false}], "case": "overlap_sep0.7_h9000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2230.673291475814, "delta_bic_vs_winner": 943.8171305221599, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "name": "P2"}, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 3.31, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.3432, "d_fwhm_ev": 0.4521, "matched_role": "main_a", "true_center": 197.2}, null], "truth_n": 2, "winner": "P1", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 5.964964587858943, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:134:{"case": "overlap_sep0.7_h9000", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 5, "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 13.54, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.3741, "d_fwhm_ev": 0.2657, "matched_role": "main_a#3", "true_center": 197.2}, {"d_center_ev": -1.29, "d_fwhm_ev": -0.6, "matched_role": "main_a#2", "true_center": 198.04}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:136:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 2381.548152484723, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 1.3103936426505667, "survived": true}, {"bic_star": 2284.266378162029, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.130248021669231, "survived": false}, {"bic_star": 2307.7624008384637, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 0.75, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.1237483225307239, "survived": false}], "case": "overlap_sep0.4_h9000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2284.266378162029, "delta_bic_vs_winner": 97.28177432269376, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "name": "P2"}, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "separation 0.4\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 9.66, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1969, "d_fwhm_ev": 0.1511, "matched_role": "main_a", "true_center": 197.2}, null], "truth_n": 2, "winner": "P1", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.3103936426505667, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:137:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 2381.5481756208846, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 1.310393642650553, "survived": true}, {"bic_star": 2284.266377521196, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.130248019836984, "survived": false}, {"bic_star": 2307.7624008384637, "boundary_hits": ["main_b:center@min", "main_b:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.8333333333333334, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.1237483225307239, "survived": false}], "case": "overlap_sep0.4_h9000", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": {"bic_star": 2284.266377521196, "delta_bic_vs_winner": 97.28179809968879, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_b:center@min', 'main_b:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "name": "P2"}, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "separation 0.4\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 23.91, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1969, "d_fwhm_ev": 0.1511, "matched_role": "main_a", "true_center": 197.2}, null], "truth_n": 2, "winner": "P1", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.310393642650553, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:158:{"case": "overspecified_inroi_decoy", "config": {}, "expectation": "prune", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 4, "notes": "decoy 'shoulder' window between the true peaks (real tail intensity present) \u2014 must be pruned, not populated", "regime": "overspecified", "runtime_s": 15.94, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0064, "d_fwhm_ev": 0.0535, "matched_role": "main_a#2", "true_center": 196.8}, {"d_center_ev": -0.0153, "d_fwhm_ev": 0.0551, "matched_role": "main_a#3", "true_center": 199.4}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:159:{"case": "charging_no_replica_candidate", "chi_reduced": 1.7521780523190802, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0528, "d_fwhm_ev": -0.0962, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.4595, "d_fwhm_ev": 0.4025, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:160:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3077.8924377887674, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 7.273306463854169, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.03, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1416, "d_fwhm_ev": 0.2499, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 7.273306463854169, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:161:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3077.892007835877, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 7.273306463794299, "survived": true}], "case": "charging_no_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.07, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1416, "d_fwhm_ev": 0.2499, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2, "winner": "single_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 7.273306463794299, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:162:{"case": "charging_no_replica_candidate", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 1, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 3.59, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.1085, "d_fwhm_ev": 0.1491, "matched_role": "main_a", "true_center": 197.8}, null], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:163:{"case": "charging_with_replica_candidate", "chi_reduced": 1.0564952083796528, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0319, "d_fwhm_ev": -0.0126, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.1501, "d_fwhm_ev": 0.1416, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:164:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3054.3526555265244, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 5.584627880499543, "survived": true}, {"bic_star": 2250.0786978167107, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.0564952055324386, "survived": true}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.16, "seed_offset": 2000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0319, "d_fwhm_ev": -0.0126, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": 0.1501, "d_fwhm_ev": 0.1416, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2, "winner": "main_plus_replica", "winner_absent_slots": [], "winner_autocorr_flag": false, "winner_boundary_hits": [], "winner_chi_reduced": 1.0564952055324386, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:165:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 3054.3531150263357, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main", "orphan_peaks": false, "reduced_chi_sq": 5.584627880407254, "survived": true}, {"bic_star": 2250.0820292977264, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "main_plus_replica", "orphan_peaks": false, "reduced_chi_sq": 1.0564952032164714, "survived": true}], "case": "charging_with_replica_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.45, "seed_offset": 2000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0319, "d_fwhm_ev": -0.0126, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": 0.1502, "d_fwhm_ev": 0.1416, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2, "winner": "main_plus_replica", "winner_absent_slots": [], "winner_autocorr_flag": false, "winner_boundary_hits": [], "winner_chi_reduced": 1.0564952032164714, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:166:{"case": "charging_with_replica_candidate", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": true, "n_selected": 2, "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 6.89, "seed_offset": 2000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.1001, "d_fwhm_ev": 0.1878, "matched_role": "main_a", "true_center": 197.8}, {"d_center_ev": -1.6, "d_fwhm_ev": 1.3, "matched_role": "replica", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:172:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 2811.9160721377707, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "sym_main", "orphan_peaks": false, "reduced_chi_sq": 6.339402041039051, "survived": true}, {"bic_star": 2502.999969437228, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "asym_main", "orphan_peaks": false, "reduced_chi_sq": 3.5054533590976438, "survived": true}], "case": "asym_truth_with_asym_candidate", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 1, "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 0.09, "seed_offset": 2000, "success": true, "true_candidates": ["asym_main"], "truth_match": [{"d_center_ev": -0.0006, "d_fwhm_ev": -0.065, "matched_role": "main_a", "true_center": 197.8}], "truth_n": 1, "winner": "asym_main", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 3.5054533590976438, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:176:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4273.144118402068, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 461.7861240956535, "survived": false}, {"bic_star": 3784.0798938671683, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 299.7146067606419, "survived": true}, {"bic_star": 3632.9182123482246, "boundary_hits": ["main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 276.66086742128124, "survived": false}, {"bic_star": 3627.2144296590523, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P3+bfix", "orphan_peaks": false, "reduced_chi_sq": 275.70356335310606, "survived": true}], "case": "bg_shirley_truth_linear_fit", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 12.24, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.022, "d_fwhm_ev": -0.1669, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0125, "d_fwhm_ev": 0.2415, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 275.70356335310606, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:178:{"case": "bg_shirley_truth_linear_fit", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": true, "n_selected": 2, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 15.78, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.7989, "d_fwhm_ev": 0.1534, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 2.85, "d_fwhm_ev": 1.3, "matched_role": "main_c", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:180:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4149.084639220466, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 127.55249026837087, "survived": false}, {"bic_star": 2624.164212560478, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 2.5884578681517856, "survived": true}, {"bic_star": 2639.635951866542, "boundary_hits": ["main_c:center@min", "main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min', 'main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 2.340160096106336, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 1.39, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0019, "d_fwhm_ev": 0.0101, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0009, "d_fwhm_ev": 0.0126, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 2.5884578681517856, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:181:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4149.084639220466, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 127.55249026837087, "survived": false}, {"bic_star": 2624.163913081583, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 2.5884578681434554, "survived": true}, {"bic_star": 2639.635951866542, "boundary_hits": ["main_c:center@min", "main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min', 'main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 0.9166666666666666, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 2.340160096106336, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 3.24, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0019, "d_fwhm_ev": 0.0101, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0009, "d_fwhm_ev": 0.0126, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 2.5884578681434554, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:188:{"case": "isolated_missing_peak", "chi_reduced": 1.2748899162782585, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "isolated discrete unmodeled peak at +5 eV \u2014 the proposal pass must fire (accepted proposal = the honesty signal)", "regime": "proposal_pass", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0002, "d_fwhm_ev": 0.0115, "matched_role": "1", "true_center": 196.5}, {"d_center_ev": -0.0036, "d_fwhm_ev": 0.0136, "matched_role": "2", "true_center": 201.5}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:189:{"accepted_proposals": [{"accepted": true, "fitted_center": 201.49640949291822, "near_roi_endpoint": false, "rejection_reason": null, "role": "proposed_peak_0"}], "ambiguous_pairs": [], "candidates": [{"bic_star": 2287.2017921461356, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main+prop", "orphan_peaks": false, "reduced_chi_sq": 1.2748899162477565, "survived": true}], "case": "isolated_missing_peak", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "isolated discrete unmodeled peak at +5 eV \u2014 the proposal pass must fire (accepted proposal = the honesty signal)", "regime": "proposal_pass", "runtime_s": 0.08, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0002, "d_fwhm_ev": 0.0115, "matched_role": "main_a", "true_center": 196.5}, {"d_center_ev": -0.0036, "d_fwhm_ev": 0.0136, "matched_role": "proposed_peak_0", "true_center": 201.5}], "truth_n": 2, "winner": "single_main+prop", "winner_absent_slots": [], "winner_autocorr_flag": false, "winner_boundary_hits": [], "winner_chi_reduced": 1.2748899162477565, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:190:{"accepted_proposals": [{"accepted": true, "fitted_center": 201.496409499453, "near_roi_endpoint": false, "rejection_reason": null, "role": "proposed_peak_0"}], "ambiguous_pairs": [], "candidates": [{"bic_star": 2287.201841026982, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "single_main+prop", "orphan_peaks": false, "reduced_chi_sq": 1.2748899162457255, "survived": true}], "case": "isolated_missing_peak", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "isolated discrete unmodeled peak at +5 eV \u2014 the proposal pass must fire (accepted proposal = the honesty signal)", "regime": "proposal_pass", "runtime_s": 0.2, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0002, "d_fwhm_ev": 0.0115, "matched_role": "main_a", "true_center": 196.5}, {"d_center_ev": -0.0036, "d_fwhm_ev": 0.0136, "matched_role": "proposed_peak_0", "true_center": 201.5}], "truth_n": 2, "winner": "single_main+prop", "winner_absent_slots": [], "winner_autocorr_flag": false, "winner_boundary_hits": [], "winner_chi_reduced": 1.2748899162457255, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:1:{"anchor": "Cl2p_Scan", "candidates": [{"bic_star": 1894.1501379559727, "boundary_hits": [], "conditional": null, "name": "Cl0_doublet", "rank": 2, "reduced_chi_sq": 2.399106191222575}, {"bic_star": 1788.2410439609396, "boundary_hits": ["main_cl2p12:ratio@max"], "conditional": null, "name": "Cl0r_doublet_relaxed", "rank": null, "reduced_chi_sq": 1.622106489375858}, {"bic_star": 1782.9423620800894, "boundary_hits": [], "conditional": null, "name": "Cl0r_doublet_relaxed+bfix", "rank": 1, "reduced_chi_sq": 1.613787975869576}], "conditional": null, "config": {"enable_proposal_pass": false, "n_refits": 4, "noise_floor": 1.0, "rng_seed": 0}, "expert": {"chi_reduced": 2.851136794742553, "peaks": [{"amplitude": 5822.889190894942, "center": 197.9167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2911.444595447471, "center": 199.5167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "ic_model_comparison", "peaks": [{"amplitude": 5717.033919631427, "center": 197.89914981007865, "fwhm": 1.6280369396936925, "gl_ratio": 0.139294230120932, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 39.599934138930756, "center": 0.0049431518890450665, "fwhm": 0.012450580237590863, "gl_ratio": 0.014507440178487525}}, {"amplitude": 3144.368655797285, "center": 199.4980083579558, "fwhm": 1.6280369396936925, "gl_ratio": 0.139294230120932, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 21.77996375249046, "center": 0.009009580567391942, "fwhm": 0.01245058022928556, "gl_ratio": 0.014507440205382317, "offset": 0.009119185516544923, "ratio": 0.0}}], "runtime_s": 0.3, "seed": 0, "success": true, "winner": "Cl0r_doublet_relaxed+bfix"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:2:{"anchor": "Cl2p_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1481.26396673415, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.05645725615977426, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.05645725615977426, "min_effective_sample_size": 10.350584165604227, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 5.7737353402677815e-22, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 106.60371342503906, "swap_acceptance": 0.5787878787878787}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1432.3604139320091, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.5188018739002018, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.5188018739002018, "min_effective_sample_size": 11.860513326203993, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 81.49334133679332, "swap_acceptance": 0.5339393939393939}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 48.5 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.6077230683072066, "ci_level": 0.68, "ci_low": 1.5882775890481415, "ess": 48.505669505382485, "median": 1.5992353398002828}, "ratio": {"ci_high": 0.5498249410603676, "ci_level": 0.68, "ci_low": 0.5482127564989837, "ess": 65.85481522026386, "median": 0.5493936199943856}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 11.9 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5738.475664681449, "ci_level": 0.68, "ci_low": 5656.147539361833, "ess": 19.62851013839095, "median": 5725.686763100099}, "center": {"ci_high": 197.89945720802086, "ci_level": 0.68, "ci_low": 197.88984501139063, "ess": 19.28435238096058, "median": 197.89503566425037}, "fwhm": {"ci_high": 1.6442812386633079, "ci_level": 0.68, "ci_low": 1.618972458662571, "ess": 11.860513326203993, "median": 1.6309401352528183}, "gl_ratio": {"ci_high": 0.17901445897134605, "ci_level": 0.68, "ci_low": 0.13204818856736547, "ess": 47.67768996616846, "median": 0.15332268268324245}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 2.851136794742553, "peaks": [{"amplitude": 5822.889190894942, "center": 197.9167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2911.444595447471, "center": 199.5167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5725.686763100099, "center": 197.89503566425037, "fwhm": 1.6309401352528183, "gl_ratio": 0.15332268268324245, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 3145.6557777334997, "center": 199.49427100405066, "fwhm": 1.6309401352528183, "gl_ratio": 0.15332268268324245, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 25.2, "seed": 0, "selection_warning": null, "sigma_hat": 81.49334133679332, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:3:{"anchor": "Cl2p_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1480.1911328217734, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.9666745924947691, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.9666745924947691, "min_effective_sample_size": 29.190014248315034, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 7.28904367227661e-21, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 106.72905483459655, "swap_acceptance": 0.583939393939394}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1433.8232182228126, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.3408599491743871, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.3408599491743871, "min_effective_sample_size": 6.135776335172147, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 81.48941728358463, "swap_acceptance": 0.5236363636363637}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 37.3 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.6077751029876326, "ci_level": 0.68, "ci_low": 1.5893680447540435, "ess": 37.2886218531279, "median": 1.59787049660024}, "ratio": {"ci_high": 0.5498990283470473, "ci_level": 0.68, "ci_low": 0.5484819615645766, "ess": 62.85734088655587, "median": 0.5492481492814276}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 6.1 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5747.120405361032, "ci_level": 0.68, "ci_low": 5698.59268998664, "ess": 6.135776335172147, "median": 5711.134019699916}, "center": {"ci_high": 197.89793292530445, "ci_level": 0.68, "ci_low": 197.88951012461266, "ess": 30.879483976879847, "median": 197.89527081723674}, "fwhm": {"ci_high": 1.636709686265114, "ci_level": 0.68, "ci_low": 1.6142922826272914, "ess": 23.849734518160577, "median": 1.626148018180968}, "gl_ratio": {"ci_high": 0.18206329349945147, "ci_level": 0.68, "ci_low": 0.1363721795983906, "ess": 59.90166849862524, "median": 0.15923319624735174}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 2.851136794742553, "peaks": [{"amplitude": 5822.889190894942, "center": 197.9167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2911.444595447471, "center": 199.5167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5711.134019699916, "center": 197.89527081723674, "fwhm": 1.626148018180968, "gl_ratio": 0.15923319624735174, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 3136.8297906183793, "center": 199.493141313837, "fwhm": 1.626148018180968, "gl_ratio": 0.15923319624735174, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 25.3, "seed": 1, "selection_warning": null, "sigma_hat": 81.48941728358463, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:4:{"anchor": "Cl2p_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1481.2431336180211, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 2.519151352479298, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 2.519151352479298, "min_effective_sample_size": 10.75078050687602, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 2.1910337090404343e-21, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 106.4645690613904, "swap_acceptance": 0.4738095238095238}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1433.6732201108719, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.9722565619269972, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.9722565619269972, "min_effective_sample_size": 14.697984177041747, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 81.48905909436992, "swap_acceptance": 0.4419047619047619}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 36.5 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.6060939940018115, "ci_level": 0.68, "ci_low": 1.5864268868406584, "ess": 36.51686260815219, "median": 1.5970687447907324}, "ratio": {"ci_high": 0.5497150524363908, "ci_level": 0.68, "ci_low": 0.548343649192046, "ess": 59.511111228703015, "median": 0.5492500006195842}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 14.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5705.947703181851, "ci_level": 0.68, "ci_low": 5649.654419621443, "ess": 14.697984177041747, "median": 5674.4220465091585}, "center": {"ci_high": 197.8981164828045, "ci_level": 0.68, "ci_low": 197.88977424316928, "ess": 22.817538827822833, "median": 197.89252570684843}, "fwhm": {"ci_high": 1.6471848373765678, "ci_level": 0.68, "ci_low": 1.628730940120245, "ess": 28.791083578737247, "median": 1.6382056282355002}, "gl_ratio": {"ci_high": 0.17358178218102832, "ci_level": 0.68, "ci_low": 0.13716589237253848, "ess": 69.3591072102325, "median": 0.15486606534837816}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 8, "n_sweeps": 1500}, "expert": {"chi_reduced": 2.851136794742553, "peaks": [{"amplitude": 5822.889190894942, "center": 197.9167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2911.444595447471, "center": 199.5167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5674.4220465091585, "center": 197.89252570684843, "fwhm": 1.6382056282355002, "gl_ratio": 0.15486606534837816, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 3116.6763125609373, "center": 199.48959445163916, "fwhm": 1.6382056282355002, "gl_ratio": 0.15486606534837816, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 17.2, "seed": 0, "selection_warning": null, "sigma_hat": 81.48905909436992, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:5:{"anchor": "Cl2p_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1480.3678625592675, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.18703219383655778, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.18703219383655778, "min_effective_sample_size": 31.01954366675076, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 3.312861143349379e-21, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 106.52467636496254, "swap_acceptance": 0.6644444444444444}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1433.2113878161695, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.7726081088655974, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.7726081088655974, "min_effective_sample_size": 36.70337485399092, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 81.34318563960808, "swap_acceptance": 0.6197777777777778}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 46.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.6062726933865419, "ci_level": 0.68, "ci_low": 1.5902865612671417, "ess": 53.442966286096926, "median": 1.5984148768140662}, "ratio": {"ci_high": 0.5499354711455805, "ci_level": 0.68, "ci_low": 0.5482896185570167, "ess": 46.66538895528372, "median": 0.5492967419637056}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 36.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5709.128748151064, "ci_level": 0.68, "ci_low": 5678.817325621692, "ess": 36.70337485399092, "median": 5698.705000050067}, "center": {"ci_high": 197.90108651867584, "ci_level": 0.68, "ci_low": 197.88851148552763, "ess": 56.55712075746652, "median": 197.89497399388878}, "fwhm": {"ci_high": 1.6413040122487346, "ci_level": 0.68, "ci_low": 1.6198800176458008, "ess": 41.36147138739061, "median": 1.6295751002405965}, "gl_ratio": {"ci_high": 0.17959110561264457, "ci_level": 0.68, "ci_low": 0.14150003134054978, "ess": 44.883412880283664, "median": 0.15786836991699604}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 16, "n_sweeps": 1500}, "expert": {"chi_reduced": 2.851136794742553, "peaks": [{"amplitude": 5822.889190894942, "center": 197.9167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2911.444595447471, "center": 199.5167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5698.705000050067, "center": 197.89497399388878, "fwhm": 1.6295751002405965, "gl_ratio": 0.15786836991699604, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 3130.2800899397803, "center": 199.49338887070286, "fwhm": 1.6295751002405965, "gl_ratio": 0.15786836991699604, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 34.1, "seed": 0, "selection_warning": null, "sigma_hat": 81.34318563960808, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:6:{"anchor": "Cl2p_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1480.3195780082501, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.16840703655066136, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.16840703655066136, "min_effective_sample_size": 18.291669354139326, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 9.835783690725008e-22, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 106.78921306119172, "swap_acceptance": 0.5433333333333333}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1431.9487330949037, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.09984165072717133, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.09984165072717133, "min_effective_sample_size": 13.862279778117212, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 81.29076257924838, "swap_acceptance": 0.48727272727272725}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.604737001993962, "ci_level": 0.68, "ci_low": 1.5870381392473236, "ess": 56.60164779174874, "median": 1.5949651708769537}, "ratio": {"ci_high": 0.5498621104330439, "ci_level": 0.68, "ci_low": 0.54842785615914, "ess": 87.05121931550542, "median": 0.5494463299939899}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 13.9 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5728.995480731608, "ci_level": 0.68, "ci_low": 5686.998920923235, "ess": 13.862279778117212, "median": 5700.438422091099}, "center": {"ci_high": 197.89933196778188, "ci_level": 0.68, "ci_low": 197.8899303928198, "ess": 66.042491267449, "median": 197.8968953921812}, "fwhm": {"ci_high": 1.6375738011524468, "ci_level": 0.68, "ci_low": 1.6179927988209366, "ess": 20.421575605486485, "median": 1.6264423130991048}, "gl_ratio": {"ci_high": 0.18207874234109467, "ci_level": 0.68, "ci_low": 0.13975392195015976, "ess": 54.66624191207374, "median": 0.16291616757876895}}}}}, "config": {"beta_min": 0.001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 2.851136794742553, "peaks": [{"amplitude": 5822.889190894942, "center": 197.9167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2911.444595447471, "center": 199.5167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5700.438422091099, "center": 197.8968953921812, "fwhm": 1.6264423130991048, "gl_ratio": 0.16291616757876895, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 3132.084970374685, "center": 199.49186056305814, "fwhm": 1.6264423130991048, "gl_ratio": 0.16291616757876895, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 26.1, "seed": 0, "selection_warning": null, "sigma_hat": 81.29076257924838, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:7:{"anchor": "Cl2p_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1480.9692268348947, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.8105127825409681, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.8105127825409681, "min_effective_sample_size": 37.60510362423811, "n_components": 2, "n_posterior_samples": 1500, "name": "Cl0_doublet", "posterior_weight": 5.465456067499753e-22, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 106.66575088387333, "swap_acceptance": 0.5762121212121212}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1432.0108023595967, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.2832634694433409, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.2832634694433409, "min_effective_sample_size": 36.51465960934892, "n_components": 2, "n_posterior_samples": 1500, "name": "Cl0r_doublet_relaxed", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 81.44164023836905, "swap_acceptance": 0.5348484848484848}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.6043251906670009, "ci_level": 0.68, "ci_low": 1.5861314370481159, "ess": 63.96779697365789, "median": 1.595055640348217}, "ratio": {"ci_high": 0.5498693075264929, "ci_level": 0.68, "ci_low": 0.548315489444085, "ess": 146.1032706217116, "median": 0.5493586637064942}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 36.5 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5719.216888667075, "ci_level": 0.68, "ci_low": 5663.176838383433, "ess": 39.928389882337314, "median": 5696.889242007927}, "center": {"ci_high": 197.89911765639334, "ci_level": 0.68, "ci_low": 197.8895049938237, "ess": 36.51465960934892, "median": 197.89381598280744}, "fwhm": {"ci_high": 1.6416505359095959, "ci_level": 0.68, "ci_low": 1.616559342385302, "ess": 56.13259508250893, "median": 1.6308304049920912}, "gl_ratio": {"ci_high": 0.18093995149336334, "ci_level": 0.68, "ci_low": 0.1431594182996548, "ess": 78.17885772545725, "median": 0.16188396877332284}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 3000}, "expert": {"chi_reduced": 2.851136794742553, "peaks": [{"amplitude": 5822.889190894942, "center": 197.9167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2911.444595447471, "center": 199.5167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5696.889242007927, "center": 197.89381598280744, "fwhm": 1.6308304049920912, "gl_ratio": 0.16188396877332284, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 3129.6354612733776, "center": 199.48887162315566, "fwhm": 1.6308304049920912, "gl_ratio": 0.16188396877332284, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 48.9, "seed": 0, "selection_warning": null, "sigma_hat": 81.44164023836905, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:8:{"anchor": "Cl2p_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1481.1695072938533, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.3453761961455939, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.3453761961455939, "min_effective_sample_size": 33.06935618949634, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 4.2144011343110026e-22, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 106.81362643616333, "swap_acceptance": 0.5715757575757576}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1431.9511427497023, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.3141841742959741, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.3141841742959741, "min_effective_sample_size": 23.65189668493586, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 81.40231540821954, "swap_acceptance": 0.540060606060606}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 23.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.6057983875775315, "ci_level": 0.68, "ci_low": 1.5843996456517142, "ess": 23.65189668493586, "median": 1.5952272713625764}, "ratio": {"ci_high": 0.5498987055202629, "ci_level": 0.68, "ci_low": 0.5483105081337271, "ess": 75.09265240615848, "median": 0.5494399377337225}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 31.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5695.188967084182, "ci_level": 0.68, "ci_low": 5650.383778078533, "ess": 42.80206428314586, "median": 5685.538435889075}, "center": {"ci_high": 197.89747286563107, "ci_level": 0.68, "ci_low": 197.8895039836248, "ess": 31.715145599293198, "median": 197.89465779779107}, "fwhm": {"ci_high": 1.642713854012452, "ci_level": 0.68, "ci_low": 1.62158664907488, "ess": 38.693664537726356, "median": 1.6342260823289974}, "gl_ratio": {"ci_high": 0.17982969349380376, "ci_level": 0.68, "ci_low": 0.13902014737024979, "ess": 69.17978729131043, "median": 0.15903687045449366}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 1, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 2.851136794742553, "peaks": [{"amplitude": 5822.889190894942, "center": 197.9167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2911.444595447471, "center": 199.5167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5685.538435889075, "center": 197.89465779779107, "fwhm": 1.6342260823289974, "gl_ratio": 0.15903687045449366, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 3123.861884197579, "center": 199.48988506915364, "fwhm": 1.6342260823289974, "gl_ratio": 0.15903687045449366, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 26.4, "seed": 0, "selection_warning": null, "sigma_hat": 81.40231540821954, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:9:{"anchor": "Cl2p_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1480.6535050277812, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.3188232162347049, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.3188232162347049, "min_effective_sample_size": 11.967798505343836, "n_components": 2, "n_posterior_samples": 1050, "name": "Cl0_doublet", "posterior_weight": 1.1395363852130257e-21, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 106.54665540620664, "swap_acceptance": 0.5748484848484848}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1432.4298395749584, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.6225514213608676, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.6225514213608676, "min_effective_sample_size": 24.514980929478124, "n_components": 2, "n_posterior_samples": 1050, "name": "Cl0r_doublet_relaxed", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 81.24204364379398, "swap_acceptance": 0.5372727272727272}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.6039225364803456, "ci_level": 0.68, "ci_low": 1.5905698884750845, "ess": 96.0039531672233, "median": 1.5972961794442282}, "ratio": {"ci_high": 0.5498941683770179, "ci_level": 0.68, "ci_low": 0.5483451506553252, "ess": 74.43945832777823, "median": 0.5494346574095819}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 24.5 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5737.369430297504, "ci_level": 0.68, "ci_low": 5671.845000450258, "ess": 24.514980929478124, "median": 5705.1850455446765}, "center": {"ci_high": 197.89978879971895, "ci_level": 0.68, "ci_low": 197.8896257953114, "ess": 54.9091015458626, "median": 197.89414036904225}, "fwhm": {"ci_high": 1.6398285633249898, "ci_level": 0.68, "ci_low": 1.6207443567933741, "ess": 38.91906918431555, "median": 1.632040313506593}, "gl_ratio": {"ci_high": 0.1747295589786246, "ci_level": 0.68, "ci_low": 0.13740781710445923, "ess": 116.23503175129065, "median": 0.15528369714162382}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.3, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 2.851136794742553, "peaks": [{"amplitude": 5822.889190894942, "center": 197.9167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2911.444595447471, "center": 199.5167453118655, "fwhm": 1.6491896310628458, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5705.1850455446765, "center": 197.89414036904225, "fwhm": 1.632040313506593, "gl_ratio": 0.15528369714162382, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 3134.626390957109, "center": 199.49143654848646, "fwhm": 1.632040313506593, "gl_ratio": 0.15528369714162382, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 26.9, "seed": 0, "selection_warning": null, "sigma_hat": 81.24204364379398, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:10:{"anchor": "Cl2p_Scan_0", "candidates": [{"bic_star": 1879.9840017689532, "boundary_hits": [], "conditional": null, "name": "Cl0_doublet", "rank": 2, "reduced_chi_sq": 3.2530643364742438}, {"bic_star": 1807.3546937887884, "boundary_hits": ["main_cl2p12:ratio@max"], "conditional": null, "name": "Cl0r_doublet_relaxed", "rank": null, "reduced_chi_sq": 2.671820888609569}, {"bic_star": 1802.0561470593743, "boundary_hits": [], "conditional": null, "name": "Cl0r_doublet_relaxed+bfix", "rank": 1, "reduced_chi_sq": 2.658119242701632}], "conditional": null, "config": {"enable_proposal_pass": false, "n_refits": 4, "noise_floor": 1.0, "rng_seed": 0}, "expert": {"chi_reduced": 4.938573321633435, "peaks": [{"amplitude": 5390.869523728373, "center": 197.82979333181197, "fwhm": 1.6722221137560755, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2695.4347618641864, "center": 199.42979333181196, "fwhm": 1.6722221137560755, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "ic_model_comparison", "peaks": [{"amplitude": 5262.9989745929115, "center": 197.81898992539408, "fwhm": 1.6524442438158358, "gl_ratio": 0.2733373372563739, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 50.66029152075276, "center": 0.006819319115851115, "fwhm": 0.018661535376515628, "gl_ratio": 0.020469235446814275}}, {"amplitude": 2894.6494360261017, "center": 199.38404463694866, "fwhm": 1.6524442438158358, "gl_ratio": 0.2733373372563739, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 27.86316027187521, "center": 0.012589219163560053, "fwhm": 0.018661535372170607, "gl_ratio": 0.020469235511469015, "offset": 0.01301424370064148, "ratio": 0.0}}], "runtime_s": 0.3, "seed": 0, "success": true, "winner": "Cl0r_doublet_relaxed+bfix"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:11:{"anchor": "Cl2p_Scan_0", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1472.9475912706116, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.3717652835644003, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.3717652835644003, "min_effective_sample_size": 21.286739374699597, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 3.9031343621109107e-14, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 103.15504735932852, "swap_acceptance": 0.5851515151515152}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1442.0731798816432, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.6092149214189249, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.6092149214189249, "min_effective_sample_size": 15.578710250492291, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 0.9999999999999609, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 86.02909904110291, "swap_acceptance": 0.5518181818181818}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 15.8 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.5824915426927928, "ci_level": 0.68, "ci_low": 1.5604325168103927, "ess": 15.755874591978095, "median": 1.5715521797417775}, "ratio": {"ci_high": 0.5497207046809288, "ci_level": 0.68, "ci_low": 0.5472391178960939, "ess": 81.8816120852402, "median": 0.5489629485726946}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 15.6 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5273.815538065123, "ci_level": 0.68, "ci_low": 5164.804704417271, "ess": 15.578710250492291, "median": 5230.503988856987}, "center": {"ci_high": 197.8213437301635, "ci_level": 0.68, "ci_low": 197.81083519554772, "ess": 48.84612319927136, "median": 197.81643490527102}, "fwhm": {"ci_high": 1.6940078049453728, "ci_level": 0.68, "ci_low": 1.656203763433418, "ess": 20.329589736773247, "median": 1.6720222600336863}, "gl_ratio": {"ci_high": 0.2858855384768324, "ci_level": 0.68, "ci_low": 0.24225091868997767, "ess": 32.519156941281345, "median": 0.2642500890489522}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 4.938573321633435, "peaks": [{"amplitude": 5390.869523728373, "center": 197.82979333181197, "fwhm": 1.6722221137560755, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2695.4347618641864, "center": 199.42979333181196, "fwhm": 1.6722221137560755, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5230.503988856987, "center": 197.81643490527102, "fwhm": 1.6720222600336863, "gl_ratio": 0.2642500890489522, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 2871.352892244172, "center": 199.3879870850128, "fwhm": 1.6720222600336863, "gl_ratio": 0.2642500890489522, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 26.2, "seed": 0, "selection_warning": null, "sigma_hat": 86.02909904110291, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:12:{"anchor": "Cl2p_Scan_0", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1474.4173710851055, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.5389052798042258, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.5389052798042258, "min_effective_sample_size": 32.329444573093134, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 1.7080034063681756e-15, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 103.09648484420022, "swap_acceptance": 0.5787878787878787}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1440.41391977992, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.3830449032255956, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.3830449032255956, "min_effective_sample_size": 7.414616356384448, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 0.9999999999999982, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 85.5753387052785, "swap_acceptance": 0.5475757575757576}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.5800320293386683, "ci_level": 0.68, "ci_low": 1.559612165155169, "ess": 70.55659441976493, "median": 1.5710535198076472}, "ratio": {"ci_high": 0.5497140680909408, "ci_level": 0.68, "ci_low": 0.5474658798995519, "ess": 82.84258218107803, "median": 0.5492967931545869}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 7.4 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5257.213225957213, "ci_level": 0.68, "ci_low": 5202.623834955895, "ess": 7.414616356384448, "median": 5236.788472009286}, "center": {"ci_high": 197.81936291583537, "ci_level": 0.68, "ci_low": 197.81023692788145, "ess": 40.995011502147484, "median": 197.81363834238223}, "fwhm": {"ci_high": 1.6841615466646378, "ci_level": 0.68, "ci_low": 1.656735639002588, "ess": 9.326148457974492, "median": 1.6658090942358288}, "gl_ratio": {"ci_high": 0.2851265582780015, "ci_level": 0.68, "ci_low": 0.2448708482758602, "ess": 69.15336139921632, "median": 0.2683495939157859}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 4.938573321633435, "peaks": [{"amplitude": 5390.869523728373, "center": 197.82979333181197, "fwhm": 1.6722221137560755, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2695.4347618641864, "center": 199.42979333181196, "fwhm": 1.6722221137560755, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5236.788472009286, "center": 197.81363834238223, "fwhm": 1.6658090942358288, "gl_ratio": 0.2683495939157859, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 2876.55111410361, "center": 199.38469186218987, "fwhm": 1.6658090942358288, "gl_ratio": 0.2683495939157859, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 26.4, "seed": 1, "selection_warning": null, "sigma_hat": 85.5753387052785, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:13:{"anchor": "Cl2p_Scan_0", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1475.2112473085356, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.3744337257106736, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.3744337257106736, "min_effective_sample_size": 17.124048778991217, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 3.0138219376688495e-14, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 103.30016663773259, "swap_acceptance": 0.4738095238095238}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1444.078265026667, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.3002697171589261, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.3002697171589261, "min_effective_sample_size": 3.8366266277241996, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 0.9999999999999698, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 85.68105236706982, "swap_acceptance": 0.44666666666666666}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 17.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.5805988990914108, "ci_level": 0.68, "ci_low": 1.5592561417849464, "ess": 17.685659702826435, "median": 1.5698629190050697}, "ratio": {"ci_high": 0.5497045605967678, "ci_level": 0.68, "ci_low": 0.5471051414032684, "ess": 60.885126325293555, "median": 0.5486552382063591}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 3.8 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5224.345248803513, "ci_level": 0.68, "ci_low": 5174.720836919904, "ess": 3.8366266277241996, "median": 5212.984323179396}, "center": {"ci_high": 197.81906121992895, "ci_level": 0.68, "ci_low": 197.80969287115357, "ess": 23.354050324438575, "median": 197.81387225471303}, "fwhm": {"ci_high": 1.6872169777324977, "ci_level": 0.68, "ci_low": 1.66684028254697, "ess": 11.738326440365983, "median": 1.6787311804637333}, "gl_ratio": {"ci_high": 0.28635629795357703, "ci_level": 0.68, "ci_low": 0.24655826064346908, "ess": 65.8990168428752, "median": 0.26636316685591516}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 8, "n_sweeps": 1500}, "expert": {"chi_reduced": 4.938573321633435, "peaks": [{"amplitude": 5390.869523728373, "center": 197.82979333181197, "fwhm": 1.6722221137560755, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2695.4347618641864, "center": 199.42979333181196, "fwhm": 1.6722221137560755, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5212.984323179396, "center": 197.81387225471303, "fwhm": 1.6787311804637333, "gl_ratio": 0.26636316685591516, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 2860.131155600007, "center": 199.3837351737181, "fwhm": 1.6787311804637333, "gl_ratio": 0.26636316685591516, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 17.0, "seed": 0, "selection_warning": null, "sigma_hat": 85.68105236706982, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:14:{"anchor": "Cl2p_Scan_0", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1472.9857344296329, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.7371080274450605, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.7371080274450605, "min_effective_sample_size": 24.737507037282896, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 5.18543706084527e-14, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 103.38550020945809, "swap_acceptance": 0.6751111111111111}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1442.3953972591617, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.15816997989622905, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.15816997989622905, "min_effective_sample_size": 24.212844241160226, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 0.999999999999948, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 85.55572203362335, "swap_acceptance": 0.6284444444444445}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.581644849811311, "ci_level": 0.68, "ci_low": 1.5605331348251976, "ess": 67.97438495703918, "median": 1.5697108775573012}, "ratio": {"ci_high": 0.5496145842187585, "ci_level": 0.68, "ci_low": 0.547971978295376, "ess": 149.3715931919162, "median": 0.5490855695294573}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 24.2 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5239.410015292131, "ci_level": 0.68, "ci_low": 5201.245872153716, "ess": 24.212844241160226, "median": 5221.2972771434015}, "center": {"ci_high": 197.82043440689677, "ci_level": 0.68, "ci_low": 197.81002295012502, "ess": 76.53496947248007, "median": 197.815401239124}, "fwhm": {"ci_high": 1.690826336316749, "ci_level": 0.68, "ci_low": 1.659044694453747, "ess": 39.41616179024982, "median": 1.674129715000507}, "gl_ratio": {"ci_high": 0.28972133183555804, "ci_level": 0.68, "ci_low": 0.23824127816265428, "ess": 78.30506471533987, "median": 0.2623512903419379}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 16, "n_sweeps": 1500}, "expert": {"chi_reduced": 4.938573321633435, "peaks": [{"amplitude": 5390.869523728373, "center": 197.82979333181197, "fwhm": 1.6722221137560755, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2695.4347618641864, "center": 199.42979333181196, "fwhm": 1.6722221137560755, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5221.2972771434015, "center": 197.815401239124, "fwhm": 1.674129715000507, "gl_ratio": 0.2623512903419379, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 2866.9389891028895, "center": 199.38511211668128, "fwhm": 1.674129715000507, "gl_ratio": 0.2623512903419379, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 35.0, "seed": 0, "selection_warning": null, "sigma_hat": 85.55572203362335, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:15:{"anchor": "Cl2p_Scan_0", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1474.3201208803857, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.4924515474626787, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.4924515474626787, "min_effective_sample_size": 23.111512440861766, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 1.88419907582127e-15, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 103.31882755201099, "swap_acceptance": 0.5272727272727272}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1440.4148473226187, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.7587572673560317, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.7587572673560317, "min_effective_sample_size": 22.655957054771427, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 0.9999999999999982, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 86.02100542088971, "swap_acceptance": 0.5163636363636364}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 44.0 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.5811539623588986, "ci_level": 0.68, "ci_low": 1.5605947952321875, "ess": 44.034750843573576, "median": 1.5701384714472586}, "ratio": {"ci_high": 0.5496691764743408, "ci_level": 0.68, "ci_low": 0.5464478053223919, "ess": 64.29913927614135, "median": 0.548896336628358}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 22.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5262.728318363409, "ci_level": 0.68, "ci_low": 5185.675615660533, "ess": 22.655957054771427, "median": 5215.201085446856}, "center": {"ci_high": 197.82315807030747, "ci_level": 0.68, "ci_low": 197.80956276688474, "ess": 28.86686824459775, "median": 197.81706741173957}, "fwhm": {"ci_high": 1.688342090170673, "ci_level": 0.68, "ci_low": 1.6575186285063965, "ess": 44.119996703000325, "median": 1.674174723368424}, "gl_ratio": {"ci_high": 0.2881653019273884, "ci_level": 0.68, "ci_low": 0.240152819416427, "ess": 70.66761134100332, "median": 0.26427092321045875}}}}}, "config": {"beta_min": 0.001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 4.938573321633435, "peaks": [{"amplitude": 5390.869523728373, "center": 197.82979333181197, "fwhm": 1.6722221137560755, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2695.4347618641864, "center": 199.42979333181196, "fwhm": 1.6722221137560755, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5215.201085446856, "center": 197.81706741173957, "fwhm": 1.674174723368424, "gl_ratio": 0.26427092321045875, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 2862.6047705820156, "center": 199.38720588318682, "fwhm": 1.674174723368424, "gl_ratio": 0.26427092321045875, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 27.2, "seed": 0, "selection_warning": null, "sigma_hat": 86.02100542088971, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:16:{"anchor": "Cl2p_Scan_0", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1473.2469860447864, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.3797413785674735, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.3797413785674735, "min_effective_sample_size": 28.32257012558609, "n_components": 2, "n_posterior_samples": 1500, "name": "Cl0_doublet", "posterior_weight": 6.006008974666582e-15, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 103.04736561897813, "swap_acceptance": 0.5756060606060606}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1440.5009701137192, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.5755304541028181, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.5755304541028181, "min_effective_sample_size": 19.634298173469205, "n_components": 2, "n_posterior_samples": 1500, "name": "Cl0r_doublet_relaxed", "posterior_weight": 0.999999999999994, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 85.63465103251998, "swap_acceptance": 0.5554545454545454}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.5792580782468304, "ci_level": 0.68, "ci_low": 1.5607503861126348, "ess": 75.2965025789916, "median": 1.5703088349009335}, "ratio": {"ci_high": 0.5496444959637782, "ci_level": 0.68, "ci_low": 0.5471542616890204, "ess": 254.23285586159042, "median": 0.5488208482260962}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 19.6 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5286.9345952122385, "ci_level": 0.68, "ci_low": 5218.535954177217, "ess": 19.634298173469205, "median": 5245.285808199463}, "center": {"ci_high": 197.82104884395915, "ci_level": 0.68, "ci_low": 197.81091054471952, "ess": 107.00372725150113, "median": 197.81558830904987}, "fwhm": {"ci_high": 1.6820958413767584, "ci_level": 0.68, "ci_low": 1.6462782985716258, "ess": 31.840556203296934, "median": 1.6668599762787537}, "gl_ratio": {"ci_high": 0.29112620787099924, "ci_level": 0.68, "ci_low": 0.24512871777053236, "ess": 93.8738656004915, "median": 0.26618041990546354}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 3000}, "expert": {"chi_reduced": 4.938573321633435, "peaks": [{"amplitude": 5390.869523728373, "center": 197.82979333181197, "fwhm": 1.6722221137560755, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2695.4347618641864, "center": 199.42979333181196, "fwhm": 1.6722221137560755, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5245.285808199463, "center": 197.81558830904987, "fwhm": 1.6668599762787537, "gl_ratio": 0.26618041990546354, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 2878.722206444334, "center": 199.3858971439508, "fwhm": 1.6668599762787537, "gl_ratio": 0.26618041990546354, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 51.7, "seed": 0, "selection_warning": null, "sigma_hat": 85.63465103251998, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:17:{"anchor": "Cl2p_Scan_0", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1473.2304436039562, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.7395217912047656, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.7395217912047656, "min_effective_sample_size": 20.684374308336903, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0_doublet", "posterior_weight": 3.5319931601474715e-15, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 103.13100347901381, "swap_acceptance": 0.5817575757575758}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1439.9535295552473, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.7380618131642223, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.7380618131642223, "min_effective_sample_size": 7.225896048456788, "n_components": 2, "n_posterior_samples": 750, "name": "Cl0r_doublet_relaxed", "posterior_weight": 0.9999999999999964, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 85.62223233675857, "swap_acceptance": 0.5392121212121213}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.579171561985343, "ci_level": 0.68, "ci_low": 1.55734096719466, "ess": 57.06850276569578, "median": 1.566558502041988}, "ratio": {"ci_high": 0.549764887343123, "ci_level": 0.68, "ci_low": 0.547425344373149, "ess": 85.41242944853359, "median": 0.5488246343977703}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 7.2 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5256.936097082505, "ci_level": 0.68, "ci_low": 5214.90820747329, "ess": 7.225896048456788, "median": 5232.142723619015}, "center": {"ci_high": 197.82256024913403, "ci_level": 0.68, "ci_low": 197.81026602969823, "ess": 48.21815233209739, "median": 197.81540534401904}, "fwhm": {"ci_high": 1.6795538831312302, "ci_level": 0.68, "ci_low": 1.6517718608974739, "ess": 9.576311654957737, "median": 1.6678516526121303}, "gl_ratio": {"ci_high": 0.2980319546544451, "ci_level": 0.68, "ci_low": 0.2468442811731639, "ess": 42.95543818806933, "median": 0.2730231345755179}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 1, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 4.938573321633435, "peaks": [{"amplitude": 5390.869523728373, "center": 197.82979333181197, "fwhm": 1.6722221137560755, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2695.4347618641864, "center": 199.42979333181196, "fwhm": 1.6722221137560755, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5232.142723619015, "center": 197.81540534401904, "fwhm": 1.6678516526121303, "gl_ratio": 0.2730231345755179, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 2871.5288174071597, "center": 199.38196384606104, "fwhm": 1.6678516526121303, "gl_ratio": 0.2730231345755179, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 27.4, "seed": 0, "selection_warning": null, "sigma_hat": 85.62223233675857, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:18:{"anchor": "Cl2p_Scan_0", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1474.0916166688653, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.8726461280788271, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.8726461280788271, "min_effective_sample_size": 7.5087253977162645, "n_components": 2, "n_posterior_samples": 1050, "name": "Cl0_doublet", "posterior_weight": 4.219158195969241e-15, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 102.98856786797472, "swap_acceptance": 0.5836363636363636}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1440.9924759024757, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.6862899360135089, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.6862899360135089, "min_effective_sample_size": 9.657876901994673, "n_components": 2, "n_posterior_samples": 1050, "name": "Cl0r_doublet_relaxed", "posterior_weight": 0.9999999999999958, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 85.54381716668294, "swap_acceptance": 0.5490909090909091}], "confidence": {"main_cl2p12": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 1.5807743744969904, "ci_level": 0.68, "ci_low": 1.5612023593760596, "ess": 70.22489291585961, "median": 1.5698005091057672}, "ratio": {"ci_high": 0.5498841460653824, "ci_level": 0.68, "ci_low": 0.5475559554521303, "ess": 119.9682443469296, "median": 0.5490102160872052}}}}, "main_cl2p32": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 9.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 5266.865029528373, "ci_level": 0.68, "ci_low": 5203.5535358185825, "ess": 9.657876901994673, "median": 5238.073549214881}, "center": {"ci_high": 197.8214415348672, "ci_level": 0.68, "ci_low": 197.81037491289882, "ess": 64.61390307045127, "median": 197.8151457097792}, "fwhm": {"ci_high": 1.6758560907062219, "ci_level": 0.68, "ci_low": 1.6535701148925581, "ess": 32.82466133655663, "median": 1.6638888732947288}, "gl_ratio": {"ci_high": 0.29281104905093885, "ci_level": 0.68, "ci_low": 0.24790402822172108, "ess": 53.729950239548636, "median": 0.2694077663965322}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.3, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 4.938573321633435, "peaks": [{"amplitude": 5390.869523728373, "center": 197.82979333181197, "fwhm": 1.6722221137560755, "name": "Cl 2p3/2", "shape": "GL"}, {"amplitude": 2695.4347618641864, "center": 199.42979333181196, "fwhm": 1.6722221137560755, "name": "Cl 2p1/2", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 5238.073549214881, "center": 197.8151457097792, "fwhm": 1.6638888732947288, "gl_ratio": 0.2694077663965322, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p32", "shape": "pseudo_voigt_gl"}, {"amplitude": 2875.7558911351357, "center": 199.38494621888495, "fwhm": 1.6638888732947288, "gl_ratio": 0.2694077663965322, "phase_id": "UCl4", "region": "Cl 2p", "role": "main_cl2p12", "shape": "pseudo_voigt_gl"}], "runtime_s": 28.3, "seed": 0, "selection_warning": null, "sigma_hat": 85.54381716668294, "success": true, "winner": "Cl0r_doublet_relaxed"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:19:{"anchor": "B1s_Scan", "candidates": [{"bic_star": 2015.5793171441512, "boundary_hits": [], "conditional": null, "name": "B1_low", "rank": 3, "reduced_chi_sq": 68.92400388089678}, {"bic_star": 2016.8478942186584, "boundary_hits": ["main_b_mid:center@min"], "conditional": null, "name": "B2_low_mid", "rank": null, "reduced_chi_sq": 63.82228280296653}, {"bic_star": 1704.6694232780123, "boundary_hits": [], "conditional": null, "name": "B2b_low_oxide", "rank": 2, "reduced_chi_sq": 7.994825977237744}, {"bic_star": 1366.483290435591, "boundary_hits": [], "conditional": null, "name": "B3_low_mid_oxide", "rank": 1, "reduced_chi_sq": 1.2588022557672092}], "conditional": null, "config": {"enable_proposal_pass": false, "n_refits": 4, "noise_floor": 1.0, "rng_seed": 0}, "expert": {"chi_reduced": 1.4265863110880088, "peaks": [{"amplitude": 1983.7464958794415, "center": 188.5451767387288, "fwhm": 1.8525484474576044, "name": "B-B", "shape": "GL"}, {"amplitude": 2300.416063771059, "center": 192.99838091823622, "fwhm": 1.6179616826553664, "name": "B-O", "shape": "Gaussian"}, {"amplitude": 7387.003496848665, "center": 187.16003377896104, "fwhm": 1.6686511208264643, "name": "B-C", "shape": "GL"}]}, "method": "ic_model_comparison", "peaks": [{"amplitude": 7688.133165498477, "center": 187.211409511551, "fwhm": 1.7271877467434202, "gl_ratio": 0.04453437321110043, "phase_id": "B4C", "region": "B 1s", "role": "main_b_low", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 46.39260955037003, "center": 0.010708750236042296, "fwhm": 0.018132815770626948, "gl_ratio": 0.015396272708934568}}, {"amplitude": 1300.1185615208988, "center": 188.7171124140521, "fwhm": 1.2602911020246341, "gl_ratio": 1.661853987755535e-11, "phase_id": "B4C", "region": "B 1s", "role": "main_b_mid", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 68.63650973371432, "center": 0.0425117037539577, "fwhm": 0.06574396588135549, "gl_ratio": 3.571703517565689}}, {"amplitude": 1938.0114030404895, "center": 192.98584606930964, "fwhm": 1.3421259794132938, "gl_ratio": 1.0697748242805005e-10, "phase_id": "B4C", "region": "B 1s", "role": "main_b_oxide", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 29.69451910033184, "center": 0.008563469426293834, "fwhm": 0.022941559398213685, "gl_ratio": 0.15860438165913027}}], "runtime_s": 4.6, "seed": 0, "success": true, "winner": "B3_low_mid_oxide"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:20:{"anchor": "B1s_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1414.1446095097285, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.054467679163508365, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.054467679163508365, "min_effective_sample_size": 28.11182167351473, "n_components": 1, "n_posterior_samples": 750, "name": "B1_low", "posterior_weight": 6.046591250983731e-123, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 508.2127926199669, "swap_acceptance": 0.6409090909090909}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1412.325251368904, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.23004256946660462, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.23004256946660462, "min_effective_sample_size": 29.94752895534675, "n_components": 2, "n_posterior_samples": 750, "name": "B2_low_mid", "posterior_weight": 3.7294759637654493e-122, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 487.69677387188085, "swap_acceptance": 0.6045454545454545}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1258.844116706839, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.5519616655608388, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.5519616655608388, "min_effective_sample_size": 8.673230635212724, "n_components": 2, "n_posterior_samples": 750, "name": "B2b_low_oxide", "posterior_weight": 1.6891089864706996e-55, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 174.68620723293805, "swap_acceptance": 0.5512121212121213}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1132.726137755128, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.6852117945099963, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.6852117945099963, "min_effective_sample_size": 3.8824174405983016, "n_components": 3, "n_posterior_samples": 750, "name": "B3_low_mid_oxide", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 60.05619432298507, "swap_acceptance": 0.5248484848484849}], "confidence": {"main_b_low": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 3.9 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 7619.8764039604175, "ci_level": 0.68, "ci_low": 7564.848768042683, "ess": 3.8824174405983016, "median": 7587.797092193534}, "center": {"ci_high": 187.2239123147272, "ci_level": 0.68, "ci_low": 187.21255689260317, "ess": 4.533738964469063, "median": 187.2166650448847}, "fwhm": {"ci_high": 1.775658982341081, "ci_level": 0.68, "ci_low": 1.7544109150178462, "ess": 6.397270423336882, "median": 1.763174415394593}, "gl_ratio": {"ci_high": 0.021055777524161774, "ci_level": 0.68, "ci_low": 0.0031711942216604496, "ess": 43.259897691843626, "median": 0.008165577815326695}}}}, "main_b_mid": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 4.2 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1264.2684964303573, "ci_level": 0.68, "ci_low": 1173.6748484102884, "ess": 4.2050978921108095, "median": 1202.3288273097883}, "center": {"ci_high": 188.78635837018973, "ci_level": 0.68, "ci_low": 188.72556170461263, "ess": 5.556151274413758, "median": 188.7519308130714}, "fwhm": {"ci_high": 1.3252348232085043, "ci_level": 0.68, "ci_low": 1.2245872602970858, "ess": 6.684068092318436, "median": 1.288085363643988}, "gl_ratio": {"ci_high": 0.10547080386716567, "ci_level": 0.68, "ci_low": 0.01347393001073877, "ess": 14.882244208328615, "median": 0.04391574519959192}}}}, "main_b_oxide": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 10.3 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1939.2769316822266, "ci_level": 0.68, "ci_low": 1902.1503752908502, "ess": 10.310705533430731, "median": 1928.2487500788448}, "center": {"ci_high": 192.99339608739848, "ci_level": 0.68, "ci_low": 192.97910378046183, "ess": 113.28088332962493, "median": 192.9867166217856}, "fwhm": {"ci_high": 1.382715460264016, "ci_level": 0.68, "ci_low": 1.345145419555262, "ess": 25.653103396209787, "median": 1.363373666357709}, "gl_ratio": {"ci_high": 0.02103576888481281, "ci_level": 0.68, "ci_low": 0.003689621269456094, "ess": 98.19697104146002, "median": 0.008633664044168349}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.4265863110880088, "peaks": [{"amplitude": 1983.7464958794415, "center": 188.5451767387288, "fwhm": 1.8525484474576044, "name": "B-B", "shape": "GL"}, {"amplitude": 2300.416063771059, "center": 192.99838091823622, "fwhm": 1.6179616826553664, "name": "B-O", "shape": "Gaussian"}, {"amplitude": 7387.003496848665, "center": 187.16003377896104, "fwhm": 1.6686511208264643, "name": "B-C", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 7587.797092193534, "center": 187.2166650448847, "fwhm": 1.763174415394593, "gl_ratio": 0.008165577815326695, "phase_id": "B4C", "region": "B 1s", "role": "main_b_low", "shape": "pseudo_voigt_gl"}, {"amplitude": 1202.3288273097883, "center": 188.7519308130714, "fwhm": 1.288085363643988, "gl_ratio": 0.04391574519959192, "phase_id": "B4C", "region": "B 1s", "role": "main_b_mid", "shape": "pseudo_voigt_gl"}, {"amplitude": 1928.2487500788448, "center": 192.9867166217856, "fwhm": 1.363373666357709, "gl_ratio": 0.008633664044168349, "phase_id": "B4C", "region": "B 1s", "role": "main_b_oxide", "shape": "pseudo_voigt_gl"}], "runtime_s": 46.8, "seed": 0, "selection_warning": null, "sigma_hat": 60.05619432298507, "success": true, "winner": "B3_low_mid_oxide"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:21:{"anchor": "B1s_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1413.7405763887264, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.46990168059437565, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.46990168059437565, "min_effective_sample_size": 22.249736502985158, "n_components": 1, "n_posterior_samples": 750, "name": "B1_low", "posterior_weight": 4.476565736312204e-120, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 507.6701416127054, "swap_acceptance": 0.6427272727272727}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1413.198045415932, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.5324721125783753, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.5324721125783753, "min_effective_sample_size": 14.57689732344871, "n_components": 2, "n_posterior_samples": 750, "name": "B2_low_mid", "posterior_weight": 7.701284618647388e-120, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 489.9342836748387, "swap_acceptance": 0.6072727272727273}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1260.1739489695615, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.0365377028051626, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.0365377028051626, "min_effective_sample_size": 39.03372763584081, "n_components": 2, "n_posterior_samples": 750, "name": "B2b_low_oxide", "posterior_weight": 2.2084311229283606e-53, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 174.41885149956727, "swap_acceptance": 0.5581818181818182}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1138.9292214051816, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 2.3548727845972053, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 2.3548727845972053, "min_effective_sample_size": 3.130689636804131, "n_components": 3, "n_posterior_samples": 750, "name": "B3_low_mid_oxide", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 68.85627844978742, "swap_acceptance": 0.5160606060606061}], "confidence": {"main_b_low": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 3.1 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 6596.299469343896, "ci_level": 0.68, "ci_low": 6540.290756712629, "ess": 3.130689636804131, "median": 6594.130468267339}, "center": {"ci_high": 187.08811322108136, "ci_level": 0.68, "ci_low": 187.08279182988323, "ess": 21.74366269175579, "median": 187.08473673198245}, "fwhm": {"ci_high": 1.630200464842896, "ci_level": 0.68, "ci_low": 1.6106314523360055, "ess": 17.75563654448041, "median": 1.622794181068513}, "gl_ratio": {"ci_high": 0.05707441724049389, "ci_level": 0.68, "ci_low": 0.014621193646132052, "ess": 31.441557562197808, "median": 0.03613551860862395}}}}, "main_b_mid": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 9.6 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2272.6860459848267, "ci_level": 0.68, "ci_low": 2249.161431306663, "ess": 9.696751483963975, "median": 2265.373088798972}, "center": {"ci_high": 188.16269174641837, "ci_level": 0.68, "ci_low": 188.1329846972973, "ess": 9.585566241795307, "median": 188.1502856627342}, "fwhm": {"ci_high": 1.9253457585262694, "ci_level": 0.68, "ci_low": 1.8785172793574232, "ess": 10.966436684093182, "median": 1.8965642988654738}, "gl_ratio": {"ci_high": 0.026406252779331223, "ci_level": 0.68, "ci_low": 0.0019985767279157227, "ess": 104.92088316460394, "median": 0.011058127597503048}}}}, "main_b_oxide": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 17.3 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1948.2788202825504, "ci_level": 0.68, "ci_low": 1902.4186876898884, "ess": 17.32858169723233, "median": 1940.792255716696}, "center": {"ci_high": 192.99709264472017, "ci_level": 0.68, "ci_low": 192.97436049026325, "ess": 136.59116926339055, "median": 192.9861895568562}, "fwhm": {"ci_high": 1.377622581530415, "ci_level": 0.68, "ci_low": 1.3382936186890901, "ess": 51.428191202710806, "median": 1.3587520049937853}, "gl_ratio": {"ci_high": 0.01966165565775624, "ci_level": 0.68, "ci_low": 0.0020148391143290654, "ess": 80.1221996260108, "median": 0.006046841354004666}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.4265863110880088, "peaks": [{"amplitude": 1983.7464958794415, "center": 188.5451767387288, "fwhm": 1.8525484474576044, "name": "B-B", "shape": "GL"}, {"amplitude": 2300.416063771059, "center": 192.99838091823622, "fwhm": 1.6179616826553664, "name": "B-O", "shape": "Gaussian"}, {"amplitude": 7387.003496848665, "center": 187.16003377896104, "fwhm": 1.6686511208264643, "name": "B-C", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 6594.130468267339, "center": 187.08473673198245, "fwhm": 1.622794181068513, "gl_ratio": 0.03613551860862395, "phase_id": "B4C", "region": "B 1s", "role": "main_b_low", "shape": "pseudo_voigt_gl"}, {"amplitude": 2265.373088798972, "center": 188.1502856627342, "fwhm": 1.8965642988654738, "gl_ratio": 0.011058127597503048, "phase_id": "B4C", "region": "B 1s", "role": "main_b_mid", "shape": "pseudo_voigt_gl"}, {"amplitude": 1940.792255716696, "center": 192.9861895568562, "fwhm": 1.3587520049937853, "gl_ratio": 0.006046841354004666, "phase_id": "B4C", "region": "B 1s", "role": "main_b_oxide", "shape": "pseudo_voigt_gl"}], "runtime_s": 48.2, "seed": 1, "selection_warning": null, "sigma_hat": 68.85627844978742, "success": true, "winner": "B3_low_mid_oxide"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:22:{"anchor": "B1s_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1413.0076354193393, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.0998841712660123, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.0998841712660123, "min_effective_sample_size": 32.17118744480364, "n_components": 1, "n_posterior_samples": 750, "name": "B1_low", "posterior_weight": 7.528322654827258e-117, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 508.17939986159024, "swap_acceptance": 0.5285714285714286}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1412.3062608489947, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.9887185524021334, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.9887185524021334, "min_effective_sample_size": 11.223927897577086, "n_components": 2, "n_posterior_samples": 750, "name": "B2_low_mid", "posterior_weight": 1.518103319161062e-116, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 494.69013727551624, "swap_acceptance": 0.5228571428571429}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1258.5473670520996, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 3.6395301063473653, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 3.6395301063473653, "min_effective_sample_size": 6.1374114879142105, "n_components": 2, "n_posterior_samples": 750, "name": "B2b_low_oxide", "posterior_weight": 9.076960579485433e-50, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 174.68011034418896, "swap_acceptance": 0.48428571428571426}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1145.6238518010312, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 5.837187186629876, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 5.837187186629876, "min_effective_sample_size": 4.2460043646437065, "n_components": 3, "n_posterior_samples": 750, "name": "B3_low_mid_oxide", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 59.95188562998825, "swap_acceptance": 0.4976190476190476}], "confidence": {"main_b_low": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 4.2 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 7658.501778945259, "ci_level": 0.68, "ci_low": 7600.973184836577, "ess": 4.2460043646437065, "median": 7621.842021672549}, "center": {"ci_high": 187.22898260832628, "ci_level": 0.68, "ci_low": 187.2193916358978, "ess": 7.628252859393342, "median": 187.22287639465253}, "fwhm": {"ci_high": 1.7803901950990555, "ci_level": 0.68, "ci_low": 1.7607856911448554, "ess": 8.452239256833268, "median": 1.7706006953286697}, "gl_ratio": {"ci_high": 0.02428367820956802, "ci_level": 0.68, "ci_low": 0.005836497507770347, "ess": 34.01904067064389, "median": 0.011870385974819419}}}}, "main_b_mid": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 6.3 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1200.309212213574, "ci_level": 0.68, "ci_low": 1162.519392317275, "ess": 6.281031995420664, "median": 1182.2223296530055}, "center": {"ci_high": 188.8024361093008, "ci_level": 0.68, "ci_low": 188.75573022693322, "ess": 8.654530654489452, "median": 188.77642011885953}, "fwhm": {"ci_high": 1.2872716788347132, "ci_level": 0.68, "ci_low": 1.2080581358554794, "ess": 7.426212103517536, "median": 1.239504930537468}, "gl_ratio": {"ci_high": 0.08630157487525629, "ci_level": 0.68, "ci_low": 0.010126219344727641, "ess": 27.676944770939706, "median": 0.03530781041429584}}}}, "main_b_oxide": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 24.1 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1944.9981824724748, "ci_level": 0.68, "ci_low": 1908.6245461426956, "ess": 24.0850479826758, "median": 1921.1935630576093}, "center": {"ci_high": 192.9946233776622, "ci_level": 0.68, "ci_low": 192.9783358298047, "ess": 67.17294812692002, "median": 192.9839302954117}, "fwhm": {"ci_high": 1.3827117613689872, "ci_level": 0.68, "ci_low": 1.3480580474578745, "ess": 62.188805413432014, "median": 1.365270619381978}, "gl_ratio": {"ci_high": 0.022960514634765884, "ci_level": 0.68, "ci_low": 0.002633272842486928, "ess": 57.309493218407674, "median": 0.00875175496341212}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 8, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.4265863110880088, "peaks": [{"amplitude": 1983.7464958794415, "center": 188.5451767387288, "fwhm": 1.8525484474576044, "name": "B-B", "shape": "GL"}, {"amplitude": 2300.416063771059, "center": 192.99838091823622, "fwhm": 1.6179616826553664, "name": "B-O", "shape": "Gaussian"}, {"amplitude": 7387.003496848665, "center": 187.16003377896104, "fwhm": 1.6686511208264643, "name": "B-C", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 7621.842021672549, "center": 187.22287639465253, "fwhm": 1.7706006953286697, "gl_ratio": 0.011870385974819419, "phase_id": "B4C", "region": "B 1s", "role": "main_b_low", "shape": "pseudo_voigt_gl"}, {"amplitude": 1182.2223296530055, "center": 188.77642011885953, "fwhm": 1.239504930537468, "gl_ratio": 0.03530781041429584, "phase_id": "B4C", "region": "B 1s", "role": "main_b_mid", "shape": "pseudo_voigt_gl"}, {"amplitude": 1921.1935630576093, "center": 192.9839302954117, "fwhm": 1.365270619381978, "gl_ratio": 0.00875175496341212, "phase_id": "B4C", "region": "B 1s", "role": "main_b_oxide", "shape": "pseudo_voigt_gl"}], "runtime_s": 29.2, "seed": 0, "selection_warning": null, "sigma_hat": 59.95188562998825, "success": true, "winner": "B3_low_mid_oxide"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:23:{"anchor": "B1s_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1413.210376032794, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.04822311959276249, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.04822311959276249, "min_effective_sample_size": 29.27924797888823, "n_components": 1, "n_posterior_samples": 750, "name": "B1_low", "posterior_weight": 1.0495710302518739e-132, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 506.992249589657, "swap_acceptance": 0.7284444444444444}, {"ci_reliability_warning": null, "free_energy": 1412.4294089779169, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.06783668501054763, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.06783668501054763, "min_effective_sample_size": 52.361803270684796, "n_components": 2, "n_posterior_samples": 750, "name": "B2_low_mid", "posterior_weight": 2.2918253427337122e-132, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 488.81764693983075, "swap_acceptance": 0.6855555555555556}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1257.6230639266573, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.9927266536028583, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.9927266536028583, "min_effective_sample_size": 18.250360674660282, "n_components": 2, "n_posterior_samples": 750, "name": "B2b_low_oxide", "posterior_weight": 3.905916338895706e-65, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 174.33810883869657, "swap_acceptance": 0.624}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1109.317525295656, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 3.6850363467157194, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 3.6850363467157194, "min_effective_sample_size": 13.32069218506868, "n_components": 3, "n_posterior_samples": 750, "name": "B3_low_mid_oxide", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 59.0913485211063, "swap_acceptance": 0.5797777777777777}], "confidence": {"main_b_low": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 18.6 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 7651.672298442839, "ci_level": 0.68, "ci_low": 7625.6378699406205, "ess": 18.897610895618545, "median": 7643.408460053027}, "center": {"ci_high": 187.22199988776055, "ci_level": 0.68, "ci_low": 187.21198836389456, "ess": 18.574089440886432, "median": 187.21665254374935}, "fwhm": {"ci_high": 1.7662731920840822, "ci_level": 0.68, "ci_low": 1.749504474660967, "ess": 27.62932610120596, "median": 1.7570577365489544}, "gl_ratio": {"ci_high": 0.020014826791031587, "ci_level": 0.68, "ci_low": 0.002574009976078654, "ess": 58.85784169708988, "median": 0.010384242866593351}}}}, "main_b_mid": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 13.3 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1284.0058488497825, "ci_level": 0.68, "ci_low": 1196.9815911775609, "ess": 25.948355229210478, "median": 1241.5032097497442}, "center": {"ci_high": 188.7807636555687, "ci_level": 0.68, "ci_low": 188.733356821269, "ess": 19.828537125191435, "median": 188.75325389291277}, "fwhm": {"ci_high": 1.302116628392737, "ci_level": 0.68, "ci_low": 1.2293709941666429, "ess": 13.32069218506868, "median": 1.259510047643075}, "gl_ratio": {"ci_high": 0.07132171505728042, "ci_level": 0.68, "ci_low": 0.0063782797053482075, "ess": 90.27601588839192, "median": 0.027907728729554014}}}}, "main_b_oxide": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 32.3 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1952.5396523110958, "ci_level": 0.68, "ci_low": 1919.5946546163707, "ess": 32.28745401636339, "median": 1934.5767176374434}, "center": {"ci_high": 192.99355995577787, "ci_level": 0.68, "ci_low": 192.9764314012295, "ess": 151.97004327563067, "median": 192.98463429594935}, "fwhm": {"ci_high": 1.3778009036666699, "ci_level": 0.68, "ci_low": 1.3433984470498883, "ess": 79.84989886368201, "median": 1.359928345374897}, "gl_ratio": {"ci_high": 0.02303377948949193, "ci_level": 0.68, "ci_low": 0.0016638822754074685, "ess": 71.82624016619496, "median": 0.007587149474662942}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 16, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.4265863110880088, "peaks": [{"amplitude": 1983.7464958794415, "center": 188.5451767387288, "fwhm": 1.8525484474576044, "name": "B-B", "shape": "GL"}, {"amplitude": 2300.416063771059, "center": 192.99838091823622, "fwhm": 1.6179616826553664, "name": "B-O", "shape": "Gaussian"}, {"amplitude": 7387.003496848665, "center": 187.16003377896104, "fwhm": 1.6686511208264643, "name": "B-C", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 7643.408460053027, "center": 187.21665254374935, "fwhm": 1.7570577365489544, "gl_ratio": 0.010384242866593351, "phase_id": "B4C", "region": "B 1s", "role": "main_b_low", "shape": "pseudo_voigt_gl"}, {"amplitude": 1241.5032097497442, "center": 188.75325389291277, "fwhm": 1.259510047643075, "gl_ratio": 0.027907728729554014, "phase_id": "B4C", "region": "B 1s", "role": "main_b_mid", "shape": "pseudo_voigt_gl"}, {"amplitude": 1934.5767176374434, "center": 192.98463429594935, "fwhm": 1.359928345374897, "gl_ratio": 0.007587149474662942, "phase_id": "B4C", "region": "B 1s", "role": "main_b_oxide", "shape": "pseudo_voigt_gl"}], "runtime_s": 58.2, "seed": 0, "selection_warning": null, "sigma_hat": 59.0913485211063, "success": true, "winner": "B3_low_mid_oxide"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:24:{"anchor": "B1s_Scan", "candidates": [{"ci_reliability_warning": null, "free_energy": 1413.4600303956488, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.5484967880624936, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.5484967880624936, "min_effective_sample_size": 58.63201054573928, "n_components": 1, "n_posterior_samples": 750, "name": "B1_low", "posterior_weight": 7.641623621444315e-131, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 507.8285560571695, "swap_acceptance": 0.6142424242424243}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1411.9813006045013, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.5523466794041951, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.5523466794041951, "min_effective_sample_size": 6.39124975324663, "n_components": 2, "n_posterior_samples": 750, "name": "B2_low_mid", "posterior_weight": 3.3526624609763228e-130, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 487.5272298419112, "swap_acceptance": 0.5775757575757576}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1257.2554653648308, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.41264928687621705, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.41264928687621705, "min_effective_sample_size": 5.623223851157123, "n_components": 2, "n_posterior_samples": 750, "name": "B2b_low_oxide", "posterior_weight": 5.271889323528165e-63, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 174.59661213803318, "swap_acceptance": 0.49575757575757573}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1113.8549933099248, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.6291624585203408, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.6291624585203408, "min_effective_sample_size": 7.355468641818928, "n_components": 3, "n_posterior_samples": 750, "name": "B3_low_mid_oxide", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 59.40228725549562, "swap_acceptance": 0.44212121212121214}], "confidence": {"main_b_low": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 7.4 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 7641.727153119729, "ci_level": 0.68, "ci_low": 7610.923333438039, "ess": 7.355468641818928, "median": 7629.4423999038945}, "center": {"ci_high": 187.22524087878773, "ci_level": 0.68, "ci_low": 187.20845226790885, "ess": 18.03557769448093, "median": 187.2219414590832}, "fwhm": {"ci_high": 1.773274770269104, "ci_level": 0.68, "ci_low": 1.7469616445750635, "ess": 25.547470044893362, "median": 1.7649508487326289}, "gl_ratio": {"ci_high": 0.02271277276018776, "ci_level": 0.68, "ci_low": 0.004508075432655809, "ess": 118.31089420093302, "median": 0.011800544204547438}}}}, "main_b_mid": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 24.5 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1283.0876486986222, "ci_level": 0.68, "ci_low": 1186.3721591916453, "ess": 24.452037675010047, "median": 1199.0645466240398}, "center": {"ci_high": 188.78600631615012, "ci_level": 0.68, "ci_low": 188.71825742327368, "ess": 25.795684079080033, "median": 188.76960305044278}, "fwhm": {"ci_high": 1.3158193224771846, "ci_level": 0.68, "ci_low": 1.2239688455547453, "ess": 32.553838650613365, "median": 1.257505707414168}, "gl_ratio": {"ci_high": 0.07173455635665632, "ci_level": 0.68, "ci_low": 0.008972339647994527, "ess": 98.325190417954, "median": 0.030095641679549503}}}}, "main_b_oxide": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1945.7049116361195, "ci_level": 0.68, "ci_low": 1910.910701176508, "ess": 52.72260179255196, "median": 1930.9558890507694}, "center": {"ci_high": 192.99264121980642, "ci_level": 0.68, "ci_low": 192.9782648903643, "ess": 93.28269285796362, "median": 192.98498651799838}, "fwhm": {"ci_high": 1.3775751034369974, "ci_level": 0.68, "ci_low": 1.3460398557156732, "ess": 95.28496735263158, "median": 1.3609334161312503}, "gl_ratio": {"ci_high": 0.021419752050041218, "ci_level": 0.68, "ci_low": 0.0025231515887322777, "ess": 90.09124150882795, "median": 0.007013318194780424}}}}}, "config": {"beta_min": 0.001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.4265863110880088, "peaks": [{"amplitude": 1983.7464958794415, "center": 188.5451767387288, "fwhm": 1.8525484474576044, "name": "B-B", "shape": "GL"}, {"amplitude": 2300.416063771059, "center": 192.99838091823622, "fwhm": 1.6179616826553664, "name": "B-O", "shape": "Gaussian"}, {"amplitude": 7387.003496848665, "center": 187.16003377896104, "fwhm": 1.6686511208264643, "name": "B-C", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 7629.4423999038945, "center": 187.2219414590832, "fwhm": 1.7649508487326289, "gl_ratio": 0.011800544204547438, "phase_id": "B4C", "region": "B 1s", "role": "main_b_low", "shape": "pseudo_voigt_gl"}, {"amplitude": 1199.0645466240398, "center": 188.76960305044278, "fwhm": 1.257505707414168, "gl_ratio": 0.030095641679549503, "phase_id": "B4C", "region": "B 1s", "role": "main_b_mid", "shape": "pseudo_voigt_gl"}, {"amplitude": 1930.9558890507694, "center": 192.98498651799838, "fwhm": 1.3609334161312503, "gl_ratio": 0.007013318194780424, "phase_id": "B4C", "region": "B 1s", "role": "main_b_oxide", "shape": "pseudo_voigt_gl"}], "runtime_s": 44.5, "seed": 0, "selection_warning": null, "sigma_hat": 59.40228725549562, "success": true, "winner": "B3_low_mid_oxide"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:25:{"anchor": "B1s_Scan", "candidates": [{"ci_reliability_warning": null, "free_energy": 1413.6898772940876, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.007328532410042499, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.007328532410042499, "min_effective_sample_size": 71.64768090834633, "n_components": 1, "n_posterior_samples": 1500, "name": "B1_low", "posterior_weight": 1.156799676755115e-125, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 507.764494143447, "swap_acceptance": 0.6472727272727272}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1411.5092232494785, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.18104184864034778, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.18104184864034778, "min_effective_sample_size": 6.870484847009758, "n_components": 2, "n_posterior_samples": 1500, "name": "B2_low_mid", "posterior_weight": 1.0240099512699741e-124, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 489.7944564329689, "swap_acceptance": 0.610909090909091}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1257.0782437895596, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.2940345163428901, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.2940345163428901, "min_effective_sample_size": 24.7371468862308, "n_components": 2, "n_posterior_samples": 1500, "name": "B2b_low_oxide", "posterior_weight": 1.1990199010229014e-57, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 174.3724037639264, "swap_acceptance": 0.5516666666666666}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1126.012397962824, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.4345819584983701, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.4345819584983701, "min_effective_sample_size": 8.106901851998598, "n_components": 3, "n_posterior_samples": 1500, "name": "B3_low_mid_oxide", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 59.23882436722428, "swap_acceptance": 0.5156060606060606}], "confidence": {"main_b_low": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 8.1 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 7670.140610066042, "ci_level": 0.68, "ci_low": 7601.693606120662, "ess": 8.106901851998598, "median": 7647.732589266062}, "center": {"ci_high": 187.22025484957396, "ci_level": 0.68, "ci_low": 187.20743904991738, "ess": 10.145871688913495, "median": 187.21617504716446}, "fwhm": {"ci_high": 1.7610519016146597, "ci_level": 0.68, "ci_low": 1.7397020857715058, "ess": 13.990273819749675, "median": 1.7535530799302594}, "gl_ratio": {"ci_high": 0.024508293358690453, "ci_level": 0.68, "ci_low": 0.004347700753346661, "ess": 58.661806879604704, "median": 0.012920510915067619}}}}, "main_b_mid": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 9.5 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1283.672119834878, "ci_level": 0.68, "ci_low": 1225.2153245253578, "ess": 10.669088692425388, "median": 1253.3004644855182}, "center": {"ci_high": 188.76982199534106, "ci_level": 0.68, "ci_low": 188.70871270456632, "ess": 9.580696858501057, "median": 188.74765970853136}, "fwhm": {"ci_high": 1.3263387075602255, "ci_level": 0.68, "ci_low": 1.2317951281927495, "ess": 9.456606314408008, "median": 1.2671596817650383}, "gl_ratio": {"ci_high": 0.06506969723332602, "ci_level": 0.68, "ci_low": 0.007607993936555427, "ess": 25.867895197904673, "median": 0.028982939721730997}}}}, "main_b_oxide": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1955.3428450444676, "ci_level": 0.68, "ci_low": 1903.4072312698902, "ess": 54.52394879619008, "median": 1932.9517409256027}, "center": {"ci_high": 192.9945136129011, "ci_level": 0.68, "ci_low": 192.97703120598402, "ess": 270.73130879652894, "median": 192.98608182777153}, "fwhm": {"ci_high": 1.3768747869285687, "ci_level": 0.68, "ci_low": 1.3422931290205722, "ess": 142.13297354586385, "median": 1.3595129033599869}, "gl_ratio": {"ci_high": 0.018220181704691266, "ci_level": 0.68, "ci_low": 0.001481124875119305, "ess": 196.5313780856996, "median": 0.006421581131814116}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 3000}, "expert": {"chi_reduced": 1.4265863110880088, "peaks": [{"amplitude": 1983.7464958794415, "center": 188.5451767387288, "fwhm": 1.8525484474576044, "name": "B-B", "shape": "GL"}, {"amplitude": 2300.416063771059, "center": 192.99838091823622, "fwhm": 1.6179616826553664, "name": "B-O", "shape": "Gaussian"}, {"amplitude": 7387.003496848665, "center": 187.16003377896104, "fwhm": 1.6686511208264643, "name": "B-C", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 7647.732589266062, "center": 187.21617504716446, "fwhm": 1.7535530799302594, "gl_ratio": 0.012920510915067619, "phase_id": "B4C", "region": "B 1s", "role": "main_b_low", "shape": "pseudo_voigt_gl"}, {"amplitude": 1253.3004644855182, "center": 188.74765970853136, "fwhm": 1.2671596817650383, "gl_ratio": 0.028982939721730997, "phase_id": "B4C", "region": "B 1s", "role": "main_b_mid", "shape": "pseudo_voigt_gl"}, {"amplitude": 1932.9517409256027, "center": 192.98608182777153, "fwhm": 1.3595129033599869, "gl_ratio": 0.006421581131814116, "phase_id": "B4C", "region": "B 1s", "role": "main_b_oxide", "shape": "pseudo_voigt_gl"}], "runtime_s": 85.9, "seed": 0, "selection_warning": null, "sigma_hat": 59.23882436722428, "success": true, "winner": "B3_low_mid_oxide"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:26:{"anchor": "B1s_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1413.1999238792664, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.866677485751552, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.866677485751552, "min_effective_sample_size": 35.632418047077856, "n_components": 1, "n_posterior_samples": 750, "name": "B1_low", "posterior_weight": 2.949469692344706e-125, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 507.6086807894321, "swap_acceptance": 0.652060606060606}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1412.0257670412032, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.38431644591469194, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.38431644591469194, "min_effective_sample_size": 12.963270777940188, "n_components": 2, "n_posterior_samples": 750, "name": "B2_low_mid", "posterior_weight": 9.542754991518356e-125, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 489.6585539708442, "swap_acceptance": 0.618909090909091}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1256.540287523414, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.37527074208128397, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.37527074208128397, "min_effective_sample_size": 15.344219712851704, "n_components": 2, "n_posterior_samples": 750, "name": "B2b_low_oxide", "posterior_weight": 3.207447409089668e-57, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 174.4391713435091, "swap_acceptance": 0.5596969696969697}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1126.4584126438958, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.4200021174575568, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.4200021174575568, "min_effective_sample_size": 4.6557101063479065, "n_components": 3, "n_posterior_samples": 750, "name": "B3_low_mid_oxide", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 63.682634075625494, "swap_acceptance": 0.5184848484848484}], "confidence": {"main_b_low": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 4.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 7432.042952644995, "ci_level": 0.68, "ci_low": 7369.672213678771, "ess": 4.6557101063479065, "median": 7409.384148323155}, "center": {"ci_high": 187.1672412890168, "ci_level": 0.68, "ci_low": 187.15972952214327, "ess": 63.67634946402745, "median": 187.16404866042552}, "fwhm": {"ci_high": 1.6978824517708948, "ci_level": 0.68, "ci_low": 1.6811019847232869, "ess": 78.8864666486914, "median": 1.6904906873501906}, "gl_ratio": {"ci_high": 0.034654945534850094, "ci_level": 0.68, "ci_low": 0.007358236976773209, "ess": 66.83364636273355, "median": 0.02031714768119395}}}}, "main_b_mid": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 6.1 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1578.0738442320348, "ci_level": 0.68, "ci_low": 1547.8971174329893, "ess": 125.27247181401422, "median": 1564.6689800295997}, "center": {"ci_high": 188.53376499305745, "ci_level": 0.68, "ci_low": 188.4993116510486, "ess": 16.38450940564348, "median": 188.51640960869923}, "fwhm": {"ci_high": 1.6030118803127937, "ci_level": 0.68, "ci_low": 1.5399761651737398, "ess": 6.118943760309785, "median": 1.5735833014213751}, "gl_ratio": {"ci_high": 0.04262316096861588, "ci_level": 0.68, "ci_low": 0.003249271702501714, "ess": 121.6723462479397, "median": 0.013346837816506911}}}}, "main_b_oxide": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 24.5 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1947.1858738417075, "ci_level": 0.68, "ci_low": 1913.8382472234769, "ess": 24.488445044379265, "median": 1937.1158079413503}, "center": {"ci_high": 192.99551578417888, "ci_level": 0.68, "ci_low": 192.97910231299826, "ess": 126.42153928053085, "median": 192.98773890148692}, "fwhm": {"ci_high": 1.374989533052308, "ci_level": 0.68, "ci_low": 1.3399339610646408, "ess": 138.8381137944305, "median": 1.3581051891151787}, "gl_ratio": {"ci_high": 0.022957982832889162, "ci_level": 0.68, "ci_low": 0.002367063984425601, "ess": 84.55678036380489, "median": 0.009953014716786066}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 1, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.4265863110880088, "peaks": [{"amplitude": 1983.7464958794415, "center": 188.5451767387288, "fwhm": 1.8525484474576044, "name": "B-B", "shape": "GL"}, {"amplitude": 2300.416063771059, "center": 192.99838091823622, "fwhm": 1.6179616826553664, "name": "B-O", "shape": "Gaussian"}, {"amplitude": 7387.003496848665, "center": 187.16003377896104, "fwhm": 1.6686511208264643, "name": "B-C", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 7409.384148323155, "center": 187.16404866042552, "fwhm": 1.6904906873501906, "gl_ratio": 0.02031714768119395, "phase_id": "B4C", "region": "B 1s", "role": "main_b_low", "shape": "pseudo_voigt_gl"}, {"amplitude": 1564.6689800295997, "center": 188.51640960869923, "fwhm": 1.5735833014213751, "gl_ratio": 0.013346837816506911, "phase_id": "B4C", "region": "B 1s", "role": "main_b_mid", "shape": "pseudo_voigt_gl"}, {"amplitude": 1937.1158079413503, "center": 192.98773890148692, "fwhm": 1.3581051891151787, "gl_ratio": 0.009953014716786066, "phase_id": "B4C", "region": "B 1s", "role": "main_b_oxide", "shape": "pseudo_voigt_gl"}], "runtime_s": 45.0, "seed": 0, "selection_warning": null, "sigma_hat": 63.682634075625494, "success": true, "winner": "B3_low_mid_oxide"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:27:{"anchor": "B1s_Scan", "candidates": [{"ci_reliability_warning": null, "free_energy": 1413.5914176737938, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.009392260242407247, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.009392260242407247, "min_effective_sample_size": 53.097123072982306, "n_components": 1, "n_posterior_samples": 1050, "name": "B1_low", "posterior_weight": 2.22341956876447e-124, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 508.0376815326401, "swap_acceptance": 0.6445454545454545}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1411.1743369792453, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.22232719902876852, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.22232719902876852, "min_effective_sample_size": 17.333118818519388, "n_components": 2, "n_posterior_samples": 1050, "name": "B2_low_mid", "posterior_weight": 2.493137502891001e-123, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 487.7802620998975, "swap_acceptance": 0.6133333333333333}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1259.1300182709588, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.11730224526343136, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.11730224526343136, "min_effective_sample_size": 18.952576617230623, "n_components": 2, "n_posterior_samples": 1050, "name": "B2b_low_oxide", "posterior_weight": 2.683829061973386e-57, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 174.85975519924563, "swap_acceptance": 0.5596969696969697}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1128.86991249959, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 2.353747431324905, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 2.353747431324905, "min_effective_sample_size": 5.184530874642533, "n_components": 3, "n_posterior_samples": 1050, "name": "B3_low_mid_oxide", "posterior_weight": 1.0, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 59.788007927502406, "swap_acceptance": 0.5181818181818182}], "confidence": {"main_b_low": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 7.1 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 7624.230833268837, "ci_level": 0.68, "ci_low": 7600.819292486143, "ess": 7.120691885466271, "median": 7620.02776201325}, "center": {"ci_high": 187.2012517885317, "ci_level": 0.68, "ci_low": 187.19477515464087, "ess": 16.510650041858643, "median": 187.1996358659438}, "fwhm": {"ci_high": 1.7307958504627785, "ci_level": 0.68, "ci_low": 1.7180968714290874, "ess": 22.160941553410016, "median": 1.7240005406135293}, "gl_ratio": {"ci_high": 0.030016574866597888, "ci_level": 0.68, "ci_low": 0.0057592061623693526, "ess": 33.58720561061282, "median": 0.016201929271977878}}}}, "main_b_mid": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 5.2 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1381.369605229491, "ci_level": 0.68, "ci_low": 1363.3365491609404, "ess": 5.184530874642533, "median": 1364.9890763916376}, "center": {"ci_high": 188.69458421691232, "ci_level": 0.68, "ci_low": 188.66118456709114, "ess": 24.036876190646577, "median": 188.67290251573925}, "fwhm": {"ci_high": 1.378300325638229, "ci_level": 0.68, "ci_low": 1.3206315383664249, "ess": 28.264869836868602, "median": 1.351245864587704}, "gl_ratio": {"ci_high": 0.058269066769517514, "ci_level": 0.68, "ci_low": 0.006299393459841925, "ess": 56.119119054489474, "median": 0.025128313712362647}}}}, "main_b_oxide": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 31.0 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1948.8523114223283, "ci_level": 0.68, "ci_low": 1908.813573068154, "ess": 31.005640546801597, "median": 1923.4348362315156}, "center": {"ci_high": 192.99248392965248, "ci_level": 0.68, "ci_low": 192.97763839644293, "ess": 85.12057391557299, "median": 192.9851493784654}, "fwhm": {"ci_high": 1.3780184432804041, "ci_level": 0.68, "ci_low": 1.3450004247362337, "ess": 90.54492494555609, "median": 1.3594343587187774}, "gl_ratio": {"ci_high": 0.021675723437439773, "ci_level": 0.68, "ci_low": 0.0020610736973662724, "ess": 106.77062474817896, "median": 0.0077218893169545555}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.3, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.4265863110880088, "peaks": [{"amplitude": 1983.7464958794415, "center": 188.5451767387288, "fwhm": 1.8525484474576044, "name": "B-B", "shape": "GL"}, {"amplitude": 2300.416063771059, "center": 192.99838091823622, "fwhm": 1.6179616826553664, "name": "B-O", "shape": "Gaussian"}, {"amplitude": 7387.003496848665, "center": 187.16003377896104, "fwhm": 1.6686511208264643, "name": "B-C", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 7620.02776201325, "center": 187.1996358659438, "fwhm": 1.7240005406135293, "gl_ratio": 0.016201929271977878, "phase_id": "B4C", "region": "B 1s", "role": "main_b_low", "shape": "pseudo_voigt_gl"}, {"amplitude": 1364.9890763916376, "center": 188.67290251573925, "fwhm": 1.351245864587704, "gl_ratio": 0.025128313712362647, "phase_id": "B4C", "region": "B 1s", "role": "main_b_mid", "shape": "pseudo_voigt_gl"}, {"amplitude": 1923.4348362315156, "center": 192.9851493784654, "fwhm": 1.3594343587187774, "gl_ratio": 0.0077218893169545555, "phase_id": "B4C", "region": "B 1s", "role": "main_b_oxide", "shape": "pseudo_voigt_gl"}], "runtime_s": 46.2, "seed": 0, "selection_warning": null, "sigma_hat": 59.788007927502406, "success": true, "winner": "B3_low_mid_oxide"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:28:{"anchor": "U4f_Scan", "candidates": [{"bic_star": 4486.2345563620875, "boundary_hits": ["main_u4f72:fwhm@min", "main_u4f52:ratio@min"], "conditional": null, "name": "U0_mains", "rank": null, "reduced_chi_sq": 29.134009265742645}, {"bic_star": 3568.1413539281757, "boundary_hits": ["satellite_u4f52:offset@max", "satellite_u4f52:ratio@max"], "conditional": null, "name": "U1_mains_satpair", "rank": null, "reduced_chi_sq": 1.9766454475099426}, {"bic_star": 3512.9238853325796, "boundary_hits": ["satellite_u4f52:ratio@max"], "conditional": null, "name": "U1b_mains_satpair_freesep", "rank": null, "reduced_chi_sq": 1.6794087359924286}, {"bic_star": 3454.0587846694775, "boundary_hits": [], "conditional": null, "name": "U2_mains_satfree", "rank": 1, "reduced_chi_sq": 1.3957888681832606}], "conditional": null, "config": {"enable_proposal_pass": false, "n_refits": 4, "noise_floor": 1.0, "rng_seed": 0}, "expert": {"chi_reduced": 1.7129708462685973, "peaks": [{"amplitude": 16166.479492182621, "center": 380.6179633862216, "fwhm": 2.737096332065471, "name": "U 4f7/2", "shape": "LACX"}, {"amplitude": 10508.211669918705, "center": 391.5179633862216, "fwhm": 2.737096332065471, "name": "U 4f5/2", "shape": "LACX"}, {"amplitude": 2214.057182779663, "center": 397.8977471164976, "fwhm": 2.556902102730025, "name": "Satellite 2", "shape": "Voigt"}, {"amplitude": 2436.210453422618, "center": 386.6877864274504, "fwhm": 2.512044323701672, "name": "Satellite 1", "shape": "Voigt"}]}, "method": "ic_model_comparison", "peaks": [{"alpha": 1.1929683541174385, "amplitude": 16147.374185747914, "beta": 2.7244542537388607, "center": 380.63175029067355, "fwhm": 2.651934019549572, "m": 5.680148780270161, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f72", "shape": "la_casaxps", "stderr": {"alpha": 0.03362315035319755, "amplitude": 65.45952859906556, "beta": 0.026030429527573055, "center": 0.007702915364359588, "fwhm": 0.08198054101319714, "m": 1.2179429154636825}}, {"alpha": 1.1929683541174385, "amplitude": 10589.893565256372, "beta": 2.7244542537388607, "center": 391.485155325005, "fwhm": 2.651934019549572, "m": 5.680148780270161, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f52", "shape": "la_casaxps", "stderr": {"alpha": 0.03362315033943434, "amplitude": 52.6687950480711, "beta": 0.026030429529227024, "center": 0.008691400058028013, "fwhm": 0.08198054080363705, "m": 1.2179429154799262, "offset": 0.005675594606790693, "ratio": 0.0031883679684345536}}, {"amplitude": 2368.323826734655, "center": 386.7004235249773, "fwhm": 2.5000746190644314, "gl_ratio": 0.599042750876529, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f72", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 51.58940057597443, "center": 0.01988856629661784, "fwhm": 0.06916678675947037, "gl_ratio": 0.11648158965102576, "offset": 0.022687845680594163}}, {"amplitude": 2202.2677860329227, "center": 397.8992514516975, "fwhm": 2.5324190034815364, "gl_ratio": 4.1807821952732915e-06, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f52", "shape": "pseudo_voigt_gl", "stderr": {"amplitude": 44.740252714257174, "center": 0.020686764127437675, "fwhm": 0.05667275476382342, "gl_ratio": 0.079882375340173, "offset": 0.02344656058738351}}], "runtime_s": 10.8, "seed": 0, "success": true, "winner": "U2_mains_satfree"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:29:{"anchor": "U4f_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 3275.143842059182, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.07512604961107172, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.07512604961107172, "min_effective_sample_size": 6.576873550871323, "n_components": 2, "n_posterior_samples": 750, "name": "U0_mains", "posterior_weight": 9.977754927780837e-206, "posterior_weight_reliable": true, "rank": 4, "sigma_hat": 574.3525085569566, "swap_acceptance": 0.5045454545454545}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2837.113926377493, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.0073423184153398, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.0073423184153398, "min_effective_sample_size": 3.1609685868208746, "n_components": 4, "n_posterior_samples": 750, "name": "U1_mains_satpair", "posterior_weight": 1.710047294452894e-15, "posterior_weight_reliable": true, "rank": 3, "sigma_hat": 151.1768203353449, "swap_acceptance": 0.4487878787878788}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2803.153312658433, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.0981159498237503, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.0981159498237503, "min_effective_sample_size": 3.0607289931766535, "n_components": 4, "n_posterior_samples": 750, "name": "U1b_mains_satpair_freesep", "posterior_weight": 0.9592134549126059, "posterior_weight_reliable": true, "rank": 1, "sigma_hat": 137.0369805115589, "swap_acceptance": 0.44515151515151513}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2806.3110740395196, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.286025999778758, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.286025999778758, "min_effective_sample_size": 2.6119870811326766, "n_components": 4, "n_posterior_samples": 750, "name": "U2_mains_satfree", "posterior_weight": 0.040786545087392344, "posterior_weight_reliable": true, "rank": 2, "sigma_hat": 125.28536795174338, "swap_acceptance": 0.45515151515151514}], "confidence": {"main_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "ok", "reliability_note": null, "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 10.850261633646841, "ci_level": 0.68, "ci_low": 10.840709249885967, "ess": 71.93924089092587, "median": 10.845143851273434}, "ratio": {"ci_high": 0.6635475304895153, "ci_level": 0.68, "ci_low": 0.6588772499992596, "ess": 136.11917913911302, "median": 0.6610971283491758}}}}, "main_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 3.1 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"alpha": {"ci_high": 1.2197126677458525, "ci_level": 0.68, "ci_low": 1.156437001016647, "ess": 3.113225315117738, "median": 1.20898511200007}, "amplitude": {"ci_high": 16159.078749739467, "ci_level": 0.68, "ci_low": 16137.691286978325, "ess": 6.060904187091269, "median": 16148.671718978323}, "beta": {"ci_high": 2.8007926160774073, "ci_level": 0.68, "ci_low": 2.5984820884701536, "ess": 3.0607289931766535, "median": 2.7448559086222994}, "center": {"ci_high": 380.63847192647637, "ci_level": 0.68, "ci_low": 380.6335760417565, "ess": 5.1195981381135525, "median": 380.63760169621736}, "fwhm": {"ci_high": 2.755956709209375, "ci_level": 0.68, "ci_low": 2.6047059663659096, "ess": 3.1021883279644245, "median": 2.7205941414067025}, "m": {"ci_high": 5.783422031978548, "ci_level": 0.68, "ci_low": 4.458119033369167, "ess": 21.840636868252698, "median": 4.91243170100973}}}}, "satellite_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 26.4 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 11.216631331687328, "ci_level": 0.68, "ci_low": 11.154029062478353, "ess": 26.43979089742022, "median": 11.189574463886249}, "ratio": {"ci_high": 0.8494164681991332, "ci_level": 0.68, "ci_low": 0.8444825625425573, "ess": 85.93479044911935, "median": 0.8477156839710492}}}}, "satellite_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 8.1 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2461.580960114206, "ci_level": 0.68, "ci_low": 2402.1896398114113, "ess": 8.050196931272309, "median": 2420.743726353216}, "fwhm": {"ci_high": 2.6169083021075523, "ci_level": 0.68, "ci_low": 2.51142551525748, "ess": 19.551355197259664, "median": 2.570951457284406}, "gl_ratio": {"ci_high": 0.23286136816703903, "ci_level": 0.68, "ci_low": 0.06263634399130641, "ess": 10.911976798120111, "median": 0.14235869380240743}, "offset": {"ci_high": 6.0994818307358125, "ci_level": 0.68, "ci_low": 6.044909324841423, "ess": 13.990205703377487, "median": 6.0731835996022}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.7129708462685973, "peaks": [{"amplitude": 16166.479492182621, "center": 380.6179633862216, "fwhm": 2.737096332065471, "name": "U 4f7/2", "shape": "LACX"}, {"amplitude": 10508.211669918705, "center": 391.5179633862216, "fwhm": 2.737096332065471, "name": "U 4f5/2", "shape": "LACX"}, {"amplitude": 2214.057182779663, "center": 397.8977471164976, "fwhm": 2.556902102730025, "name": "Satellite 2", "shape": "Voigt"}, {"amplitude": 2436.210453422618, "center": 386.6877864274504, "fwhm": 2.512044323701672, "name": "Satellite 1", "shape": "Voigt"}]}, "method": "bayesian_exchange_mc", "peaks": [{"alpha": 1.20898511200007, "amplitude": 16148.671718978323, "beta": 2.7448559086222994, "center": 380.63760169621736, "fwhm": 2.7205941414067025, "m": 4.91243170100973, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f72", "shape": "la_casaxps"}, {"alpha": 1.20898511200007, "amplitude": 10675.840500070117, "beta": 2.7448559086222994, "center": 391.4827455474908, "fwhm": 2.7205941414067025, "m": 4.91243170100973, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f52", "shape": "la_casaxps"}, {"amplitude": 2420.743726353216, "center": 386.71078529581956, "fwhm": 2.570951457284406, "gl_ratio": 0.14235869380240743, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f72", "shape": "pseudo_voigt_gl"}, {"amplitude": 2052.102423704143, "center": 397.9003597597058, "fwhm": 2.570951457284406, "gl_ratio": 0.14235869380240743, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f52", "shape": "pseudo_voigt_gl"}], "runtime_s": 307.0, "seed": 0, "selection_warning": null, "sigma_hat": 137.0369805115589, "success": true, "winner": "U1b_mains_satpair_freesep"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:30:{"anchor": "U4f_Scan", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 3275.8653945587066, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.14477112745930754, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.14477112745930754, "min_effective_sample_size": 19.28253695057585, "n_components": 2, "n_posterior_samples": 750, "name": "U0_mains", "posterior_weight": 2.464632247092009e-207, "posterior_weight_reliable": false, "rank": 4, "sigma_hat": 573.387468071737, "swap_acceptance": 0.4863636363636364}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2844.2086982208093, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.5815332846641468, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.5815332846641468, "min_effective_sample_size": 3.4385170487557475, "n_components": 4, "n_posterior_samples": 750, "name": "U1_mains_satpair", "posterior_weight": 7.208973392584402e-20, "posterior_weight_reliable": false, "rank": 3, "sigma_hat": 148.66479452995452, "swap_acceptance": 0.43787878787878787}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2806.5777928677244, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.7867632228535513, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.7867632228535513, "min_effective_sample_size": 2.983880808048932, "n_components": 4, "n_posterior_samples": 750, "name": "U1b_mains_satpair_freesep", "posterior_weight": 0.001587698251371118, "posterior_weight_reliable": false, "rank": 2, "sigma_hat": 136.5071227591875, "swap_acceptance": 0.4406060606060606}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 2800.133911875463, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 3.5329734956487755, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 3.5329734956487755, "min_effective_sample_size": 3.754834800879, "n_components": 4, "n_posterior_samples": 750, "name": "U2_mains_satfree", "posterior_weight": 0.9984123017486289, "posterior_weight_reliable": false, "rank": 1, "sigma_hat": 129.25347086856078, "swap_acceptance": 0.4542424242424242}], "confidence": {"main_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 11.2 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"offset": {"ci_high": 10.861757448200263, "ci_level": 0.68, "ci_low": 10.851773176667246, "ess": 48.94615768154585, "median": 10.85727194773624}, "ratio": {"ci_high": 0.6635838075418771, "ci_level": 0.68, "ci_low": 0.6584050540389826, "ess": 11.22488899035955, "median": 0.6605336818820506}}}}, "main_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 3.8 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"alpha": {"ci_high": 1.4216656540911476, "ci_level": 0.68, "ci_low": 1.3571740187030115, "ess": 9.18801526266417, "median": 1.374742342891894}, "amplitude": {"ci_high": 16121.875987554462, "ci_level": 0.68, "ci_low": 15981.63871482141, "ess": 3.754834800879, "median": 15981.63871482141}, "beta": {"ci_high": 3.3978832824587712, "ci_level": 0.68, "ci_low": 3.203817264799955, "ess": 4.502956189506384, "median": 3.2760712391362157}, "center": {"ci_high": 380.6392746735966, "ci_level": 0.68, "ci_low": 380.6157727918216, "ess": 5.589729730663764, "median": 380.6288831574634}, "fwhm": {"ci_high": 3.078861264390619, "ci_level": 0.68, "ci_low": 2.9387071399369615, "ess": 8.055666282099534, "median": 3.0077280400563975}, "m": {"ci_high": 5.754764950755495, "ci_level": 0.68, "ci_low": 2.4922951815072767, "ess": 4.200845794074715, "median": 4.179002142180813}}}}, "satellite_u4f52": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 12.8 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2337.1020488056065, "ci_level": 0.68, "ci_low": 2213.794067767326, "ess": 12.75359891489697, "median": 2272.63776846611}, "fwhm": {"ci_high": 2.678006980740226, "ci_level": 0.68, "ci_low": 2.5322353720844704, "ess": 15.77355528722878, "median": 2.6127209229379984}, "gl_ratio": {"ci_high": 0.1267260573322226, "ci_level": 0.68, "ci_low": 0.02111169644924705, "ess": 88.20047812663083, "median": 0.057495623276168056}, "offset": {"ci_high": 6.417000799780815, "ci_level": 0.68, "ci_low": 6.373933033966472, "ess": 46.12968433352226, "median": 6.3964750597643185}}}}, "satellite_u4f72": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 11.5 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2504.6958783249006, "ci_level": 0.68, "ci_low": 2464.1837781194417, "ess": 11.545264878618854, "median": 2470.604532690152}, "fwhm": {"ci_high": 2.7100130616120204, "ci_level": 0.68, "ci_low": 2.5790498070707066, "ess": 16.450150862408726, "median": 2.6470772568802916}, "gl_ratio": {"ci_high": 0.964886007002836, "ci_level": 0.68, "ci_low": 0.8355605759511769, "ess": 56.692207928860284, "median": 0.9178875257660675}, "offset": {"ci_high": 6.0571560657850165, "ci_level": 0.68, "ci_low": 6.005922631023874, "ess": 21.232672932441368, "median": 6.031726107250276}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.7129708462685973, "peaks": [{"amplitude": 16166.479492182621, "center": 380.6179633862216, "fwhm": 2.737096332065471, "name": "U 4f7/2", "shape": "LACX"}, {"amplitude": 10508.211669918705, "center": 391.5179633862216, "fwhm": 2.737096332065471, "name": "U 4f5/2", "shape": "LACX"}, {"amplitude": 2214.057182779663, "center": 397.8977471164976, "fwhm": 2.556902102730025, "name": "Satellite 2", "shape": "Voigt"}, {"amplitude": 2436.210453422618, "center": 386.6877864274504, "fwhm": 2.512044323701672, "name": "Satellite 1", "shape": "Voigt"}]}, "method": "bayesian_exchange_mc", "peaks": [{"alpha": 1.374742342891894, "amplitude": 15981.63871482141, "beta": 3.2760712391362157, "center": 380.6288831574634, "fwhm": 3.0077280400563975, "m": 4.179002142180813, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f72", "shape": "la_casaxps"}, {"alpha": 1.374742342891894, "amplitude": 10556.41066280971, "beta": 3.2760712391362157, "center": 391.48615510519966, "fwhm": 3.0077280400563975, "m": 4.179002142180813, "phase_id": "UCl4", "region": "U 4f", "role": "main_u4f52", "shape": "la_casaxps"}, {"amplitude": 2470.604532690152, "center": 386.6606092647137, "fwhm": 2.6470772568802916, "gl_ratio": 0.9178875257660675, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f72", "shape": "pseudo_voigt_gl"}, {"amplitude": 2272.63776846611, "center": 397.882630164964, "fwhm": 2.6127209229379984, "gl_ratio": 0.057495623276168056, "phase_id": "UCl4", "region": "U 4f", "role": "satellite_u4f52", "shape": "pseudo_voigt_gl"}], "runtime_s": 312.0, "seed": 1, "selection_warning": "UNRESOLVED model selection: top-2 \u0394F=6.4 is within 2\u00d7(MC errors 3.5+1.8; split-half (lower bound)) \u2014 increase n_sweeps/n_replicas or seed_replicates before trusting the winner", "sigma_hat": 129.25347086856078, "success": true, "winner": "U2_mains_satfree"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:31:{"anchor": "C1s_Scan_8", "candidates": [{"bic_star": 2163.8231648781107, "boundary_hits": ["satellite_pi:fwhm@min"], "conditional": null, "name": "A0_graphite_asym_satellite", "rank": 19, "reduced_chi_sq": 240.19194160113287}, {"bic_star": 2160.815299805517, "boundary_hits": ["contamination_CO:center@min", "contamination_CO:fwhm@max", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A1_graphite_asym_sat_plus_CO", "rank": 16, "reduced_chi_sq": 181.88951637848314}, {"bic_star": 2161.051121689465, "boundary_hits": ["contamination_CO:center@min", "contamination_CO:fwhm@max", "contamination_C=O:center@min", "contamination_C=O:fwhm@min", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A2_graphite_asym_sat_plus_CO_C=O", "rank": 17, "reduced_chi_sq": 187.39611578006767}, {"bic_star": 2161.0789397180533, "boundary_hits": ["contamination_CO:center@min", "contamination_CO:fwhm@max", "contamination_C=O:fwhm@min", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "rank": null, "reduced_chi_sq": 193.64161917230317}, {"bic_star": 2160.8152315307166, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A1_linked", "rank": 15, "reduced_chi_sq": 181.88941232293445}, {"bic_star": 2175.934967343506, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A2_linked", "rank": 20, "reduced_chi_sq": 186.10274165270138}, {"bic_star": 2175.9350957501024, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min", "contamination_OC=O:center@min", "satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "A3_linked", "rank": 21, "reduced_chi_sq": 190.60538447543084}, {"bic_star": 2163.2109656964235, "boundary_hits": ["?:shared_contamination_fwhm@max", "satellite_pi:offset@min", "satellite_pi:fwhm@max", "contamination_CO:offset@min"], "conditional": null, "name": "A1_linked_offset", "rank": 18, "reduced_chi_sq": 178.85948534555155}, {"bic_star": 2163.553211914591, "boundary_hits": ["?:shared_contamination_fwhm@max", "satellite_pi:offset@min", "satellite_pi:fwhm@max", "contamination_CO:offset@min"], "conditional": null, "name": "A2_linked_offset", "rank": null, "reduced_chi_sq": 182.95020993312485}, {"bic_star": 2178.4289658127022, "boundary_hits": ["?:shared_contamination_fwhm@max", "satellite_pi:offset@min", "satellite_pi:fwhm@max", "contamination_CO:offset@min", "contamination_C=O:offset@min", "contamination_OC=O:offset@min"], "conditional": null, "name": "A3_linked_offset", "rank": 22, "reduced_chi_sq": 187.37614575574315}, {"bic_star": 1922.159197935138, "boundary_hits": ["satellite_pi:offset@min", "satellite_pi:fwhm@max"], "conditional": null, "name": "AG0_graphite_asymGL_satellite", "rank": 14, "reduced_chi_sq": 49.09198395188531}, {"bic_star": 1827.6972718306833, "boundary_hits": ["contamination_CO:center@min", "contamination_CO:fwhm@max"], "conditional": null, "name": "AG1_graphite_asymGL_sat_plus_CO", "rank": 4, "reduced_chi_sq": 30.67097468365853}, {"bic_star": 1857.2378471705656, "boundary_hits": ["contamination_C=O:center@min", "contamination_C=O:fwhm@max"], "conditional": null, "name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "rank": 9, "reduced_chi_sq": 34.77674005662118}, {"bic_star": 1866.4202137678092, "boundary_hits": ["contamination_CO:center@min"], "conditional": null, "name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "rank": 10, "reduced_chi_sq": 32.27014779205738}, {"bic_star": 1827.7348381771212, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min"], "conditional": null, "name": "AG1_linked", "rank": 6, "reduced_chi_sq": 30.670969061936145}, {"bic_star": 1827.7383651902487, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min", "contamination_C=O:center@max"], "conditional": null, "name": "AG2_linked", "rank": 7, "reduced_chi_sq": 31.401280684846206}, {"bic_star": 1827.698891160666, "boundary_hits": ["?:shared_contamination_fwhm@max", "contamination_CO:center@min", "contamination_C=O:center@max", "contamination_OC=O:center@max"], "conditional": null, "name": "AG3_linked", "rank": 5, "reduced_chi_sq": 32.16709223938828}, {"bic_star": 1906.6151965335823, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@max"], "conditional": null, "name": "M0_graph_asym_aliph_sym_satellite", "rank": 13, "reduced_chi_sq": 51.026123997036166}, {"bic_star": 1852.892023570819, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@max"], "conditional": null, "name": "M1_graph_asym_aliph_sym_sat_CO", "rank": 8, "reduced_chi_sq": 33.249614334092435}, {"bic_star": 1876.4721336150988, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@max", "contamination_C=O:center@min"], "conditional": null, "name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "rank": 11, "reduced_chi_sq": 31.449919222263258}, {"bic_star": 1741.1828905801303, "boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min", "satellite_pi:offset@min"], "conditional": null, "name": "MG1_graphAsymGL_aliph_sat_CO", "rank": 3, "reduced_chi_sq": 12.39542802308734}, {"bic_star": 1723.5295130712864, "boundary_hits": ["contamination_CO:center@max", "main_aliphatic:offset@min"], "conditional": null, "name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "rank": 1, "reduced_chi_sq": 9.040578699307785}, {"bic_star": 1739.4848904150426, "boundary_hits": ["contamination_CO:fwhm@min", "main_aliphatic:offset@min"], "conditional": null, "name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "rank": 2, "reduced_chi_sq": 8.963144376610053}, {"bic_star": 2273.9968677512966, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min"], "conditional": null, "name": "B2_linked", "rank": 23, "reduced_chi_sq": 195.26270825938678}, {"bic_star": 2287.4247672279807, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min", "contamination_OC=O:center@max"], "conditional": null, "name": "B3_linked", "rank": 24, "reduced_chi_sq": 191.20066833957887}, {"bic_star": 1894.6355482027723, "boundary_hits": ["contamination_CO:fwhm@max", "contamination_C=O:center@max", "contamination_C=O:fwhm@max"], "conditional": null, "name": "B2_graphite_sym_CO_C=O", "rank": 12, "reduced_chi_sq": 54.892341034848926}, {"bic_star": 1900.289299700932, "boundary_hits": [], "conditional": null, "name": "B3_graphite_sym_CO_C=O_OC=O", "rank": null, "reduced_chi_sq": 59.05393024039974}], "conditional": null, "config": {"enable_proposal_pass": false, "n_refits": 4, "noise_floor": 1.0, "rng_seed": 0}, "expert": {"chi_reduced": 1.2046857566409657, "peaks": [{"amplitude": 68687.50247254308, "center": 284.4998947390668, "fwhm": 0.666639931355077, "name": "Graphite", "shape": "asym-GL"}, {"amplitude": 6769.104782616617, "center": 284.84600000000006, "fwhm": 2.4362161470016317, "name": "Adventitious 1", "shape": "GL"}, {"amplitude": 980.2757090919454, "center": 286.6204483360466, "fwhm": 1.920204116987471, "name": "Adventitious 2", "shape": "GL"}, {"amplitude": 967.1178669586701, "center": 288.3459999999785, "fwhm": 3.7870918615811546, "name": "Adventitious 3", "shape": "GL"}, {"amplitude": 1039.5910934477724, "center": 291.21704604934337, "fwhm": 2.10582966510949, "name": "\u03c0\u2192\u03c0* satellite", "shape": "GL"}, {"amplitude": 3096.5394911174, "center": 283.45958350730706, "fwhm": 1.114128341337902, "name": "Unknown 1", "shape": "GL"}]}, "method": "ic_model_comparison", "peaks": [{"amplitude": 64934.51584247545, "asymmetry": 0.004564543290729389, "center": 284.5088393082103, "fwhm": 0.6743371621568794, "gl_ratio": 0.3478253485659817, "phase_id": "graphite", "region": "C 1s", "role": "main_graphitic", "shape": "asymmetric_gl"}, {"amplitude": 10638.980534673961, "center": 284.70883930821725, "fwhm": 2.557408591874607, "gl_ratio": 1.3836677359435612e-09, "phase_id": "graphite", "region": "C 1s", "role": "main_aliphatic", "shape": "pseudo_voigt_gl"}, {"amplitude": 1296.8516923145844, "center": 290.81708874220726, "fwhm": 2.7391088473614142, "gl_ratio": 2.95354034007822e-08, "phase_id": "graphite", "region": "C 1s", "role": "satellite_pi", "shape": "pseudo_voigt_gl"}, {"amplitude": 859.3391603349102, "center": 286.79999999924433, "fwhm": 0.9620619090767639, "gl_ratio": 2.5914003165539157e-09, "phase_id": "graphite", "region": "C 1s", "role": "contamination_CO", "shape": "pseudo_voigt_gl"}, {"amplitude": 1236.7569090879415, "center": 287.9541720087798, "fwhm": 1.9478282631295034, "gl_ratio": 1.3878992399796175e-10, "phase_id": "graphite", "region": "C 1s", "role": "contamination_C=O", "shape": "pseudo_voigt_gl"}], "runtime_s": 799.3, "seed": 0, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:32:{"anchor": "C1s_Scan_8", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1431.7384748727427, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 2.840805932549074, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 2.840805932549074, "min_effective_sample_size": 3.6378511930847868, "n_components": 4, "n_posterior_samples": 750, "name": "A2_linked", "posterior_weight": 9.34316052336157e-63, "posterior_weight_reliable": false, "rank": 4, "sigma_hat": 1591.1691144439912, "swap_acceptance": 0.59}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1291.695287428086, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.9735464150554662, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.9735464150554662, "min_effective_sample_size": 3.618167492044223, "n_components": 4, "n_posterior_samples": 750, "name": "AG2_linked", "posterior_weight": 0.06172730921141825, "posterior_weight_reliable": false, "rank": 2, "sigma_hat": 520.1780829088461, "swap_acceptance": 0.5654545454545454}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1288.973973252434, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.4610272658262602, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.4610272658262602, "min_effective_sample_size": 0.0, "n_components": 5, "n_posterior_samples": 750, "name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "posterior_weight": 0.9382726903971659, "posterior_weight_reliable": false, "rank": 1, "sigma_hat": 314.3142924012769, "swap_acceptance": 0.5427272727272727}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1310.5715093836916, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 2.959159662583147, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 2.959159662583147, "min_effective_sample_size": 0.0, "n_components": 6, "n_posterior_samples": 750, "name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "posterior_weight": 3.9141576285369144e-10, "posterior_weight_reliable": false, "rank": 3, "sigma_hat": 442.63466643193914, "swap_acceptance": 0.5648484848484848}], "confidence": {"contamination_C=O": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 4.5 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1413.8977807492288, "ci_level": 0.68, "ci_low": 1070.8289532804656, "ess": 4.49719611437458, "median": 1070.8289532804656}, "center": {"ci_high": 288.032722402536, "ci_level": 0.68, "ci_low": 287.70594780120274, "ess": 16.779000590905873, "median": 287.88346859207536}, "fwhm": {"ci_high": 2.0550491331827967, "ci_level": 0.68, "ci_low": 1.4346222838496572, "ess": 26.34233810365543, "median": 1.7966987440135327}, "gl_ratio": {"ci_high": 0.352846479858547, "ci_level": 0.68, "ci_low": 0.02824471383267556, "ess": 35.136567438855394, "median": 0.12565048346474644}}}}, "contamination_CO": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 7.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 763.5535401648384, "ci_level": 0.68, "ci_low": 429.2235408358105, "ess": 7.660437122561276, "median": 746.146872276544}, "center": {"ci_high": 286.7848965004658, "ci_level": 0.68, "ci_low": 286.6892224969777, "ess": 60.08554906935291, "median": 286.75295555811783}, "fwhm": {"ci_high": 1.0293830242196573, "ci_level": 0.68, "ci_low": 0.8170395331043406, "ess": 53.764117853639654, "median": 0.8829835082000135}, "gl_ratio": {"ci_high": 0.5761545619818959, "ci_level": 0.68, "ci_low": 0.052668552537415134, "ess": 13.713931350340532, "median": 0.20894908504740461}}}}, "main_aliphatic": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "stuck_chain", "reliability_note": "a sampled parameter never moved \u2014 intervals are meaningless; refit with larger steps/more sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 10591.011092574081, "ci_level": 0.68, "ci_low": 10591.011092574081, "ess": 0.0, "median": 10591.011092574081}, "fwhm": {"ci_high": 2.6486049720889735, "ci_level": 0.68, "ci_low": 2.610852203471151, "ess": 25.481737605006753, "median": 2.6306356976479814}, "gl_ratio": {"ci_high": 0.037139353550702615, "ci_level": 0.68, "ci_low": 0.005173505187192258, "ess": 44.32272219715784, "median": 0.014940168495951336}, "offset": {"ci_high": 0.20254970288043916, "ci_level": 0.68, "ci_low": 0.20056982358918704, "ess": 11.39453788515903, "median": 0.20133004996670265}}}}, "main_graphitic": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 2.8 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 65143.20439031434, "ci_level": 0.68, "ci_low": 64878.97252048374, "ess": 3.242813445025664, "median": 64878.97252048374}, "asymmetry": {"ci_high": 0.04527048451758119, "ci_level": 0.68, "ci_low": 0.028131929542454068, "ess": 3.573143648780697, "median": 0.03603303530979708}, "center": {"ci_high": 284.5065872710428, "ci_level": 0.68, "ci_low": 284.5040719145873, "ess": 2.8106927076404142, "median": 284.5040719145873}, "fwhm": {"ci_high": 0.6666833317825636, "ci_level": 0.68, "ci_low": 0.6629091741172232, "ess": 5.197830796670883, "median": 0.6647855925503354}, "gl_ratio": {"ci_high": 0.33356328407057734, "ci_level": 0.68, "ci_low": 0.3066350353457373, "ess": 29.222663581185778, "median": 0.31945250416635734}}}}, "satellite_pi": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 3.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1306.2409784416934, "ci_level": 0.68, "ci_low": 1138.072227140848, "ess": 3.67697265576572, "median": 1138.072227140848}, "fwhm": {"ci_high": 3.5493557774095663, "ci_level": 0.68, "ci_low": 2.632122835086131, "ess": 10.47322998773568, "median": 3.0904204438391005}, "gl_ratio": {"ci_high": 0.4028246074155279, "ci_level": 0.68, "ci_low": 0.048810734865377944, "ess": 33.65779476865091, "median": 0.16313646989546973}, "offset": {"ci_high": 6.385082154504203, "ci_level": 0.68, "ci_low": 6.034991605178216, "ess": 17.120604075459617, "median": 6.246191695477605}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.2046857566409657, "peaks": [{"amplitude": 68687.50247254308, "center": 284.4998947390668, "fwhm": 0.666639931355077, "name": "Graphite", "shape": "asym-GL"}, {"amplitude": 6769.104782616617, "center": 284.84600000000006, "fwhm": 2.4362161470016317, "name": "Adventitious 1", "shape": "GL"}, {"amplitude": 980.2757090919454, "center": 286.6204483360466, "fwhm": 1.920204116987471, "name": "Adventitious 2", "shape": "GL"}, {"amplitude": 967.1178669586701, "center": 288.3459999999785, "fwhm": 3.7870918615811546, "name": "Adventitious 3", "shape": "GL"}, {"amplitude": 1039.5910934477724, "center": 291.21704604934337, "fwhm": 2.10582966510949, "name": "\u03c0\u2192\u03c0* satellite", "shape": "GL"}, {"amplitude": 3096.5394911174, "center": 283.45958350730706, "fwhm": 1.114128341337902, "name": "Unknown 1", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 64878.97252048374, "asymmetry": 0.03603303530979708, "center": 284.5040719145873, "fwhm": 0.6647855925503354, "gl_ratio": 0.31945250416635734, "phase_id": "graphite", "region": "C 1s", "role": "main_graphitic", "shape": "asymmetric_gl"}, {"amplitude": 10591.011092574081, "center": 284.705401964554, "fwhm": 2.6306356976479814, "gl_ratio": 0.014940168495951336, "phase_id": "graphite", "region": "C 1s", "role": "main_aliphatic", "shape": "pseudo_voigt_gl"}, {"amplitude": 1138.072227140848, "center": 290.7502636100649, "fwhm": 3.0904204438391005, "gl_ratio": 0.16313646989546973, "phase_id": "graphite", "region": "C 1s", "role": "satellite_pi", "shape": "pseudo_voigt_gl"}, {"amplitude": 746.146872276544, "center": 286.75295555811783, "fwhm": 0.8829835082000135, "gl_ratio": 0.20894908504740461, "phase_id": "graphite", "region": "C 1s", "role": "contamination_CO", "shape": "pseudo_voigt_gl"}, {"amplitude": 1070.8289532804656, "center": 287.88346859207536, "fwhm": 1.7966987440135327, "gl_ratio": 0.12565048346474644, "phase_id": "graphite", "region": "C 1s", "role": "contamination_C=O", "shape": "pseudo_voigt_gl"}], "runtime_s": 351.9, "seed": 0, "selection_warning": "UNRESOLVED model selection: top-2 \u0394F=2.7 is within 2\u00d7(MC errors 1.5+2.0; split-half (lower bound)) \u2014 increase n_sweeps/n_replicas or seed_replicates before trusting the winner", "sigma_hat": 314.3142924012769, "success": true, "winner": "MG2_graphAsymGL_aliph_sat_CO_C=O"}
docs/autofit/inventory/bayesian_real_validation_runs.jsonl:33:{"anchor": "C1s_Scan_8", "candidates": [{"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1432.3123717828046, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 1.5767789384881326, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 1.5767789384881326, "min_effective_sample_size": 4.830195498907848, "n_components": 4, "n_posterior_samples": 750, "name": "A2_linked", "posterior_weight": 1.0045260375983973e-63, "posterior_weight_reliable": false, "rank": 4, "sigma_hat": 1568.9120875718368, "swap_acceptance": 0.5860606060606061}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1287.2570839379591, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.05101774597437725, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.05101774597437725, "min_effective_sample_size": 3.3607026389866252, "n_components": 4, "n_posterior_samples": 750, "name": "AG2_linked", "posterior_weight": 0.9969474805518356, "posterior_weight_reliable": false, "rank": 1, "sigma_hat": 529.8277714891781, "swap_acceptance": 0.5533333333333333}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1293.0458147326071, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 3.6050356867839355, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 3.6050356867839355, "min_effective_sample_size": 0.0, "n_components": 5, "n_posterior_samples": 750, "name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "posterior_weight": 0.0030525194427866295, "posterior_weight_reliable": false, "rank": 2, "sigma_hat": 469.6960960957663, "swap_acceptance": 0.5390909090909091}, {"ci_reliability_warning": "LOW effective sample size \u2014 credible intervals likely underestimate uncertainty; increase n_sweeps", "free_energy": 1313.202748044098, "free_energy_is_replicate_mean": false, "free_energy_mc_error": 0.6148932367710813, "free_energy_replicate_spread": null, "free_energy_replicates": null, "free_energy_split_half_error": 0.6148932367710813, "min_effective_sample_size": 3.0929555897848777, "n_components": 6, "n_posterior_samples": 750, "name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "posterior_weight": 5.3779099948391794e-12, "posterior_weight_reliable": false, "rank": 3, "sigma_hat": 504.0302174682879, "swap_acceptance": 0.5678787878787879}], "confidence": {"contamination_C=O": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 6.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 947.4502444479704, "ci_level": 0.68, "ci_low": 8.943859856637715, "ess": 6.703778149639552, "median": 44.20134045434408}, "center": {"ci_high": 288.13981931769206, "ci_level": 0.68, "ci_low": 287.39027824482486, "ess": 18.494725105592117, "median": 287.7136990891674}, "gl_ratio": {"ci_high": 0.9008351877769487, "ci_level": 0.68, "ci_low": 0.2460603312810472, "ess": 38.68490592601473, "median": 0.6227775367672694}}}}, "contamination_CO": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 5.9 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 2763.8397415059867, "ci_level": 0.68, "ci_low": 1907.4860935498482, "ess": 5.930302734634696, "median": 2763.8397415059867}, "center": {"ci_high": 286.21646368310815, "ci_level": 0.68, "ci_low": 285.902886225705, "ess": 15.490046188388668, "median": 286.06604076853813}, "gl_ratio": {"ci_high": 0.905373741939193, "ci_level": 0.68, "ci_low": 0.29703603027491793, "ess": 22.794517983717185, "median": 0.6863458818442999}}}}, "main_graphitic": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 3.4 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 75670.07960539138, "ci_level": 0.68, "ci_low": 74304.1215008268, "ess": 3.3607026389866252, "median": 75182.83796196862}, "asymmetry": {"ci_high": 0.06411185354281144, "ci_level": 0.68, "ci_low": 0.005720442168551424, "ess": 4.608136250915466, "median": 0.019322144429815412}, "center": {"ci_high": 284.5116815478861, "ci_level": 0.68, "ci_low": 284.50487224200293, "ess": 4.9245469245747255, "median": 284.5101441169939}, "fwhm": {"ci_high": 0.7386515990808544, "ci_level": 0.68, "ci_low": 0.7208923240318421, "ess": 4.30588682494465, "median": 0.7313939010197432}, "gl_ratio": {"ci_high": 0.8585684753676883, "ci_level": 0.68, "ci_low": 0.7795479230847857, "ess": 4.064653073514586, "median": 0.8259047260523992}}}}, "satellite_pi": {"reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "sigma_stat": {"reliability": "low_ess", "reliability_note": "min ESS 8.7 < 50 \u2014 random-walk quantiles likely UNDERESTIMATE uncertainty; increase n_sweeps", "uncertainty_kind": "posterior_ci", "values": {"amplitude": {"ci_high": 1018.1337732563006, "ci_level": 0.68, "ci_low": 832.5473218273703, "ess": 8.709101910667593, "median": 944.1752219389329}, "fwhm": {"ci_high": 3.764922903042545, "ci_level": 0.68, "ci_low": 2.4045858240539673, "ess": 25.034683327822968, "median": 3.0376604099137596}, "gl_ratio": {"ci_high": 0.7231013016358745, "ci_level": 0.68, "ci_low": 0.09858359768562923, "ess": 57.45897131672182, "median": 0.36946575087271255}, "offset": {"ci_high": 6.499785545200142, "ci_level": 0.68, "ci_low": 6.025032304381504, "ess": 114.0163562068376, "median": 6.30521394522488}}}}}, "config": {"beta_min": 0.0001, "burn_fraction": 0.5, "exchange_every": 5, "n_replicas": 12, "n_sweeps": 1500}, "expert": {"chi_reduced": 1.2046857566409657, "peaks": [{"amplitude": 68687.50247254308, "center": 284.4998947390668, "fwhm": 0.666639931355077, "name": "Graphite", "shape": "asym-GL"}, {"amplitude": 6769.104782616617, "center": 284.84600000000006, "fwhm": 2.4362161470016317, "name": "Adventitious 1", "shape": "GL"}, {"amplitude": 980.2757090919454, "center": 286.6204483360466, "fwhm": 1.920204116987471, "name": "Adventitious 2", "shape": "GL"}, {"amplitude": 967.1178669586701, "center": 288.3459999999785, "fwhm": 3.7870918615811546, "name": "Adventitious 3", "shape": "GL"}, {"amplitude": 1039.5910934477724, "center": 291.21704604934337, "fwhm": 2.10582966510949, "name": "\u03c0\u2192\u03c0* satellite", "shape": "GL"}, {"amplitude": 3096.5394911174, "center": 283.45958350730706, "fwhm": 1.114128341337902, "name": "Unknown 1", "shape": "GL"}]}, "method": "bayesian_exchange_mc", "peaks": [{"amplitude": 75182.83796196862, "asymmetry": 0.019322144429815412, "center": 284.5101441169939, "fwhm": 0.7313939010197432, "gl_ratio": 0.8259047260523992, "phase_id": "graphite", "region": "C 1s", "role": "main_graphitic", "shape": "asymmetric_gl"}, {"amplitude": 944.1752219389329, "center": 290.81535806221876, "fwhm": 3.0376604099137596, "gl_ratio": 0.36946575087271255, "phase_id": "graphite", "region": "C 1s", "role": "satellite_pi", "shape": "pseudo_voigt_gl"}, {"amplitude": 2763.8397415059867, "center": 286.06604076853813, "fwhm": 2.006946238084523, "gl_ratio": 0.6863458818442999, "phase_id": "graphite", "region": "C 1s", "role": "contamination_CO", "shape": "pseudo_voigt_gl"}, {"amplitude": 44.20134045434408, "center": 287.7136990891674, "fwhm": 2.006946238084523, "gl_ratio": 0.6227775367672694, "phase_id": "graphite", "region": "C 1s", "role": "contamination_C=O", "shape": "pseudo_voigt_gl"}], "runtime_s": 342.3, "seed": 1, "selection_warning": "UNRESOLVED model selection: top-2 \u0394F=5.8 is within 2\u00d7(MC errors 0.1+3.6; split-half (lower bound)) \u2014 increase n_sweeps/n_replicas or seed_replicates before trusting the winner", "sigma_hat": 529.8277714891781, "success": true, "winner": "AG2_linked"}

exec
/bin/zsh -lc "find docs/autofit/test_data -maxdepth 1 -name '*.proj.zip' -exec unzip -l {} \\;" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
Archive:  docs/autofit/test_data/Cl2p_projfit_test.proj.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    64085  07-02-2026 17:24   spectrum_0_XPS_Survey_0.json
    26749  07-02-2026 17:24   spectrum_1_C1s_Scan.json
    28768  07-02-2026 17:24   spectrum_2_C1s_Scan_0.json
    26774  07-02-2026 17:24   spectrum_3_C1s_Scan_1.json
    26757  07-02-2026 17:24   spectrum_4_C1s_Scan_2.json
    26815  07-02-2026 17:24   spectrum_5_C1s_Scan_3.json
    26762  07-02-2026 17:24   spectrum_6_C1s_Scan_4.json
    26761  07-02-2026 17:24   spectrum_7_C1s_Scan_5.json
    34732  07-02-2026 17:24   spectrum_8_U4f_Scan.json
    34695  07-02-2026 17:24   spectrum_9_U4f_Scan_0.json
    34704  07-02-2026 17:24   spectrum_10_U4f_Scan_1.json
    34696  07-02-2026 17:24   spectrum_11_U4f_Scan_2.json
    34366  07-02-2026 17:24   spectrum_12_U4f_Scan_3.json
    34674  07-02-2026 17:24   spectrum_13_U4f_Scan_4.json
    34727  07-02-2026 17:24   spectrum_14_U4f_Scan_5.json
    26928  07-02-2026 17:24   spectrum_15_Cl2p_Scan.json
    26523  07-02-2026 17:24   spectrum_16_Cl2p_Scan_0.json
    27087  07-02-2026 17:24   spectrum_17_Cl2p_Scan_1.json
     2521  07-02-2026 17:24   manifest.json
---------                     -------
   579124                     19 files
Archive:  docs/autofit/test_data/B4C-UCl4.proj.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    64103  06-30-2026 05:22   spectrum_0_XPS_Survey_0.json
    64114  06-30-2026 05:22   spectrum_1_XPS_Survey_1.json
    64105  06-30-2026 05:22   spectrum_2_XPS_Survey_3.json
    64145  06-30-2026 05:22   spectrum_3_XPS_Survey_2.json
    64143  06-30-2026 05:22   spectrum_4_XPS_Survey_6.json
    64130  06-30-2026 05:22   spectrum_5_XPS_Survey_7.json
    64114  06-30-2026 05:22   spectrum_6_XPS_Survey_5.json
    64131  06-30-2026 05:22   spectrum_7_XPS_Survey_4.json
    64137  06-30-2026 05:22   spectrum_8_XPS_Survey.json
    64133  06-30-2026 05:22   spectrum_9_XPS_Survey_8.json
    18160  06-30-2026 05:22   spectrum_10_B1s_Scan.json
    18082  06-30-2026 05:22   spectrum_11_B1s_Scan_0.json
    18137  06-30-2026 05:22   spectrum_12_B1s_Scan_1.json
    18130  06-30-2026 05:22   spectrum_13_B1s_Scan_2.json
    20514  06-30-2026 05:22   spectrum_14_B1s_Scan_3.json
    18094  06-30-2026 05:22   spectrum_15_B1s_Scan_4.json
    18169  06-30-2026 05:22   spectrum_16_B1s_Scan_5.json
    18137  06-30-2026 05:22   spectrum_17_B1s_Scan_6.json
    24616  06-30-2026 05:22   spectrum_18_B1s_Scan_7.json
    18165  06-30-2026 05:22   spectrum_19_B1s_Scan_8.json
     9462  06-30-2026 05:22   spectrum_20_C1s_Scan_4.json
     9470  06-30-2026 05:22   spectrum_21_C1s_Scan_5.json
     9478  06-30-2026 05:22   spectrum_22_C1s_Scan_7.json
     9471  06-30-2026 05:22   spectrum_23_C1s_Scan_6.json
     9467  06-30-2026 05:22   spectrum_24_C1s_Scan_2.json
     9474  06-30-2026 05:22   spectrum_25_C1s_Scan_3.json
     9472  06-30-2026 05:22   spectrum_26_C1s_Scan_1.json
     9472  06-30-2026 05:22   spectrum_27_C1s_Scan_0.json
     9454  06-30-2026 05:22   spectrum_28_C1s_Scan.json
     9474  06-30-2026 05:22   spectrum_29_C1s_Scan_8.json
    10008  06-30-2026 05:22   spectrum_30_Cl2p_Scan.json
    10020  06-30-2026 05:22   spectrum_31_Cl2p_Scan_1.json
     9998  06-30-2026 05:22   spectrum_32_Cl2p_Scan_0.json
    49619  06-30-2026 05:22   spectrum_33_U4f_Scan.json
    49899  06-30-2026 05:22   spectrum_34_U4f_Scan_0.json
    49743  06-30-2026 05:22   spectrum_35_U4f_Scan_1.json
    49790  06-30-2026 05:22   spectrum_36_U4f_Scan_2.json
    49803  06-30-2026 05:22   spectrum_37_U4f_Scan_3.json
    49727  06-30-2026 05:22   spectrum_38_U4f_Scan_4.json
    49431  06-30-2026 05:22   spectrum_39_U4f_Scan_5.json
    49970  06-30-2026 05:22   spectrum_40_U4f_Scan_6.json
    49693  06-30-2026 05:22   spectrum_41_U4f_Scan_7.json
    49314  06-30-2026 05:22   spectrum_42_U4f_Scan_8.json
     1459  06-30-2026 05:22   spectrum_43___Stack_2.json
     5998  06-30-2026 05:22   manifest.json
---------                     -------
  1460625                     45 files
Archive:  docs/autofit/test_data/UCl4_on_graphite.proj.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    64151  06-24-2026 05:50   spectrum_0_XPS_Survey.json
    64144  06-24-2026 05:50   spectrum_1_XPS_Survey_0.json
    64162  06-24-2026 05:50   spectrum_2_XPS_Survey_1.json
    64148  06-24-2026 05:50   spectrum_3_XPS_Survey_2.json
    64162  06-24-2026 05:50   spectrum_4_XPS_Survey_3.json
    64130  06-24-2026 05:50   spectrum_5_XPS_Survey_4.json
    64136  06-24-2026 05:50   spectrum_6_XPS_Survey_5.json
    64133  06-24-2026 05:50   spectrum_7_XPS_Survey_6.json
    64103  06-24-2026 05:50   spectrum_8_XPS_Survey_7.json
    64181  06-24-2026 05:50   spectrum_9_XPS_Survey_8.json
    35391  06-24-2026 05:50   spectrum_10_C1s_Scan.json
    35286  06-24-2026 05:50   spectrum_11_C1s_Scan_0.json
    32004  06-24-2026 05:50   spectrum_12_C1s_Scan_1.json
    31937  06-24-2026 05:50   spectrum_13_C1s_Scan_2.json
    32048  06-24-2026 05:50   spectrum_14_C1s_Scan_3.json
    34018  06-24-2026 05:50   spectrum_15_C1s_Scan_4.json
    32033  06-24-2026 05:50   spectrum_16_C1s_Scan_5.json
    32079  06-24-2026 05:50   spectrum_17_C1s_Scan_6.json
    31906  06-24-2026 05:50   spectrum_18_C1s_Scan_7.json
    32012  06-24-2026 05:50   spectrum_19_C1s_Scan_8.json
    45141  06-24-2026 05:50   spectrum_20_U4f_Scan.json
    50248  06-24-2026 05:50   spectrum_21_U4f_Scan_0.json
    44931  06-24-2026 05:50   spectrum_22_U4f_Scan_1.json
    45221  06-24-2026 05:50   spectrum_23_U4f_Scan_2.json
    50307  06-24-2026 05:50   spectrum_24_U4f_Scan_3.json
    44985  06-24-2026 05:50   spectrum_25_U4f_Scan_4.json
    50144  06-24-2026 05:50   spectrum_26_U4f_Scan_5.json
    50284  06-24-2026 05:50   spectrum_27_U4f_Scan_6.json
    49825  06-24-2026 05:50   spectrum_28_U4f_Scan_7.json
    50120  06-24-2026 05:50   spectrum_29_U4f_Scan_8.json
     4138  06-24-2026 05:50   manifest.json
---------                     -------
  1455508                     31 files
Archive:  docs/autofit/test_data/4-GTA UCl4-BN.proj.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    22454  06-25-2026 00:13   spectrum_0_B1s_Scan.json
    45401  06-25-2026 00:13   spectrum_1_U4f_Scan.json
    20746  06-25-2026 00:13   spectrum_2_B1s_Scan_0.json
    45260  06-25-2026 00:13   spectrum_3_U4f_Scan_0.json
    20790  06-25-2026 00:13   spectrum_4_B1s_Scan_1.json
    45145  06-25-2026 00:13   spectrum_5_U4f_Scan_1.json
    20754  06-25-2026 00:13   spectrum_6_B1s_Scan_2.json
    45519  06-25-2026 00:13   spectrum_7_U4f_Scan_2.json
    20734  06-25-2026 00:13   spectrum_8_B1s_Scan_3.json
    45550  06-25-2026 00:13   spectrum_9_U4f_Scan_3.json
    20850  06-25-2026 00:13   spectrum_10_B1s_Scan_4.json
    45433  06-25-2026 00:13   spectrum_11_U4f_Scan_4.json
    20303  06-25-2026 00:13   spectrum_12_B1s_Scan_5.json
    50239  06-25-2026 00:13   spectrum_13_U4f_Scan_5.json
    22445  06-25-2026 00:13   spectrum_14_B1s_Scan_6.json
    44898  06-25-2026 00:13   spectrum_15_U4f_Scan_6.json
    22362  06-25-2026 00:13   spectrum_16_B1s_Scan_7.json
    45671  06-25-2026 00:13   spectrum_17_U4f_Scan_7.json
    20301  06-25-2026 00:13   spectrum_18_B1s_Scan_8.json
    45648  06-25-2026 00:13   spectrum_19_U4f_Scan_8.json
     2782  06-25-2026 00:13   manifest.json
---------                     -------
   673285                     21 files
Archive:  docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    34999  06-23-2026 18:02   spectrum_0_C1s_Scan.json
    49977  06-23-2026 18:02   spectrum_1_U4f_Scan.json
    34621  06-23-2026 18:02   spectrum_2_C1s_Scan_0.json
    49882  06-23-2026 18:02   spectrum_3_U4f_Scan_0.json
    34389  06-23-2026 18:02   spectrum_4_C1s_Scan_1.json
    49776  06-23-2026 18:02   spectrum_5_U4f_Scan_1.json
    34482  06-23-2026 18:02   spectrum_6_C1s_Scan_2.json
    50002  06-23-2026 18:02   spectrum_7_U4f_Scan_2.json
    34376  06-23-2026 18:02   spectrum_8_C1s_Scan_3.json
    49976  06-23-2026 18:02   spectrum_9_U4f_Scan_3.json
    34370  06-23-2026 18:02   spectrum_10_C1s_Scan_4.json
    49742  06-23-2026 18:02   spectrum_11_U4f_Scan_4.json
    34351  06-23-2026 18:02   spectrum_12_C1s_Scan_5.json
    49778  06-23-2026 18:02   spectrum_13_U4f_Scan_5.json
    35033  06-23-2026 18:02   spectrum_14_C1s_Scan_6.json
    50286  06-23-2026 18:02   spectrum_15_U4f_Scan_6.json
    34388  06-23-2026 18:02   spectrum_16_C1s_Scan_7.json
    49701  06-23-2026 18:02   spectrum_17_U4f_Scan_7.json
    34756  06-23-2026 18:02   spectrum_18_C1s_Scan_8.json
    49787  06-23-2026 18:02   spectrum_19_U4f_Scan_8.json
     2782  06-23-2026 18:02   manifest.json
---------                     -------
   847454                     21 files
Archive:  docs/autofit/test_data/8-JT Graphite.proj.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    64662  06-26-2026 18:38   spectrum_0_XPS_Survey_8.json
    64706  06-26-2026 18:38   spectrum_1_XPS_Survey_7.json
    64637  06-26-2026 18:38   spectrum_2_XPS_Survey_6.json
    64683  06-26-2026 18:38   spectrum_3_XPS_Survey_5.json
    64681  06-26-2026 18:38   spectrum_4_XPS_Survey_4.json
    64699  06-26-2026 18:38   spectrum_5_XPS_Survey_3.json
    64706  06-26-2026 18:38   spectrum_6_XPS_Survey_2.json
    64727  06-26-2026 18:38   spectrum_7_XPS_Survey_1.json
    64747  06-26-2026 18:38   spectrum_8_XPS_Survey_0.json
    64708  06-26-2026 18:38   spectrum_9_XPS_Survey.json
    31285  06-26-2026 18:38   spectrum_10_C1s_Scan.json
    31284  06-26-2026 18:38   spectrum_11_C1s_Scan_0.json
    31295  06-26-2026 18:38   spectrum_12_C1s_Scan_1.json
    31298  06-26-2026 18:38   spectrum_13_C1s_Scan_2.json
    31256  06-26-2026 18:38   spectrum_14_C1s_Scan_3.json
    31644  06-26-2026 18:38   spectrum_15_C1s_Scan_4.json
    31905  06-26-2026 18:38   spectrum_16_C1s_Scan_5.json
    31665  06-26-2026 18:38   spectrum_17_C1s_Scan_6.json
    31242  06-26-2026 18:38   spectrum_18_C1s_Scan_7.json
    33230  06-26-2026 18:38   spectrum_19_C1s_Scan_8.json
     2838  06-26-2026 18:38   manifest.json
---------                     -------
   965898                     21 files
Archive:  docs/autofit/test_data/Project9_CasaXPS_newfit.proj.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    64065  04-27-2026 06:35   spectrum_0_XPS_Survey_0.json
    26640  04-27-2026 06:35   spectrum_1_C1s_Scan.json
    28659  04-27-2026 06:35   spectrum_2_C1s_Scan_0.json
    26665  04-27-2026 06:35   spectrum_3_C1s_Scan_1.json
    26648  04-27-2026 06:35   spectrum_4_C1s_Scan_2.json
    26675  04-27-2026 06:35   spectrum_5_C1s_Scan_3.json
    26622  04-27-2026 06:35   spectrum_6_C1s_Scan_4.json
    26621  04-27-2026 06:35   spectrum_7_C1s_Scan_5.json
    34623  04-27-2026 06:35   spectrum_8_U4f_Scan.json
    34586  04-27-2026 06:35   spectrum_9_U4f_Scan_0.json
    34595  04-27-2026 06:35   spectrum_10_U4f_Scan_1.json
    34587  04-27-2026 06:35   spectrum_11_U4f_Scan_2.json
    34257  04-27-2026 06:35   spectrum_12_U4f_Scan_3.json
    34565  04-27-2026 06:35   spectrum_13_U4f_Scan_4.json
    34587  04-27-2026 06:35   spectrum_14_U4f_Scan_5.json
     2120  04-27-2026 06:35   manifest.json
---------                     -------
   496515                     16 files

exec
/bin/zsh -lc "find docs/autofit/test_data -maxdepth 1 -name '*.proj.zip' -exec zipgrep -n -i \"15\\.0\\|15\\.00\\|fwhm\\|FWHM\\|width\\|3\\.5\\|3\\.50\\|3\\.575\\|5\\.46\" {} \\;" in /Users/skyefortier/xps-verify
 succeeded in 2127ms:
exec
/bin/zsh -lc "unzip -p 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip' spectrum_0_C1s_Scan.json | rg -n -i \"fwhm|width|15\\.0|3\\.5|5\\.46|peaks|name|center|shape\" -S" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
3:  "name": "C1s Scan",
106:    283.51999999999975,
254:    6373.530927781035,
278:    7183.558564748362,
288:    6983.579791171962,
359:    3963.5516334418753,
394:  "peaks": [
398:      "name": "Graphite",
399:      "center": 284.49873759080685,
400:      "fwhm": 0.6596412636634877,
402:      "shape": "asym-GL",
417:      "fixCenter": true,
418:      "fixFwhm": false,
431:      "_afCenterMin": 284.2,
432:      "_afCenterMax": 284.8,
433:      "_afFwhmMin": 0.4,
434:      "_afFwhmMax": 1.2,
458:        "center": {
466:        "fwhm": {
489:      "name": "Adventitious 1",
490:      "center": 284.799,
491:      "fwhm": 1.5672103495943768,
493:      "shape": "GL",
508:      "fixCenter": true,
509:      "fixFwhm": false,
522:      "_afCenterMin": 284.8,
523:      "_afCenterMax": 285.3,
524:      "_afFwhmMin": 0.8,
525:      "_afFwhmMax": 3,
539:        "center": {
547:        "fwhm": {
570:      "name": "Adventitious 2",
571:      "center": 285.86699999999996,
572:      "fwhm": 1.929056140249611,
574:      "shape": "GL",
589:      "fixCenter": true,
590:      "fixFwhm": false,
603:      "_afCenterMin": 285.7,
604:      "_afCenterMax": 286.7,
605:      "_afFwhmMin": 0.8,
606:      "_afFwhmMax": 3,
620:        "center": {
628:        "fwhm": {
651:      "name": "Adventitious 3",
652:      "center": 287.54519422007803,
653:      "fwhm": 2.663643228613519,
655:      "shape": "GL",
670:      "fixCenter": false,
671:      "fixFwhm": false,
684:      "_afCenterMin": 287.3,
685:      "_afCenterMax": 288.3,
686:      "_afFwhmMin": 0.8,
687:      "_afFwhmMax": 3.5,
701:        "center": {
709:        "fwhm": {
732:      "name": "π→π* satellite",
733:      "center": 290.85728399439745,
734:      "fwhm": 3.9483293300972853,
736:      "shape": "GL",
751:      "fixCenter": false,
752:      "fixFwhm": false,
765:      "_afCenterMin": 290,
766:      "_afCenterMax": 292,
767:      "_afFwhmMin": 1,
768:      "_afFwhmMax": 4,
782:        "center": {
790:        "fwhm": {
813:      "name": "Unknown 1",
814:      "center": 283.4448115743895,
815:      "fwhm": 1.0825884884772137,
817:      "shape": "GL",
832:      "fixCenter": false,
833:      "fixFwhm": false,
846:      "_afCenterMin": 282.2,
847:      "_afCenterMax": 283.8,
848:      "_afFwhmMin": 0.5,
849:      "_afFwhmMax": 3,
863:        "center": {
871:        "fwhm": {
931:      5613.557552511294,
1016:      10455.46411828689,
1067:      3323.512755381873,
1118:      295.46,
1137:      293.56,
1218:      285.46,
1237:      283.56,
1358:      5273.54,
1391:      5093.54,
1535:      1203.51,
1597:      6253.5,
1602:      8843.54,
1610:      38113.5,
1657:      15.0539,
1676:  "lineWidth": 1.5,

exec
/bin/zsh -lc "unzip -p 'docs/autofit/test_data/UCl4_on_graphite.proj.zip' spectrum_10_C1s_Scan.json | rg -n -i \"fwhm|width|15\\.0|3\\.5|5\\.46|peaks|name|center|shape\" -S" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
3:  "name": "C1s Scan",
106:    283.51999999999975,
254:    6373.530927781035,
278:    7183.558564748362,
288:    6983.579791171962,
359:    3963.5516334418753,
394:  "peaks": [
398:      "name": "Graphite",
399:      "center": 284.500358976782,
400:      "fwhm": 0.663954782693843,
402:      "shape": "asym-GL",
417:      "fixCenter": true,
418:      "fixFwhm": false,
431:      "_afCenterMin": 284.2,
432:      "_afCenterMax": 284.8,
433:      "_afFwhmMin": 0.4,
434:      "_afFwhmMax": 1.2,
458:        "center": {
466:        "fwhm": {
489:      "name": "Adventitious 1",
490:      "center": 284.75900000000007,
491:      "fwhm": 2.52821436637877,
493:      "shape": "GL",
508:      "fixCenter": true,
509:      "fixFwhm": false,
522:      "_afCenterMin": 284.8,
523:      "_afCenterMax": 285.3,
524:      "_afFwhmMin": 0.8,
525:      "_afFwhmMax": 3,
539:        "center": {
547:        "fwhm": {
570:      "name": "Adventitious 2",
571:      "center": 286.41309491035526,
572:      "fwhm": 1.5617626389024108,
574:      "shape": "GL",
589:      "fixCenter": true,
590:      "fixFwhm": false,
603:      "_afCenterMin": 285.7,
604:      "_afCenterMax": 286.7,
605:      "_afFwhmMin": 0.8,
606:      "_afFwhmMax": 3,
620:        "center": {
628:        "fwhm": {
651:      "name": "Adventitious 3",
652:      "center": 287.58545217239237,
653:      "fwhm": 2.7876421858248523,
655:      "shape": "GL",
670:      "fixCenter": true,
671:      "fixFwhm": false,
684:      "_afCenterMin": 287.3,
685:      "_afCenterMax": 288.3,
686:      "_afFwhmMin": 0.8,
687:      "_afFwhmMax": 3.5,
701:        "center": {
709:        "fwhm": {
732:      "name": "π→π* satellite",
733:      "center": 290.90825845990554,
734:      "fwhm": 4.20402469415282,
736:      "shape": "GL",
751:      "fixCenter": true,
752:      "fixFwhm": false,
765:      "_afCenterMin": 290,
766:      "_afCenterMax": 292,
767:      "_afFwhmMin": 1,
768:      "_afFwhmMax": 4,
782:        "center": {
790:        "fwhm": {
813:      "name": "Unknown 1",
814:      "center": 283.2877762563003,
815:      "fwhm": 0.7989215246876384,
817:      "shape": "GL",
832:      "fixCenter": true,
833:      "fixFwhm": false,
846:      "_afCenterMin": 282.2,
847:      "_afCenterMax": 283.8,
848:      "_afFwhmMin": 0.5,
849:      "_afFwhmMax": 3,
863:        "center": {
871:        "fwhm": {
902:      5413.5009396070545,
1136:      293.559,
1236:      283.559,
1338:      5353.5,
1386:      5115.01,
1654:      15.0539,
1672:  "lineWidth": 1.5,

exec
/bin/zsh -lc "unzip -p 'docs/autofit/test_data/8-JT Graphite.proj.zip' spectrum_10_C1s_Scan.json | rg -n -i \"fwhm|width|15\\.0|3\\.5|5\\.46|peaks|name|center|shape\" -S" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
3:  "name": "C1s Scan",
106:    283.51999999999975,
340:    85793.5594529846,
394:  "peaks": [
398:      "name": "Graphite",
399:      "center": 284.3967935692768,
400:      "fwhm": 0.6402984258920098,
402:      "shape": "asym-GL",
417:      "fixCenter": true,
418:      "fixFwhm": false,
431:      "_afCenterMin": 284.2,
432:      "_afCenterMax": 284.8,
433:      "_afFwhmMin": 0.4,
434:      "_afFwhmMax": 1.2,
458:        "center": {
466:        "fwhm": {
489:      "name": "Adventitious 1",
490:      "center": 284.7148212610782,
491:      "fwhm": 1.9089824951157317,
493:      "shape": "GL",
508:      "fixCenter": true,
509:      "fixFwhm": false,
522:      "_afCenterMin": 284.8,
523:      "_afCenterMax": 285.3,
524:      "_afFwhmMin": 0.8,
525:      "_afFwhmMax": 3,
539:        "center": {
547:        "fwhm": {
570:      "name": "Adventitious 2",
571:      "center": 286.4083267268941,
572:      "fwhm": 1.4233559986717281,
574:      "shape": "GL",
589:      "fixCenter": false,
590:      "fixFwhm": false,
603:      "_afCenterMin": 285.7,
604:      "_afCenterMax": 286.7,
605:      "_afFwhmMin": 0.8,
606:      "_afFwhmMax": 3,
620:        "center": {
628:        "fwhm": {
651:      "name": "Adventitious 3",
652:      "center": 287.3170000000017,
653:      "fwhm": 3.990893151293674,
655:      "shape": "GL",
670:      "fixCenter": true,
671:      "fixFwhm": false,
684:      "_afCenterMin": 287.3,
685:      "_afCenterMax": 288.3,
686:      "_afFwhmMin": 0.8,
687:      "_afFwhmMax": 3.5,
701:        "center": {
709:        "fwhm": {
732:      "name": "π→π* satellite",
733:      "center": 291.10123470083283,
734:      "fwhm": 3.4816659139593606,
736:      "shape": "GL",
751:      "fixCenter": true,
752:      "fixFwhm": false,
765:      "_afCenterMin": 290,
766:      "_afCenterMax": 292,
767:      "_afFwhmMin": 1,
768:      "_afFwhmMax": 4,
782:        "center": {
790:        "fwhm": {
849:      5183.53624745885,
864:      6515.0573625678535,
878:      6155.461131860289,
907:      8163.562091297921,
953:      1063.5762528899481,
1003:      293.517,
1103:      283.517,
1448:      253.508,
1471:  "lineWidth": 1.5,

exec
/bin/zsh -lc "unzip -p 'docs/autofit/test_data/Cl2p_projfit_test.proj.zip' spectrum_1_C1s_Scan.json | rg -n -i \"fwhm|width|15\\.0|3\\.5|5\\.46|peaks|name|center|shape\" -S" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
3:  "name": "C1s Scan",
106:    283.51999999999975,
354:    5563.508358604201,
394:  "peaks": [
398:      "name": "Graphite",
399:      "center": 284.49985921191154,
400:      "fwhm": 0.6414557003192596,
402:      "shape": "asym-GL",
417:      "fixCenter": true,
418:      "fixFwhm": false,
431:      "_afCenterMin": 284.2,
432:      "_afCenterMax": 284.8,
433:      "_afFwhmMin": 0.4,
434:      "_afFwhmMax": 1.2,
458:        "center": {
466:        "fwhm": {
489:      "name": "Adventitious 1",
490:      "center": 284.852002566043,
491:      "fwhm": 1.495155170684445,
493:      "shape": "GL",
508:      "fixCenter": true,
509:      "fixFwhm": false,
522:      "_afCenterMin": 284.8,
523:      "_afCenterMax": 285.3,
524:      "_afFwhmMin": 0.8,
525:      "_afFwhmMax": 3,
539:        "center": {
547:        "fwhm": {
570:      "name": "Adventitious 2",
571:      "center": 285.98308468924773,
572:      "fwhm": 1.8480190712579603,
574:      "shape": "GL",
589:      "fixCenter": true,
590:      "fixFwhm": false,
603:      "_afCenterMin": 285.7,
604:      "_afCenterMax": 286.7,
605:      "_afFwhmMin": 0.8,
606:      "_afFwhmMax": 3,
620:        "center": {
628:        "fwhm": {
651:      "name": "Adventitious 3",
652:      "center": 287.5879343614907,
653:      "fwhm": 3.5476363434178904,
655:      "shape": "GL",
670:      "fixCenter": true,
671:      "fixFwhm": false,
684:      "_afCenterMin": 287.3,
685:      "_afCenterMax": 288.3,
686:      "_afFwhmMin": 0.8,
687:      "_afFwhmMax": 3.5,
701:        "center": {
709:        "fwhm": {
714:          "value": 3.5476363434178904,
732:      "name": "π→π* satellite",
733:      "center": 291.1600984121252,
734:      "fwhm": 4.140356877285836,
736:      "shape": "GL",
751:      "fixCenter": true,
752:      "fixFwhm": false,
765:      "_afCenterMin": 290,
766:      "_afCenterMax": 292,
767:      "_afFwhmMin": 1,
768:      "_afFwhmMax": 4,
774:          "stderr": 223.59121611585135,
782:        "center": {
790:        "fwhm": {
813:      "name": "Unknown 1",
814:      "center": 283.8509401262397,
815:      "fwhm": 1.6526233630844314,
817:      "shape": "GL",
832:      "fixCenter": true,
833:      "fixFwhm": false,
846:      "_afCenterMin": 282.2,
847:      "_afCenterMax": 283.8,
848:      "_afFwhmMin": 0.5,
849:      "_afFwhmMax": 3,
863:        "center": {
871:        "fwhm": {
1036:      70643.58533958357,
1095:  "lineWidth": 1.5,

codex
The project archives themselves do contain lab-fit width metadata around 3.0 to 4.0 eV and the removed 3.5 max, but not 15.0 as a C 1s width cap. I’m extracting the peak FWHM maxima structurally from the zip JSON now, which is less noisy than text grep and avoids mistaking raw spectral values near 15 for fit constraints.
codex
The sandbox blocks shell here-docs because it cannot create temporary files. I’m switching to `python -c` inline so the JSON extraction still stays read-only.
exec
/bin/zsh -lc 'python3 -B -c $'"'import json, zipfile\\nfrom pathlib import Path\\nfor zp in sorted(Path(\"docs/autofit/test_data\").glob(\"*.proj.zip\")):\\n    rows=[]\\n    with zipfile.ZipFile(zp) as z:\\n        for name in z.namelist():\\n            if not name.endswith(\".json\") or name == \"manifest.json\": continue\\n            data=json.loads(z.read(name))\\n            if \"C1s\" not in data.get(\"name\",\"\") and \"C 1s\" not in data.get(\"name\",\"\"): continue\\n            for p in data.get(\"peaks\",[]) or []:\\n                rows.append((float(p.get(\"fwhm\", -1) or -1), p.get(\"_afFwhmMax\"), data.get(\"name\"), p.get(\"name\"), name))\\n    if rows:\\n        rows.sort(reverse=True)\\n        print(zp.name)\\n        for f,maxv,spec,pname,name in rows[:8]:\\n            print(f\"  fwhm={f:.6g} afMax={maxv"'!r} spectrum={spec!r} peak={pname!r} file={name}")'"'" in /Users/skyefortier/xps-verify
 succeeded in 182ms:
1-GTA UCl4-graphite one set of U doublets.proj.zip
  fwhm=4.9981 afMax=4 spectrum='C1s Scan_8' peak='π→π* satellite' file=spectrum_18_C1s_Scan_8.json
  fwhm=4.93864 afMax=4 spectrum='C1s Scan_3' peak='π→π* satellite' file=spectrum_8_C1s_Scan_3.json
  fwhm=4.9037 afMax=4 spectrum='C1s Scan_5' peak='π→π* satellite' file=spectrum_12_C1s_Scan_5.json
  fwhm=4.69234 afMax=4 spectrum='C1s Scan_2' peak='π→π* satellite' file=spectrum_6_C1s_Scan_2.json
  fwhm=4.57381 afMax=4 spectrum='C1s Scan_0' peak='π→π* satellite' file=spectrum_2_C1s_Scan_0.json
  fwhm=4.28016 afMax=4 spectrum='C1s Scan_7' peak='π→π* satellite' file=spectrum_16_C1s_Scan_7.json
  fwhm=4.14187 afMax=4 spectrum='C1s Scan_6' peak='π→π* satellite' file=spectrum_14_C1s_Scan_6.json
  fwhm=4.04829 afMax=4 spectrum='C1s Scan_4' peak='π→π* satellite' file=spectrum_10_C1s_Scan_4.json
8-JT Graphite.proj.zip
  fwhm=5.46193 afMax=3.5 spectrum='C1s Scan_4' peak='Adventitious 3' file=spectrum_15_C1s_Scan_4.json
  fwhm=5.43471 afMax=3.5 spectrum='C1s Scan_5' peak='Adventitious 3' file=spectrum_16_C1s_Scan_5.json
  fwhm=5.03767 afMax=4 spectrum='C1s Scan_2' peak='π→π* satellite' file=spectrum_13_C1s_Scan_2.json
  fwhm=4.98809 afMax=4 spectrum='C1s Scan_4' peak='π→π* satellite' file=spectrum_15_C1s_Scan_4.json
  fwhm=4.95098 afMax=4 spectrum='C1s Scan_5' peak='π→π* satellite' file=spectrum_16_C1s_Scan_5.json
  fwhm=4.79895 afMax=4 spectrum='C1s Scan_6' peak='π→π* satellite' file=spectrum_17_C1s_Scan_6.json
  fwhm=4.73233 afMax=3.5 spectrum='C1s Scan_8' peak='Adventitious 3' file=spectrum_19_C1s_Scan_8.json
  fwhm=4.61961 afMax=4 spectrum='C1s Scan_3' peak='π→π* satellite' file=spectrum_14_C1s_Scan_3.json
Cl2p_projfit_test.proj.zip
  fwhm=4.2879 afMax=4 spectrum='C1s Scan_1' peak='π→π* satellite' file=spectrum_3_C1s_Scan_1.json
  fwhm=4.25536 afMax=4 spectrum='C1s Scan_4' peak='π→π* satellite' file=spectrum_6_C1s_Scan_4.json
  fwhm=4.25015 afMax=4 spectrum='C1s Scan_3' peak='π→π* satellite' file=spectrum_5_C1s_Scan_3.json
  fwhm=4.24807 afMax=4 spectrum='C1s Scan_5' peak='π→π* satellite' file=spectrum_7_C1s_Scan_5.json
  fwhm=4.16708 afMax=4 spectrum='C1s Scan_0' peak='π→π* satellite' file=spectrum_2_C1s_Scan_0.json
  fwhm=4.14036 afMax=4 spectrum='C1s Scan' peak='π→π* satellite' file=spectrum_1_C1s_Scan.json
  fwhm=4.00681 afMax=4 spectrum='C1s Scan_2' peak='π→π* satellite' file=spectrum_4_C1s_Scan_2.json
  fwhm=3.59478 afMax=3.5 spectrum='C1s Scan_4' peak='Adventitious 3' file=spectrum_6_C1s_Scan_4.json
Project9_CasaXPS_newfit.proj.zip
  fwhm=4.2879 afMax=4 spectrum='C1s Scan_1' peak='π→π* satellite' file=spectrum_3_C1s_Scan_1.json
  fwhm=4.25536 afMax=4 spectrum='C1s Scan_4' peak='π→π* satellite' file=spectrum_6_C1s_Scan_4.json
  fwhm=4.25015 afMax=4 spectrum='C1s Scan_3' peak='π→π* satellite' file=spectrum_5_C1s_Scan_3.json
  fwhm=4.24807 afMax=4 spectrum='C1s Scan_5' peak='π→π* satellite' file=spectrum_7_C1s_Scan_5.json
  fwhm=4.16708 afMax=4 spectrum='C1s Scan_0' peak='π→π* satellite' file=spectrum_2_C1s_Scan_0.json
  fwhm=4.14036 afMax=4 spectrum='C1s Scan' peak='π→π* satellite' file=spectrum_1_C1s_Scan.json
  fwhm=4.00681 afMax=4 spectrum='C1s Scan_2' peak='π→π* satellite' file=spectrum_4_C1s_Scan_2.json
  fwhm=3.59478 afMax=3.5 spectrum='C1s Scan_4' peak='Adventitious 3' file=spectrum_6_C1s_Scan_4.json
UCl4_on_graphite.proj.zip
  fwhm=5.16588 afMax=3.5 spectrum='C1s Scan_0' peak='Adventitious 3' file=spectrum_11_C1s_Scan_0.json
  fwhm=4.41814 afMax=4 spectrum='C1s Scan_0' peak='π→π* satellite' file=spectrum_11_C1s_Scan_0.json
  fwhm=4.20402 afMax=4 spectrum='C1s Scan' peak='π→π* satellite' file=spectrum_10_C1s_Scan.json
  fwhm=4.09649 afMax=3.5 spectrum='C1s Scan_5' peak='Adventitious 3' file=spectrum_16_C1s_Scan_5.json
  fwhm=3.78709 afMax=3.5 spectrum='C1s Scan_8' peak='Adventitious 3' file=spectrum_19_C1s_Scan_8.json
  fwhm=3.52421 afMax=3.5 spectrum='C1s Scan_1' peak='Adventitious 3' file=spectrum_12_C1s_Scan_1.json
  fwhm=2.8866 afMax=3.5 spectrum='C1s Scan_6' peak='Adventitious 3' file=spectrum_17_C1s_Scan_6.json
  fwhm=2.82858 afMax=3 spectrum='C1s Scan_4' peak='Adventitious 1' file=spectrum_15_C1s_Scan_4.json

codex
Structurally extracted archive widths top out around 5.46 eV for C 1s fitted peaks, and the archived `_afFwhmMax` values are 3, 3.5, or 4 eV in these C 1s fits. That supports the 15.0 claim as a reused fitting guard rather than a disguised lab-fit value; the degeneracy risk is still real because the new bound is much wider than any archived C 1s fit.
exec
/bin/zsh -lc "nl -ba autofit/methods/ic_model_comparison.py | sed -n '1,220p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""
     2	Method 2 — grammar + information-criterion model comparison (fitalg engine).
     3	
     4	Runs the full comparison pipeline over a resolved grammar and returns the
     5	top survivor's decomposition, per-slot confidence vectors, and the complete
     6	candidate/criteria record for the ``analysis`` namespace.
     7	"""
     8	
     9	from __future__ import annotations
    10	
    11	from typing import Any, Callable, Optional
    12	
    13	import numpy as np
    14	
    15	from ..confidence import build_confidence_vector
    16	from ..criteria import build_criteria_panel
    17	from ..engine import ComparisonResult, ModelReport, compare_models, _slot_prefix
    18	from ..grammar import BACKEND_SHAPE, CandidateGrammar
    19	from .base import MethodResult, PeakFitMethod, poisson_like_weights
    20	
    21	_ALLOWED_OPTIONS = {
    22	    "noise_floor", "n_refits", "rng_seed", "candidate_filter",
    23	    "enable_proposal_pass", "persistence_threshold", "bic_ambiguity_threshold",
    24	    "absent_slot_area_fraction", "absent_slot_persistence_threshold",
    25	    "enable_preseed", "fit_full_window",
    26	}
    27	
    28	ENGINE_VERSION = "autofit-stage2"
    29	
    30	
    31	class ICModelComparisonMethod(PeakFitMethod):
    32	    id = "ic_model_comparison"
    33	    label = "Auto — model comparison (IC)"
    34	    requires_grammar = True
    35	
    36	    def run(
    37	        self,
    38	        x: np.ndarray,
    39	        y: np.ndarray,
    40	        weights: Optional[np.ndarray] = None,
    41	        grammar: Optional[CandidateGrammar] = None,
    42	        peak_specs: Optional[list[dict]] = None,
    43	        options: Optional[dict[str, Any]] = None,
    44	        progress_cb: Optional[Callable[[dict], None]] = None,
    45	    ) -> MethodResult:
    46	        if grammar is None:
    47	            raise ValueError("ic_model_comparison requires a resolved grammar")
    48	        opts = dict(options or {})
    49	        unknown = set(opts) - _ALLOWED_OPTIONS
    50	        if unknown:
    51	            raise ValueError(f"unknown ic_model_comparison options: {sorted(unknown)}")
    52	
    53	        x = np.asarray(x, dtype=float)
    54	        y = np.asarray(y, dtype=float)
    55	        w = np.asarray(weights, dtype=float) if weights is not None \
    56	            else poisson_like_weights(y)
    57	        noise_floor = float(opts.pop("noise_floor", 1.0))
    58	
    59	        result = compare_models(
    60	            x, y, w, grammar,
    61	            noise_floor=noise_floor,
    62	            n_refits=int(opts.pop("n_refits", 20)),
    63	            rng_seed=int(opts.pop("rng_seed", 0)),
    64	            candidate_filter=opts.pop("candidate_filter", None),
    65	            enable_proposal_pass=bool(opts.pop("enable_proposal_pass", True)),
    66	            enable_preseed=bool(opts.pop("enable_preseed", True)),
    67	            persistence_threshold=float(opts.pop("persistence_threshold", 0.7)),
    68	            bic_ambiguity_threshold=float(opts.pop("bic_ambiguity_threshold", 2.0)),
    69	            absent_slot_area_fraction=float(opts.pop("absent_slot_area_fraction", 0.02)),
    70	            absent_slot_persistence_threshold=float(
    71	                opts.pop("absent_slot_persistence_threshold", 0.7)),
    72	            progress_cb=progress_cb,
    73	            fit_full_window=bool(opts.pop("fit_full_window", False)),
    74	        )
    75	
    76	        analysis = build_analysis_record(grammar, result)
    77	        truncation_note = (
    78	            f"analysis truncated — {result.n_candidates_evaluated} of "
    79	            f"{result.n_candidates_total} candidates evaluated before the "
    80	            "overall time budget was reached"
    81	            if result.analysis_truncated else None
    82	        )
    83	        if not result.survivors:
    84	            return MethodResult(
    85	                method_id=self.id, success=False, peaks=[], analysis=analysis,
    86	                confidence={}, diagnostics={
    87	                    "n_reports": len(result.reports),
    88	                    "analysis_truncated": result.analysis_truncated,
    89	                    "n_candidates_evaluated": result.n_candidates_evaluated,
    90	                    "n_candidates_total": result.n_candidates_total,
    91	                },
    92	                message=("no candidate survived filter-then-rank — see analysis "
    93	                         "for filtered/non-converged detail (diagnostic, not "
    94	                         "prescriptive: manual attention required)"
    95	                         + (f"; {truncation_note}" if truncation_note else "")),
    96	            )
    97	
    98	        top = result.survivors[0]
    99	        # Slots classified "correctly absent" won the BIC*-adjustment benefit
   100	        # precisely because they carry no real signal — emitting them as
   101	        # fitted peaks would contradict that classification (Codex finding
   102	        # #4).  They remain visible in analysis.candidates[].absent_slots.
   103	        absent_roles = {a.role for a in top.absent_slots}
   104	        peaks = _peaks_from_report(top, exclude_roles=absent_roles)
   105	        confidence = {
   106	            slot.role: build_confidence_vector(top, slot.role, noise_floor)
   107	            for slot in top.model.slots
   108	            if slot.role not in absent_roles
   109	        }
   110	        message = ""
   111	        winner_unassigned_roles = sorted(
   112	            slot.role for slot in top.model.slots
   113	            if slot.region == "unassigned"
   114	            and slot.role not in absent_roles
   115	        )
   116	        if winner_unassigned_roles:
   117	            centers = [
   118	                f"{c.position:.2f}" for r in winner_unassigned_roles
   119	                for c in top.primary_fit.components if c.slot_role == r
   120	            ]
   121	            message += (
   122	                f"DATA-DRIVEN component(s) at {', '.join(centers)} eV "
   123	                "(detected/seeded/proposed, region-unassigned): chemical "
   124	                "assignment requires human review; positions are "
   125	                "data-driven, not literature-anchored. "
   126	            )
   127	        if result.conditional:
   128	            # the conditional banner leads, but must not CLOBBER the
   129	            # data-driven/human-review note (Stage-2: a conditional
   130	            # detection-family winner still needs its assignment caveat)
   131	            if result.conditional_reason == "decisive_override":
   132	                message = (
   133	                    "CONDITIONAL result (decisive_override): clean candidates "
   134	                    "exist but a bound-fixed refit of a constraint-limited "
   135	                    f"candidate dominates them — winner {top.model.name} with "
   136	                    f"parameters fixed at bounds: {top.boundary_fixed_params}; "
   137	                    "clean alternatives retained in the ranking "
   138	                    "(see analysis.candidates). "
   139	                ) + message
   140	            elif result.conditional_reason == "unstable_last_resort":
   141	                message = (
   142	                    "UNSTABLE result (last resort): NO candidate passed any "
   143	                    "selection tier — component identities are NOT stable "
   144	                    "across refits (min persistence "
   145	                    f"{top.active_min_persistence:.2f}, orphan rate "
   146	                    f"{top.stability.orphan_rate:.2f}).  Showing the best "
   147	                    f"CONVERGED model ({top.model.name}, χ²ᵣ "
   148	                    f"{top.reduced_chi_sq:.1f}) so you can see what the data "
   149	                    "supports — treat EVERY component as a low-confidence "
   150	                    "suggestion; the data may not distinguish one broad "
   151	                    "feature from several overlapping ones here. "
   152	                ) + message
   153	            else:
   154	                message = (
   155	                    "CONDITIONAL result (no_clean_survivor): no candidate "
   156	                    "passed plausibility cleanly; ranking the stable-but-"
   157	                    f"boundary-limited tier — winner {top.model.name} has "
   158	                    f"constraint violations {top.plausibility.boundary_hits} "
   159	                    "(see analysis.candidates). "
   160	                ) + message
   161	        if top.plausibility.unphysical_widths:
   162	            message += (
   163	                " LOW CONFIDENCE — width(s) held at the ordinary physical "
   164	                f"FWHM cap ({', '.join(top.plausibility.unphysical_widths)}): "
   165	                "the data wants a broader component than an ordinary core line "
   166	                "physically has, but no known-broad class (satellite / plasmon "
   167	                "/ loss) is assigned here. The width is capped at the physical "
   168	                "limit rather than silently widened; a human should identify "
   169	                "the feature (or justify a wider width) before trusting it."
   170	            )
   171	        return MethodResult(
   172	            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
   173	            confidence=confidence,
   174	            diagnostics={
   175	                "winner": top.model.name,
   176	                "conditional": bool(result.conditional),
   177	                "conditional_reason": result.conditional_reason,
   178	                "winner_boundary_hits": list(top.plausibility.boundary_hits),
   179	                "winner_unphysical_widths": list(top.plausibility.unphysical_widths),
   180	                "winner_boundary_fixed_params": list(top.boundary_fixed_params),
   181	                # stress-suite finding 0: buried decisive evidence is a
   182	                # RESULT-level flag, not candidate-table archaeology
   183	                "filtered_dominant_alternative":
   184	                    result.filtered_dominant_alternative,
   185	                "weighted_ic_disagreement": result.weighted_ic_disagreement,
   186	                "preseeded_features": result.preseeded_features,
   187	                "n_survivors": len(result.survivors),
   188	                "n_filtered": len(result.filtered_out),
   189	                "n_non_converged": len(result.non_converged),
   190	                "analysis_truncated": result.analysis_truncated,
   191	                "n_candidates_evaluated": result.n_candidates_evaluated,
   192	                "n_candidates_total": result.n_candidates_total,
   193	            },
   194	            message=(message + (
   195	                f" WARNING: filtered candidate "
   196	                f"{result.filtered_dominant_alternative['name']} beats this "
   197	                f"winner by ΔBIC* "
   198	                f"{result.filtered_dominant_alternative['delta_bic_vs_winner']:.1f} "
   199	                "but did not survive filtering "
   200	                f"({result.filtered_dominant_alternative['filter_reason']})"
   201	                if result.filtered_dominant_alternative else "")
   202	                + (f" {truncation_note}." if truncation_note else "")),
   203	        )
   204	
   205	
   206	def _peaks_from_report(
   207	    report: ModelReport, exclude_roles: frozenset | set = frozenset()
   208	) -> list[dict]:
   209	    """Winning decomposition as backend-spec-shaped dicts."""
   210	    peaks = []
   211	    lm = report.primary_fit.lmfit_result
   212	    for slot in report.model.slots:
   213	        if slot.role in exclude_roles:
   214	            continue
   215	        comp = next((c for c in report.primary_fit.components
   216	                     if c.slot_role == slot.role), None)
   217	        if comp is None:
   218	            continue
   219	        rec = {
   220	            "role": slot.role,

exec
/bin/zsh -lc "rg -n \"def run|class .*Method|ic_model_comparison|fit_candidate\\(|rank_and_filter|CandidateReport\" autofit/methods autofit/engine.py -S" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/engine.py:160:# See fit_candidate() docstring: deterministic per-call ceiling on lmfit's
autofit/engine.py:768:    tier via rank_and_filter) rather than silently accepted.  Region-agnostic:
autofit/engine.py:838:def fit_candidate(
autofit/engine.py:1147:def run_stability_analysis(
autofit/engine.py:1210:        outcome = fit_candidate(x, y, weights, model, initial_params=init)
autofit/engine.py:1628:def rank_and_filter(
autofit/engine.py:1701:    # compare_models — it needs the spectrum to refit; rank_and_filter is
autofit/engine.py:2189:    primary = fit_candidate(x, y, weights, aug_model, initial_params=init)
autofit/engine.py:2414:    outcome = fit_candidate(x, y, weights, report.model, initial_params=params)
autofit/engine.py:2732:            outcome = fit_candidate(x, y, weights, model,
autofit/engine.py:2783:        primary = screen_fit.get(model.name) or fit_candidate(
autofit/engine.py:2907:    result = rank_and_filter(
autofit/methods/base.py:22:class MethodResult:
autofit/methods/base.py:38:class PeakFitMethod(ABC):
autofit/methods/base.py:47:    def run(
autofit/methods/base.py:65:        ``ic_model_comparison`` threads it through to a real signal
autofit/methods/base.py:71:class NotImplementedMethod(PeakFitMethod):
autofit/methods/base.py:77:    def run(self, *args, **kwargs) -> MethodResult:  # noqa: D102
autofit/methods/ic_model_comparison.py:31:class ICModelComparisonMethod(PeakFitMethod):
autofit/methods/ic_model_comparison.py:32:    id = "ic_model_comparison"
autofit/methods/ic_model_comparison.py:36:    def run(
autofit/methods/ic_model_comparison.py:47:            raise ValueError("ic_model_comparison requires a resolved grammar")
autofit/methods/ic_model_comparison.py:51:            raise ValueError(f"unknown ic_model_comparison options: {sorted(unknown)}")
autofit/methods/ic_model_comparison.py:307:        "method": "ic_model_comparison",
autofit/methods/__init__.py:7:  2. ic_model_comparison     — fitalg engine port (peak-count by IC panel)
autofit/methods/__init__.py:22:from .ic_model_comparison import ICModelComparisonMethod
autofit/methods/sparse_map.py:171:class SparseMAPMethod(PeakFitMethod):
autofit/methods/sparse_map.py:176:    def run(
autofit/methods/multivariate_mcr.py:100:class MultivariateMCRMethod(PeakFitMethod):
autofit/methods/multivariate_mcr.py:105:    def run(
autofit/methods/least_squares.py:26:class LeastSquaresMethod(PeakFitMethod):
autofit/methods/least_squares.py:31:    def run(
autofit/methods/max_entropy.py:64:class MaxEntropyMethod(PeakFitMethod):
autofit/methods/max_entropy.py:71:    def run(
autofit/methods/bayesian_exchange_mc.py:120:def run_exchange_mc(
autofit/methods/bayesian_exchange_mc.py:294:class BayesianExchangeMCMethod(PeakFitMethod):
autofit/methods/bayesian_exchange_mc.py:299:    def run(

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '820,940p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
   846	) -> FitOutcome:
   847	    """One fit of ``model`` to (x, y, weights); background subtracted first.
   848	
   849	    ``max_nfev`` bounds leastsq's own effort per call. lmfit's default
   850	    (200000*(nvars+1), see lmfit.Minimizer) is effectively unbounded: a
   851	    candidate whose params wander to a valid-but-degenerate corner (e.g.
   852	    DS+G's alpha/beta pinned at their bounds — a shape preference, not a
   853	    param error; see _BOUNDARY_EXCLUDED) produces a landscape leastsq can't
   854	    descend, and it spins for tens of thousands of evaluations without
   855	    terminating. Diagnostic run (2026-07-05, Suggest-peaks hang
   856	    investigation) showed a clean bimodal split: converged fits topped out
   857	    at nfev=14890; non-convergent ones started at nfev=21604. This cap sits
   858	    between the two so lmfit's own AbortFitException (caught internally by
   859	    leastsq(), surfacing as result.success=False) cuts off the latter
   860	    deterministically, without clipping legitimate slow-but-converging fits.
   861	    """
   862	    x = np.asarray(x, dtype=float)
   863	    y = np.asarray(y, dtype=float)
   864	    weights = np.asarray(weights, dtype=float)
   865	
   866	    bg = _compute_background(x, y, model.background)
   867	    y_sub = y - bg
   868	    composite = _build_composite_model(model)
   869	    params = initial_params if initial_params is not None else \
   870	        _default_params_from_slots(model, x=x, y_net=y_sub,
   871	                                   fit_full_window=fit_full_window)
   872	
   873	    try:
   874	        result = composite.fit(y_sub, params, x=x, weights=weights,
   875	                               method="leastsq", nan_policy="omit",
   876	                               max_nfev=max_nfev)
   877	        if (not result.success and result.chisqr is not None
   878	                and np.isfinite(result.chisqr)):
   879	            # ONE warm restart (Stage-2, measured on the real diagnosis
   880	            # scans): a model whose optimum sits against parameter bounds
   881	            # stalls MINPACK on a flat transformed gradient — it reaches
   882	            # the minimum, then burns the whole nfev budget without
   883	            # satisfying ftol (success=False at a genuinely converged
   884	            # χ²).  Restarting AT the exit point resets leastsq's internal
   885	            # diag scaling and it certifies in tens of evaluations
   886	            # (measured: 6000 nfev burned cold → 33 nfev warm, identical
   887	            # χ²).  Fires ONLY on a failed-but-finite fit, so converging
   888	            # fits are byte-identical; cost is bounded by one
   889	            # WARM_RESTART_MAX_NFEV fit.
   890	            retry = composite.fit(y_sub, result.params.copy(), x=x,
   891	                                  weights=weights, method="leastsq",
   892	                                  nan_policy="omit",
   893	                                  max_nfev=WARM_RESTART_MAX_NFEV)
   894	            if retry.success:
   895	                result = retry
   896	    except Exception as exc:
   897	        log.debug("fit_candidate failed for %s: %s", model.name, exc)
   898	        return FitOutcome(
   899	            converged=False, components=[], residual_sum_sq=float("inf"),
   900	            weighted_chi_sq=float("inf"),
   901	            n_params=len([q for q in params.values() if q.vary]),
   902	            n_data=len(y_sub), lmfit_result=None, background=bg,
   903	        )
   904	
   905	    unweighted_r = y_sub - result.best_fit
   906	    return FitOutcome(
   907	        converged=bool(result.success),
   908	        components=_extract_fitted_components(result, model),
   909	        residual_sum_sq=float(np.sum(unweighted_r ** 2)),
   910	        weighted_chi_sq=float(result.chisqr) if result.chisqr is not None else float("inf"),
   911	        n_params=result.nvarys,
   912	        n_data=len(y_sub),
   913	        lmfit_result=result,
   914	        background=bg,
   915	        boundary_hits=_detect_boundary_hits(result.params, model),
   916	    )
   917	
   918	
   919	def compute_slot_areas(
   920	    model: CandidateModel, primary: FitOutcome, x: np.ndarray
   921	) -> dict[str, float]:
   922	    if primary.lmfit_result is None:
   923	        return {}
   924	    composite = primary.lmfit_result.model
   925	    params = primary.lmfit_result.params
   926	    out: dict[str, float] = {}
   927	    for slot in model.slots:
   928	        prefix = _slot_prefix(slot.role)
   929	        sub = next((c for c in composite.components if c.prefix == prefix), None)
   930	        if sub is None:
   931	            continue
   932	        out[slot.role] = float(abs(trapezoid(sub.eval(params, x=x), x)))
   933	    return out
   934	
   935	
   936	def perturb_initial_params(
   937	    model: CandidateModel,
   938	    seed: int,
   939	    position_jitter_eV: float = 0.15,
   940	    fwhm_jitter_frac: float = 0.20,

exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '1,140p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""
     2	Composable grammar for the autofit engine (spec v2.1 §2).
     3	
     4	``resolve(phases, regions, ...)`` → :class:`CandidateGrammar`.
     5	
     6	Three layers:
     7	
     8	- **Layer A** — material class (per phase): lineshape family admissibility,
     9	  charge strategy, reference.
    10	- **Layer B** — region/element module (``autofit.regions``): doublet
    11	  Δso/ratio, BE windows, allowed lineshapes, satellites, core-hole width.
    12	- **Layer C** — oxidation-state override (multiplet fingerprint, BE shift).
    13	  Seam only in Stage 2 — region modules may accept it, none require it.
    14	
    15	Multi-phase model (v2 B1 fix): a ``phases`` list, never a pairwise
    16	``mixed{analyte, matrix}``.  Every :class:`ComponentSlot` carries a
    17	``phase_id``; when the same region is contributed by more than one phase the
    18	caller MUST disambiguate with ``target_phases`` (Codex precondition 2 — a
    19	region is not a unique key).
    20	
    21	Multi-region co-fit ([Skye]): ``regions`` is multi-valued; the grammars of
    22	all requested regions are composed into joint candidates fit together in the
    23	shared window (e.g. U 4f + N 1s overlap).
    24	"""
    25	
    26	from __future__ import annotations
    27	
    28	import itertools
    29	import re
    30	from dataclasses import dataclass, field
    31	from enum import Enum
    32	from typing import Optional
    33	
    34	from .fit_physics import provenance_entries as _fit_physics_provenance
    35	
    36	__all__ = [
    37	    "LineShape", "BackgroundType", "MaterialClass", "Phase", "ComponentSlot",
    38	    "CandidateModel", "CandidateGrammar", "PhaseAmbiguityError",
    39	    "UnknownRegionError", "resolve", "BACKEND_SHAPE",
    40	]
    41	
    42	
    43	class LineShape(Enum):
    44	    GAUSSIAN = "gaussian"
    45	    LORENTZIAN = "lorentzian"
    46	    PSEUDO_VOIGT = "pseudo_voigt"    # backend pseudo_voigt_gl
    47	    ASYM_GL = "asym_gl"              # backend asymmetric_gl
    48	    DS = "doniach_sunjic"
    49	    DS_G = "ds_g"                    # DS core ⊗ Gaussian (fitalg's "LA_ASYMMETRIC")
    50	    LACX = "la_casaxps"              # true CasaXPS LA(α, β, m)
    51	
    52	
    53	# LineShape → fitting.py _SHAPE_FUNCS key
    54	BACKEND_SHAPE: dict[LineShape, str] = {
    55	    LineShape.GAUSSIAN: "gaussian",
    56	    LineShape.LORENTZIAN: "lorentzian",
    57	    LineShape.PSEUDO_VOIGT: "pseudo_voigt_gl",
    58	    LineShape.ASYM_GL: "asymmetric_gl",
    59	    LineShape.DS: "doniach_sunjic",
    60	    LineShape.DS_G: "ds_g",
    61	    LineShape.LACX: "la_casaxps",
    62	}
    63	
    64	# Shapes whose asymmetric tail encodes physics (metallic screening or an
    65	# unresolvable multiplet envelope) — admissible only where Layer A allows.
    66	ASYMMETRIC_SHAPES = frozenset({LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G, LineShape.LACX})
    67	
    68	
    69	class BackgroundType(Enum):
    70	    SHIRLEY = "shirley"
    71	    SMART = "smart"
    72	    SMART_EXP = "smart_exp"      # Avantage-style constrained Shirley
    73	    LINEAR = "linear"
    74	    TOUGAARD = "tougaard"
    75	
    76	
    77	class MaterialClass(Enum):
    78	    CONDUCTOR = "conductor"
    79	    SEMICONDUCTOR = "semiconductor"
    80	    INSULATOR = "insulator"
    81	    # Analyte embedded in a different matrix (2026-07-20): differential
    82	    # charging between analyte and matrix is possible, which voids the
    83	    # single-species-homogeneity assumption behind some region modules'
    84	    # width ceilings. MIXED only RELAXES existing constraints (region
    85	    # modules opt in — see autofit.regions.c1s) — it asserts no new
    86	    # position or width value, and it must never reach charge-correction
    87	    # (that stays byte-identical to every other material class; see
    88	    # tests/test_api_analyze.py::test_material_class_does_not_affect_charge_correction).
    89	    # Appended LAST so the default dropdown/first-enum-member selection
    90	    # (conductor) is unchanged.
    91	    MIXED = "mixed"
    92	
    93	
    94	@dataclass(frozen=True)
    95	class Phase:
    96	    """
    97	    One physical phase of the sample (spec §2).  ``regions`` declares which
    98	    core-level regions this phase's material contributes signal to — the
    99	    resolver uses it to detect region↔phase ambiguity.
   100	    """
   101	    id: str
   102	    material_class: MaterialClass
   103	    regions: tuple[str, ...]
   104	    role: str = "analyte"                    # analyte | matrix | phase
   105	    material: Optional[str] = None           # e.g. "graphite" — region-module hint
   106	    # Per-phase charge reference (Layer A default when None):
   107	    #   conductor → internal (graphite C 1s 284.4 eV / Fermi edge)
   108	    #   insulator → adventitious C 1s 284.8 eV (CONDITIONAL, Biesinger 2022)
   109	    #   semiconductor → internal-if-present else adventitious
   110	    charge_reference: Optional[dict] = None
   111	    shift_model: str = "rigid"               # per-phase rigid shift (Stage 2)
   112	
   113	
   114	@dataclass(frozen=True)
   115	class ComponentSlot:
   116	    """
   117	    A component defined by grammar role — the stable identity used for
   118	    cross-refit matching (never optimizer index).  Ported from fitalg with
   119	    two generalizations: ``phase_id``/``region`` tagging, and generic
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

codex
One consequential implementation detail: the engine’s “ordinary physical width” warning explicitly skips slots whose declared maximum is above the ordinary cap. Under MIXED, that means a 15 eV contamination fit is treated as grammar-sanctioned broad, so the existing low-confidence width warning will not fire for the exact pathology this feature opens.
exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '690,835p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
   726	        if short == "amplitude" and at_min:
   727	            continue
   728	        # relaxed doublet ratio at a bound is a real constraint violation —
   729	        # counted (it means the data is fighting the physical ratio window).
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

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '1585,1665p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
  1585	    # uncertainty, not a dead end).
  1586	    conditional: bool = False
  1587	    conditional_reason: Optional[str] = None
  1588	    # The ambiguity threshold ACTUALLY used for ambiguous_pairs — consumers
  1589	    # (criteria panel) must reuse it so the payload can never disagree with
  1590	    # the ranking (Codex Stage-2 re-review finding #1).
  1591	    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY
  1592	    # A filtered candidate whose BIC* beats the winner's by more than the
  1593	    # decisive threshold — {name, bic_star, delta_bic_vs_winner,
  1594	    # filter_reason} or None.  Stress-suite finding 0: evidence burial must
  1595	    # be machine-visible at the result level.
  1596	    filtered_dominant_alternative: Optional[dict] = None
  1597	    # The weighted-χ² criterion (consistent with the fit weights) prefers a
  1598	    # DIFFERENT survivor than the ranking's RSS-form BIC* — {rss_bic_top,
  1599	    # weighted_bic_top, note} or None (BIC/IC math review blocker:
  1600	    # selection must not silently rest on a likelihood the fits reject).
  1601	    weighted_ic_disagreement: Optional[dict] = None
  1602	    # Set when the sweep hit TOTAL_ANALYSIS_TIMEOUT_SEC and stopped before
  1603	    # evaluating every candidate in the grammar. The candidates evaluated so
  1604	    # far are still ranked/reported normally (best-so-far) — this only flags
  1605	    # that the comparison is partial, so a slow/pathological spectrum
  1606	    # returns an honest incomplete result instead of a request timeout.
  1607	    analysis_truncated: bool = False
  1608	    n_candidates_evaluated: int = 0
  1609	    n_candidates_total: int = 0
  1610	    # Pre-fit out-of-grammar dominant seeding (unit F1): the detected
  1611	    # features every candidate was augmented with, incl. the gate values
  1612	    # (UNVERIFIED tunables) — empty when detection found nothing, in which
  1613	    # case the candidate set ran unmodified.
  1614	    preseeded_features: list[dict] = field(default_factory=list)
  1615	    # Two-phase sweep record (unit F3) — None when the classic single-phase
  1616	    # path ran (candidate set ≤ SCREEN_TOP_K).  Otherwise every candidate's
  1617	    # screen outcome: {name, converged, bic, selected} — screened-out
  1618	    # candidates are visible here and can never be survivors.
  1619	    screen: Optional[list[dict]] = None
  1620	    # Candidate-generation layer (autofit.candidates): the OVERCOMPLETE,
  1621	    # provenance-tagged detection pool payload — every feature any source
  1622	    # (local_max / curvature_shoulder / residual_gap / grammar) proposed,
  1623	    # with per-feature gate outcomes and seeding decisions.  None when the
  1624	    # layer did not run (enable_preseed=False or no candidates).
  1625	    candidate_pool: Optional[dict] = None
  1626	
  1627	
  1628	def rank_and_filter(
  1629	    reports: list[ModelReport],
  1630	    persistence_threshold: float = DEFAULT_PERSISTENCE_THRESHOLD,
  1631	    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY,
  1632	    allow_conditional: bool = True,
  1633	    allow_last_resort: bool = False,
  1634	) -> ComparisonResult:
  1635	    """
  1636	    Filter (plausibility, active persistence) then rank (χ²ᵣ, BIC*).
  1637	
  1638	    Two-tier semantics (departure from fitalg, which returned zero survivors
  1639	    whenever every candidate had any boundary hit — routine on real composite
  1640	    samples): when NO candidate passes plausibility cleanly but some are
  1641	    otherwise stable, those are ranked as a CONDITIONAL tier with
  1642	    ``result.conditional = True`` and every violation preserved.  Stability
  1643	    failures are never promoted — an unstable fit is pathology, not a
  1644	    constraint conflict.
  1645	    """
  1646	    filtered_out: list[tuple[ModelReport, str]] = []
  1647	    survivors: list[ModelReport] = []
  1648	    conditional_pool: list[ModelReport] = []
  1649	
  1650	    for r in reports:
  1651	        active_min = r.active_min_persistence
  1652	        stable = active_min >= persistence_threshold
  1653	        if r.plausibility.boundary_hits or r.plausibility.unphysical_widths \
  1654	                or r.plausibility.orphan_peaks:
  1655	            # orphan_peaks included (Codex Stage-2 re-review finding #3):
  1656	            # refits repeatedly producing unmatched components is a
  1657	            # plausibility violation, not clean-survivor material.
  1658	            filtered_out.append((r, f"plausibility: {r.plausibility}"))
  1659	            if stable:
  1660	                conditional_pool.append(r)
  1661	            continue
  1662	        if not stable:
  1663	            absent_roles = [a.role for a in r.absent_slots]
  1664	            extra = f"  (absent slots excluded: {absent_roles})" if absent_roles else ""
  1665	            filtered_out.append((r, f"stability: active min persistence "

exec
/bin/zsh -lc 'rg -n "unphysical_widths|boundary_hits|shared_contamination_fwhm|shared_fwhm" autofit/engine.py autofit/methods -S' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/engine.py:112:# the physical limit and the result is flagged (unphysical_widths →
autofit/engine.py:494:    for name, lo_b, hi_b in model.shared_fwhm_params:
autofit/engine.py:652:    boundary_hits: list[str] = field(default_factory=list)
autofit/engine.py:703:def _detect_boundary_hits(params: Parameters, model: CandidateModel) -> list[str]:
autofit/engine.py:750:    return [h for h in outcome.boundary_hits if h.startswith(f"{role}:")]
autofit/engine.py:915:        boundary_hits=_detect_boundary_hits(result.params, model),
autofit/engine.py:1422:    boundary_hits: list[str] = field(default_factory=list)
autofit/engine.py:1423:    unphysical_widths: list[str] = field(default_factory=list)
autofit/engine.py:1441:    boundary_hits: list[str] = field(default_factory=list)
autofit/engine.py:1653:        if r.plausibility.boundary_hits or r.plausibility.unphysical_widths \
autofit/engine.py:1901:        shared_fwhm_params=base.shared_fwhm_params,
autofit/engine.py:2108:        shared_fwhm_params=base.shared_fwhm_params,
autofit/engine.py:2203:    # (unphysical_widths + the fwhm@max boundary hit → CONDITIONAL) rather
autofit/engine.py:2212:    pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
autofit/engine.py:2215:    spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
autofit/engine.py:2273:    pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
autofit/engine.py:2274:    spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
autofit/engine.py:2279:    pr.width_capped = pr.boundary_hits == [width_cap_hit]
autofit/engine.py:2303:            boundary_hits=list(primary.boundary_hits),
autofit/engine.py:2304:            unphysical_widths=_unphysical_width_flags(primary.components, aug_model),
autofit/engine.py:2394:    if lm is None or not report.plausibility.boundary_hits:
autofit/engine.py:2398:    for hit in report.plausibility.boundary_hits:
autofit/engine.py:2417:    if outcome.boundary_hits:
autofit/engine.py:2439:            boundary_hits=[],
autofit/engine.py:2443:            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
autofit/engine.py:2815:                boundary_hits=list(primary.boundary_hits),
autofit/engine.py:2816:                unphysical_widths=_unphysical_width_flags(primary.components, model),
autofit/methods/ic_model_comparison.py:158:                    f"constraint violations {top.plausibility.boundary_hits} "
autofit/methods/ic_model_comparison.py:161:        if top.plausibility.unphysical_widths:
autofit/methods/ic_model_comparison.py:164:                f"FWHM cap ({', '.join(top.plausibility.unphysical_widths)}): "
autofit/methods/ic_model_comparison.py:178:                "winner_boundary_hits": list(top.plausibility.boundary_hits),
autofit/methods/ic_model_comparison.py:179:                "winner_unphysical_widths": list(top.plausibility.unphysical_widths),
autofit/methods/ic_model_comparison.py:286:            "unphysical_widths": list(r.plausibility.unphysical_widths),
autofit/methods/ic_model_comparison.py:289:            "boundary_hits": r.plausibility.boundary_hits,
autofit/methods/ic_model_comparison.py:292:            "unphysical_widths": r.plausibility.unphysical_widths,

codex
I’m going to run the narrow structural test file first; it does not need uploads or temp fixtures, so it should survive the read-only sandbox. API tests may still be blocked because the Flask upload fixture has to write session files.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -p no:cacheprovider tests/autofit/test_c1s_mixed_material_class.py' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: pytest

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 node --test tests/js/fp_material_mixed.test.js' in /Users/skyefortier/xps-verify
 succeeded in 123ms:
# Subtest: FP_STRINGS.materials.mixed has a clear, non-bare label
ok 1 - FP_STRINGS.materials.mixed has a clear, non-bare label
  ---
  duration_ms: 0.89356
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed hint is advisory, never claims correction
ok 2 - FP_STRINGS.materials.mixed hint is advisory, never claims correction
  ---
  duration_ms: 0.271473
  type: 'test'
  ...
# Subtest: FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
ok 3 - FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
  ---
  duration_ms: 0.151227
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
# duration_ms 84.31823

codex
`pytest` is not on PATH in this sandbox; the JS test runs and passes. I’ll try `python -m pytest` once before falling back to static/test-path reasoning.
codex
The Python test runner is not installed for the system interpreter here, so I can’t execute the Python tests in this environment. I’m continuing with direct code execution where possible and static review for the API test path.
exec
/bin/zsh -lc "python3 -B -c \"from autofit.grammar import MaterialClass, Phase, resolve; g=resolve([Phase(id='sample', material_class=MaterialClass.MIXED, regions=('C 1s',))], 'C 1s'); print(len(g.candidates)); print([c.name for c in g.candidates if c.name in ('A1_linked','A3_linked','AG3_linked','B3_linked')]); print([c.shared_fwhm_params for c in g.candidates if c.name in ('A3_linked','AG3_linked')])\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-5uFi5pvw' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-U4aWpwiH' (errno=Operation not permitted)
29
['A1_linked', 'A3_linked', 'AG3_linked', 'B3_linked']
[(('shared_contamination_fwhm', 0.8, 15.0),), (('shared_contamination_fwhm', 0.8, 15.0),)]

codex
The direct grammar execution confirms the linked families carry `shared_contamination_fwhm` with `(0.8, 15.0)` under MIXED. Full optimizer execution is blocked because `lmfit` is not installed in this interpreter, so I can only reason through the degeneracy from the model geometry and engine code.
exec
/bin/zsh -lc 'python3 -B -c $'"'from autofit.grammar import MaterialClass, Phase, resolve\\nfrom autofit.regions.c1s import FWHM_RANGE_CONTAMINATION\\nfor mc in [MaterialClass.CONDUCTOR,MaterialClass.SEMICONDUCTOR,MaterialClass.INSULATOR,MaterialClass.MIXED]:\\n    g=resolve([Phase(id=\"s\",material_class=mc,regions=(\"C 1s\",))],\"C 1s\")\\n    vals=sorted({s.fwhm_range for c in g.candidates for s in c.slots if s.fwhm_range[0]==FWHM_RANGE_CONTAMINATION[0]})\\n    shared=sorted({tuple(c.shared_fwhm_params) for c in g.candidates if c.shared_fwhm_params})\\n    print(mc.value, vals, shared[:2])'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-6nrfF3NQ' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-AIik9WSu' (errno=Operation not permitted)
conductor [(0.8, 2.0)] [(('shared_contamination_fwhm', 0.8, 2.0),)]
semiconductor [(0.8, 2.0)] [(('shared_contamination_fwhm', 0.8, 2.0),)]
insulator [(0.8, 2.0)] [(('shared_contamination_fwhm', 0.8, 2.0),)]
mixed [(0.8, 15.0)] [(('shared_contamination_fwhm', 0.8, 15.0),)]

codex
I’ve finished the main trace. The charge-correction isolation is clean in `_validate_analyze_request`: `corrected = energy - cc_shift` is computed before `Phase(material_class=mclass, ...)`, and the material class only enters grammar resolution after `x/y` are fixed.
exec
/bin/zsh -lc "rg -n \"FWHM_MAX_ORDINARY_EV|PROPOSAL_FWHM_MAX|FWHM_RANGE|15\\.0\" autofit/engine.py autofit/regions -S" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/engine.py:116:FWHM_MAX_ORDINARY_EV = 2.0
autofit/engine.py:120:PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV
autofit/engine.py:158:PROPOSAL_MIN_FIT_BUDGET_SEC = 15.0
autofit/engine.py:757:    ceiling (:data:`FWHM_MAX_ORDINARY_EV`) with NO known-broad justification.
autofit/engine.py:790:            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and \
autofit/engine.py:791:                    declared_hi <= FWHM_MAX_ORDINARY_EV:
autofit/engine.py:794:                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (DS+G "
autofit/engine.py:805:            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and \
autofit/engine.py:806:                    declared_hi <= FWHM_MAX_ORDINARY_EV:
autofit/engine.py:809:                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (asym-GL "
autofit/engine.py:826:        if declared_hi > FWHM_MAX_ORDINARY_EV:
autofit/engine.py:831:        if eff_fwhm >= FWHM_MAX_ORDINARY_EV - tol:
autofit/engine.py:833:                f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥{FWHM_MAX_ORDINARY_EV:.1f}eV "
autofit/engine.py:1853:                                  PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX))
autofit/engine.py:1893:            fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/engine.py:2054:                                  PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX))
autofit/engine.py:2102:        fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/engine.py:2619:                fwhm_clip=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/regions/u4f.py:75:U4F_MAIN_FWHM_RANGE = (1.5, 3.5)
autofit/regions/u4f.py:98:U4F_SAT_FWHM_RANGE = (1.5, 4.5)
autofit/regions/u4f.py:151:            {"constant": "satellite_fwhm_ev", "value": list(U4F_SAT_FWHM_RANGE),
autofit/regions/u4f.py:154:            {"constant": "main_fwhm_range_ev", "value": list(U4F_MAIN_FWHM_RANGE),
autofit/regions/u4f.py:203:            "main_u4f72", U4F72_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
autofit/regions/u4f.py:209:            "main_u4f52", U4F52_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
autofit/regions/u4f.py:219:            U4F_SAT_FWHM_RANGE,
autofit/regions/u4f.py:225:            U4F_SAT_FWHM_RANGE,
autofit/regions/u4f.py:235:            U4F_SAT_FWHM_RANGE,
autofit/regions/u4f.py:247:            U4F_SAT_FWHM_RANGE,
autofit/regions/u4f.py:253:            U4F_SAT_FWHM_RANGE,
autofit/regions/n1s.py:35:N1S_FWHM_RANGE = (0.7, 2.5)       # UNVERIFIED-empirical (exemplar 1.05 eV)
autofit/regions/n1s.py:55:            {"constant": "fwhm_range_ev", "value": list(N1S_FWHM_RANGE),
autofit/regions/n1s.py:74:            fwhm_range=N1S_FWHM_RANGE,
autofit/regions/n1s.py:79:            fwhm_range=N1S_FWHM_RANGE,
autofit/regions/b1s.py:49:B1S_FWHM_RANGE = (1.2, 2.5)
autofit/regions/b1s.py:75:            {"constant": "fwhm_range_ev", "value": list(B1S_FWHM_RANGE),
autofit/regions/b1s.py:95:                fwhm_range=B1S_FWHM_RANGE,
autofit/regions/c1s.py:60:FWHM_RANGE_GRAPHITIC = (0.4, 1.2)
autofit/regions/c1s.py:64:FWHM_RANGE_AROMATIC_POLYMER = (0.8, 1.8)
autofit/regions/c1s.py:70:FWHM_RANGE_SATELLITE = (1.0, 5.5)
autofit/regions/c1s.py:82:FWHM_RANGE_CONTAMINATION = (0.8, 2.0)
autofit/regions/c1s.py:84:# MIXED material class (2026-07-20): FWHM_RANGE_CONTAMINATION's ceiling is
autofit/regions/c1s.py:105:# fitting.py's OWN existing fwhm_max default (15.0 eV), the ceiling the
autofit/regions/c1s.py:122:FWHM_MIXED_CEILING_NUMERIC_GUARD_EV = 15.0
autofit/regions/c1s.py:126:    """FWHM_RANGE_CONTAMINATION, widened under MIXED. See the constant
autofit/regions/c1s.py:129:        return (FWHM_RANGE_CONTAMINATION[0], FWHM_MIXED_CEILING_NUMERIC_GUARD_EV)
autofit/regions/c1s.py:130:    return FWHM_RANGE_CONTAMINATION
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
autofit/regions/cl2p.py:54:CL2P_FWHM_RANGE = (1.2, 2.2)        # UNVERIFIED-empirical (labeled 1.65–1.80)
autofit/regions/cl2p.py:64:CL2P_12_FWHM_RANGE = (CL2P_FWHM_RANGE[0],
autofit/regions/cl2p.py:65:                      CL2P_FWHM_RANGE[1] + CL2P_12_FWHM_EXCESS_RANGE[1])
autofit/regions/cl2p.py:91:            {"constant": "fwhm_range_ev", "value": list(CL2P_FWHM_RANGE),
autofit/regions/cl2p.py:130:                fwhm_range=CL2P_FWHM_RANGE,
autofit/regions/cl2p.py:140:                    fwhm_range=CL2P_12_FWHM_RANGE,
autofit/regions/cl2p.py:151:                fwhm_range=CL2P_FWHM_RANGE,

codex
1. **MAJOR** [autofit/engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:753), [autofit/regions/c1s.py](/Users/skyefortier/xps-verify/autofit/regions/c1s.py:122): MIXED makes contamination slots “grammar-sanctioned broad,” so the existing unphysical-width warning is bypassed for the exact new failure mode. `_unphysical_width_flags()` skips any slot with `declared_hi > FWHM_MAX_ORDINARY_EV`, and MIXED raises contamination slots and `shared_contamination_fwhm` to 15.0 eV. A linked C 1s contaminant family can fit `shared_contamination_fwhm ~= 8-14 eV`, spanning most/all of the 280-292 eV region, without `unphysical_widths` unless it pegs the 15 eV boundary. Concrete scenario: an A3/AG3 linked-offset candidate on a spectrum with broad residual curvature can let CO/C=O/OC=O act as a smooth background/envelope and absorb aliphatic or neighboring contaminant intensity, then survive as clean if stable. This needs either a much lower guard or an explicit “numeric guard / absorption risk” diagnostic for broad MIXED contamination widths.

2. **MAJOR** [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13030): the only user-facing MIXED copy overstates scope. “Peak width limits are relaxed accordingly” reads globally, but the code relaxes only C 1s contamination/adventitious widths; U 4f, Cl 2p, B 1s, N 1s, graphitic C 1s, satellites, BE windows, and charge correction are unchanged. Concrete scenario: a chemist selects MIXED for U 4f in BN/graphite and believes analyte peak widths or charging treatment changed, when the app does no such thing. The hint should say “For C 1s, adventitious/contamination width limits are relaxed...” and keep the “does not correct” warning.

3. **MINOR** [tests/autofit/test_c1s_mixed_material_class.py](/Users/skyefortier/xps-verify/tests/autofit/test_c1s_mixed_material_class.py:92): the tests do not fully protect the provenance trap. `test_mixed_relaxes_contamination_fwhm_ceiling` only checks `> 2.0`, so a lab-derived 3.5 eV cap would pass. The provenance tests check “string not bare number” and code/doc equality, but do not assert the guard equals `fitting.py`’s existing `fwhm_max` default or inspect `shared_fwhm_params` directly. Concrete scenario: code and provenance both drift to `3.5` under “numeric guard” wording, or linked shared-width bounds stop matching slots, and these tests can still pass.

Self-reference check otherwise passes: `fitting.py` has the pre-existing `spec.get("fwhm_max", 15.0)` default at [fitting.py](/Users/skyefortier/xps-verify/fitting.py:867) and [fitting.py](/Users/skyefortier/xps-verify/fitting.py:916). I found lab/archive C 1s fitted widths around 3-5.46 eV and old `_afFwhmMax` values of 3/3.5/4, but no C 1s fit-width source near 15. Charge-correction isolation also passes statically: `corrected = energy - cc_shift` is computed before `Phase(material_class=mclass, ...)` at [app.py](/Users/skyefortier/xps-verify/app.py:253). JS test passed; Python tests could not be run here because `pytest` and `lmfit` are not installed.

VERDICT: NO-GO
tokens used
162,054
1. **MAJOR** [autofit/engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:753), [autofit/regions/c1s.py](/Users/skyefortier/xps-verify/autofit/regions/c1s.py:122): MIXED makes contamination slots “grammar-sanctioned broad,” so the existing unphysical-width warning is bypassed for the exact new failure mode. `_unphysical_width_flags()` skips any slot with `declared_hi > FWHM_MAX_ORDINARY_EV`, and MIXED raises contamination slots and `shared_contamination_fwhm` to 15.0 eV. A linked C 1s contaminant family can fit `shared_contamination_fwhm ~= 8-14 eV`, spanning most/all of the 280-292 eV region, without `unphysical_widths` unless it pegs the 15 eV boundary. Concrete scenario: an A3/AG3 linked-offset candidate on a spectrum with broad residual curvature can let CO/C=O/OC=O act as a smooth background/envelope and absorb aliphatic or neighboring contaminant intensity, then survive as clean if stable. This needs either a much lower guard or an explicit “numeric guard / absorption risk” diagnostic for broad MIXED contamination widths.

2. **MAJOR** [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13030): the only user-facing MIXED copy overstates scope. “Peak width limits are relaxed accordingly” reads globally, but the code relaxes only C 1s contamination/adventitious widths; U 4f, Cl 2p, B 1s, N 1s, graphitic C 1s, satellites, BE windows, and charge correction are unchanged. Concrete scenario: a chemist selects MIXED for U 4f in BN/graphite and believes analyte peak widths or charging treatment changed, when the app does no such thing. The hint should say “For C 1s, adventitious/contamination width limits are relaxed...” and keep the “does not correct” warning.

3. **MINOR** [tests/autofit/test_c1s_mixed_material_class.py](/Users/skyefortier/xps-verify/tests/autofit/test_c1s_mixed_material_class.py:92): the tests do not fully protect the provenance trap. `test_mixed_relaxes_contamination_fwhm_ceiling` only checks `> 2.0`, so a lab-derived 3.5 eV cap would pass. The provenance tests check “string not bare number” and code/doc equality, but do not assert the guard equals `fitting.py`’s existing `fwhm_max` default or inspect `shared_fwhm_params` directly. Concrete scenario: code and provenance both drift to `3.5` under “numeric guard” wording, or linked shared-width bounds stop matching slots, and these tests can still pass.

Self-reference check otherwise passes: `fitting.py` has the pre-existing `spec.get("fwhm_max", 15.0)` default at [fitting.py](/Users/skyefortier/xps-verify/fitting.py:867) and [fitting.py](/Users/skyefortier/xps-verify/fitting.py:916). I found lab/archive C 1s fitted widths around 3-5.46 eV and old `_afFwhmMax` values of 3/3.5/4, but no C 1s fit-width source near 15. Charge-correction isolation also passes statically: `corrected = energy - cc_shift` is computed before `Phase(material_class=mclass, ...)` at [app.py](/Users/skyefortier/xps-verify/app.py:253). JS test passed; Python tests could not be run here because `pytest` and `lmfit` are not installed.

VERDICT: NO-GO
