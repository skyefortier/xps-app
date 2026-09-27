OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e254-a2ab-73e3-a67f-91cc6d6b471b
--------
user
Re-review unit F3 (the Auto-Fit C1s gate on live data), round 3: branch fix-noise-floor-scale-free. Round 2 was GO x2 (docs/autofit/codex/f3_c1s_gate_r2_verdict_run{A,B}.md) with MINORs fixed in the latest commit (git diff HEAD~1..HEAD): a behavioural caller test in tests/js/autofit_c1s_gate.test.js (each caller executed; the record reaching isC1sTab must be the active one), and the parked write-up docs/findings/noise-floor-occupancy/README.md corrected (LR described as what it is; F's invariance qualified by the Poisson variance floor). Earlier prompts: docs/autofit/codex/f3_c1s_gate_review_prompt.txt, _recheck_prompt.txt; plan docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

TRY TO BREAK
a. The behavioural test: does it now fail for your round-2 mutations (tabs[0] || ..., _getTab('inactive') || ...) and for any other way a caller could judge a non-active record; is it robust (not passing because a caller returned early before the gate).
b. The corrected README: accurate now, nothing overstated, recommendation sound.
c. Anything else in the unit (git diff 07e0839..HEAD, excluding merges of fix-fit-start-poll).

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll check the prior review requirements, challenge the caller test with mutations, and review the full F3 diff and corrected README. I’ll keep the workspace read-only and finish with a verdict.

exec
/bin/zsh -lc "pwd; git status --short; rg --files -g AGENTS.md -g '*f3_c1s*' -g '*2026-09-27-f3*'; git diff --stat HEAD~1..HEAD; git log --oneline -10" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-qr1bSIup' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-7ZK8E9nh' (errno=Operation not permitted)
?? docs/autofit/codex/f3_c1s_gate_r3_verdict_runA.md
?? docs/autofit/codex/f3_c1s_gate_r3_verdict_runB.md
docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md
docs/autofit/codex/f3_c1s_gate_r2_verdict_runB.md
docs/autofit/codex/f3_c1s_gate_recheck2_prompt.txt
docs/autofit/codex/f3_c1s_gate_verdict_runA.md
docs/autofit/codex/f3_c1s_gate_review_prompt.txt
docs/autofit/codex/f3_c1s_gate_r3_verdict_runB.md
docs/autofit/codex/f3_c1s_gate_r3_verdict_runA.md
docs/autofit/codex/f3_c1s_gate_r2_verdict_runA.md
docs/autofit/codex/f3_c1s_gate_recheck_prompt.txt
docs/autofit/codex/f3_c1s_gate_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Su12HnIm' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1YYO3uM7' (errno=Operation not permitted)
 docs/autofit/codex/f3_c1s_gate_r2_verdict_runA.md  | 21986 +++++++++++++++++++
 docs/autofit/codex/f3_c1s_gate_r2_verdict_runB.md  |  2143 ++
 docs/autofit/codex/f3_c1s_gate_recheck2_prompt.txt |     8 +
 docs/findings/noise-floor-occupancy/README.md      |    14 +-
 .../2026-09-27-f3-noise-floor-and-c1s-gate.md      |     9 +
 tests/js/autofit_c1s_gate.test.js                  |    20 +
 6 files changed, 24177 insertions(+), 3 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-prJPYQ7P' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-U3xrMas6' (errno=Operation not permitted)
398a762 fix(F3): Codex round 2 (GO x2) - behavioural caller test; parked write-up corrected
5181304 fix(F3): Codex round 1 (GO x2) - record path mirrors getROIData; caller test proves the active tab; parked recommendation revised to F
895f323 fix(F3): the Auto-Fit C1s gate judges the data the fit would use; the noise-floor half PARKED for an owner decision
07e0839 Merge branch 'fix-acceptance-holes' into fix-fit-start-poll
c00c893 feat(unit 2): long fits via start-then-poll - no request of Run Fit or Auto-Fit meets the public ~100 s ceiling
0224141 fix(F2): Codex round 2 (A GO, B NO-GO) - linear token scan for the unreadable-reply message
a5a14a0 fix(F2): Codex round 1 (A GO, B NO-GO) - unverified DE refit gives no required verdict; NaN token test ignores strings
9210786 fix(F2): holes in the acceptance rule - basinhopping verified, NaN reply, undetermined models, required refit, Auto-Fit HTTP status
07e8f46 docs(F1): deploy-log entry
2e85ed7 docs(F1): owner's notes at deploy - 'two readings of one field' design rule; legacy verification on load logged in the sealed-fit-record memo

exec
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if [ -f "$p" ]; then cat "$p"; fi; done; rg --files --hidden -g AGENTS.md -g '"'"'!node_modules'"' -g '"'!.git'"'; cat docs/autofit/codex/f3_c1s_gate_review_prompt.txt docs/autofit/codex/f3_c1s_gate_recheck_prompt.txt docs/autofit/codex/f3_c1s_gate_recheck2_prompt.txt; cat docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
Review unit F3 (the Auto-Fit C1s gate on live data): branch fix-noise-floor-scale-free, stacked on fix-fit-start-poll. Review git diff 07e0839..HEAD (07e0839 is the unit-2 commit F3 was cut from; later unit-2 commits are NOT part of F3): templates/index.html (isC1sTab only), tests/js/autofit_c1s_gate.test.js, CLAUDE.md, docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md, and the PARKED half's write-up docs/findings/noise-floor-occupancy/ (README + two patches that are NOT applied — review the write-up's claims and the patches as proposals, and say which variant you would choose and why). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO (for the shipped gate change; the parked half is advice). Budget your time: a verdict is required within the run.

OWNER'S BRIEF (verbatim): "Find Peaks' absolute 1.0-count noise floor -> scale-free, per the design rule. Include the Auto-Fit C1s gate judging a stale typed window." Source: docs/findings/2026-09-25-fail-open-guards-sweep.md (branch sweep-fail-open-guards) M5 and M9.

TRY TO BREAK
a. isC1sTab: every caller and the moment it runs (menu state on ROI input, charge-reference permission, the Auto-Fit run at click time), the active tab vs a record (tab switch in progress, a stack tab active, a survey tab, a tab with no ROI typed, a reversed min/max, an ROI outside the data, an empty selection, a charge shift), getROIData()'s own semantics (corrected frame, inclusive, clipped), a very long scan (performance of the record path).
b. Anything the old behaviour allowed that users rely on (e.g. enabling Auto-Fit before the ROI is set).
c. The tests: real and non-vacuous (would fail on the old isC1sTab).
d. The parked half: are the measurements and the causal explanation in the README right (engine.py _extract_fitted_components / match_components_to_slots / rank_and_filter / the decisive override); is the recommendation sound; is anything in either patch wrong regardless of the choice (the variance floor left alone, orphans, the detectability payload, the grammar.contains change).

Finish with VERDICT: GO or VERDICT: NO-GO.
Re-review unit F3 (the Auto-Fit C1s gate on live data), round 2: branch fix-noise-floor-scale-free. Round 1 was GO x2 (docs/autofit/codex/f3_c1s_gate_verdict_run{A,B}.md) with two MINORs on the shipped change, fixed in the latest non-merge commit: (1) isC1sTab's record path now makes exactly getROIData()'s selection (each bound open on its own side when blank, never reordered — min > max selects nothing — inclusive, corrected frame, the shift read as getCorrectedBE reads state.ccShift); (2) the caller test now proves each caller looks the tab up by tabManager.activeId and judges that tab. The parked half's write-up (docs/findings/noise-floor-occupancy/README.md) was revised after your round-1 review: the LR recommendation is withdrawn, F is recommended with the two follow-ups you named. Review git diff 895f323..HEAD for the round-1 fixes (ignore any merge of fix-fit-start-poll: those are unit 2's changes, reviewed separately), and git diff 07e0839..HEAD minus unit-2 merges for the whole unit. Plan: docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

TRY TO BREAK
a. The record path vs getROIData()/getCorrectedBE(): every input (blank / NaN / reversed / equal bounds, Infinity or NaN ccShift, an empty rawBE); performance on a long record.
b. The strengthened caller test: would it catch a caller judging an inactive record?
c. The revised parked write-up: does it now state the evidence and your round-1 findings correctly; is the recommendation sound.
d. Anything round 1 verified that these changes touched.

Finish with VERDICT: GO or VERDICT: NO-GO.
Re-review unit F3 (the Auto-Fit C1s gate on live data), round 3: branch fix-noise-floor-scale-free. Round 2 was GO x2 (docs/autofit/codex/f3_c1s_gate_r2_verdict_run{A,B}.md) with MINORs fixed in the latest commit (git diff HEAD~1..HEAD): a behavioural caller test in tests/js/autofit_c1s_gate.test.js (each caller executed; the record reaching isC1sTab must be the active one), and the parked write-up docs/findings/noise-floor-occupancy/README.md corrected (LR described as what it is; F's invariance qualified by the Poisson variance floor). Earlier prompts: docs/autofit/codex/f3_c1s_gate_review_prompt.txt, _recheck_prompt.txt; plan docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

TRY TO BREAK
a. The behavioural test: does it now fail for your round-2 mutations (tabs[0] || ..., _getTab('inactive') || ...) and for any other way a caller could judge a non-active record; is it robust (not passing because a caller returned early before the gate).
b. The corrected README: accurate now, nothing overstated, recommendation sound.
c. Anything else in the unit (git diff 07e0839..HEAD, excluding merges of fix-fit-start-poll).

Finish with VERDICT: GO or VERDICT: NO-GO.
# F3 — the Auto-Fit C1s gate on live data; Find Peaks' noise floor (PARKED) (2026-09-27)

Branch `fix-noise-floor-scale-free`, stacked on `fix-fit-start-poll` (unit 2,
itself on F2): deploy F2 → unit 2 → F3, three fast-forwards. F3 touches
neither Run Fit nor the job path (only `isC1sTab`), so it can be rebased onto
main alone if unit 2 is held.

Owner's brief (2026-09-27): "Find Peaks' absolute 1.0-count noise floor ->
scale-free, per the design rule. Include the Auto-Fit C1s gate judging a
stale typed window." Sources: sweep M9 (first bullet) and M5
(`docs/findings/2026-09-25-fail-open-guards-sweep.md`).

## 1. Shipped: the Auto-Fit C1s gate judges the data the fit would use (M5)

| site | before | after |
|---|---|---|
| `isC1sTab(tab)` | the midpoint of `tab.ui.roiMin/roiMax` — for the ACTIVE tab a record synced only on a tab switch or save, and the TYPED values even where they reach past the data | for the active tab the live selection `getROIData()` returns (the fields clipped to the data, corrected frame); for any other record its saved window over its own corrected data; an empty selection is not C 1s; the midpoint of the SELECTED points is tested (270–315 eV, unchanged) |
| callers (`_recomputeAutoFitMenuState`, `_isChargeRefAllowed`, `runAutoFitC1sGraphite`) | — | unchanged; all three are for the active tab; the ROI fields already refresh the menu on every keystroke |

The sweep's reproduction (a wide 270–420 eV scan, the record's window on
C 1s, a U 4f window typed in the fields without a tab switch): the menu was
enabled and the gate passed, and the fit then took the U 4f₅/₂ line as
"Graphite" (the step (c) refit refused it in the page runs, but a server
construction passed every gate with a 107 eV provisional shift). Now the gate
closes. Not in scope (sweep suggestion, a threshold of its own): bounding the
provisional shift.

Tests: `tests/js/autofit_c1s_gate.test.js` (the reproduction closes; a live
C 1s selection passes; the selected data decide, not a typed window reaching
past them; an empty selection; a non-active record judged on its own
corrected data incl. a charge shift; every caller is the active tab; the ROI
fields refresh the menu).

## 2. PARKED for an owner decision: the occupancy floor (M9)

`docs/findings/noise-floor-occupancy/README.md`: two variants implemented as
patches and measured. The first draft recommended the likelihood ratio; Codex
round 1 (both runs) showed it is NOT invariant to intensity units and its
patch was inconsistent, and that the honesty failure under F comes from a
background-compensating component in a two-peak fixture. Revised
recommendation, both reviewers: F, as its own unit, with an unsupported
in-window component kept distinct from an orphan and a mismatch signal that
does not ride on that component.

## 3. Codex rounds

**Round 1 — GO ×2 for the shipped gate** (`f3_c1s_gate_verdict_run{A,B}.md`).
MINORs fixed: the record path now makes exactly getROIData()'s selection
(each bound open on its own side when blank, never reordered, the shift read
as getCorrectedBE reads it) — nonblocking, all callers pass the active tab;
the caller test now proves each caller looks the tab up by
`tabManager.activeId` and judges that tab. Three of the four gate tests fail
on the old code. The parked half's review is recorded in the findings README
(recommendation revised to F). Round 2 confirms the MINOR fixes.

