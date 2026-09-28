# Find Peaks occupancy: the server's support F test instead of a 1-count floor (2026-09-27)

Owner, 2026-09-27: "switch Find Peaks' occupancy test from the absolute
1.0-count floor to the same F test the server's support check uses, per
docs/findings/noise-floor-occupancy/. Scale-free, no tolerance, per the
design rule. Build to 'ready for deploy' only — do NOT deploy it. Enumerate
sites first; Codex x2."

Starting point: `docs/findings/noise-floor-occupancy/variant_F_support_test.patch`
(measured in F3) plus the README's two required follow-ups.

## 1. Sites — every read of `noise_floor` in the Find Peaks engine (`autofit/`)

`noise_floor` (default 1.0; the page never sends it) had two jobs.

**A. Poisson variance floor, σ = √max(y, noise_floor) — KEPT, unchanged.** Not
a decision threshold: it is the counting convention the server's weights use
(`fitting`: 1/√max(counts, 1)).

| site | what |
|---|---|
| `candidates.py:621–622` | local σ for candidate detection gates |
| `engine.py` `compute_residual_diagnostics` | standardised residuals r/σ |
| `engine.py` preseed local σ (`_detect_*` / `local_sigma`) | preseed SNR gate |
| `engine.py` fit weights (`sigma = sqrt(max(y, noise_floor))`, two sites) | the fit's weights |
| `engine.py` `_attempt_proposal` local σ | the proposal's SNR gate (below) |

**B. Occupancy threshold, `amplitude > noise_floor` — REPLACED by the support F
test.**

