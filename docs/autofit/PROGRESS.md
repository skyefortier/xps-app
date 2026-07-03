# Autofit Engine — PROGRESS / Handoff Log

*Continuously updated during the Fable 5 unsupervised weekend run (started 2026-07-02).
This is the handoff map for the Monday session (Sonnet 5 / Opus 4.8). Read this first.*

**Branch:** `feature-autofit-stage2` (never merged to main; new engine is strictly additive + opt-in).
**Rails honored:** no merge to main, no deploy, no force-push, `/api/fit` and the manual-fit
path untouched.

---

## Status board

| Unit | Status | Tested | Notes |
|---|---|---|---|
| Recon + data inventory | DONE | n/a | see below |
| Baseline test suite | DONE | ✅ | **123 passed, 1 pre-existing failure**: `test_machine_tier.py::test_deterministic_reproducible_from_stage9` (`.stage9` regeneration check, SystemExit in `scripts/gen_machine_tier.py:193`; unrelated to fitting; present before any autofit work). "Green" = no NEW failures beyond this. |
| C 1s characterization battery + parity net | DONE | ✅ 59 tests | `tests/autofit/test_c1s_parity_battery.py`: 29 expert C 1s fits frozen (eval parity ≤1.2e-7; refit drift ≤2e-4 eV; fixture rtol 1e-6). 15 tabs excluded w/ reasons (legacy no-`be`; 1 internally inconsistent). Regenerate fixture ONLY via `scripts/gen_c1s_battery_fixture.py` after reviewed numerics changes. |
| Schema round-trip (`analysis` ns + `_confidence`) | DONE | ✅ 3 browser tests | `analysis` whitelisted in buildTabData + load (v3 kept, omitted-when-absent); `_confidence` proven on the peak-spread channel; save→load→save deep-diff on both formats; pre-engine saves load clean. |
| Resolver skeleton + PeakFitMethod seam | DONE | ✅ 18 tests | `autofit/`: grammar.py (phases[], phase disambiguation mandatory, leakage guards, joint co-fit composition), engine.py (fitalg port, region-agnostic; fitalg LA→`ds_g`), regions/c1s.py (A/AG/M/B families), criteria.py, confidence.py, methods/ (LS + IC implemented; bayesian/sparse/multivariate/maxent stubs). |
| C 1s parity gate | **PROVEN** | ✅ 3/3 anchors | `tests/autofit/test_c1s_parity_gate.py` (env-gated: `RUN_AUTOFIT_GATE=1`, ~4 min): main Δ 4–12 meV, satellite Δ 0.08–0.29 eV, domain envelope R 0.004–0.014 vs expert fits. Winners: MG3/MG2 (conditional tier, violations surfaced) + AG2 (clean) — see calibration log. |
| Codex checkpoint: Stage 2 | DONE* | review #1 ✅ / re-review HUNG | Review #1: NO-GO w/ 9 findings → all fixed + test-pinned (`2669ed9`). Re-review hung (known issue) → killed, logged, proceeded per rails. Monday re-runs `docs/autofit/codex/stage2_rereview_prompt.txt`. |
| Stage 3: U 4f module | **DONE** | ✅ 62 tests | `regions/u4f.py` (LACX main doublet w/ shared α/β/m + bounded-asymmetry safeguard; explicit satellite doublet + free variant; NIST/Ilton-Bagus-cited constants) + minimal `regions/n1s.py` (co-fit partner). Engine prereqs: `share_parent_params`, linked-chain topological param ordering, linked-group absent-slot atomicity. U 4f manual-path battery (29 expert fits frozen) + engine parity gate incl. **U 4f + N 1s co-fit** (in normal suite, ~20 s). |
| Codex checkpoint: Stage 3 (U 4f) | DONE | **GO** ✅ | 3 majors + 2 minors, all fixed same-session (see verdict section). Verdict + prompt in `docs/autofit/codex/`. |
| U 4f module | TODO | — | |
| B 1s / N 1s / Cl 2p cookbook | DONE | ✅ 21 tests | `regions/b1s.py` (position-neutral roles per discrepancy #8; good-exemplar windows; component ladder) + `regions/cl2p.py` (doublet, Δso/ratio CONDITIONAL-cited, fixed + relaxed variants) + minimal `n1s.py` (validated by the U 4f co-fit gate). Batteries (B 1s ×4, Cl 2p ×3) + engine gates: B 1s 3-component winner beats expert (χ²ᵣ 1.26 vs 1.43); Cl 2p relaxed-ratio CONDITIONAL winner beats expert on both anchors (discrepancy #7). Engine: `smart_exp` bg + decisive-override rule (ΔBIC*>10, Kass & Raftery 1995) for the conditional tier. |
| Bayesian exchange-MC method | TODO | — | |
| Element-physics DB | TODO | — | |

## Codex checkpoint verdicts

### Stage 2 review #1 (2026-07-03, codex exec read-only, high effort)
**VERDICT: NO-GO** — 2 blockers, 6 majors, 1 minor. Manual-fit path confirmed
unchanged vs main; template diff confined to the intended `analysis` additions.
Findings + dispositions:
1. **BLOCKER** resolver can't co-fit the same region from two phases
   (BN+B4C B 1s) — ACCEPTED, fixed: structured region requests
   `(region, phase_id)`, phase-qualified role slugs.
2. **BLOCKER** proposal slots copy region/phase from `base.slots[0]` (phase
   leakage in joint fits) — ACCEPTED, fixed: proposals tagged
   `unassigned` (they spawn outside all grammar windows by construction;
   assignment is adjudication, not inheritance).
3. **MAJOR** ranking was (χ²ᵣ, BIC*) — spec says BIC* is the ranking default —
   ACCEPTED, fixed: sort (BIC*, χ²ᵣ). (fitalg itself ranked χ²-first; port
   was faithful but spec-noncompliant.)
4. **MAJOR** absent slots still emitted as output peaks — ACCEPTED, fixed:
   winner's absent slots excluded from peaks/confidence (remain in analysis).
5. **MAJOR** F-test ran on absent-slot-adjusted models — ACCEPTED, fixed:
   pairs with absent slots skipped.
6. **MAJOR** AICc used adjusted k (suppressed the BIC*/AICc conflict signal) —
   ACCEPTED, fixed: AICc from actual fitted k; BIC* stays adjusted+starred.
7. **MAJOR** C1S_WINDOWS / FWHM_RANGE_GRAPHITIC uncited — ACCEPTED, fixed:
   explicit UNVERIFIED-calibration markings.
8. **MAJOR** stage gates can skip silently (no CI in repo) — PARTIAL: skips
   made loud; the always-on battery remains non-skipping; full fix needs CI
   infra (logged for Monday; out of window scope).
9. **MINOR** `<` vs `<=` ambiguity-threshold mismatch — fixed (`<=` both).

All 9 fixes landed in commit `2669ed9` with pinning tests; gate re-proven
3/3 under the BIC*-first ranking; suite 213 passed + baseline failure.

### Stage 2 re-review #2 (2026-07-03) — **CODEX HUNG, logged per run rails**
`codex exec` (read-only, high effort) produced no output for >5 min
(0.0% CPU, empty output, no verdict file) — the known hanging behavior.
Killed and proceeded to Stage 3 per the run brief ("NEVER let a Codex call
stall the run"). **Monday action:** re-run the re-review —
prompt preserved at `docs/autofit/codex/stage2_rereview_prompt.txt`
(review #1 verdict + prompt also preserved in that directory). Note that
review #1 DID complete and its 9 findings are all dispositioned above with
pinning tests, and it independently confirmed the manual-fit path is
byte-unchanged vs main.

## Discrepancies vs expert reference fits (for human adjudication)

1. **Stray `Zr 3d` RSF tag** (the known error from the run brief, now located):
   `B4C-UCl4.proj.zip`, ALL 10 B 1s tabs — peaks `B-B` and `B-C` carry
   `_rsfKey: 'Zr 3d'` (the `B₂O₃`-type third peak is tagged correctly). Affects
   any atomic-% computed from those fits. Source data NOT altered; quantification
   lint (spec §8, later gate) should flag exactly this pattern.
2. **Systematic `K 2p` RSF tag on every C 1s π→π* satellite** — all 44 C 1s tabs
   across 5 projects (1-GTA, 8-JT, Cl2p_projfit, Project9, UCl4_on_graphite).
   π→π* (~291 eV corrected) sits near the K 2p window, so this looks like a
   dropdown mis-pick propagated by batch fitting. Same lint pattern as #1.
   NOT flagged in the run brief — needs Skye's confirmation it's unintended.
3. `4-GTA UCl4-BN` B 1s fits: single asym-GL peak with χ²ᵣ 17–105,358 (two tabs
   catastrophically bad) — treated as suspect reference per the run brief; NOT
   used as parity anchors.
4. One internally inconsistent C 1s tab (`UCl4_on_graphite / C1s Scan_4`):
   saved `fittedY` has 143 pts vs `be` 142 (stale fittedY from an earlier ROI).
   Excluded from the battery with recorded reason.
5. **Width-convention conflict, engine grammar vs expert C 1s practice**: the
   expert fits let adventitious GL components go to FWHM 1.57–2.66 eV and the
   π→π* satellite to 3.95 eV; the grammar caps contamination at 1.6 eV
   (Biesinger 2022 / Greczynski & Hultman 2020) and the satellite at 3.0 eV
   (fitalg UNVERIFIED tunable). Engine caps kept (lit-based; NOT silently
   widened to force a match). Consequence: peak-by-peak width parity is not
   achievable by construction; the parity gate asserts main/satellite position
   + envelope R-factor instead. Needs Skye's ruling on which convention the
   engine should encode for adventitious carbon on composite samples.
6. **Low-BE 'Unknown' C 1s component at ~283.4 eV** in the UCl4-graphite
   expert fits sits OUTSIDE every grammar window (below the graphitic window
   floor 284.0). It is exactly the case the residual-guided proposal pass
   exists for; whether it's carbide-like chemistry or a U-related artifact is
   an open question for adjudication.
7. **Cl 2p intensity ratio rejects 2:1**: on both corrected Cl 2p anchors
   the relaxed-ratio doublet beats the fixed-0.5 candidate by very strong
   evidence (χ²ᵣ 2.40→1.62; 3.25→2.67) with the ratio pegged at the 0.55
   bound — i.e. the data wants 2p1/2 : 2p3/2 > 0.55. Together with the
   documented elevated χ²ᵣ this points at unmodeled structure (second
   chloride species / plasmon / background shape) rather than exotic
   physics; engine reports it as a CONDITIONAL winner with the violation
   surfaced. Needs adjudication before the Cl 2p Δso/ratio constants can
   leave CONDITIONAL status (spec §9).
8. **B 1s component-assignment conflict between the two expert sources**:
   spec §3.3 (from the 4-GTA analysis) says B-C 189.41 / B-B 187.39, but the
   good B4C-UCl4 fits (χ²ᵣ 1.4–2.5) label B-C 187.10–187.24 / B-B
   188.12–188.77 — the low/mid assignments are SWAPPED between sources
   (identical positions, opposite chemistry labels). The engine's B 1s
   module will use position-neutral role names (low/mid/oxide) and defer the
   chemical assignment to Skye. Also: B-O is center-pinned at exactly 193.00
   in all 10 B4C-UCl4 fits (analyst fixed it), and the `Zr 3d` RSF mis-tag
   (discrepancy #1) sits on B-B and B-C in those same fits.

## UNVERIFIED / suspect items

- All fitalg pipeline thresholds (persistence 0.7, absent-area 2%, ΔBIC 2, SNR 5×,
  0.5×FWHM separation) are UNVERIFIED tunables per spec §9 — carried over as-is, flagged
  in code.
- Spec §9 constants adopted with their recorded verdicts (C 1s β=0.05 eV VERIFIED
  Campbell & Papp; graphite 284.4 VERIFIED; adventitious 284.8 CONDITIONAL; U 4f
  Δso 10.9 / ratio 0.75 VERIFIED Ilton & Bagus; Cl 2p 1.60/0.5 CONDITIONAL; h-BN N 1s
  UNVERIFIED).

---

## Recon findings (2026-07-02)

### Repos / code
- **fitalg engine** (`xps-app-fitalg/model_comparison.py`, 2471 LOC, cloned to scratchpad):
  grammar slots (`ComponentSlot`, `CandidateModel`), C 1s A/B/M candidate families,
  fit → 20-refit stability → slot matching → absent-slot detection → residual-guided
  proposal pass (Iteration B, capped/timeout-guarded) → filter-then-rank with `BIC*`.
  Region-agnostic core; C 1s-specific grammar constants.
- **CRITICAL porting detail:** fitalg was written when `la_casaxps` in its fitting.py was
  what current main calls **`ds_g`** (DS core ⊗ Gaussian; params `alpha/beta/m_gauss`,
  β = Lorentzian HWHM eV, fixed 0.05 for C 1s). Current `la_casaxps` is the TRUE CasaXPS
  LA (params `alpha/beta/m` exponents + kernel-points) with a **different signature**.
  ⇒ Port maps fitalg `LineShape.LA_ASYMMETRIC` → backend `ds_g` to preserve the math.
  The U 4f module uses true `la_casaxps` (LACX), matching Skye's real U 4f fits.
- **Current `fitting.py`** (1209 LOC): 7 shapes, 6+manual backgrounds, `run_fit` =
  manual-fit path (do not touch), Poisson weights 1/√max(y,1), `_validate_constraint_graph`,
  spin-orbit via lmfit exprs (`constrain_to`/`splitting`/`area_ratio`).
- **Save/load (v3)**: `buildTabData` at `templates/index.html:8504` (fitResult whitelist
  8526–8537), load whitelist `_loadProjectJSON` 8827–8886, `_normalizePeaksCRef` 4540,
  zip version gate 8987 (`manifest.version !== 3` rejected), `.proj.json` <5 tabs else zip.
  Peak-level unknown fields survive both directions (spread-copy) — `_confidence` rides
  free; tab-level `analysis` key must be added to BOTH 8520-block and 8860-block.
- **Test harness**: pytest; 7 Playwright browser test files (self-skip without
  playwright/gunicorn/chromium; pattern: module-scoped gunicorn on free port +
  `page.evaluate`); node-native tests in `tests/js` (`node --test tests/js/*.test.js`).
  playwright 1.60 + pytest 9.0.3 in venv. lmfit 1.3.4, numpy 2.4.4, scipy 1.17.1.
- **Tiered reference system**: `data/xps/` (schema.json; curated/machine/legacy tiers;
  `sources.json`; machine tier = no-invention policy w/ provenance sidecar + sha256 +
  starred-NIST-record parse method; loader `xps_reference.py`; served at
  `/api/xps-reference`). Element-physics DB should extend THIS pattern.

### Data inventory (docs/autofit/test_data/, 8.4 MB)
Machine-readable: `docs/autofit/inventory/reference_fits_inventory.json`.

- **7 .proj.zip projects, 121 fitted spectra total.** All v3. Raw VGD .DATA dirs for
  5 sample sets + one no-kapton U set.
- **C 1s parity anchors** (best quality): `UCl4_on_graphite.proj.zip` (10 C 1s fits,
  χ²ᵣ 1.2–2.3), `Project9_CasaXPS_newfit.proj.zip` / `Cl2p_projfit_test.proj.zip`
  (7 C 1s each, χ²ᵣ 1.5–2.3). Expert C 1s model: **asym-GL graphitic ~284.5 +
  3×GL adventitious + GL π→π* satellite (+ occasional low-BE 'Unknown' GL)**, cc ≈ −4.7,
  graphite-referenced (ccLit 284.5).
- **U 4f anchors**: 40+ U 4f fits. Canonical (UCl4_on_graphite): LACX 4f7/2 379.54
  (caAlpha 1.075, caBeta 2.54, caM 8.2, fwhm 2.44) + linked LACX 4f5/2 (+10.9 eV,
  ratio 0.65) + 2 Voigt satellites at +6.4 eV (385.9) and +17.4 eV (396.97 — sits in
  N 1s territory, tagged rsf 'N 1s'). Matches spec §3.2 numbers exactly.
- **B 1s**: good exemplar `B4C-UCl4.proj.zip` (3 peaks GL+Gaussian, χ²ᵣ 1.4–2.5);
  known-rough `4-GTA UCl4-BN.proj.zip` B 1s = single asym-GL, χ²ᵣ 17–105358 (!) —
  treat as suspect reference, per goal instructions.
- **Cl 2p**: `Cl2p_projfit_test.proj.zip` — 2×GL (χ²ᵣ 2.85/4.94, the documented elevated-χ²
  case) + one 2×Voigt fit (cc=0, χ²ᵣ 1.83).
- **N 1s**: NOT present as a dedicated region scan in the fitted projects; N 1s signal
  appears inside U 4f windows (UCl4-BN 5-peak fits incl. asym-GL N-region peak) — the
  co-fit exemplar. Raw `3 BN-graphite ... .DATA` has N1s scans (unfitted).
- **RSF-tag bugs to lint** (goal mentioned 'Zr 3d' on a boron peak): confirmed stray tags
  seen so far: 'K 2p' on a C 1s π→π* satellite (1-GTA), 'N 1s' on a U 4f satellite
  (UCl4_on_graphite — may be intentional: that satellite sits at ~397 eV).
  Zr-3d-on-B1s to be confirmed when B 1s parity work starts.
- Standalone `U4f_5_Scan1_...fit.json`: `.fit.json` export (version 1) with
  `_backendParams` incl. bounds — useful for LACX param cross-checks.

### Tab JSON schema (observed, v3)
Top-level: `id,name,color,isSurvey,rawBE,rawIntensity,ccShift,chargeVerified,peaks,nextId,
fitResult{chi,chiReduced,rmse,fittedY,be,bgIntensity,bgSubtracted,roiRange},notes,
manualAnchors,lineWidth,ui{bgType,bgStart,bgEnd,shirleyIter,endpointAvg,roiMin,roiMax,
ccMethod,ccObs,ccLit,bgSubtractedView}`.

### Decisions made
- Bg for parity/battery fits comes from each tab's persisted `ui.bgType` (observed:
  'smart' on U 4f anchors) — reproduce with `fitting.py` equivalents.
- New engine lives in a new `autofit/` package; tests in `tests/autofit/`;
  nothing imports it from the existing request path (strictly additive).

## Parity-gate calibration log (2026-07-03)

Iterating the C 1s gate on 3 real anchors exposed four issues; each fix is a
documented methodological decision (Codex should adversarially review all):

1. **Satellite FWHM cap recalibrated** (1.0,3.0)→(1.0,5.5): fitalg UNVERIFIED
   tunable; 44 labeled expert fits span 1.9–5.0 eV (median 4.17, both
   analysts). With 3.0, every candidate pegged `satellite_pi:fwhm@max` → zero
   survivors on all anchors.
2. **Lab-practice contamination width range** (0.8,3.5) for AG/MG families
   only (labeled set: median 2.08, 70% >1.6); A/M/B keep the Biesinger
   (0.8,1.6) convention so model comparison arbitrates. Discrepancy #5.
3. **Best-minimum promotion** (engine improvement over fitalg): the report
   now uses the best converged fit found across primary + stability refits,
   not unconditionally the primary. Before: two anchors reported graphitic
   main exactly at the 284.400 init (window midpoint) while refits had found
   deeper minima; after: Scan_6 main lands 284.512 (Δ12 meV vs expert 284.50).
4. **Two-tier rank_and_filter** (departure from fitalg, documented in code):
   when NO candidate passes plausibility cleanly, stable-but-boundary-limited
   candidates are ranked as a CONDITIONAL tier (`conditional=True`, violations
   preserved and surfaced). fitalg's absolutist filter returned zero survivors
   on 2/3 real composite anchors — routine data, not pathology. Stability
   failures are never promoted.
5. **MG family added** (asym-GL graphitic + aliphatic + satellite +
   contaminants = the expert model's exact structure; χ²ᵣ 3.8–7.1 vs AG's
   31–94 on the anchors) with the aliphatic center OFFSET-LINKED to the
   graphitic main (+0.2…+0.6 eV) — a free aliphatic slides into the graphitic
   flank and pegs the window floor (overlap degeneracy, fitalg LIMITATIONS §9).

Engine winners vs expert (post-fix, reduced 4-candidate gate, n_refits=4):
main Δ 12–100 meV; satellite Δ 0.2–0.3 eV; envelope R-factor (≥284 eV domain)
0.014–0.053. The low-BE 'Unknown' (~283.4) is intentionally out of gate scope
(proposal-pass territory, discrepancy #6).

## Stage-3 design cautions (carry into U 4f implementation)

- **Linked-pair absent-slot atomicity**: today only non-main slots are
  absent-eligible and every linked child references a main, so a parent can
  never be absent while its child is emitted. The U 4f satellite DOUBLET
  (sat5/2 linked to sat7/2) breaks that invariant — the module must either
  make the pair's absent classification atomic or make the engine treat
  linked groups as one absent/present unit.

### Stage 3 (U 4f) review (2026-07-03) — **VERDICT: GO**
No blockers; "core Stage 3 model decision" explicitly confirmed sound.
Findings + dispositions (all fixed same-session):
1. **MAJOR** U1-vs-U2 satellite-separation conclusion confounded (U2 frees
   shape AND offset) — ACCEPTED, fixed: added `U1b` (free pair separation,
   shape+amplitude still tied). Clean result: U1→U1b ΔBIC* = −55.7 from
   separation freedom alone; finding stands.
2. **MAJOR** absent-slot area normalized against ALL mains in a joint model
   (BN N 1s dilutes U satellites) — ACCEPTED, fixed: normalization scoped to
   the slot's own (region, phase) mains, global fallback; pinned by test.
3. **MAJOR** co-fit U-main tolerance 0.5 eV too broad — ACCEPTED, fixed:
   measured seed envelope (5 seeds, same winner, ≤39 meV from expert) →
   0.3 eV documented-envelope gate.
4. **MINOR** U4f EVAL_TOL 3e-2 loose vs measured drift — fixed: measured all
   29 fits (median 6.0e-3, max 1.12e-2) → 1.5e-2.
5. **MINOR** satellite fallback windows uncited — fixed: now DERIVED from
   the cited/flagged constants.

### Cookbook re-check (2026-07-03) — **NO-GO → all findings fixed (2nd round)**
The re-check (archived `docs/autofit/codex/stage4_cookbook_verdict2.md`)
found 2 blockers + 3 majors + 1 minor IN MY OVERRIDE IMPLEMENTATION, all
verified real and fixed:
1. **BLOCKER** stale absent-slot adjustment on bound-fixed refits — fixed:
   refits carry NO absent-slot adjustment (conservative full-k BIC*).
2. **BLOCKER** refit could peg a NEW bound and still be treated as decisive
   — fixed: fresh boundary hits → no promotion (interior optimum required);
   gate asserts `winner_boundary_hits == []`.
3. **MAJOR** inherited stability — fixed: fresh stability pass runs on the
   bound-fixed model (constrained params stay fixed in every multi-start
   refit via `run_stability_analysis(fixed_param_values=…)`), with an
   active-persistence requirement before promotion.
4. **MAJOR** provenance region-wide + returned by reference — fixed:
   deep-copied; scope explicitly labeled `region-wide`; per-candidate
   provenance logged as FUTURE WORK.
5. **MAJOR** only the best free-BIC candidate tried — fixed: up to 3
   conditional candidates attempted in BIC* order.
6. **MINOR** gate missing fresh-peg/dominance-margin assertions — fixed.

### Cookbook review (2026-07-03) — **VERDICT: NO-GO → all findings fixed**
3 blockers + 4 majors + 1 minor (verdict archived at
`docs/autofit/codex/stage4_cookbook_verdict.md`). Dispositions:
1. **BLOCKER** CONDITIONAL provenance comments-only, runtime-invisible —
   ACCEPTED, fixed: region modules now expose machine-readable
   `provenance()` ({constant, value, status, source}); flows through
   `resolve()` into the analysis namespace with a
   `uses_conditional_or_unverified_constants` rollup.
2. **BLOCKER** decisive override made BIC* a hard decision rule — ACCEPTED,
   reworked into a DOMINANCE rule: fires only when the boundary-limited
   candidate is refit with pegged params FIXED at bounds (see 3), beats the
   clean best on BIC* (>10) AND χ²ᵣ, and the clean best itself shows
   residual-structure flags (spec trust order: residual evidence above
   BIC*). Clean survivors kept as ranked alternatives.
3. **BLOCKER** boundary-pegged winner invalidates interior-Laplace BIC* —
   ACCEPTED, fixed: `_bound_fixed_refit` refits with pegged parameters
   fixed at their bounds (honest k) before any comparison; the refit
   (name+`+bfix`, `boundary_fixed_params` recorded) is what gets promoted.
4. **MAJOR** override promoted the whole conditional pool — fixed: only the
   dominating refit candidate is promoted.
5. **MAJOR** misleading conditional message — fixed: `conditional_reason`
   enum (`no_clean_survivor` | `decisive_override`) in result + analysis.
6. **MAJOR** tautological Cl 2p gate — fixed: gate pins the known anchor
   result directly (relaxed+bfix winner, conditional, ratio fixed at 0.55,
   fixed-vs-relaxed evidence, provenance visibility).
7. **MAJOR** B 1s knife-edge 187.9 boundary — fixed: windows overlap
   0.2 eV so the nearest-center rule owns the ambiguity band; role-swap
   detection for symmetric overlapping components logged as FUTURE WORK.
8. **MINOR** discrepancy numbering — fixed (#8 for the B-assignment
   conflict).

## Stage-3 U 4f results (2026-07-03)

- **Single-region parity (good anchors)**: engine winner = mains + free
  satellite pair; main Δ 2–14 meV, satellite Δ 0.01–0.02 eV, splitting
  10.85, ratio 0.640–0.656 — and the engine's χ²ᵣ BEATS the expert fits
  (1.40 vs 1.71 on B4C-UCl4; 1.42 vs 2.00 on UCl4-graphite).
- **Physics finding — satellite pair separation ≈ 11.2 eV ≠ Δso 10.90**
  (cleanly isolated post-Codex via the U1b candidate): freeing ONLY the
  pair separation (shape+amplitude still tied) improves BIC* by 55.7
  (χ²ᵣ 1.98→1.68) and fits the separation at 11.20 eV; expert satellite
  fits agree (11.21 eV in B4C-UCl4). Shake-up separations need not track
  the core splitting — worth Skye's eyes.
- **Second satellite observation**: the satellite pair's amplitude ratio is
  ~0.91 (B4C expert fit 2436/2214), NOT the core doublet's 0.75 — U1b pegs
  its ratio bound (0.85) on that account and the fully-free U2 wins. Both
  the separation AND the intensity ratio of the shake-up pair decouple from
  the core doublet. U2 (independent satellites) is the physically safer
  default; logged for adjudication.
- **Co-fit (4-GTA UCl4-BN, U 4f + N 1s joint)**: winner
  `U2_mains_satfree+N0_asymGL`, χ²ᵣ 7.1 vs expert 11.4 (rough reference).
  N 1s at 398.28 (phase BN, no leakage). DISCREPANCY vs expert (logged, not
  forced): the engine gives the U 4f5/2 satellite more weight in the
  N-overlap zone (amp ~8.5k at 398.1 vs expert 1.2k at 397.8) and narrower
  U mains (fwhm 1.7 vs 2.5) — multiple near-equal minima in the overlap;
  winner params vary at the few-hundred-meV level with run-order FP wobble.
  Exactly the identifiability situation the confidence machinery is for;
  needs human adjudication of the rough reference.
- **Numerical stability findings** (documented in battery_common.py):
  LACX fits reproduce exactly in-process but wobble ~1e-5–1e-4 relative
  across processes (worst: a flat α/β/m valley tab at 1.4e-4); U 4f
  batteries use fixture rtol 1e-3. Eval-parity vs saved fittedY is bounded
  ~1e-2 by bg-anchor drift (ui bg fields moved by post-fit cc nudges;
  'smart' background amplifies ±1-point anchor shifts to O(100 counts)).

## U 4f design extraction (for Stage 3; from expert fits 2026-07-03)

Canonical structure across all 3 U 4f projects (UCl4-graphite, UCl4-BN, B4C-UCl4):
- **Main doublet**: LACX 4f7/2 (free) + 4f5/2 linked at **Δso = +10.90 eV exactly**,
  ratio 0.65 (graphite, B4C) / 0.75 (BN). Spec default 0.75 theoretical with bounded
  relaxation — expert data spans [0.65, 0.75].
- **LACX params** (main): caAlpha 0.96–1.24, caBeta 2.23–2.85, caM 0–8.2 (points),
  fwhm 2.44–2.74 eV. All free ("FitAllFree").
- **Satellite pair**: Voigt sat at main+6.1–6.4 eV; second satellite at main+17.2–17.4
  = sat + 10.9 → **satellites form their own Δso doublet** (4-GTA explicitly links
  sat5/2 = sat7/2 + 10.9, ratio 0.75, shared fwhm). One shake-up pair explains both
  observed satellites.
- **Co-fit exemplar** (4-GTA UCl4-BN): N 1s asym-GL at 398.30 (amp 105,851 —
  ~67× the U satellite at 397.78) inside the U 4f window: THE joint-fit case.
- U4f battery eligibility: UCl4_on_graphite 6/10, 4-GTA 3/10, B4C-UCl4 10/10.
- NOTE the 'N 1s' `_rsfKey` on Sat2 in UCl4_on_graphite/B4C (quantification-lint
  candidates; sat2 sits ~397–398 eV so the tag may be deliberate on some).

## Next actions
1. Commit unit 0 (docs + data + inventory + this file), push with `-u`.
2. C 1s characterization battery (Task-1): parity harness reading the inventory,
   refitting with `run_fit` from saved peak specs, asserting reproduction within
   tolerance.