**Round 2 — GO ×2** (`f3_c1s_gate_r2_verdict_run{A,B}.md`; the record path
matched getROIData() on 18 900 and 43 350 exact comparisons). MINORs fixed:
a BEHAVIOURAL caller test (each caller run with an inactive C 1s record first
and an active U 4f record; the record reaching `isC1sTab` must be the active
one — the reviewers' mutation `tabs[0] || _getTab(activeId)` now fails it);
the parked README's stale claims replaced (LR described as what it is; only F
is a ratio; F's invariance qualified by the retained Poisson variance floor).
Round 3 confirms.

exec
/bin/zsh -lc "cat docs/findings/noise-floor-occupancy/variant_F_support_test.patch docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch; rg -n 'def _component_support|def _extract_fitted_components|def match_components_to_slots|def rank_and_filter|decisive|filtered_dominant_alternative' fitting.py autofit" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
diff --git a/autofit/confidence.py b/autofit/confidence.py
index bb74778..ab2897f 100644
--- a/autofit/confidence.py
+++ b/autofit/confidence.py
@@ -83,6 +83,9 @@ def _max_correlation(report: ModelReport, role: str) -> Optional[float]:
     return float(np.max(sub)) if sub.size else None
 
 
+from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # F3: one threshold, the server's
+
+
 def build_confidence_vector(
     report: ModelReport,
     role: str,
@@ -96,12 +99,19 @@ def build_confidence_vector(
                 if h.startswith(f"{role}:")]
 
     amplitude = float(comp.amplitude) if comp is not None else None
-    floor = detection_floor_multiple * noise_floor
+    # F3 (2026-09-27): detectability is the support F test on the fit
+    # (fitting._component_support, the server's statistic), not multiples of an
+    # absolute 1-count floor. above_floor = supported (F >= SUPPORT_MIN_F);
+    # present_but_poorly_constrained = the fit gains from it but not
+    # significantly; not_confidently_detected = removing it costs nothing.
+    support = getattr(comp, "support", None) if comp is not None else None
     if amplitude is None:
         detect_status = "not_fitted"
-    elif amplitude >= floor:
+    elif support is None:
+        detect_status = "above_floor" if amplitude > 0 else "not_confidently_detected"
+    elif support.get("supported"):
         detect_status = "above_floor"
-    elif amplitude > noise_floor:
+    elif (support.get("delta_chi2") or 0.0) > 0:
         detect_status = "present_but_poorly_constrained"
     else:
         detect_status = "not_confidently_detected"
@@ -122,9 +132,9 @@ def build_confidence_vector(
         },
         "detectability": {
             "amplitude": amplitude,
-            "noise_floor": noise_floor,
-            "floor_multiple": detection_floor_multiple,
-            "floor_multiple_is_tunable": True,
+            "basis": "support_f_test",       # F3: fitting._component_support, F >= SUPPORT_MIN_F
+            "support_f": (support or {}).get("f"),
+            "support_min_f": _SUPPORT_MIN_F,
             "status": detect_status,
         },
         "identifiability": {
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..9bad455 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -36,6 +36,7 @@ from typing import Callable, Optional
 
 import numpy as np
 from lmfit import Model, Parameters
+import fitting as _fitting  # F3: the server's support statistic, one definition
 from lmfit.model import ModelResult
 from scipy.integrate import trapezoid
 
@@ -637,6 +638,17 @@ class FittedComponent:
     amplitude: float
     shape_params: dict
     line_shape: Optional[LineShape] = None
+    # Unit F3 (2026-09-27): does the fit that produced this component need it?
+    # fitting._component_support on that fit — with the other components held
+    # as fitted, removing this one must make the fit significantly worse (F >=
+    # SUPPORT_MIN_F). The occupancy decisions (slot matching, the proposal
+    # gate, detectability) read this instead of an absolute amplitude floor
+    # of 1 count, which judged a slot "occupied" at amplitude 1.5 and not at
+    # 0.5 whatever the data's scale (sweep M9; design rule "thresholds on
+    # data-scaled quantities fail"). None only where no fit is behind the
+    # component (hand-built in tests): then occupancy falls back to amplitude
+    # > 0, a sign test.
+    support: Optional[dict] = None
 
 
 @dataclass
@@ -652,10 +664,46 @@ class FitOutcome:
     boundary_hits: list[str] = field(default_factory=list)
 
 
+def _component_supports(result: ModelResult) -> dict[str, dict]:
+    """``fitting._component_support`` for every peak component of an lmfit
+    result, keyed by prefix — the one definition the server uses (step (b)).
+    Empty when the result carries no data (never raises: occupancy then falls
+    back to the sign test)."""
+    try:
+        comps = result.eval_components()
+        data = np.asarray(result.data, float)
+        fitted = np.asarray(result.best_fit, float)
+        w = result.weights if result.weights is not None else np.ones_like(data)
+        w = np.broadcast_to(np.asarray(w, float), data.shape)
+        n_free_total = int(result.nvarys)
+    except Exception:
+        return {}
+    out = {}
+    for prefix, comp_y in comps.items():
+        n_free_comp = sum(1 for n, par in result.params.items()
+                          if n.startswith(prefix) and par.vary and par.expr is None)
+        try:
+            out[prefix] = _fitting._component_support(data, fitted, np.asarray(comp_y, float), w,
+                                                      n_free_comp, n_free_total)
+        except Exception:
+            continue
+    return out
+
+
+def _occupies(comp: "FittedComponent") -> bool:
+    """A slot is occupied by a component the data support (F3). No threshold
+    on any data-scaled quantity: the support F test where a fit is behind the
+    component, else the sign of its amplitude."""
+    if comp.support is not None:
+        return bool(comp.support.get("supported"))
+    return comp.amplitude > 0
+
+
 def _extract_fitted_components(
     result: ModelResult, model: CandidateModel
 ) -> list[FittedComponent]:
     out: list[FittedComponent] = []
+    supports = _component_supports(result)
     for slot in model.slots:
         prefix = _slot_prefix(slot.role)
         pars = result.params
@@ -676,6 +724,7 @@ def _extract_fitted_components(
             slot_role=slot.role, position=center, fwhm=fwhm,
             amplitude=amplitude, shape_params=shape_params,
             line_shape=slot.line_shape,
+            support=supports.get(prefix),
         ))
     return out
 
@@ -1055,7 +1104,7 @@ def match_components_to_slots(
                                       (bound_overrides or {}).get(slot.role))
         return (lo <= comp.position <= hi
                 and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
-                and comp.amplitude > noise_floor)
+                and _occupies(comp))       # F3: supported by the data, not amplitude > 1 count
 
     def _window_center(slot: ComponentSlot) -> float:
         # NEVER the widened bound (Codex-caught, round 2): this is a
@@ -1077,7 +1126,7 @@ def match_components_to_slots(
             orphans.append(FittedComponent(
                 slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                 amplitude=comp.amplitude, shape_params=comp.shape_params,
-                line_shape=comp.line_shape,
+                line_shape=comp.line_shape, support=comp.support,
             ))
             continue
 
@@ -1095,7 +1144,7 @@ def match_components_to_slots(
         claimed = FittedComponent(
             slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
             amplitude=comp.amplitude, shape_params=comp.shape_params,
-            line_shape=comp.line_shape,
+            line_shape=comp.line_shape, support=comp.support,
         )
         if incumbent is None:
             slot_map[best_slot.role] = claimed
@@ -2229,8 +2278,10 @@ def _attempt_proposal(
     # to a wall (Codex fwhm-cap review, run B BLOCKER).
     width_cap_hit = f"{spec.role}:fwhm@max"
     pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
-    if comp.amplitude <= noise_floor:
-        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
+    if not _occupies(comp):
+        f = (comp.support or {}).get("f")
+        return _fast("not supported by the data (removing it does not make the fit significantly worse"
+                     + (f", F = {f:.2f} < {_fitting.SUPPORT_MIN_F:.0f}" if f is not None else "") + ")")
     spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
     if spurious_hits:
         return _fast(f"proposed slot boundary pegs: {spurious_hits}")
diff --git a/autofit/grammar.py b/autofit/grammar.py
index c9a85cd..bed2606 100644
--- a/autofit/grammar.py
+++ b/autofit/grammar.py
@@ -181,11 +181,15 @@ class ComponentSlot:
     broad_justification: Optional[str] = None
 
     def contains(self, be: float, fwhm: float, amplitude: float,
-                 noise_floor: float) -> bool:
+                 noise_floor: float = 0.0) -> bool:
+        # F3 (2026-09-27): occupancy is decided by the support F test on the
+        # fit (engine._occupies); this geometric check keeps only the sign of
+        # the amplitude. ``noise_floor`` is accepted and ignored (no caller in
+        # the engine passes it any more).
         return (
             self.be_window[0] <= be <= self.be_window[1]
             and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
-            and amplitude > noise_floor
+            and amplitude > 0
         )
 
 
diff --git a/autofit/confidence.py b/autofit/confidence.py
index bb74778..ab2897f 100644
--- a/autofit/confidence.py
+++ b/autofit/confidence.py
@@ -83,6 +83,9 @@ def _max_correlation(report: ModelReport, role: str) -> Optional[float]:
     return float(np.max(sub)) if sub.size else None
 
 
+from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # F3: one threshold, the server's
+
+
 def build_confidence_vector(
     report: ModelReport,
     role: str,
@@ -96,12 +99,19 @@ def build_confidence_vector(
                 if h.startswith(f"{role}:")]
 
     amplitude = float(comp.amplitude) if comp is not None else None
-    floor = detection_floor_multiple * noise_floor
+    # F3 (2026-09-27): detectability is the support F test on the fit
+    # (fitting._component_support, the server's statistic), not multiples of an
+    # absolute 1-count floor. above_floor = supported (F >= SUPPORT_MIN_F);
+    # present_but_poorly_constrained = the fit gains from it but not
+    # significantly; not_confidently_detected = removing it costs nothing.
+    support = getattr(comp, "support", None) if comp is not None else None
     if amplitude is None:
         detect_status = "not_fitted"
-    elif amplitude >= floor:
+    elif support is None:
+        detect_status = "above_floor" if amplitude > 0 else "not_confidently_detected"
+    elif support.get("supported"):
         detect_status = "above_floor"
-    elif amplitude > noise_floor:
+    elif (support.get("delta_chi2") or 0.0) > 0:
         detect_status = "present_but_poorly_constrained"
     else:
         detect_status = "not_confidently_detected"
@@ -122,9 +132,9 @@ def build_confidence_vector(
         },
         "detectability": {
             "amplitude": amplitude,
-            "noise_floor": noise_floor,
-            "floor_multiple": detection_floor_multiple,
-            "floor_multiple_is_tunable": True,
+            "basis": "support_f_test",       # F3: fitting._component_support, F >= SUPPORT_MIN_F
+            "support_f": (support or {}).get("f"),
+            "support_min_f": _SUPPORT_MIN_F,
             "status": detect_status,
         },
         "identifiability": {
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..e1a729e 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -36,6 +36,7 @@ from typing import Callable, Optional
 
 import numpy as np
 from lmfit import Model, Parameters
+import fitting as _fitting  # F3: the server's support statistic, one definition
 from lmfit.model import ModelResult
 from scipy.integrate import trapezoid
 
@@ -637,6 +638,17 @@ class FittedComponent:
     amplitude: float
     shape_params: dict
     line_shape: Optional[LineShape] = None
+    # Unit F3 (2026-09-27): does the fit that produced this component need it?
+    # fitting._component_support on that fit — with the other components held
+    # as fitted, removing this one must make the fit significantly worse (F >=
+    # SUPPORT_MIN_F). The occupancy decisions (slot matching, the proposal
+    # gate, detectability) read this instead of an absolute amplitude floor
+    # of 1 count, which judged a slot "occupied" at amplitude 1.5 and not at
+    # 0.5 whatever the data's scale (sweep M9; design rule "thresholds on
+    # data-scaled quantities fail"). None only where no fit is behind the
+    # component (hand-built in tests): then occupancy falls back to amplitude
+    # > 0, a sign test.
+    support: Optional[dict] = None
 
 
 @dataclass
@@ -652,10 +664,50 @@ class FitOutcome:
     boundary_hits: list[str] = field(default_factory=list)
 
 
+def _component_supports(result: ModelResult) -> dict[str, dict]:
+    """``fitting._component_support`` for every peak component of an lmfit
+    result, keyed by prefix — the one definition the server uses (step (b)).
+    Empty when the result carries no data (never raises: occupancy then falls
+    back to the sign test)."""
+    try:
+        comps = result.eval_components()
+        data = np.asarray(result.data, float)
+        fitted = np.asarray(result.best_fit, float)
+        w = result.weights if result.weights is not None else np.ones_like(data)
+        w = np.broadcast_to(np.asarray(w, float), data.shape)
+        n_free_total = int(result.nvarys)
+    except Exception:
+        return {}
+    out = {}
+    for prefix, comp_y in comps.items():
+        n_free_comp = sum(1 for n, par in result.params.items()
+                          if n.startswith(prefix) and par.vary and par.expr is None)
+        try:
+            out[prefix] = _fitting._component_support(data, fitted, np.asarray(comp_y, float), w,
+                                                      n_free_comp, n_free_total)
+            out[prefix]["_p"] = max(1, n_free_comp)
+        except Exception:
+            continue
+    return out
+
+
+def _occupies(comp: "FittedComponent") -> bool:
+    """A slot is occupied by a component the data support (F3). No threshold
+    on any data-scaled quantity: the support F test where a fit is behind the
+    component, else the sign of its amplitude."""
+    if comp.support is not None:
+        # PROBE (likelihood-ratio variant, not for shipping): the Poisson-weighted
+        # chi-square gain per free parameter, NOT normalised by the fit's misfit
+        d = comp.support.get("delta_chi2") or 0.0
+        return bool(d > 0 and d / max(1, comp.support.get("_p", 1)) >= _fitting.SUPPORT_MIN_F)
+    return comp.amplitude > 0
+
+
 def _extract_fitted_components(
     result: ModelResult, model: CandidateModel
 ) -> list[FittedComponent]:
     out: list[FittedComponent] = []
+    supports = _component_supports(result)
     for slot in model.slots:
         prefix = _slot_prefix(slot.role)
         pars = result.params
@@ -676,6 +728,7 @@ def _extract_fitted_components(
             slot_role=slot.role, position=center, fwhm=fwhm,
             amplitude=amplitude, shape_params=shape_params,
             line_shape=slot.line_shape,
+            support=supports.get(prefix),
         ))
     return out
 
@@ -1055,7 +1108,7 @@ def match_components_to_slots(
                                       (bound_overrides or {}).get(slot.role))
         return (lo <= comp.position <= hi
                 and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
-                and comp.amplitude > noise_floor)
+                and _occupies(comp))       # F3: supported by the data, not amplitude > 1 count
 
     def _window_center(slot: ComponentSlot) -> float:
         # NEVER the widened bound (Codex-caught, round 2): this is a
@@ -1077,7 +1130,7 @@ def match_components_to_slots(
             orphans.append(FittedComponent(
                 slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                 amplitude=comp.amplitude, shape_params=comp.shape_params,
-                line_shape=comp.line_shape,
+                line_shape=comp.line_shape, support=comp.support,
             ))
             continue
 
@@ -1095,7 +1148,7 @@ def match_components_to_slots(
         claimed = FittedComponent(
             slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
             amplitude=comp.amplitude, shape_params=comp.shape_params,
-            line_shape=comp.line_shape,
+            line_shape=comp.line_shape, support=comp.support,
         )
         if incumbent is None:
             slot_map[best_slot.role] = claimed
@@ -2229,8 +2282,10 @@ def _attempt_proposal(
     # to a wall (Codex fwhm-cap review, run B BLOCKER).
     width_cap_hit = f"{spec.role}:fwhm@max"
     pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
-    if comp.amplitude <= noise_floor:
-        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
+    if not _occupies(comp):
+        f = (comp.support or {}).get("f")
+        return _fast("not supported by the data (removing it does not make the fit significantly worse"
+                     + (f", F = {f:.2f} < {_fitting.SUPPORT_MIN_F:.0f}" if f is not None else "") + ")")
     spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
     if spurious_hits:
         return _fast(f"proposed slot boundary pegs: {spurious_hits}")
diff --git a/autofit/grammar.py b/autofit/grammar.py
index c9a85cd..bed2606 100644
--- a/autofit/grammar.py
+++ b/autofit/grammar.py
@@ -181,11 +181,15 @@ class ComponentSlot:
     broad_justification: Optional[str] = None
 
     def contains(self, be: float, fwhm: float, amplitude: float,
-                 noise_floor: float) -> bool:
+                 noise_floor: float = 0.0) -> bool:
+        # F3 (2026-09-27): occupancy is decided by the support F test on the
+        # fit (engine._occupies); this geometric check keeps only the sign of
+        # the amplitude. ``noise_floor`` is accepted and ignored (no caller in
+        # the engine passes it any more).
         return (
             self.be_window[0] <= be <= self.be_window[1]
             and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
-            and amplitude > noise_floor
+            and amplitude > 0
         )
 
 
fitting.py:1444:def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
autofit/methods/ic_model_comparison.py:132:            if result.conditional_reason == "decisive_override":
autofit/methods/ic_model_comparison.py:134:                    "CONDITIONAL result (decisive_override): clean candidates "
autofit/methods/ic_model_comparison.py:182:                # stress-suite finding 0: buried decisive evidence is a
autofit/methods/ic_model_comparison.py:184:                "filtered_dominant_alternative":
autofit/methods/ic_model_comparison.py:185:                    result.filtered_dominant_alternative,
autofit/methods/ic_model_comparison.py:197:                f"{result.filtered_dominant_alternative['name']} beats this "
autofit/methods/ic_model_comparison.py:199:                f"{result.filtered_dominant_alternative['delta_bic_vs_winner']:.1f} "
autofit/methods/ic_model_comparison.py:201:                f"({result.filtered_dominant_alternative['filter_reason']})"
autofit/methods/ic_model_comparison.py:202:                if result.filtered_dominant_alternative else "")
autofit/methods/ic_model_comparison.py:341:        "filtered_dominant_alternative": result.filtered_dominant_alternative,
autofit/methods/ic_model_comparison.py:343:        # BIC/IC math review: the ΔBIC thresholds (decisive 10 / ambiguity
autofit/methods/bayesian_exchange_mc.py:442:        # (Codex Stage-5 blocker #1: never report decisive weights on an
autofit/engine.py:83:# candidate; the result carries conditional_reason='decisive_override'.
autofit/engine.py:84:# Without any override, a clean-but-terrible fit masks a decisively better
autofit/engine.py:655:def _extract_fitted_components(
autofit/engine.py:1039:def match_components_to_slots(
autofit/engine.py:1500:    # Full lmfit param names fixed at their bounds by the decisive-override
autofit/engine.py:1597:    #   'decisive_override'  — clean survivors exist but a bound-fixed refit
autofit/engine.py:1610:    # decisive threshold — {name, bic_star, delta_bic_vs_winner,
autofit/engine.py:1613:    filtered_dominant_alternative: Optional[dict] = None
autofit/engine.py:1645:def rank_and_filter(
autofit/engine.py:1716:    # NOTE: the decisive-override path (clean survivors exist but a
autofit/engine.py:2472:        # promoted via decisive-override keeps its width_capped/proposed_peaks
autofit/engine.py:2479:def _apply_decisive_override(
autofit/engine.py:2524:        result.conditional_reason = "decisive_override"
autofit/engine.py:2575:    proposals, bound-fixed refits, decisive override, detection). Default 1
autofit/engine.py:2586:    refits, the proposal pass, and the bound-fixed decisive-override
autofit/engine.py:2950:    result = _apply_decisive_override(
autofit/engine.py:3000:    # at ΔBIC* +74…+944): a FILTERED candidate whose BIC* decisively beats
autofit/engine.py:3006:        # promotion LINEAGE, not just names: a decisive-override winner is
autofit/engine.py:3026:            result.filtered_dominant_alternative = {

exec
/bin/zsh -lc "git diff 07e0839..HEAD -- templates/index.html CLAUDE.md; rg -n 'function (isC1sTab|_recomputeAutoFitMenuState|_isChargeRefAllowed|runAutoFitC1sGraphite|getROIData|getCorrectedBE)|isC1sTab\\(|activeId =|_recomputeAutoFitMenuState\\(' templates/index.html; rg -n 'MINOR|VERDICT:|tabs\\[0\\]|_getTab\\(.inactive|11\\.67|10\\.07' docs/autofit/codex/f3_c1s_gate_r2_verdict_runB.md | tail -35; rg --files tests/js; ls -a | head -40" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-M7KFkug1' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-FfvffA4O' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 4b92c72..7f03bea 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -936,8 +936,10 @@ invariants worth knowing before touching the code:
 - **`+ Stack` / `+ Add Spectrum ▾`** (chart toolbar): create a new
   empty stack and add open spectrum tabs to the active stack.
 - **Auto-Fit C1s Graphite** (Actions menu): one-click C1s peak model
-  + charge correction. Enabled only when the active ROI midpoint is in
-  270–315 eV.
+  + charge correction. Enabled only when the midpoint of the DATA the fit
+  would use is in 270–315 eV — for the active tab the live selection
+  `getROIData()` returns, never the tab record's stale window or a typed
+  window reaching past the data (`isC1sTab`, unit F3 2026-09-27, sweep M5).
 - **ROI past the data / centre outside the data** (2026-09-25, warn only):
   `getROIData()` has always clamped an ROI to the data it selects; the page
   now SAYS so under the ROI fields ("ROI extends past your data — clipped
diff --git a/templates/index.html b/templates/index.html
index 72a215e..8b3f506 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7748,20 +7748,34 @@ async function runAutoFitC1sGraphite() {
   }
 }
 
+// Is this a C 1s spectrum, as Auto-Fit C1s Graphite would fit it? Unit F3
+// (2026-09-27, sweep M5): judged on the DATA the fit would use — for the active
+// tab the live selection getROIData() returns (the typed fields, clipped to the
+// data, in the corrected frame); for any other record its saved window over
+// its own corrected data. It used to read tab.ui, which for the ACTIVE tab is
+// synced only on a tab switch or save, and the TYPED midpoint: a wide scan with
+// the record's C 1s window but a U 4f window typed in the fields passed the
+// gate, and the fit then took the U 4f line as "Graphite".
 function isC1sTab(tab) {
   if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
-  const ui = tab.ui || {};
-  let lo = parseFloat(ui.roiMin);
-  let hi = parseFloat(ui.roiMax);
-  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
-    // Fall back to full raw range (no UI ROI set yet)
-    let rmin = Infinity, rmax = -Infinity;
-    for (const v of tab.rawBE) {
-      if (v < rmin) rmin = v;
-      if (v > rmax) rmax = v;
-    }
-    lo = rmin; hi = rmax;
-  }
+  let be;
+  const isActive = typeof tabManager !== 'undefined' && tabManager && tab.id === tabManager.activeId;
+  if (isActive && typeof getROIData === 'function') {
+    be = getROIData().be;
+  } else {
+    // the SAME selection getROIData() makes, on the record's own data: each
+    // bound independently open when blank, never reordered (min > max selects
+    // nothing), inclusive, corrected frame (Codex round 1)
+    const shift = isNaN(tab.ccShift) ? 0 : tab.ccShift;   // read as getCorrectedBE() reads state.ccShift
+    const ui = tab.ui || {};
+    const a = parseFloat(ui.roiMin), b = parseFloat(ui.roiMax);
+    const lo = isNaN(a) ? -Infinity : a, hi = isNaN(b) ? Infinity : b;
+    be = [];
+    for (const v of tab.rawBE) { const c = v - shift; if (c >= lo && c <= hi) be.push(c); }
+  }
+  if (!be || !be.length) return false;
+  let lo = Infinity, hi = -Infinity;
+  for (const v of be) { if (v < lo) lo = v; if (v > hi) hi = v; }
   if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
   const mid = (lo + hi) / 2;
   return mid >= 270.0 && mid <= 315.0;
2064:                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
2068:                <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
3136:    this.activeId = null;
3219:    if (this.activeId === id) return;
3229:    this.activeId = id;
3247:    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
3301:      this.activeId = null;
3327:    if (this.activeId === id) {
3329:      this.activeId = null; // force re-activate
5079:function getCorrectedBE() {
5087:function getROIData() {
6099:function _isChargeRefAllowed() {
6105:  return !!(tab && isC1sTab(tab));
6712:function _recomputeAutoFitMenuState() {
6718:  const enabled = !!tab && isC1sTab(tab);
6732:  if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
7558:async function runAutoFitC1sGraphite() {
7563:  if (!isC1sTab(tab)) {
7759:function isC1sTab(tab) {
12455:    if (tabManager.activeId === tid) {
13:Re-review unit F3 (the Auto-Fit C1s gate on live data), round 2: branch fix-noise-floor-scale-free. Round 1 was GO x2 (docs/autofit/codex/f3_c1s_gate_verdict_run{A,B}.md) with two MINORs on the shipped change, fixed in the latest non-merge commit: (1) isC1sTab's record path now makes exactly getROIData()'s selection (each bound open on its own side when blank, never reordered — min > max selects nothing — inclusive, corrected frame, the shift read as getCorrectedBE reads state.ccShift); (2) the caller test now proves each caller looks the tab up by tabManager.activeId and judges that tab. The parked half's write-up (docs/findings/noise-floor-occupancy/README.md) was revised after your round-1 review: the LR recommendation is withdrawn, F is recommended with the two follow-ups you named. Review git diff 895f323..HEAD for the round-1 fixes (ignore any merge of fix-fit-start-poll: those are unit 2's changes, reviewed separately), and git diff 07e0839..HEAD minus unit-2 merges for the whole unit. Plan: docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.
21:Finish with VERDICT: GO or VERDICT: NO-GO.
226:MINORs fixed: the record path now makes exactly getROIData()'s selection
232:(recommendation revised to F). Round 2 confirms the MINOR fixes.
343:/bin/zsh -lc "git diff 895f323..HEAD -- templates/index.html tests/js/autofit_c1s_gate.test.js docs/findings/noise-floor-occupancy/README.md; git diff 07e0839..HEAD -- templates/index.html tests/js/autofit_c1s_gate.test.js CLAUDE.md; rg -n 'MINOR|MAJOR|BLOCKER|VERDICT:|recommend|follow.up' docs/autofit/codex/f3_c1s_gate_verdict_runA.md docs/autofit/codex/f3_c1s_gate_verdict_runB.md | tail -70" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
646:docs/autofit/codex/f3_c1s_gate_verdict_runB.md:13:Review unit F3 (the Auto-Fit C1s gate on live data): branch fix-noise-floor-scale-free, stacked on fix-fit-start-poll. Review git diff 07e0839..HEAD (07e0839 is the unit-2 commit F3 was cut from; later unit-2 commits are NOT part of F3): templates/index.html (isC1sTab only), tests/js/autofit_c1s_gate.test.js, CLAUDE.md, docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md, and the PARKED half's write-up docs/findings/noise-floor-occupancy/ (README + two patches that are NOT applied — review the write-up's claims and the patches as proposals, and say which variant you would choose and why). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO (for the shipped gate change; the parked half is advice). Budget your time: a verdict is required within the run.
648:docs/autofit/codex/f3_c1s_gate_verdict_runB.md:23:Finish with VERDICT: GO or VERDICT: NO-GO.
651:docs/autofit/codex/f3_c1s_gate_verdict_runB.md:2122:        # record on the winner row (Codex fwhm-cap review, run A MINOR)
658:docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4401:4. **MINOR — shipped: inactive records use different ROI semantics.** [templates/index.html:7771](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7771). Saved `295–280` is reordered and passes, while the live selector returns nothing. On a 270–420 scan, saved `min=""`, `max=295` uses the whole scan and fails; the live selector selects 270–295 and passes. Mirror independent open bounds and preserve reversed bounds. This is nonblocking because all three current callers pass the active tab.
659:docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4403:5. **MINOR — tests: the caller assertion does not establish active-tab ownership.** [autofit_c1s_gate.test.js:60](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:60). Replacing a caller’s lookup with an inactive record would still satisfy `/isC1sTab\(tab\)/`. The other three tests are substantive: all three fail against `07e0839`.
660:docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4411:VERDICT: GO
665:docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4430:4. **MINOR — shipped: inactive records use different ROI semantics.** [templates/index.html:7771](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7771). Saved `295–280` is reordered and passes, while the live selector returns nothing. On a 270–420 scan, saved `min=""`, `max=295` uses the whole scan and fails; the live selector selects 270–295 and passes. Mirror independent open bounds and preserve reversed bounds. This is nonblocking because all three current callers pass the active tab.
666:docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4432:5. **MINOR — tests: the caller assertion does not establish active-tab ownership.** [autofit_c1s_gate.test.js:60](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:60). Replacing a caller’s lookup with an inactive record would still satisfy `/isC1sTab\(tab\)/`. The other three tests are substantive: all three fail against `07e0839`.
667:docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4440:VERDICT: GO
668:docs/autofit/codex/f3_c1s_gate_verdict_runA.md:13:Review unit F3 (the Auto-Fit C1s gate on live data): branch fix-noise-floor-scale-free, stacked on fix-fit-start-poll. Review git diff 07e0839..HEAD (07e0839 is the unit-2 commit F3 was cut from; later unit-2 commits are NOT part of F3): templates/index.html (isC1sTab only), tests/js/autofit_c1s_gate.test.js, CLAUDE.md, docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md, and the PARKED half's write-up docs/findings/noise-floor-occupancy/ (README + two patches that are NOT applied — review the write-up's claims and the patches as proposals, and say which variant you would choose and why). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO (for the shipped gate change; the parked half is advice). Budget your time: a verdict is required within the run.
670:docs/autofit/codex/f3_c1s_gate_verdict_runA.md:23:Finish with VERDICT: GO or VERDICT: NO-GO.
678:docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5152:- **MINOR — inactive-record selection disagrees with the actual fit.** [index.html:7770](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7770). On a 270–420 eV scan, saved bounds `295,280` return **true** through the record path, while the active path selects nothing and returns **false**. Bounds `'',295` produce the opposite disagreement: the active selection is 270–295 and passes; the record path uses the entire scan and fails. Preserve bound order and default missing bounds independently, matching `getROIData()`. This is nonblocking because all three production callers currently supply the active tab.
679:docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5154:- **MINOR — the parked write-up overstates what the stress failure demonstrates.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). F does return `conditional:false`, but also returns `filtered_dominant_alternative` naming P3 with ΔBIC ≈ 152.95; the page displays that warning. It does not silently produce an entirely unqualified answer. Moreover, this fixture contains **two true peaks**: P3’s third component compensates for background mismatch. Calling it a rejected “real component” is unsupported.
680:docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5172:VERDICT: GO
685:docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5183:- **MINOR — inactive-record selection disagrees with the actual fit.** [index.html:7770](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7770). On a 270–420 eV scan, saved bounds `295,280` return **true** through the record path, while the active path selects nothing and returns **false**. Bounds `'',295` produce the opposite disagreement: the active selection is 270–295 and passes; the record path uses the entire scan and fails. Preserve bound order and default missing bounds independently, matching `getROIData()`. This is nonblocking because all three production callers currently supply the active tab.
686:docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5185:- **MINOR — the parked write-up overstates what the stress failure demonstrates.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). F does return `conditional:false`, but also returns `filtered_dominant_alternative` naming P3 with ΔBIC ≈ 152.95; the page displays that warning. It does not silently produce an entirely unqualified answer. Moreover, this fixture contains **two true peaks**: P3’s third component compensates for background mismatch. Calling it a rejected “real component” is unsupported.
687:docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5203:VERDICT: GO
853:- **MINOR — the parked write-up overstates what the stress failure demonstrates.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). F does return `conditional:false`, but also returns `filtered_dominant_alternative` naming P3 with ΔBIC ≈ 152.95; the page displays that warning. It does not silently produce an entirely unqualified answer. Moreover, this fixture contains **two true peaks**: P3’s third component compensates for background mismatch. Calling it a rejected “real component” is unsupported.
871:VERDICT: GO
884:4. **MINOR — shipped: inactive records use different ROI semantics.** [templates/index.html:7771](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7771). Saved `295–280` is reordered and passes, while the live selector returns nothing. On a 270–420 scan, saved `min=""`, `max=295` uses the whole scan and fails; the live selector selects 270–295 and passes. Mirror independent open bounds and preserve reversed bounds. This is nonblocking because all three current callers pass the active tab.
886:5. **MINOR — tests: the caller assertion does not establish active-tab ownership.** [autofit_c1s_gate.test.js:60](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:60). Replacing a caller’s lookup with an inactive record would still satisfy `/isC1sTab\(tab\)/`. The other three tests are substantive: all three fail against `07e0839`.
894:VERDICT: GO
2120:No BLOCKER or MAJOR found in the shipped gate. Two MINORs remain:
2122:1. **MINOR — caller test still permits judging an inactive record.** [autofit_c1s_gate.test.js:72](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:72). Replacing each caller’s lookup with `_getTab('inactive') || _getTab(tabManager.activeId)` leaves all five tests passing, while execution judges the inactive record. I reproduced this separately for all three callers. Add a behavioral assertion on the record passed to `isC1sTab`. Current production callers are correct.
2124:2. **MINOR — parked write-up retains contradictory scale-invariance claims.** [README.md:33](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:33) still says both variants are scale-free, contradicting the correction below. The documented LR example reproduces: rescaling by 0.1 changes its statistic from 32 to 3.2. The blanket claim for F at [line 84](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:84) also needs round 1’s variance-floor qualification: with `y=[1,100]`, fit `[0.99,90]`, component `[0.9,22]`, and one free parameter, the retained floor makes F change **10.067 → 9.323** under that rescaling, flipping support. Remove the stale claim and qualify F’s invariance.
2130:VERDICT: GO
2133:No BLOCKER or MAJOR found in the shipped gate. Two MINORs remain:
2135:1. **MINOR — caller test still permits judging an inactive record.** [autofit_c1s_gate.test.js:72](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:72). Replacing each caller’s lookup with `_getTab('inactive') || _getTab(tabManager.activeId)` leaves all five tests passing, while execution judges the inactive record. I reproduced this separately for all three callers. Add a behavioral assertion on the record passed to `isC1sTab`. Current production callers are correct.
2137:2. **MINOR — parked write-up retains contradictory scale-invariance claims.** [README.md:33](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:33) still says both variants are scale-free, contradicting the correction below. The documented LR example reproduces: rescaling by 0.1 changes its statistic from 32 to 3.2. The blanket claim for F at [line 84](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:84) also needs round 1’s variance-floor qualification: with `y=[1,100]`, fit `[0.99,90]`, component `[0.9,22]`, and one free parameter, the retained floor makes F change **10.067 → 9.323** under that rescaling, flipping support. Remove the stale claim and qualify F’s invariance.
2143:VERDICT: GO
tests/js/batch_propagation.test.js
tests/js/fit_acceptance.test.js
tests/js/local_lm_descent.test.js
tests/js/fp_material_mixed.test.js
tests/js/bg_window_indices.test.js
tests/js/local_lm_server_parity_backend.py
tests/js/find_peaks_periodic_table.test.js
tests/js/shape_switch_roundtrip.test.js
tests/js/unsupported_components.test.js
tests/js/find_peaks_progress.test.js
tests/js/fixtures/autofit_anchor.json
tests/js/find_peaks_coverage.test.js
tests/js/lib/acorn.LICENSE
tests/js/lib/acorn.js
tests/js/lib/module_state_scan.js
tests/js/ref_core.test.js
tests/js/endpoint_avg_default.test.js
tests/js/tougaard_twin.test.js
tests/js/stale_statistics.test.js
tests/js/module_state_scan.test.js
tests/js/lineshape_roundtrip_backend.py
tests/js/per_tab_state.test.js
tests/js/lineshape_parity_backend.py
tests/js/fit_start_poll.test.js
tests/js/find_peaks_plain_message.test.js
tests/js/scattered_starts.test.js
tests/js/find_peaks_endpoint_avg.test.js
tests/js/lineshape_roundtrip.test.js
tests/js/fp_experimental_notice.test.js
tests/js/autofit_c1s_gate.test.js
tests/js/lineshape_parity.test.js
tests/js/autofit_required.test.js
tests/js/roi_clamp_centre_warning.test.js
tests/js/autofit_zero_graphite.test.js
.
..
.codex
.git
.github
.gitignore
.impeccable
.stage9
CLAUDE.md
DEPLOY.md
DESIGN.md
PRODUCT.md
__pycache__
app.py
autofit
data
docs
fitting.py
parser.py
requirements-dev.txt
requirements.txt
scripts
static
templates
tests
uploads
vgd_parser.py
xps-fitting-tool.html
xps_reference.py

exec
/bin/zsh -lc 'node --test tests/js/autofit_c1s_gate.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 49ms:
# Subtest: the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
ok 1 - the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
  ---
  duration_ms: 4.260336
  type: 'test'
  ...
# Subtest: the SELECTED data decide, not the typed midpoint of a window that reaches past the data
ok 2 - the SELECTED data decide, not the typed midpoint of a window that reaches past the data
  ---
  duration_ms: 1.122067
  type: 'test'
  ...
# Subtest: a non-active record is judged on its saved window over its own corrected data
ok 3 - a non-active record is judged on its saved window over its own corrected data
  ---
  duration_ms: 0.704152
  type: 'test'
  ...
# Subtest: the record path makes the SAME selection getROIData() makes (Codex round 1)
ok 4 - the record path makes the SAME selection getROIData() makes (Codex round 1)
  ---
  duration_ms: 0.588696
  type: 'test'
  ...
# Subtest: every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)
ok 5 - every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)
  ---
  duration_ms: 1.981507
  type: 'test'
  ...
# Subtest: BEHAVIOURAL: each caller hands isC1sTab the ACTIVE record, not merely a record looked up the right way (Codex round 2)
ok 6 - BEHAVIOURAL: each caller hands isC1sTab the ACTIVE record, not merely a record looked up the right way (Codex round 2)
  ---
  duration_ms: 3.147561
  type: 'test'
  ...
1..6
# tests 6
# suites 0
# pass 6
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 106.832195

codex
All six gate tests pass. The new behavioral test checks that the gate is reached, but its fixture IDs may miss the literal `_getTab('inactive')` mutation from round 2. I’ll test that alongside the first-tab mutation and early-return cases, entirely in memory.

exec
/bin/zsh -lc "sed -n '3210,3255p' templates/index.html; sed -n '5070,5118p' templates/index.html; sed -n '6090,6112p' templates/index.html; sed -n '6700,6745p' templates/index.html; sed -n '7545,7625p' templates/index.html; sed -n '1440,1535p' fitting.py; sed -n '1645,1730p' autofit/engine.py; nl -ba docs/findings/noise-floor-occupancy/README.md | sed -n '20,116p'; nl -ba tests/js/autofit_c1s_gate.test.js | tail -35" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
            endpointAvg: '1', roiMin: '', roiMax: '',
            ccMethod: 'none', ccObs: '', ccLit: '' },
    };
    this.tabs.push(tab);
    this.activateTab(id);
    return tab;
  }

  activateTab(id) {
    if (this.activeId === id) return;
    const tab = this._getTab(id);
    if (!tab) return;
    // Cancel any armed placement mode so a click on the new tab's chart
    // isn't consumed by a placement aimed at the previous spectrum.
    if (placeMode) togglePlaceMode(placeMode);
    // Clear stale history preview from previous tab
    if (typeof _historyPreview !== 'undefined') _historyPreview = null;
    // Save current tab's live state
    this._syncActiveToRecord();
    this.activeId = id;

    // Swap global state fields — peaks uses reference sharing
    state.rawBE = tab.rawBE;
    state.rawIntensity = tab.rawIntensity;
    state.ccShift = tab.ccShift;
    state.peaks = tab.peaks;
    state.nextId = tab.nextId;
    state.fitResult = tab.fitResult;
    state.lineWidth = tab.lineWidth ?? 1.5;

    // Restore DOM form fields
    this._restoreUI(tab.ui);
    _updateUndoButtons();   // history is per tab: buttons reflect the incoming record
    const notesEl = document.getElementById('spectrum-notes');
    if (notesEl) notesEl.value = tab.notes || '';
    this._updateCCVerifiedUI(tab.chargeVerified ?? true);
    this._updateInfoBadge(tab);
    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
    // Update chi-squared display for this tab's fit result
    _applyStatDisplay(state.fitResult);
    // F1: never computed over an edited model and cached under the fit's key
    // (without a stored curve _computeRFactor evaluates the CURRENT peaks)
    if (state.fitResult && state.fitResult.rFactor == null && _statsLiveState() !== 'stale') {
      state.fitResult.rFactor = _computeRFactor(state.fitResult);
    }
    _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
  // already works around). renderPeakList/_refOnTabChange only refresh panel/legend
  // DOM — no chart repaint — so element reference overlays (lines, bands, labels)
  // would vanish until the next hover/toggle. Re-issue the guarded reference-overlay
  // repaint so they stay painted through a charge-correction change. Leaf-level
  // chart.update('none'); positioning math and ccShift are untouched (overlays stay
  // at nominal corrected BE), and it is a no-op when no chart/spectrum/overlays exist.
  if (typeof _refRepaint === 'function') _refRepaint();
}

function getCorrectedBE() {
  const shift = isNaN(state.ccShift) ? 0 : state.ccShift;
  return state.rawBE.map(b => b - shift);
}

// ═══════════════════════════════════════════════════
// ROI FILTERING
// ═══════════════════════════════════════════════════
function getROIData() {
  const roiMinRaw = parseFloat(document.getElementById('roi-min').value);
  const roiMaxRaw = parseFloat(document.getElementById('roi-max').value);
  // NaN bounds mean the field is empty — use full range rather than filtering everything out
  const roiMin = isNaN(roiMinRaw) ? -Infinity : roiMinRaw;
  const roiMax = isNaN(roiMaxRaw) ?  Infinity : roiMaxRaw;
  const corrBE = getCorrectedBE();
  const be = [], inten = [];
  for (let i = 0; i < corrBE.length; i++) {
    if (corrBE[i] >= roiMin && corrBE[i] <= roiMax) {
      be.push(corrBE[i]);
      inten.push(state.rawIntensity[i]);
    }
  }
  return { be, inten };
}

// ── ROI past the data / centre outside the data (2026-09-25) ─────────────
// WARN, NEVER REINTERPRET. getROIData() already selects the corrected
// energies inside [roi-min, roi-max], so an ROI past the data is clamped to
// the data in every fit, background, area and export — the defect was that
// nothing said so. This reports the window actually used; it writes nothing
// back into the fields, the peaks or the fit-evidence key. Find Peaks sends
// the same two numbers against the same corrected energies to a server mask
// of the same inclusive form, so this one window is the one both use.
// Plan: docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md.
function _roiWindowStatus() {
  const corrBE = (typeof getCorrectedBE === 'function' && state.rawBE && state.rawBE.length) ? getCorrectedBE() : [];
  if (!corrBE.length) return { state: 'no-data' };
  let dMin = Infinity, dMax = -Infinity;
  for (const v of corrBE) { if (v < dMin) dMin = v; if (v > dMax) dMax = v; }
  const lo = parseFloat(document.getElementById('roi-min').value);
// ═══════════════════════════════════════════════════
// PEAK LIST UI
// ═══════════════════════════════════════════════════
// The per-peak "Charge-correction reference (C 1s graphite)" checkbox is
// only meaningful when the user is on a C 1s spectrum AND the global
// charge-correction method is set to graphite. When either condition is
// false, the checkbox is hidden completely AND any peak that previously
// held the marker is silently unchecked, so re-entering the valid mode
// gives a clean unchecked state rather than a stale stored value.
function _isChargeRefAllowed() {
  const cm = document.getElementById('cc-method');
  if (!cm || cm.value !== 'c1s') return false;
  const tab = (typeof tabManager !== 'undefined' && tabManager.activeId)
    ? tabManager._getTab(tabManager.activeId)
    : null;
  return !!(tab && isC1sTab(tab));
}

function _clearDisallowedChargeRef() {
  if (_isChargeRefAllowed()) return;
  for (const p of state.peaks) {
    if (p.isChargeReference) p.isChargeReference = false;
  }
}
function _hideFitSpinner() {
  const overlay = document.getElementById('fit-spinner-overlay');
  if (overlay) overlay.style.display = 'none';
  document.querySelector('.btn-green').disabled = false;
  clearTimeout(_showFitSpinner._timer);
  _bgSubFitInFlight = false;
  _updateBgSubPillEnabled();
}

// Sync the Auto-Fit menu item's disabled state with the active tab.
// Called from activateTab and from ROI-input event handlers.
function _recomputeAutoFitMenuState() {
  const item = document.getElementById('auto-fit-c1s-menu-item');
  if (!item) return;
  const tab = (typeof tabManager !== 'undefined' && tabManager.activeId)
    ? tabManager._getTab(tabManager.activeId)
    : null;
  const enabled = !!tab && isC1sTab(tab);
  item.disabled = !enabled;
  if (enabled) {
    item.removeAttribute('aria-disabled');
    item.title = 'Auto-Fit C1s Graphite — one-click fit + charge correction';
  } else {
    item.setAttribute('aria-disabled', 'true');
    item.title = 'Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).';
  }
}

// Late-init for Auto-Fit menu state (in case startup runs before the
// menu item is in the DOM).
window.addEventListener('DOMContentLoaded', () => {
  if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
});

// Returns a Promise<boolean> — true if user clicks Proceed, false on Cancel/X.
let _autoFitConfirmResolver = null;
function _showAutoFitConfirmModal(peakCount) {
  return new Promise(resolve => {
    _autoFitConfirmResolver = resolve;
    const span = document.getElementById('auto-fit-c1s-confirm-count');
    if (span) span.textContent = String(peakCount);
    const proceed = document.getElementById('auto-fit-c1s-confirm-proceed');
    proceed.onclick = () => {
      document.getElementById('auto-fit-c1s-confirm-overlay').classList.remove('open');
      const r = _autoFitConfirmResolver; _autoFitConfirmResolver = null;
      if (rec.status === 'cancelled') throw _fitHttpError(409, 'The fit was stopped on the server before it finished. Run it again.');
      if (Number.isFinite(rec.heartbeat_age_sec) && rec.heartbeat_age_sec > FIT_HEARTBEAT_LOST_SEC) {
        _cancelFitJob(jobId);
        throw _fitHttpError(503, 'The server stopped working on the fit (no sign of it for ' + Math.round(rec.heartbeat_age_sec) +
                                 ' s — it was probably restarted). Run the fit again.');
      }
      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
    }
  } finally {
    _runningFitJobs.delete(jobId);
  }
}

async function runAutoFitC1sGraphite() {
  // Pre-conditions
  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab) { notify('No active tab.', 'amber'); return; }
  if (!isC1sTab(tab)) {
    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
    return;
  }
  // OWNER FIRST: the confirmation below is an await; the tab that is active
  // when it resolves may not be the one the user asked to auto-fit.
  const fittingTab = _opOwner();
  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
  // Confirmation if existing peaks
  if (state.peaks.length >= 1) {
    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
    if (!proceed) return;
    if (!_ownerActive(fittingTab)) {
      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
      return;
    }
  }

  // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
  const snap = _autoFitSnapshot();

  // Step 1: find graphite in raw BE
  const { be: corrBE, inten } = getROIData();
  if (!corrBE.length) {
    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
    return;
  }
  const bgI = computeBackground(corrBE, inten);
  const bgSub = inten.map((v, i) => v - bgI[i]);
  // App convention: raw = corrected + state.ccShift
  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
  const rawBE = corrBE.map(b => b + curShift);
  const graphiteRaw = findGraphiteRawBE(rawBE, bgSub);
  if (graphiteRaw == null) {
    notify('No strong peak found in the C1s ROI; Auto-Fit cannot proceed.', 'red', true);
    return;
  }

  // Step 2: provisional shift (APP CONVENTION).
  const provisionalShift = graphiteRaw - 284.50;

  // Step 3: assess low-BE region using provisional shift (no state mutation yet).
  const assessment = assessLowBERegion(rawBE, bgSub, provisionalShift);

  // Step 4: build the peak model (in corrected frame after provisional shift).
  pushUndo();
  state.peaks = [];
  state.fitResult = null;
  // Apply provisional shift via updateChargeCorrection so ROI/bg DOM fields
  // shift along with state.ccShift.
  const cm = document.getElementById('cc-method');
  const co = document.getElementById('cc-obs');
  const cl = document.getElementById('cc-lit');
  cm.value = 'c1s';
  co.value = graphiteRaw.toFixed(3);
  cl.value = '284.50';
  updateChargeCorrection();
  // Now build the peak list (graphite center 284.50 in this frame).
  const newPeaks = buildAutoFitModel(assessment);
  state.peaks = newPeaks;
  state.nextId = Math.max(0, ...state.peaks.map(p => p.id)) + 1;
  renderPeakList();

# F >= 1.1e3 and 3 of 752 components are unsupported (F 0.95-3.9).
SUPPORT_MIN_F = 10.0


def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
    w2 = np.asarray(weights, float) ** 2
    r = np.asarray(y_sub, float) - np.asarray(fitted_sub, float)
    ok = np.isfinite(r) & np.isfinite(comp_y) & np.isfinite(w2)
    chi_with = float(np.sum(w2[ok] * r[ok] ** 2))
    chi_without = float(np.sum(w2[ok] * (r[ok] + np.asarray(comp_y, float)[ok]) ** 2))
    delta = chi_without - chi_with
    p = max(1, int(n_free_comp))
    dof = max(1, int(ok.sum()) - int(n_free_total))
    if delta <= 0:
        f = 0.0
    elif chi_with == 0:
        f = float("inf")
    else:
        f = (delta / p) / (chi_with / dof)
    return {"f": None if not np.isfinite(f) else f, "delta_chi2": delta,
            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}


# ── "Is this component REQUIRED?" — the refit test ───────────────────────────
# `support` (above) holds the OTHER components at their fitted values, so it
# cannot see redundancy under overlap: a component the others could absorb if
# they were refitted still passes. The test for that is the refit itself:
# remove the component, refit the rest from their fitted values under the
# request's own bounds, and compare the fit to the data with and without it:
#     F = ((chi2_without_refit - chi2_with) / p) / (chi2_with / dof)
# p = the component's free parameters, dof = n - nvarys of the full model.
# One extra fit, so it is done only when asked for (Auto-Fit asks for its
# charge-reference anchor: an anchor that is not required must not set the
# energy reference of a whole spectrum). Same threshold as `support`.
def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
                        chi2_with, n_free_comp, n_free_total) -> dict[str, Any]:
    """``fit_reduced(params)`` is the run's own fitter for the reduced model
    (the same candidate machinery and seeding the fit used, so differential
    evolution's box/refinement and the request seed apply to the refit too).
    ``removed_prefixes`` is the removed component AND everything linked to it,
    transitively. The reduced start is built in dependency order: plain
    parameters first, expressions after, so a child ordered before its parent
    in the request still resolves."""
    kept = [(name, par) for name, par in params_full.items() if not any(name.startswith(r) for r in removed_prefixes)]
    # ALL retained parameters exist before any expression is assigned, so a
    # chain of links in any request order resolves (lmfit evaluates an
    # expression when it is set).
    start = Parameters()
    for name, par in kept:
        start.add(name, value=par.value, min=par.min, max=par.max, vary=par.vary)
    for name, par in kept:
        if par.expr:
            start[name].set(expr=par.expr)
    refit = fit_reduced(start)
    chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
    if not refit.success or getattr(refit, "box_unverified", False):
        # F2 (2026-09-26): a refit that did not converge establishes nothing
        # (nor does a differential-evolution candidate whose search box no
        # refinement verified — the main fit's acceptance rule rejects it too;
        # Codex round 1)
        # either way — its chi-square is wherever the optimiser stopped (a
        # redundant anchor read "required", F 992, from a refit stopped early;
        # F 1.17 once it completed). No verdict; the caller decides.
        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
                "refit_converged": False, "reason": "refit_not_converged",
                "message": str(getattr(refit, "message", "") or "")[:200]}
    delta = chi2_without - chi2_with
    p = max(1, int(n_free_comp))
    dof = max(1, len(y_sub) - int(n_free_total))
    # No tolerance of any kind (Codex rounds 2-3: a floor on the chi-square
    # change relative to the data's power, and then an "exactness" cutoff on
    # the reduced fit, each masked a resolved anchor at high dynamic range —
    # the same lesson as the DE unit). Known limit, accepted: on NOISE-FREE
    # data whose full fit is numerically exact (chi2_with ~ 1e-28) F is not
    # meaningful and a truly redundant component (two identical half-amplitude
    # components) reports "required"; real data never fit to machine precision.
    if not np.isfinite(chi2_without):
        f, required = None, True                     # the rest could not even be fitted without it
    elif delta <= 0:
        f, required = 0.0, False
    elif chi2_with == 0:
        f, required = None, True
    else:
        f = (delta / p) / (chi2_with / dof)
        required = f >= SUPPORT_MIN_F
    return {"required": bool(required), "f": f, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
            "refit_converged": bool(refit.success)}


# ─────────────────────────────────────────────────────────────────────────────
# Main fitting API
# ─────────────────────────────────────────────────────────────────────────────

def _run_fit_impl(
    energy: np.ndarray,
    counts: np.ndarray,
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
    20	   stability gate follow from it. This is the design rule's case.
    21	
    22	Both variants replace (2) with a statistic on the component's own fit
    23	(computed once when the component is extracted from its lmfit result and
    24	carried on `FittedComponent.support`), leave (1) alone, and fall back to
    25	`amplitude > 0` (a sign test) for a component with no fit behind it. They
    26	differ in ONE line — what "occupied" means:
    27	
    28	| variant | occupied when | patch |
    29	|---|---|---|
    30	| **F** — the server's support test | `fitting._component_support` "supported": Δχ² > 0 and F = (Δχ²/p) / (χ²_with/dof) ≥ 10 — the step (b) "not supported by the data" statistic and threshold | `variant_F_support_test.patch` |
    31	| **LR** — the weighted removal gain per parameter (first draft called it a "Poisson likelihood ratio"; it is neither a likelihood nor a refit) | Δχ²/p ≥ 10 on the Poisson-weighted χ², with the other components held, NOT divided by the fit's own misfit χ²_with/dof | `variant_LR_likelihood_ratio.patch` |
    32	
    33	Neither carries a tolerance. Only F is a RATIO of χ² quantities and so
    34	invariant to a uniform rescaling of the intensities; LR is not (Codex rounds
    35	1–2: ×0.1 turns Δχ²/p = 32 into 3.2 and flips it, while F stays 16). F's
    36	invariance is itself QUALIFIED by the Poisson variance floor both patches
    37	keep (σ² = max(counts, 1)): a channel at or below 1 count weighs differently
    38	after a rescaling, so F can move (round 2: 11.67 → 3.18, and 10.07 → 9.32,
    39	on data with a channel near 1 count). Exact invariance holds only where every
    40	channel stays above the floor.
    41	
    42	## The evidence
    43	
    44	| suite | baseline (today) | F | LR |
    45	|---|---|---|---|
    46	| gated real-data parity gates + stress honesty (`RUN_AUTOFIT_GATE=1`: C 1s parity, Bayesian real, candidate-pool real, U 4f unresolved, stress honesty) | 17 passed, 4 skipped | **16 passed, 1 FAILED** | 17 passed, 4 skipped |
    47	| always-on `tests/autofit` (incl. the C 1s / region parity batteries) | green | **1 failed** (the same stress case), 556 passed | 557 passed, 7 skipped |
    48	
    49	The failing case, `test_stress_honesty.py::test_bg_mismatch_surfaces_loudly`:
    50	a Shirley-shaped truth fitted with a straight-line background, χ²ᵣ ≈ 280–470
    51	for every candidate. The test requires the mismatch to be machine-visible
    52	("conditional" tier), never a clean confident result. Today the 3-component
    53	candidate P3 is stable but violates plausibility, enters the conditional
    54	pool, and its bound-fixed refit wins via the decisive override →
    55	`conditional: true`. Under F, P3's third component has F < 10 BECAUSE the fit
    56	is so bad: F divides the gain by χ²_with/dof ≈ 284, so a component that
    57	removes a large χ² still reads "unsupported"; it becomes an orphan, P3's
    58	persistence drops to 0, P3 leaves the conditional pool, and P2 (χ²ᵣ 309) is
    59	returned as a CLEAN survivor. Under LR the same component is occupied (its
    60	gain per parameter is far above 10 Poisson units) and the result is
    61	conditional, as today.
    62	
    63	## Codex review of this write-up (F3 round 1, `f3_c1s_gate_verdict_run{A,B}.md`) — the recommendation below replaces the first draft's
    64	
    65	Both runs reproduced the measurements and the mechanism (P3's third component:
    66	Δχ² ≈ 10 702, F ≈ 9.42 with four free parameters → persistence 0, orphan rate 1,
    67	out of the decisive-override pool). They also found three things wrong with
    68	the first draft's recommendation of LR, all of which hold:
    69	
    70	1. **LR is not scale-free.** "Dimensionless" is not "invariant under a change
    71	   of intensity units": with Poisson weights the gain Δχ² scales with the
    72	   counts, so multiplying a spectrum by 0.1 (CPS instead of counts, a
    73	   normalisation) turned Δχ²/p = 32 into 3.2 and flipped the verdict, while F
    74	   stayed at 16 — F is a RATIO of two χ² quantities and is invariant. The
    75	   design rule asks for exactly that invariance. (The statistic is also a
    76	   gain with the other components held fixed, not a refitted likelihood
    77	   ratio; the draft's name overstated it.)
    78	2. **The LR patch is internally inconsistent**: occupancy used Δχ²/p while
    79	   detectability still used `support.supported` and reported
    80	   `basis: support_f_test`, so a component could be "unoccupied" and
    81	   `above_floor` at once, and a proposal rejection could print "F = 32.00 < 10".
    82	3. **The stress case does not show F rejecting a real peak.** The fixture
    83	   (`tests/autofit/stress_cases.py`) has TWO true peaks; P3's third component
    84	   compensates for the wrong background. F calls it unsupported — defensibly —
    85	   and the honesty flag then disappears because the "conditional" tier
    86	   depended on keeping that background-compensating component. The F result
    87	   also still carries `filtered_dominant_alternative` (P3, ΔBIC ≈ 153), which
    88	   the page shows: not a silent clean answer.
    89	
    90	Both runs, independently: **start from F** (one support definition across
    91	the app, invariant to intensity units) and fix two things around it before
    92	shipping:
    93	
    94	- an unsupported component INSIDE its slot's window must not become an
    95	  "orphan" (an unexplained extra peak) — today (and in both patches) a
    96	  component that fails occupancy has no accepting slot and counts toward
    97	  `orphan_rate`, a plausibility violation; "slot empty" and "peak nobody
    98	  expects" need distinct treatment;
    99	- the model-mismatch honesty signal must not depend on a component that only
   100	  compensates for a wrong background — report the mismatch (χ²ᵣ ≫ 1, the
   101	  residual structure) on its own terms.
   102	
   103	## The decision (owner)
   104	
   105	- **Adopt F as the occupancy statistic** (recommended, both reviewers), as a
   106	  unit of its own with the two follow-ups above, measured on the gated and
   107	  always-on suites; the honesty test is then re-examined against a
   108	  mismatch signal that does not ride on P3.
   109	- **LR**: withdrawn as a recommendation (not invariant to intensity units).
   110	- Either way `noise_floor` survives only as the Poisson variance floor (both
   111	  patches leave it; it keeps the raw-count assumption the server's weights
   112	  make). That floor is what limits F's invariance to data whose channels stay
   113	  above 1 count (see above) — a property the server's step (b) verdict shares.
   114	
   115	The two patches stay here as the measured starting points:
   116	`git apply docs/findings/noise-floor-occupancy/variant_F_support_test.patch`.
    66	  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '' } }), false);
    67	});
    68	
    69	test('every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)', () => {
    70	  for (const fn of ['_recomputeAutoFitMenuState', '_isChargeRefAllowed', 'runAutoFitC1sGraphite']) {
    71	    const src = extractFn(fn);
    72	    const lookup = src.search(/const tab = [^;]*tabManager\._getTab\(tabManager\.activeId\)/);
    73	    assert.ok(lookup >= 0, fn + ': the tab is looked up by tabManager.activeId');
    74	    assert.ok(src.indexOf('isC1sTab(tab)') > lookup, fn + ': and that tab is the one judged');
    75	    assert.ok(!/\btab\s*=(?!=)/.test(src.slice(lookup + 10, src.indexOf('isC1sTab(tab)'))), fn + ': not reassigned in between');
    76	  }
    77	  // and the ROI fields refresh the menu on every keystroke
    78	  assert.match(html, /id="roi-min"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
    79	  assert.match(html, /id="roi-max"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
    80	});
    81	
    82	test('BEHAVIOURAL: each caller hands isC1sTab the ACTIVE record, not merely a record looked up the right way (Codex round 2)', async () => {
    83	  const inactive = { id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } };   // C 1s
    84	  const active   = { id: 't2', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '415' } };   // U 4f
    85	  const seen = [];
    86	  const isC1sTab = t => { seen.push(t); return false; };
    87	  const tabManager = { activeId: 't2', tabs: [inactive, active], _getTab: id => [inactive, active].find(t => t.id === id) };
    88	  const el = { disabled: false, value: 'c1s', setAttribute() {}, removeAttribute() {}, title: '' };
    89	  const document = { getElementById: () => el };
    90	  const notes = [];
    91	  const deps = { tabManager, isC1sTab, document, notify: (m, k) => notes.push([m, k]), state: { rawBE: RAW, peaks: [] } };
    92	  const src = ['_recomputeAutoFitMenuState', '_isChargeRefAllowed', 'runAutoFitC1sGraphite'].map(extractFn).join('\n');
    93	  const fns = new Function(...Object.keys(deps), src + '\nreturn { _recomputeAutoFitMenuState, _isChargeRefAllowed, runAutoFitC1sGraphite };')(...Object.values(deps));
    94	  fns._recomputeAutoFitMenuState();
    95	  fns._isChargeRefAllowed();
    96	  await fns.runAutoFitC1sGraphite();                 // returns at the gate (isC1sTab false)
    97	  assert.strictEqual(seen.length, 3, 'each caller consulted the gate once');
    98	  for (const t of seen) assert.strictEqual(t, active, 'the active record, never ' + (t && t.id));
    99	  assert.ok(notes.some(([m]) => /only available for C1s spectra/.test(m)), 'the run stopped at the gate');
   100	});

exec
/bin/zsh -lc "node -e '
const fs = require('\\''node:fs'\\''), vm = require('\\''node:vm'\\''), path = require('\\''node:path'\\'');
const html = fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const tests = fs.readFileSync('\\''tests/js/autofit_c1s_gate.test.js'\\'','\\''utf8'\\'');
const names = ['\\''_recomputeAutoFitMenuState'\\'','\\''_isChargeRefAllowed'\\'','\\''runAutoFitC1sGraphite'\\''];
function extract(h,name) {
 const lines=h.split('\\''\\n'\\''), start=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l));
 let depth=0,seen=false;
 for(let i=start;i<lines.length;i++){ for(const ch of lines[i]) {if(ch==='\\''{'\\''){depth++;seen=true;}else if(ch==='\\''}'\\'') depth--; } if(seen&&depth===0)return lines.slice(start,i+1).join('\\''\\n'\\'');}
 throw Error(name);
}
async function run(h,t=tests) {
 const cases=[];
 vm.runInNewContext(t,{require: n=>n==='\\''node:test'\\''?{test:(name,fn)=>cases.push({name,fn})}:n==='\\''node:fs'\\''?{readFileSync:()=>h}:require(n),__dirname:path.resolve('\\''tests/js'\\'')});
 const fail=[];
 for(const c of cases)try {await c.fn();}catch(e){fail.push({test:c.name.split('\\'':'\\'')[0],error:e.message.split('\\''\\n'\\'')[0]});}
 return {pass:cases.length-fail.length,fail};
}
(async()=>{
 console.log('\\''baseline'\\'',JSON.stringify(await run(html)));
 for(const name of names) {
  const src=extract(html,name);
  for(const [label,repl] of [
   ['\\''tabs[0] fallback'\\'','\\''tabManager.tabs[0] || tabManager._getTab(tabManager.activeId)'\\''],
   ['\\''literal inactive fallback'\\'',\"tabManager._getTab('\\''inactive'\\'') || tabManager._getTab(tabManager.activeId)\"],
   ['\\''actual inactive t1 fallback'\\'',\"tabManager._getTab('\\''t1'\\'') || tabManager._getTab(tabManager.activeId)\"],
   ['\\''tabs[1] fallback'\\'','\\''tabManager.tabs[1] || tabManager._getTab(tabManager.activeId)'\\'']]) {
    const mutated=html.replace(src,src.replace('\\''tabManager._getTab(tabManager.activeId)'\\'',repl));
    console.log(name,label,JSON.stringify(await run(mutated)));
    if(label==='\\''literal inactive fallback'\\'') console.log('\\''  with inactive fixture renamed'\\'',JSON.stringify(await run(mutated,tests.replace(\"const inactive = { id: '\\''t1'\\''\",\"const inactive = { id: '\\''inactive'\\''\"))));
    if(label==='\\''tabs[1] fallback'\\'') console.log('\\''  with array order reversed'\\'',JSON.stringify(await run(mutated,tests.replace('\\''tabs: [inactive, active]'\\'','\\''tabs: [active, inactive]'\\''))));
  }
  const early=src.replace(/(function \\w+\\(\\) \\{)/,'\\''"'$1'"\\n return;'\\'');
  console.log(name,'\\''early return'\\'',JSON.stringify(await run(html.replace(src,early))));
 }
 const old=require('\\''node:child_process'\\'').execFileSync('\\''git'\\'',['\\''show'\\'','\\''07e0839:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''ignore'\\'','\\''pipe'\\'','\\''ignore'\\'']});
 console.log('\\''old gate'\\'',JSON.stringify(await run(html.replace(extract(html,'\\''isC1sTab'\\''),extract(old,'\\''isC1sTab'\\'')))));
})().catch(e=>{console.error(e);process.exitCode=1;});
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 198ms:
  with array order reversed {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"the active record, never t1"}]}
_recomputeAutoFitMenuState early return {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"each caller consulted the gate once"}]}
_isChargeRefAllowed tabs[0] fallback {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"the active record, never t1"}]}
_isChargeRefAllowed literal inactive fallback {"pass":6,"fail":[]}
  with inactive fixture renamed {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"the active record, never inactive"}]}