| # | site | before | after |
|---|---|---|---|
| B1 | `engine.match_components_to_slots._accepts` | a component occupies a slot if its window/width fit AND amplitude > 1 count | window/width only decide WHICH slot; whether it is THERE is `_occupies(comp)` = `fitting._component_support(...)["supported"]` on the fit that produced it (F ≥ `SUPPORT_MIN_F`) |
| B2 | `engine._attempt_proposal` | a proposed slot is rejected if amplitude ≤ 1 count | rejected if `not _occupies(comp)`; the message names F — checked on the initial augmented fit AND again on the stability-promoted refit that would be emitted (Codex round 1; the boundary pegs were already re-checked there) |
| B3 | `confidence.build_confidence_vector` detectability | `above_floor` ≥ 3 × floor, `present_but_poorly_constrained` > floor | `above_floor` = supported; `present_but_poorly_constrained` = Δχ² > 0 but F < 10; `not_confidently_detected` = removing it costs nothing. Status values unchanged (the payload's consumers: `test_methods_seam`, `test_browser_schema_roundtrip`; the page reads none of the detectability fields) |
| B4 | `grammar.ComponentSlot.contains` | amplitude > noise_floor | amplitude > 0 (sign only; no engine caller) |

Where the support comes from: `engine._component_supports(result)` evaluates
`fitting._component_support` for every component of an lmfit result (data,
best fit, the component's curve, the fit's own weights, its free-parameter
count — a parameter belongs to the slot that DECLARES it (`_slot_param_names`:
centre, amplitude, width, its shape's own parameters and only the auxiliaries
it creates; `_param_owner_by_name`), never to a prefix, which cannot tell
"main" + "gl_ratio" from "main_gl" + "ratio" (Codex rounds 1–2)) once, in
`_extract_fitted_components`; it rides on
`FittedComponent.support` through slot matching. A component with no fit
behind it (hand-built in tests) falls back to `amplitude > 0`.

**C. Orphans vs empty slots (README follow-up 1).** Before, a component that
failed occupancy had no accepting slot and became an ORPHAN — counted in
`orphan_rate`, a plausibility violation ("a peak nobody expects"). Under F that
would turn every unsupported in-window component into an extra-peak
violation. Now `match_components_to_slots` sets an unsupported component
aside (`"__unsupported__"`, reporting only): it occupies no slot (that slot's
persistence drops, as it should — the slot is empty) and it is NOT an orphan.
An orphan is a SUPPORTED component no slot's window/width accepts.

**Related, NOT changed: `engine._attempt_proposal`'s SNR gate** (`amplitude <
PROPOSAL_AMPLITUDE_SNR × local σ`, σ the Poisson noise). A signal-to-noise
ratio under the same counting assumption as the weights, not the 1-count
floor; listed so review can challenge it.

**E. Linked components follow their root.** The server's support check makes
a linked component FOLLOW its root (`individual_peaks[].support.follows`). The
engine now does the same for a slot whose amplitude is an expression of its
parent's (a spin-orbit partner at a fixed area ratio): `_followed_supports`
copies the root's verdict with `follows: <root role>`. A linked slot with a
free amplitude (only its position tied) keeps its own verdict.

**D. The model-mismatch honesty signal (README follow-up 2).** NOT delivered —
see §3: an owner decision.

## 2. Measurements

### Stress honesty battery (`tests/autofit/test_stress_honesty.py`)

With F + the orphan split: 11 passed, 1 failed — `test_bg_mismatch_surfaces_loudly`
(a Shirley-shaped truth fitted with straight-line backgrounds), as the README
predicted. Under F the winner is **P2, the TRUE two-peak model**
(`true_candidates=("P2",)`); P3's third component compensated for the wrong
background, F calls it unsupported (its gain divided by the misfit χ²ᵣ ≈ 284),
P3's persistence for that slot drops to 0 and P3 leaves the conditional pool.
The result still carries the winner's χ²ᵣ 308.7 (comparison table), the
winner row's `autocorr_flag`, and `filtered_dominant_alternative` (P3,
ΔBIC* 153 — the page's red "a better-scoring model was set aside" banner); it
is no longer `conditional`.

### Candidate mismatch signals, measured (winner of each run; ×0.1 = the same spectrum as a rate)

| spectrum | scale | χ²ᵣ | residual lag-1 autocorrelation flagged | n_eff / n |
|---|---|---|---|---|
| stress: bg mismatch | ×1 / ×0.1 | 308.7 / 30.9 | yes / yes | 0.0075 / 0.0075 |
| stress: bg matched control | ×1 / ×0.1 | 1.31 / 0.13 | no / no | ~1.0 / ~1.0 |
| 8 real committed C 1s scans (3 gate anchors + 5) | ×1 | 1.30–6.46 | **yes on 8 of 8** | 0.10–0.55 |
| same | ×0.1 | 0.15–3.51 | yes on 8 of 8 | 0.04–0.49 |

* χ²ᵣ is not scale-free (it moves with the counts: ×0.1 divides it by 10), and
  on real data it grows with the counts for a slightly imperfect lineshape — a
  χ²ᵣ cutoff is exactly the design rule's failure.
* The residual lag-1 autocorrelation IS scale-free (n_eff/n identical at ×1 and
  ×0.1), but real XPS fits are not noise-limited: every real winner has
  structured residuals. As a flag it fires on everything; as a number it
  separates the stress case (0.0075) from real fits (≥ 0.04) only by a factor
  of ~5 and only with a chosen constant.
* So no residual- or χ²ᵣ-based signal distinguishes "the background is wrong"
  from "the lineshape is not perfect" without a chosen cutoff.

(Also found, pre-existing and unchanged by this unit: the engine's OUTCOME is
not rescale-invariant — on main a ×0.1 rescale changes the winner or the
conditional tier on 2 of the 8 real scans (Scan_8 UCl4, Scan_7 8-JT). Not the
ranking: BIC* = n·log(RSS/n) + k·log(n), and a rescale adds the same 2n·log(c)
to every candidate's score for corresponding fits (Codex round 1). See the
trace below.)

### Real-data gates (`RUN_AUTOFIT_GATE=1`: C 1s, U 4f, B 1s / Cl 2p parity; Bayesian real and U 4f unresolved; candidate-pool real; stress honesty)

| | main (0bb200b) | this branch |
|---|---|---|
| passed / failed | 26 / 1 | 26 / 1 |
| the failure | `test_candidate_pool_real_gate` ds8 "C1s Scan": the detected shoulder is not in the final model — IDENTICAL peaks on both (the sweep hits its 240 s budget after 3 of 6 candidates); PRE-EXISTING, on local-only held-out data never committed (the datasets were symlinked in from the main checkout for this run) | the same |
| stress honesty | 12 / 12 (old wording) | 12 / 12 (option-A wording, §3) |

### What F changes on real Find Peaks results (8 committed C 1s scans, gate options, ×1 and ×0.1; both engines run twice on the differing scans — both reproduce themselves 12 / 12, so every difference below is F's)

Final code (incl. §1 E, re-measured after it — one run changed, Scan_6 ×0.1):
10 of 16 runs unchanged. Changed:

| scan | scale | main | this branch |
|---|---|---|---|
| 1-GTA Scan_6 (gate anchor) | ×1 | MG2 (conditional), χ²ᵣ 2.04 | AG2+preseed (conditional), χ²ᵣ 3.69 — MG2's lowest slot persistence drops to 0.67: in one of its three refits a component was not supported by the data, so MG2 is no longer "stable" (the 1-count floor had counted that component as present). The C 1s gate still passes (graphite centre, satellite, envelope R) |
| 1-GTA Scan_2 | ×1 | MG2, χ²ᵣ 1.54 | MG3, χ²ᵣ 1.50 |
| 8-JT Scan_7 | ×1 | MG2, χ²ᵣ 5.21 | MG3, χ²ᵣ 5.19 |
| 1-GTA Scan_6 | ×0.1 | MG2 (conditional), χ²ᵣ 0.20 | MG3 (conditional), χ²ᵣ 0.22 |
| 8-JT Scan_5 | ×0.1 | MG3 conditional | MG3 not conditional |
| UCl4 Scan_3 | ×0.1 | MG2 | MG3 |

**Scale-dependence of the OUTCOME got WORSE on these scans, not better:** main
changes its result under ×0.1 on 2 of 8 scans, this branch on 6 of 8 (Scan_8,
Scan_6, Scan_5, 1-GTA Scan_2, Scan_3, Scan_7). The occupancy statistic itself
is invariant (pinned in `test_occupancy_support.py`), but the pipeline around
it is not: the candidate-detection and proposal gates are Poisson signal-to-
noise ratios, so ×0.1 can change the candidate set (NOT the ranking: BIC* is
n·log(RSS/n) + k·log(n), shifted equally for every candidate by a rescale —
Codex round 1 corrected the first draft here). Under the 1-count floor that never reached
occupancy on real data (every real amplitude is far above 1 count, so the
floor never flipped); under F — the likely mechanism, NOT traced scan by
scan — a MARGINAL component (F near 10) now decides a candidate's stability,
and those small upstream differences push it across.
In words: F makes the occupancy test scale-free and honest about marginal
components, and in doing so exposes that the rest of Find Peaks is not
scale-free. Owner-relevant: it is not a reason for C by itself (the ×1 results
are what students get from counts data), but it is not the "scale-free Find
Peaks" the design rule might suggest.

### Traced: 8-JT Scan_7 (Codex round 1 asked for the mechanism)

| | ×1 main | ×1 this branch | ×0.1 main | ×0.1 this branch |
|---|---|---|---|---|
| MG2 | BIC* 1765.1, χ²ᵣ 5.21, plausibility-flagged (C=O width at its cap) | 1765.1, 5.21, flagged | 1024.5, 0.52, CLEAN | 1024.5, 0.52, CLEAN |
| MG3 | BIC* **1778.1**, χ²ᵣ 5.19, persistence 0.75 | BIC* **1757.8**, χ²ᵣ 5.19, 0.75 | filtered | filtered |
| winner | MG2 (conditional) | MG3 (conditional) | MG2 (clean) | MG2 (clean) |

Two separate effects:

1. **This branch, within one scale:** the same fit (same χ²ᵣ) scores a lower
   BIC* — BIC* removes an ABSENT slot's parameters, and under F more of MG3's
   slots are absent (unsupported → low persistence, small area), so MG3
   overtakes MG2 at ×1. (On Scan_6 the effect is persistence instead: MG2 no
   longer counts as stable.)
2. **Both engines, across scales:** the FIT changes under ×0.1 — MG2 presses
   a width bound at ×1 and not at ×0.1 — so plausibility, and with it the tier,
   differ. Under exact Poisson scaling the weighted fit would be identical, so
   something in the fit is not scale-free (absolute amplitude bounds or start
   values are the obvious suspects; not traced further here).

So 2/8 → 6/8 is effect 2 (pre-existing) made visible more often by effect 1,
which moves BIC* and stability for marginal components.

### A browser test's NOISE-FREE fixture

`tests/test_browser_find_peaks_full_window.py` (two of four) failed on this
branch: its synthetic C 1s spectrum is noise-free (300 + one Gaussian), fitted
to rounding (χ²ᵣ 0.00), where the support F test is meaningless (the
required-refit known limit in CLAUDE.md). The engine's outcome there turns on
the upload's rounding and wall-clock budgets ON MAIN TOO: through the page,
main returned a conditional fit and the branch none; through a direct
`/api/analyze` replay (4-dp upload) main returned NO survivor and the branch a
clean one. The test is about the apply path with the full-window option off,
not the fit, so its fixture now carries fixed pseudo-random Poisson noise
(√counts × a seeded normal): 4 / 4 pass on main AND on this branch. Known
limit, as for the required-refit test: on noise-free data the occupancy
verdicts are not meaningful.

## 3. OWNER DECISION — the background-mismatch honesty test

`test_bg_mismatch_surfaces_loudly` pinned "a wrong background is never a clean
confident result" through the conditional tier, and that tier was reached only
through the component that compensated for the wrong background (P3's third).
The README asked for a mismatch signal that does not ride on it; §2 shows the
signals at hand either are not scale-free (χ²ᵣ) or fire on every real fit
(residual structure). Options:

| | what | cost |
|---|---|---|
| **A (recommended; implemented on this branch)** | Accept F's outcome and re-state the test's contract to what is true and scale-independent in kind: the engine returns the true 2-peak model, the winner's χ²ᵣ is reported and grossly elevated, and the result carries `filtered_dominant_alternative` (the page's red banner). No new rule. The principled mismatch check is a comparison of BACKGROUND models (the matched-control case shows Shirley candidates absorb the integral background) — logged as its own unit | a wrong-background result is no longer marked "conditional"; the red banner remains |
| B | a result-level `model_mismatch` flag from a chosen constant (e.g. n_eff/n < 0.02, between the stress case's 0.0075 and real data's ≥ 0.04) | a new threshold on a data-dependent quantity (n_eff/n also depends on the sampling step) — the design rule's failure; needs calibration; NOT recommended |
| C | keep the 1-count floor until a background-comparison check exists | the occupancy floor stays scale-dependent |

A is what this branch ships; if the owner prefers C the branch waits.

What choosing A MEANS (Codex round 1, both runs): it narrows the test's
contract; it does NOT provide the README's independent mismatch signal. The
remaining warning (`filtered_dominant_alternative`) still needs a better-scoring
candidate to have been evaluated and set aside. Reproduced: `bg_mismatch_case`
with `candidate_filter=["P1", "P2"]` returns P2 at χ²ᵣ 308.7 with
`conditional` false, no `filtered_dominant_alternative` and no message — the
page then reads it as clean. That configuration behaves the same on main (it
has no P3 either), so it is a requirement left open, not a regression this
branch introduces; choosing A is choosing to defer follow-up 2 to the
background-comparison unit.

## 4. Codex rounds

**Round 1 — NO-GO ×2** (`occupancy_f_test_verdict_run{A,B}.md`; both confirmed
the central wiring: the producing fit's data, background-subtracted best fit,
weights and total parameter count; `SUPPORT_MIN_F` reused; `__unsupported__`
removed by the only production iterator; the Bayesian method does not read
this path):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): free parameters counted by `startswith(prefix)` — roles "main" / "main_extra" gave "main" both components' parameters (F 12.85 → 6.42, a supported peak read unsupported) | a parameter belongs to the LONGEST component prefix it starts with; regression `test_free_parameters_are_owned_by_the_longest_prefix` (fails on a41ee81). No resolved built-in grammar has an overlapping pair (48 grammars, 16 roles), so the gate and real-data measurements are unaffected |
| 2 | MAJOR (B): a stability-promoted refit could carry an unsupported proposal past the gate (only pegs were re-checked) | support re-checked on the promoted refit ("not supported by the data in the promoted refit (post-stability)"); regression with an injected promotion (fails on a41ee81) |
| 3 | MAJOR (A) / noted (B): option A narrows the stress test's contract and does not deliver the README's independent mismatch signal (`candidate_filter` P1/P2: P2 at χ²ᵣ 308.7, no warning at all — identical on main) | not a code fix: §3 now says so explicitly; it is the owner's decision (accept the deferral, or C) |
| 4 | MINOR (A, B): the plan blamed BIC* for the rescale sensitivity; BIC* = n·log(RSS/n) + k·log(n) shifts equally for every candidate | corrected; Scan_7 traced (§2): the absent-slot k adjustment under F within a scale, and fits that change under rescale on both engines |

**Round 2 — NO-GO ×2** (`occupancy_f_test_r2_verdict_run{A,B}.md`; both
confirmed the round-1 fixes, the Scan_7 mechanism — MG3's adjusted k 25 → 21,
BIC* 1778.10 → 1757.79 — and that §3 states the deferral accurately):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B): longest-prefix ownership is still wrong — `s_main_gl_ratio` is role "main"'s `gl_ratio`, not role "main_gl"'s (F 11.42 → 8.57, a supported component emptied) | ownership by DECLARATION: `_slot_param_names(slot)` lists the names a slot creates — centre, amplitude, width, its shape's parameters, and only the auxiliaries it actually creates (`offset` for a non-point offset range, `ratio` for an area-ratio range, `fwhm_excess`); a name two slots declare is owned by neither; shared width parameters by none. Regression parametrised over both reported collisions (main / main_extra, main / main_gl) |
| 2 | MAJOR (A): the absent-slot BIC* adjustment (`_count_slot_free_params`, pre-existing) counted by prefix too — minor / minor_extra removed 6 parameters for a 3-parameter slot, a 16.9-point BIC* bias from naming alone, exposed now that F makes such slots absent | the same declared ownership; regression (fails on 383dafe) |
| 3 | MINOR (B): the promotion regression injected no stability entry, so the old code rejected for another reason | a passing stability entry: on a41ee81 the test now fails with the false ACCEPTANCE itself; plus the supported-promotion counterpart (accepted) |

The same declared map (`_param_owner_by_name`) now serves EVERY place autofit
attributes a parameter to a slot — four more used a prefix (pre-existing,
reporting only, and harmless on the shipped grammars): boundary-hit labels
(`_role_for_param`, longest prefix), the per-slot correlation
(`confidence._max_correlation`), the payload's per-slot σ
(`ic_model_comparison._peaks_from_report`) and the Bayesian intervals. One
ownership definition, pinned by `test_one_ownership_map_for_every_attribution_site`.

Also pinned: on every built-in grammar (≥ 40 candidates) each parameter the
engine creates is declared by exactly one slot or is a shared width parameter —
so for the shipped grammars declared ownership equals what prefix matching
found, and the gate / real-data measurements above are unchanged.

**Round 3 — GO ×2** (`occupancy_f_test_r3_verdict_run{A,B}.md`; run B
checked declarations against actual parameter creation on a 1 728-case matrix
— every shape, auxiliary condition, width constraint, region prefix and
full-window mode; both restored the earlier functions and saw each regression
fail). Two MINORs, fixed after the GO:

| # | finding | fix |
|---|---|---|
| 1 | MINOR (A, B): the cross-site attribution test checked source text only | behavioural tests for the payload σ, the cross-slot correlation and the Bayesian intervals on the main / main_gl model; each fails when that site's prefix matching is restored |
| 2 | MINOR (B): §1 still described longest-prefix ownership | §1 now describes declared ownership |

**READY FOR DEPLOY — pending the owner's §3 decision** (option A implemented;
choosing C means the branch waits). NOT deployed (owner: build to ready only).

## 5. Owner's pre-deploy questions (2026-09-28) — `docs/findings/find-peaks-scale/`

Owner accepted option A's reasoning and asked for a diagnosis before any
deploy. The findings CORRECT two statements above: the Scan_6 move (§2) was
not an unsupported MG2 component but a refit capped at 18 000 evaluations plus
the 25 s wall-clock budget, and it happens on main too under the same load; and
the "6 of 16 runs change" table mixed load-dependent budget effects into this
unit's effect — deterministically (budgets off) the unit changes 3 of 16. The
×0.1 sensitivity is three pre-existing sites (wall-clock budgets, the
detection layer's Poisson SNR gates, Shirley's absolute stop tolerance),
amplified by refits that stop on `xtol` after ~30 evaluations. NOT deployed.