_isChargeRefAllowed actual inactive t1 fallback {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"the active record, never t1"}]}
_isChargeRefAllowed tabs[1] fallback {"pass":6,"fail":[]}
  with array order reversed {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"the active record, never t1"}]}
_isChargeRefAllowed early return {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"each caller consulted the gate once"}]}
runAutoFitC1sGraphite tabs[0] fallback {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"the active record, never t1"}]}
runAutoFitC1sGraphite literal inactive fallback {"pass":6,"fail":[]}
  with inactive fixture renamed {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"the active record, never inactive"}]}
runAutoFitC1sGraphite actual inactive t1 fallback {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"the active record, never t1"}]}
runAutoFitC1sGraphite tabs[1] fallback {"pass":6,"fail":[]}
  with array order reversed {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"the active record, never t1"}]}
runAutoFitC1sGraphite early return {"pass":5,"fail":[{"test":"BEHAVIOURAL","error":"each caller consulted the gate once"}]}
old gate {"pass":2,"fail":[{"test":"the sweep reproduction","error":"judged on the live U 4f selection"},{"test":"the SELECTED data decide, not the typed midpoint of a window that reaches past the data","error":"Expected values to be strictly equal:"},{"test":"a non-active record is judged on its saved window over its own corrected data","error":"corrected 70-220 has no point in 280-295: nothing selected"},{"test":"the record path makes the SAME selection getROIData() makes (Codex round 1)","error":"Expected values to be strictly equal:"}]}

exec
/bin/zsh -lc "sed -n '1,65p' tests/js/per_tab_state.test.js; sed -n '1,45p' tests/js/fit_start_poll.test.js; rg -n 'noise_floor|weights=' autofit/engine.py | head -35; rg -n '_component_support\\(' fitting.py; sed -n '1,100p' tests/autofit/test_stress_honesty.py; rg -n 'bg_mismatch|Shirley|shirley' tests/autofit/stress_cases.py; sed -n '2985,3045p' autofit/engine.py; sed -n '1,70p' docs/findings/noise-floor-occupancy/variant_F_support_test.patch" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
// Per-tab state ownership (docs/superpowers/plans/2026-09-08-per-tab-state-ownership.md).
//
// The construction rule: content that belongs to ONE spectrum tab lives on
// that tab's record, never at module scope, so "restore into whichever tab
// is active" has no path. This structural test is the class-killer: every
// module-level mutable declaration in templates/index.html must be
// allowlisted with its class (A UI-transient, B tab-independent cache /
// catalogue, B' chart-instance state reset on activation). Class C — per-tab
// content — is NOT allowed at module scope; the three instances found
// (auto-fit snapshot, undo/redo stacks, the Find Peaks result) are gone or
// on the record. A new global that is not listed fails this test.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');

// name -> class. Keep this list honest: adding a name here is a design
// decision, and "C" is not a valid value.
const ALLOWLIST = {
  state: 'B',                 // OWNERSHIP INFRASTRUCTURE, not a cache: the ACTIVE tab's working copy, swapped wholesale by activateTab / _syncActiveToRecord
  _undoDebounceTimer: 'A', _tabRuntimeTokens: 'B', _tabRuntimeSeq: 'B',
  _nextStackNum: 'B', _accSurveyCache: 'B', _accChemCache: 'B', _refUnavailableNotified: 'B',
  tabManager: 'B',            // OWNERSHIP INFRASTRUCTURE: the record store itself
  _origYMax: "B'", _origXMin: "B'", _origXMax: "B'", _origResidYMin: "B'", _origResidYMax: "B'",
  _dragZoomEnabled: 'A', placeMode: 'A', _pendingMultipletPreset: 'A', _bgSubFitInFlight: 'A',
  _autoFitConfirmResolver: 'A', _saveMode: 'A',
  _refCompoundMarkers: 'B', _refCompoundMarkerNextId: 'B',
  _refPanelOpen: 'A', _refPayload: 'B', _refError: 'B', _refFetchPromise: 'B', _refHoverId: 'A',
  _refGlobalSel: 'B', _refNotesOpen: 'A', _refSearchElements: 'B',
  _refPaletteDrag: 'A', _refChipOpenSym: 'A', _refChipOpenBtn: 'A',
  _snapshotSuppressed: 'A', _historyPreview: "B'",
  _ssFocusIdx: 'A', _ssFiltered: 'A',
  _fpMeta: 'B', _fpModalDrag: 'A', _fpRegionsSelected: 'A', _fpExpandedElement: 'A',
  _findPeaksApplyConfirmResolver: 'A',
  _runningFitJobs: 'A',       // unit 2: ids of in-flight server fit jobs, for the pagehide cancel beacon — no spectrum content
  _undoDebounce: 'A',         // burst buffer: DOES hold a peaks snapshot, but bound to its owner record at burst start and flushed onto that record only — the async-ownership exception to class A's 'no spectrum content'
  // Populated constant catalogues (read-only tables) and the chart plugin
  // object: class B. Listed, not skipped, so a per-tab store hidden in an
  // ALL_CAPS name or in a plugin property would need an explicit entry here.
  STACK_PALETTE: 'B', LEGACY_REFERENCE: 'B', LEGACY_REFERENCE_OK: 'B', ELEMENT_NAMES: 'B',
  ELEMENT_MARKER_COLORS: 'B', PEAK_COLORS: 'B', SCOFIELD_RSF: 'B', SPIN_ORBIT_PRESETS: 'B',
  TAB_COLORS: 'B', SHAPE_PARAM_SCHEMA: 'B', PLACE_MODE_BUTTONS: 'B', LOCK_ALL_KEYS: 'B',
  _BG_SUB_DEPENDENT_CONTROL_IDS: 'B', xpsRefLinesPlugin: 'B',
  _STARTS_MODEL_FIELDS: 'B', _STARTS_UI_FIELDS: 'B',   // constant tables: what the scattered-starts evidence is bound to
  FP_TIER_META: 'B', FP_STRINGS: 'B', FP_MODEL_LABELS: 'B', FP_ROLE_LABELS: 'B', FP_SHAPE_LABELS: 'B', FP_TIER_RANK: 'B',
  REF_PT_LAYOUT: 'B',        // periodic-table layout table (built by a call at load; read-only)
  _HEX_COLOR_RE: 'B', _SLUG_ID_RE: 'B',   // RegExp literals are objects (lastIndex is writable); these are validation constants
};

const { scanModuleMutables, inlineScripts } = require('./lib/module_state_scan');
function moduleLevelMutables() {
  // scan only the page's inline scripts (Jinja interpolations substituted)
  const scripts = inlineScripts(html);
  assert.ok(scripts.length >= 1, 'no inline scripts found');
  return [...new Set(scripts.flatMap(scanModuleMutables))];
}

const VALID_CLASSES = new Set(['A', 'B', "B'"]);
// Own-property lookup: an inherited name such as `constructor` or `toString`
// must NOT count as allowlisted (Codex round 4, both runs).
// '[anonymous class].…' names are rejected outright: an unbound class with
// static state has no binding to classify — give it one, or remove the state.
const isAllowlisted = (n) => !n.startsWith('[anonymous class]') && Object.hasOwn(ALLOWLIST, n) && VALID_CLASSES.has(ALLOWLIST[n]);
// Unit 2 (2026-09-27): Run Fit and Auto-Fit start the fit and poll for it
// (_serverFitJob). Pinned: the result is the /api/fit body; a bad request's
// message and status are the synchronous route's; ownership (a switched tab,
// an edited model) cancels the server's job and discards; transport keeps its
// meaning (a START that cannot reach the server may fall back to the local
// engine; one lost poll does not; five in a row do); a lost heartbeat, a
// cancelled or errored record are failed fits; F2's NaN rule applies to the
// final record; the 2-minute Auto-Fit abort cancels the job.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
const constLine = n => { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; };

// fetch scripted by URL; every call recorded
function server(script) {
  const calls = [];
  const fetch = async (url, init) => {
    calls.push({ url, method: (init && init.method) || 'GET' });
    const h = script(url, init, calls);
    if (h instanceof Error) throw h;
    return h;
  };
  return { fetch, calls };
}
const ok = (obj, status = 200) => ({ ok: true, status, text: async () => (typeof obj === 'string' ? obj : JSON.stringify(obj)) });
const bad = (status, obj) => ({ ok: false, status, json: async () => { if (obj === undefined) throw new SyntaxError('x'); return obj; } });

function make(fetch) {
  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    'const _runningFitJobs = new Set();',
889:        result = composite.fit(y_sub, params, x=x, weights=weights,
906:                                  weights=weights, method="leastsq",
1042:    noise_floor: float,
1058:                and comp.amplitude > noise_floor)
1168:    noise_floor: float,
1234:        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
1406:    noise_floor: float,
1411:    sigma = np.sqrt(np.maximum(y, noise_floor))
1808:    noise_floor: float = 1.0,
1856:        local_sigma = float(np.median(np.sqrt(np.maximum(y_asc[mask], noise_floor)))) \
1857:            if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
2007:    noise_floor: float,
2014:    sigma = np.sqrt(np.maximum(y, noise_floor))
2163:    noise_floor: float,
2232:    if comp.amplitude <= noise_floor:
2233:        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
2240:    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
2241:        if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
2273:        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
2312:    residuals = compute_residual_diagnostics(x, y, y_fit_aug, noise_floor, diagnostic_windows)
2391:    noise_floor: float,
2446:        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
2460:            x, y, y_fit, noise_floor, diagnostic_windows),
2486:    noise_floor: float,
2507:                                   diagnostic_windows, noise_floor,
2554:    noise_floor: float = 1.0,
2627:            noise_floor=noise_floor,
2646:                noise_floor=noise_floor,
2826:            noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
2840:        residuals = compute_residual_diagnostics(x, y, y_fit, noise_floor, diagnostic_windows)
2882:                    x, y, current_y_fit, noise_floor, current.model,
2903:                        x=x, y=y, weights=weights, base_report=current, spec=spec,
2904:                        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
2954:        noise_floor=noise_floor,
1444:def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
1980:        support = _component_support(y_sub, fitted_sub, peak_y, weights, n_free_comp, result.nvarys)
"""
Always-on stress-honesty net — the KEY-CRITERION invariants from the
synthetic hard-case suite (run-brief item 2), pinned on the fast subset
(IC n_refits=4 + LS + sparse; the full battery incl. Bayesian and noise
replicates is scripts/run_stress_battery.py → stress_battery_runs.jsonl,
summarized in docs/autofit/stress-test-report.md).

Where there IS a right answer the engine must recover it; where the truth
is outside the model space the mismatch must be machine-visible; an
over-specified menu must be pruned, not populated.  Values pinned from the
2026-07-04 measurement run.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import (  # noqa: E402
    asym_truth_case,
    bg_matched_control_case,
    bg_mismatch_case,
    isolated_missing_peak_case,
    overlap_case,
    overspecified_case,
    overspecified_decoy_case,
)
from autofit.methods import get_method  # noqa: E402

IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": True}


def _ic(case):
    return get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar, options=dict(IC_OPTS))


@pytest.fixture(scope="module")
def sep1():
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    return case, _ic(case)


def test_resolved_doublet_recovered_clean(sep1):
    """Separation 1×FWHM at 9000 counts: distinguishable → must recover."""
    case, res = sep1
    assert res.success
    assert res.diagnostics["winner"] == "P2"
    assert res.diagnostics["conditional"] is False
    by_role = {p["role"]: p for p in res.peaks}
    for t, role in zip(case.truth, ("main_a", "main_b")):
        assert by_role[role]["center"] == pytest.approx(t["center"], abs=0.05)


def test_resolved_doublet_ls_baseline(sep1):
    case, _ = sep1
    res = get_method("least_squares").run(
        case.x, case.y, peak_specs=case.ls_specs,
        options={"background_method": "linear"})
    assert res.success
    for t, p in zip(case.truth, res.peaks):
        assert p["center"] == pytest.approx(t["center"], abs=0.05)
        assert p["fwhm"] == pytest.approx(t["fwhm"], abs=0.1)


def test_resolved_doublet_sparse_count_only():
    """Sparse COUNT-ONLY pin — explicitly NOT a recovery claim: on this
    PV-truth case the selected atoms sit 0.45-0.75 eV off (Gaussian-atom /
    30%-Lorentzian mismatch, its documented weakness; classified
    count_ok_param_biased in the battery, never PASS).  The invariant
    worth pinning is only that the component COUNT does not hallucinate on
    a clean, well-separated doublet."""
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    res = get_method("sparse_map").run(case.x, case.y, grammar=case.grammar)
    assert res.success
    assert len(res.peaks) == 2


def test_overspecified_menu_prunes_not_invents():
    """Truth 2 peaks, menu offers up to 5: the winner must carry exactly
    the true structure — no invented components."""
    case = overspecified_case(seed=31)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert len(res.peaks) == 2
    by_role = {p["role"]: p for p in res.peaks}
    matched = 0
    for t in case.truth:
        if any(abs(p["center"] - t["center"]) < 0.3 for p in by_role.values()):
            matched += 1
    assert matched == 2


def test_inroi_decoy_pruned_not_populated():
    """The harder over-specification test (Codex stress review): a decoy
    'shoulder' window BETWEEN the true peaks, where real tail intensity
    lives — the winner must carry the true 2-component structure with the
94:def _shirley_like_bg(x, signal, k=0.15, b0=300.0):
95:    """Integral (Shirley-shaped) background: proportional to the signal area
97:    # BE axis ascends; Shirley steps up on the high-BE side of peaks
323:# Regime 6 — background mismatch (Shirley-shaped truth, linear-only fits)
404:def bg_mismatch_case(seed: int) -> StressCase:
409:    y = _noisy(sig + _shirley_like_bg(x, sig), seed)
411:        name="bg_shirley_truth_linear_fit",
412:        regime="bg_mismatch", expectation="honesty",
417:        bg="shirley_like",
424:    """Control for the mismatch case: same truth, Shirley-candidate fits.
425:    The engine's iterative Shirley should absorb the integral background."""
430:    y = _noisy(sig + _shirley_like_bg(x, sig), seed)
433:        name="bg_shirley_truth_shirley_fit",
434:        regime="bg_mismatch", expectation="recover",
439:        bg="shirley_like",
489:        bg_mismatch_case(seed=61 + o),
            coincidence_ev=PROPOSAL_COINCIDENCE_BE,
            proposal_pass_ran=enable_proposal_pass,
        )
        # loud detection-family truncation record (Codex Stage-2 MAJOR):
        # names every feature the slot cap dropped (empty = no overflow)
        pool_payload["detection_model_overflow"] = detection_overflow
        result.candidate_pool = pool_payload
    elif pool_error is not None:
        result.candidate_pool = {
            "error": pool_error,
            "note": "candidate-generation layer failed — analysis degraded "
                    "to dominant-channel-only seeding (see server log)",
        }

    # Result-level honesty flag (stress-suite finding 0 — burial measured
    # at ΔBIC* +74…+944): a FILTERED candidate whose BIC* decisively beats
    # the emitted winner must be visible at the RESULT level, not only in
    # the candidate table.  Purely additive: ranking, filtering, and the
    # promotion rules are unchanged — this only reports what they buried.
    if result.survivors:
        win_bic = result.survivors[0].bic_adjusted
        # promotion LINEAGE, not just names: a decisive-override winner is
        # renamed "X+bfix" while its free original "X" stays in
        # filtered_out — flagging the original as "buried" would name the
        # very candidate that was promoted (Codex analyze review blocker)
        survivor_names = set()
        for r in result.survivors:
            survivor_names.add(r.model.name)
            if r.model.name.endswith("+bfix"):
                survivor_names.add(r.model.name[:-len("+bfix")])
            if r.augmented_from:
                survivor_names.add(r.augmented_from)
        dominant = None
        for rep, why in result.filtered_out:
            if rep.model.name in survivor_names:
                continue        # promoted members / their free originals
            if win_bic - rep.bic_adjusted > CONDITIONAL_OVERRIDE_DELTA_BIC:
                if dominant is None or rep.bic_adjusted < dominant[0].bic_adjusted:
                    dominant = (rep, why)
        if dominant is not None:
            rep, why = dominant
            result.filtered_dominant_alternative = {
                "name": rep.model.name,
                "bic_star": float(rep.bic_adjusted),
                "delta_bic_vs_winner": float(win_bic - rep.bic_adjusted),
                "filter_reason": why,
            }
    result.weighted_ic_disagreement = _weighted_ic_disagreement(
        result.survivors)
    return result


def _weighted_ic_disagreement(survivors: "list[ModelReport]") -> Optional[dict]:
    """Result-level flag when the weighted-χ² BIC (consistent with the fit
    weights) tops a different survivor than the ranking's RSS-form BIC*."""
    if len(survivors) < 2:
        return None
    weighted_top = min(survivors, key=lambda r: r.bic_weighted)
    if weighted_top.model.name == survivors[0].model.name:
        return None
    return {
diff --git a/autofit/confidence.py b/autofit/confidence.py
index bb74778..ab2897f 100644
--- a/autofit/confidence.py
+++ b/autofit/confidence.py
@@ -83,6 +83,9 @@ def _max_correlation(report: ModelReport, role: str) -> Optional[float]:
     return float(np.max(sub)) if sub.size else None
 
 
+from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # F3: one threshold, the server's
+
+
 def build_confidence_vector(
     report: ModelReport,
     role: str,
@@ -96,12 +99,19 @@ def build_confidence_vector(
                 if h.startswith(f"{role}:")]
 
     amplitude = float(comp.amplitude) if comp is not None else None
-    floor = detection_floor_multiple * noise_floor
+    # F3 (2026-09-27): detectability is the support F test on the fit
+    # (fitting._component_support, the server's statistic), not multiples of an
+    # absolute 1-count floor. above_floor = supported (F >= SUPPORT_MIN_F);
+    # present_but_poorly_constrained = the fit gains from it but not
+    # significantly; not_confidently_detected = removing it costs nothing.
+    support = getattr(comp, "support", None) if comp is not None else None
     if amplitude is None:
         detect_status = "not_fitted"
-    elif amplitude >= floor:
+    elif support is None:
+        detect_status = "above_floor" if amplitude > 0 else "not_confidently_detected"
+    elif support.get("supported"):
         detect_status = "above_floor"
-    elif amplitude > noise_floor:
+    elif (support.get("delta_chi2") or 0.0) > 0:
         detect_status = "present_but_poorly_constrained"
     else:
         detect_status = "not_confidently_detected"
@@ -122,9 +132,9 @@ def build_confidence_vector(
         },
         "detectability": {
             "amplitude": amplitude,
-            "noise_floor": noise_floor,
-            "floor_multiple": detection_floor_multiple,
-            "floor_multiple_is_tunable": True,
+            "basis": "support_f_test",       # F3: fitting._component_support, F >= SUPPORT_MIN_F
+            "support_f": (support or {}).get("f"),
+            "support_min_f": _SUPPORT_MIN_F,
             "status": detect_status,
         },
         "identifiability": {
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..9bad455 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -36,6 +36,7 @@ from typing import Callable, Optional
 
 import numpy as np
 from lmfit import Model, Parameters
+import fitting as _fitting  # F3: the server's support statistic, one definition
 from lmfit.model import ModelResult
 from scipy.integrate import trapezoid
 
@@ -637,6 +638,17 @@ class FittedComponent:
     amplitude: float
     shape_params: dict
     line_shape: Optional[LineShape] = None
+    # Unit F3 (2026-09-27): does the fit that produced this component need it?
+    # fitting._component_support on that fit — with the other components held
+    # as fitted, removing this one must make the fit significantly worse (F >=
+    # SUPPORT_MIN_F). The occupancy decisions (slot matching, the proposal

exec
/bin/zsh -lc 'node --test tests/js/autofit_c1s_gate.test.js tests/js/per_tab_state.test.js tests/js/fit_start_poll.test.js tests/js/fit_acceptance.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 278ms:
# Subtest: the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
ok 1 - the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
  ---
  duration_ms: 4.225378
  type: 'test'
  ...
# Subtest: the SELECTED data decide, not the typed midpoint of a window that reaches past the data
ok 2 - the SELECTED data decide, not the typed midpoint of a window that reaches past the data
  ---
  duration_ms: 1.31168
  type: 'test'
  ...
# Subtest: a non-active record is judged on its saved window over its own corrected data
ok 3 - a non-active record is judged on its saved window over its own corrected data
  ---
  duration_ms: 0.65958
  type: 'test'
  ...
# Subtest: the record path makes the SAME selection getROIData() makes (Codex round 1)
ok 4 - the record path makes the SAME selection getROIData() makes (Codex round 1)
  ---
  duration_ms: 0.582453
  type: 'test'
  ...
# Subtest: every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)
ok 5 - every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)
  ---
  duration_ms: 2.442778
  type: 'test'
  ...
# Subtest: BEHAVIOURAL: each caller hands isC1sTab the ACTIVE record, not merely a record looked up the right way (Codex round 2)
ok 6 - BEHAVIOURAL: each caller hands isC1sTab the ACTIVE record, not merely a record looked up the right way (Codex round 2)
  ---
  duration_ms: 3.303359
  type: 'test'
  ...
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 7 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 9.293184
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 8 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 4.442293
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 9 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 3.008032
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 10 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 8.956973
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 11 - a converged backend result is applied (sanity)
  ---
  duration_ms: 3.653814
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 12 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.856029
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 13 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 3.433236
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 14 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 3.267042
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 15 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 1.733431
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 16 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 0.855929
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 17 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.673187
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 18 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.443642
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 19 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 3.147889
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 20 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 3.912896
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 21 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.38811
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 22 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 6.471026
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 23 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 0.770523
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 24 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 2.770265
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 25 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.539988
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 26 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.472055
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 27 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 2.689759
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 28 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 1.597658
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 29 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.25805
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 30 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 3.178928
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 31 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 0.954943
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 32 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.590083
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 33 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.311219
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 34 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.221668
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 35 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.571876
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 36 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 2.222864
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 37 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.241888
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 38 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.230298
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 39 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.333356
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 40 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.784952
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 41 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 2.495221
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 42 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 3.579378
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 43 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 2.75009
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 44 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 2.509891
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 45 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 2.462954
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 46 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 2.536359
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 47 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 2.593358
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 48 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 2.55715
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 49 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 4.73462
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 50 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 2.646861
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 51 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 5.707725
  type: 'test'
  ...
# Subtest: the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
ok 52 - the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
  ---
  duration_ms: 0.705327
  type: 'test'
  ...
# Subtest: the token scan is linear and keeps a truncated string a string (Codex round 2)
ok 53 - the token scan is linear and keeps a truncated string a string (Codex round 2)
  ---
  duration_ms: 3.194632
  type: 'test'
  ...
# Subtest: start -> running polls -> done: the result is the /api/fit body; no job is left registered
ok 54 - start -> running polls -> done: the result is the /api/fit body; no job is left registered
  ---
  duration_ms: 10.152025
  type: 'test'
  ...
# Subtest: a bad request: the synchronous route's message and status, immediately; no poll
ok 55 - a bad request: the synchronous route's message and status, immediately; no poll
  ---
  duration_ms: 3.728199
  type: 'test'
  ...
# Subtest: a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
ok 56 - a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
  ---
  duration_ms: 3.512626
  type: 'test'
  ...
# Subtest: an error record is a failed fit with the synchronous message and status
ok 57 - an error record is a failed fit with the synchronous message and status
  ---
  duration_ms: 3.352171
  type: 'test'
  ...
# Subtest: a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
ok 58 - a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
  ---
  duration_ms: 3.40025
  type: 'test'
  ...
# Subtest: one lost poll is retried; five in a row are a transport failure and cancel the job
ok 59 - one lost poll is retried; five in a row are a transport failure and cancel the job
  ---
  duration_ms: 4.962389
  type: 'test'
  ...
# Subtest: a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
ok 60 - a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
  ---
  duration_ms: 2.361627
  type: 'test'
  ...
# Subtest: a job cancelled on the server (abandoned) is reported, not waited for
ok 61 - a job cancelled on the server (abandoned) is reported, not waited for
  ---
  duration_ms: 2.394671
  type: 'test'
  ...
# Subtest: ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
ok 62 - ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
  ---
  duration_ms: 4.620447
  type: 'test'
  ...
# Subtest: the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
ok 63 - the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
  ---
  duration_ms: 2.661131
  type: 'test'
  ...
# Subtest: Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
ok 64 - Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
  ---
  duration_ms: 2.220306
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 65 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 155.054307
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 66 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 68.356858
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 67 - the known class-C holders are gone from module scope
  ---
  duration_ms: 5.248128
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 68 - async operations capture their owning record before the first await
  ---
  duration_ms: 1.901474
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 69 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.592162
  type: 'test'
  ...
1..69
# tests 69
# suites 0
# pass 69
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 334.799649

codex
The test catches `tabs[0]` and early returns in all three callers. Two mutations still pass: the literal `_getTab('inactive')` fallback, because that ID is absent from the fixture, and `tabs[1]`, because the fixture always makes the second tab active. Renaming the inactive fixture or reversing tab order makes those mutations fail. Production callers remain correct, and all 69 targeted JavaScript tests pass.

exec
/bin/zsh -lc "node -e '
const fs=require('\\''node:fs'\\''),assert=require('\\''node:assert'\\'');
const lines=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'').split('\\''\\n'\\'');
function extract(name){let start=lines.findIndex(l=>l.startsWith('\\''function '\\''+name+'\\''('\\'')),d=0,s=false;for(let i=start;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\''){d++;s=true;}else if(c==='\\''}'\\'')d--;}if(s&&"'!d)return lines.slice(start,i+1).join('"'\\''\\n'\\'');}throw Error(name);}
const state={rawBE:[],rawIntensity:[],ccShift:0},fields={'\\''roi-min'\\'':{value:'\\'''\\''},'\\''roi-max'\\'':{value:'\\'''\\''}},document={getElementById:id=>fields[id]},tabManager={activeId:'\\''live'\\''};
const funcs=new Function('\\''state'\\'','\\''document'\\'','\\''tabManager'\\'',[extract('\\''getCorrectedBE'\\''),extract('\\''getROIData'\\''),extract('\\''isC1sTab'\\''),'\\''return {getROIData,isC1sTab};'\\''].join('\\''\\n'\\''))(state,document,tabManager);
const bounds=['\\'''\\'','\\''bad'\\'','\\''270'\\'','\\''280'\\'','\\''295'\\'','\\''315'\\'','\\''420'\\'','\\''Infinity'\\'','\\''-Infinity'\\'','\\''290.5'\\'','\\''0'\\'','\\''NaN'\\''];
const shifts=[undefined,null,NaN,Infinity,-Infinity,0,100,200,'\\''100'\\'','\\''bad'\\''];
const scans=[[],[285],[270,315],[280,285,300],[420,400,380,290,270],[NaN,285,Infinity,-Infinity],Array.from({length:301},(_,i)=>420-i*.5)];
let count=0;
for(const rawBE of scans)for(const ccShift of shifts)for(const a of bounds)for(const b of bounds){
 state.rawBE=rawBE;state.rawIntensity=rawBE.map(()=>1);state.ccShift=ccShift;fields['\\''roi-min'\\''].value=a;fields['\\''roi-max'\\''].value=b;
 const rec={id:'\\''saved'\\'',rawBE,ccShift,ui:{roiMin:a,roiMax:b}};
 const live={...rec,id:'\\''live'\\''};
 assert.equal(funcs.isC1sTab(rec),funcs.isC1sTab(live),JSON.stringify({rawBE,ccShift,a,b})); count++;
}
const long={id:'\\''saved'\\'',rawBE:Array.from({length:1000000},(_,i)=>420-i*.00015),ccShift:0,ui:{roiMin:'\\''280'\\'',roiMax:'\\''295'\\''}};
let start=performance.now();assert.equal(funcs.isC1sTab(long),true);const elapsed=performance.now()-start;
console.log(JSON.stringify({active_record_comparisons:count,mismatches:0,million_point_record_ms:Math.round(elapsed)}));
function support(y,fit,c,scale){let withFit=0,without=0;for(let i=0;i<y.length;i++){const r=(y[i]-fit[i])*scale,w=1/Math.max(y[i]*scale,1);withFit+=w*r*r;without+=w*(r+c[i]*scale)**2;}return (without-withFit)/withFit;}
console.log('\\''README floor example F'\\'',support([1,100],[.99,90],[.9,22],1),support([1,100],[.99,90],[.9,22],.1));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 109ms:
{"active_record_comparisons":10080,"mismatches":0,"million_point_record_ms":13}
README floor example F 10.066993300669935 9.322706772932273

codex
No BLOCKER or MAJOR found in the shipped gate.

**MINOR — caller test still has fixture-dependent blind spots.** [autofit_c1s_gate.test.js:87](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:87). Separately for all three callers, both mutations leave all six tests passing:

- `_getTab('inactive') || _getTab(tabManager.activeId)`: no fixture has ID `inactive`, so it falls back to the active record.
- `tabs[1] || _getTab(tabManager.activeId)`: the fixture always makes the second tab active. With active U 4f first and inactive C 1s second, this mutation judges the wrong spectrum.

Renaming the inactive fixture or reversing tab order exposes these failures. Exercise both tab orders and the named inactive lookup. Current production callers are correct.

The test **does** reject `tabs[0]`, lookup of the actual inactive fixture (`t1`), and an early return before the gate, independently for every caller.

The README now correctly describes LR and qualifies F’s invariance. Its recommendation to start from F, distinguish unsupported components from orphans, and report background mismatch independently is sound. I reproduced the documented floor-sensitive F change, **10.067 → 9.323**; I did not rerun the parked Python batteries.

Validation: **69 targeted JavaScript tests passed**; **10,080 active/record comparisons matched**; the million-point record check completed without error. Restoring the original gate fails four of the six gate tests. No files changed.

VERDICT: GO
tokens used
50,753
No BLOCKER or MAJOR found in the shipped gate.

**MINOR — caller test still has fixture-dependent blind spots.** [autofit_c1s_gate.test.js:87](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:87). Separately for all three callers, both mutations leave all six tests passing:

- `_getTab('inactive') || _getTab(tabManager.activeId)`: no fixture has ID `inactive`, so it falls back to the active record.
- `tabs[1] || _getTab(tabManager.activeId)`: the fixture always makes the second tab active. With active U 4f first and inactive C 1s second, this mutation judges the wrong spectrum.

Renaming the inactive fixture or reversing tab order exposes these failures. Exercise both tab orders and the named inactive lookup. Current production callers are correct.

The test **does** reject `tabs[0]`, lookup of the actual inactive fixture (`t1`), and an early return before the gate, independently for every caller.

The README now correctly describes LR and qualifies F’s invariance. Its recommendation to start from F, distinguish unsupported components from orphans, and report background mismatch independently is sound. I reproduced the documented floor-sensitive F change, **10.067 → 9.323**; I did not rerun the parked Python batteries.

Validation: **69 targeted JavaScript tests passed**; **10,080 active/record comparisons matched**; the million-point record check completed without error. Restoring the original gate fails four of the six gate tests. No files changed.

VERDICT: GO
