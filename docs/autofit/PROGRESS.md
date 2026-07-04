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
| Baseline test suite | DONE | ✅ | **123 passed, 1 pre-existing failure**: `test_machine_tier.py::test_deterministic_reproducible_from_stage9` (`.stage9` regeneration check, SystemExit in `scripts/gen_machine_tier.py:193`; unrelated to fitting; present before any autofit work). "Green" = no NEW failures beyond this. **UPDATE 2026-07-03 late session: this failure is FIXED** — the missing `.stage9/extract_claude/*_nist.html` artifacts were re-fetched from their committed provenance URLs (27 sha256-verified exact; the rest verified by byte-identical regeneration). The suite is now fully green. |
| C 1s characterization battery + parity net | DONE | ✅ 59 tests | `tests/autofit/test_c1s_parity_battery.py`: 29 expert C 1s fits frozen (eval parity ≤1.2e-7; refit drift ≤2e-4 eV; fixture rtol 1e-6). 15 tabs excluded w/ reasons (legacy no-`be`; 1 internally inconsistent). Regenerate fixture ONLY via `scripts/gen_c1s_battery_fixture.py` after reviewed numerics changes. |
| Schema round-trip (`analysis` ns + `_confidence`) | DONE | ✅ 3 browser tests | `analysis` whitelisted in buildTabData + load (v3 kept, omitted-when-absent); `_confidence` proven on the peak-spread channel; save→load→save deep-diff on both formats; pre-engine saves load clean. |
| Resolver skeleton + PeakFitMethod seam | DONE | ✅ 18 tests | `autofit/`: grammar.py (phases[], phase disambiguation mandatory, leakage guards, joint co-fit composition), engine.py (fitalg port, region-agnostic; fitalg LA→`ds_g`), regions/c1s.py (A/AG/M/B families), criteria.py, confidence.py, methods/ (LS + IC implemented; bayesian/sparse/multivariate/maxent stubs). |
| C 1s parity gate | **PROVEN** | ✅ 3/3 anchors | `tests/autofit/test_c1s_parity_gate.py` (env-gated: `RUN_AUTOFIT_GATE=1`, ~4 min): main Δ 4–12 meV, satellite Δ 0.08–0.29 eV, domain envelope R 0.004–0.014 vs expert fits. Winners: MG3/MG2 (conditional tier, violations surfaced) + AG2 (clean) — see calibration log. |
| Codex checkpoint: Stage 2 | DONE* | review #1 ✅ / re-review HUNG | Review #1: NO-GO w/ 9 findings → all fixed + test-pinned (`2669ed9`). Re-review hung (known issue) → killed, logged, proceeded per rails. Monday re-runs `docs/autofit/codex/stage2_rereview_prompt.txt`. |
| Stage 3: U 4f module | **DONE** | ✅ 62 tests | `regions/u4f.py` (LACX main doublet w/ shared α/β/m + bounded-asymmetry safeguard; explicit satellite doublet + free variant; NIST/Ilton-Bagus-cited constants) + minimal `regions/n1s.py` (co-fit partner). Engine prereqs: `share_parent_params`, linked-chain topological param ordering, linked-group absent-slot atomicity. U 4f manual-path battery (29 expert fits frozen) + engine parity gate incl. **U 4f + N 1s co-fit** (in normal suite, ~20 s). |
| Codex checkpoint: Stage 3 (U 4f) | DONE | **GO** ✅ | 3 majors + 2 minors, all fixed same-session (see verdict section). Verdict + prompt in `docs/autofit/codex/`. |
| U 4f module | TODO | — | |
| B 1s / N 1s / Cl 2p cookbook | DONE | ✅ 21 tests | `regions/b1s.py` (position-neutral roles per discrepancy #8; good-exemplar windows; component ladder) + `regions/cl2p.py` (doublet, Δso/ratio CONDITIONAL-cited, fixed + relaxed variants) + minimal `n1s.py` (validated by the U 4f co-fit gate). Batteries (B 1s ×4, Cl 2p ×3) + engine gates: B 1s 3-component winner beats expert (χ²ᵣ 1.26 vs 1.43); Cl 2p relaxed-ratio CONDITIONAL winner beats expert on both anchors (discrepancy #7). Engine: `smart_exp` bg + decisive-override rule (ΔBIC*>10, Kass & Raftery 1995) for the conditional tier. |
| Bayesian exchange-MC method | DONE + REAL-DATA VALIDATED | ✅ 11 tests + 2 env gates | `methods/bayesian_exchange_mc.py`: replica-exchange + stepping-stone Bayes free energy; σ-marginalized Gaussian likelihood; priors = grammar bounds; typed `posterior_ci` intervals. Codex math review COMPLETED (core math confirmed; 5 honesty findings fixed — see verdict section): split-half F error bars, UNRESOLVED-selection warning, per-slot CI reliability, stuck-chain ESS, analytic Student-t evidence pin, `seed_replicates` independent-replicate errors. REAL-DATA validation (`scripts/run_bayesian_real_validation.py` + JSONL + `docs/autofit/bayesian-real-validation.md`): Cl 2p + B 1s — cross-method winner agreement with IC at every seed/tunable setting (ΔF 47 / 113–148); U 4f — honestly UNRESOLVED at default budget (seed flip, flagged by replication; env gate pins it) and RESOLVED to U2 at 16 replicas/4000 sweeps (ΔF 28.2), agreeing with IC's ΔBIC*=59. Tuning evidence: replicas drive ESS more than sweeps; LACX-scale regions need the tuned budget. |
| Sensitivity sweeps (spec §9) | DONE | ✅ 86 runs | `scripts/run_sensitivity_sweeps.py` + JSONL + `docs/autofit/sensitivity-sweeps.md`. ONLY the Cl 2p ratio cap changes any conclusion (see Sensitivity section); all pipeline thresholds insensitive on the anchors; flags kept (insensitivity ≠ verification). |
| Element-physics DB | **BROAD COVERAGE DONE** | ✅ 17+5 tests | Full-periodic-table NIST-archive sweep (committed pipeline `scripts/acquire_nist_archive.py`, resumable manifest): all 103 elements probed; **52 with usable archived SRD-20 snapshots + starred values, 51 honest failures** (no snapshot / no NIST-evaluated line — incl. the whole aspx-only + actinide tail; see format finding). Machine tier now **78 transitions / 51 elements** (was 45/37): +33 new (lanthanide 4d family, heavy-metal 4d5/2, 3d/3p secondaries, new elements Rh + Pr + Mg), every one an archived starred value, sha256-pinned, **33/33 independently agent-cross-checked (own parser, exact agreement)**; subshell-level guards prevent any curated/tiers overlap (27+10 guard skips logged); 337-entry skip audit. `fit-physics.json` regenerated: **98 transitions** (14 sourced spin-orbit, statistical 2j+1 ratios caveated). Byte-identical regeneration test GREEN (the old baseline failure is FIXED — artifacts restored sha256-verified from committed provenance). Still NOT wired into the engine (regions keep their own cited constants; deliberate). Per-value review table: `docs/autofit/fit-physics-coverage-report.md`. |

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

### Stage 2 re-review #3 (2026-07-03 late session) — **COMPLETED: VERDICT GO**
Re-run under `gtimeout -k 15 600` (the run rails' hard 10-min kill) in a
fresh session — completed in ~7 min, no hang. Verdict archived at
`docs/autofit/codex/stage2_rereview_verdict.md`. Items 1–8 of review #1
confirmed closed; item 9 partially (panel threshold, below). 4 new findings,
ALL fixed same-session and pinned in
`tests/autofit/test_stage2_rereview_findings.py`:
1. **MAJOR** criteria panel built with the default 2.0 ambiguity threshold,
   not the method option — fixed: threshold recorded on `ComparisonResult`
   and reused by `build_criteria_panel` (panel can never disagree with the
   ranking again).
2. **MAJOR** sanitized role slugs could collide (`B-4C` vs `B4C` → one
   param namespace) — fixed: loud `ValueError` at resolve time; distinct
   sanitized slugs still resolve.
3. **MAJOR** `orphan_peaks` recorded but ignored in ranking and dropped
   from the payload — fixed: orphaned reports are plausibility violations
   (conditional tier at best, never clean survivors); full plausibility
   surface (`unphysical_widths`, `orphan_peaks`) now in the per-candidate
   payload.
4. **MAJOR residual risk** best-minimum promotion could report a one-off
   deeper minimum indistinguishably from a reproducible one — surfaced:
   `best_basin_support` (count of multi-start fits within
   `BASIN_SUPPORT_RTOL` of the best χ²; UNVERIFIED reporting-only constant)
   on stability + `best_minimum_basin_support` in the payload. Ranking
   unchanged (documented decision: report the best minimum FOUND;
   promotion-vs-robustness is Skye's call, see calibration log #3).

## NIST-archive format finding (coverage sweep, 2026-07-03)

The retired SRD-20 site has TWO archived page generations: the 2004
`query_all_dat_el.asp` tables (parsed by the committed
`parse_nist_html`; carries the `<b>*</b>` NIST-evaluated marker) and the
2015/16 `query_all_dat_el.aspx` ASP.NET GridView pages. The 2016 format
(inspected: N) **does not display the evaluated-value star at all**, and the
committed parser reads 0 records from it — so aspx-only elements are
honestly skip-logged as "no NIST-evaluated value" rather than recoverable.
Consequence: a GridView parser extension would recover *records* but not
*evaluated markers*, i.e. nothing emittable under the starred-only
no-invention rule. Do not "fix" this by parsing aspx pages unless a way to
recover the evaluation flag is found. (Nuance: the N tiers-path skip
detail says "no starred value" where "page format yields no parseable
records" is the deeper cause — same outcome either way.)

## Codex checkpoint: element-physics DB (Stage 6, 2026-07-03 late) — **NO-GO → all findings fixed**

Verdict archived: `docs/autofit/codex/stage6_element_db_verdict.md`. Codex's
own inline audit found **zero data problems** ("all 78 provenance records had
local artifacts, matching SHA, a nominal value found by the committed parser,
and an independent `<b>*</b>` parse; no multiple-star ambiguity; build()
regenerated byte-identical JSON") — the blockers were TEST-coverage gaps,
all fixed same-session:
1. **BLOCKER** independent artifact oracle only covered the original 18
   expansion records — fixed: the oracle now derives the acquisition set
   from provenance and runs the independent raw-HTML starred parse + agent
   cross-check + sha check on ALL 51 (`test_expand_coverage.py`), with a
   coverage-count pin so it can never lag a future expansion again.
2. **BLOCKER** machine-internal subshell overlap unpinned — fixed:
   `test_machine_tier_no_internal_subshell_overlap` (bare '3p' can never
   coexist with a tiers-driven '3p3/2').
3. **MAJOR** loose provenance pattern checks — fixed: strict archive-URL
   regex (14-digit snapshot id_, srdata.nist.gov query, element match),
   URL-timestamp == recorded timestamp, artifact bytes re-hashed against
   the recorded sha256, for every acquisition record.

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

## Sensitivity sweeps — spec-§9 evidence (2026-07-03 late session)

Harness `scripts/run_sensitivity_sweeps.py` (resumable JSONL:
`docs/autofit/inventory/sensitivity_sweeps.jsonl`, 86 runs; report
`docs/autofit/sensitivity-sweeps.md`). OFAT around defaults, IC at gate
options, on the real anchors (Cl 2p ×2, B 1s, U 4f cheap; C 1s Scan_8 for
the proposal/α-cap constants):

- **Insensitive on every anchor** (winner AND conditional status invariant):
  persistence 0.5–0.9, absent-slot persistence 0.5/0.9, absent-slot area
  0.01–0.08, ΔBIC* ambiguity 1–4, noise floor 0.5–5 ('detection floor'
  knob), decisive-override ΔBIC* 5–30, proposal flag ratio 3/8 (proposal
  pass ON), graphitic DS α cap 0.2/0.5. **Flags KEPT** — insensitivity on
  4 anchors is evidence for the defaults, not literature verification.
- **SENSITIVE — Cl 2p ratio cap (CONDITIONAL constant, discrepancy #7)**:
  raising `CL2P_RATIO_RANGE` upper 0.55→0.65+ turns both corrected anchors
  CLEAN (interior optimum, no +bfix): fitted 2p1/2:2p3/2 amp ratio
  **0.611**, splitting 1.585 eV, χ²ᵣ 1.286 vs 1.614 at the 0.55 cap
  (Cl2p Scan; Scan_0 same pattern). The prior CONDITIONAL status was a
  **cap artifact**. 0.611 vs the statistical 0.5 still says unmodeled
  structure/second species — the constants stay CONDITIONAL; the
  adjudication question sharpens to "why 0.61" rather than "why pegged".
- **Insensitive** — Δso widening (1.55,1.65)→(1.50,1.70): splitting stays
  1.585–1.599 eV on both anchors; the 1.60 eV CONDITIONAL constant is
  well-supported by the data (still CONDITIONAL pending primary-lit cite).

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

### U 4f Bayesian resolution at tuned budget (2026-07-03 late session)
At the default sampler budget the U1b/U2 comparison is seed-noise
(UNRESOLVED, flagged); at **16 replicas / 4000 sweeps** (20 min) the
evidence RESOLVES: **U2 wins by ΔF = 28.2** (F 2772.9 vs U1b 2801.1;
U2's F dropped 2806→2773 as deeper mixing found its evidence; min ESS
3→7–20). This restores cross-method agreement with IC (ΔBIC* = 59 for U2)
and matches the Stage-3 physics conclusion (independent satellites, the
physically-safer default). Record:
`docs/autofit/inventory/bayesian_u4f_tuned_run.jsonl`. Bonus determinism
demo: two independent processes reproduced U4f seed-0 F to 4 decimals
(2803.1533) — the benign duplicate row in the battery JSONL.

### Cross-method real-data demo (2026-07-03) — Bayesian vs IC on Cl 2p
Ran `bayesian_exchange_mc` on the real `Cl2p Scan` anchor (12 replicas,
2000 sweeps, 33 s): winner `Cl0r_doublet_relaxed` by **ΔF = 47.8**
(posterior weight ~1.0), with the ratio posterior PILED AGAINST the 0.55
prior bound (median 0.5494, CI68 [0.5485, 0.5498]) and the ESS honesty
warning firing (min ESS 17.7 — boundary-piled chain, exactly the intended
behavior). **Two independent treatments — IC decisive-override and Bayesian
free energy — reach the same physics conclusion**: the Cl 2p intensity
ratio wants > 0.55 on this data (discrepancy #7). Doublet params agree
across methods (2p3/2 197.90/197.93, fwhm 1.63/1.67, splitting 1.595/1.610).
σ̂ = 81 counts — consistent with unmodeled structure inflating the
effective noise. (Bayesian math still awaits its Codex review, below.)

### Bayesian method review (2026-07-03) — **CODEX HUNG (2nd hang), logged**
`codex exec` hung again (0.0% CPU, ~0.2 s total, no output — same signature
as the Stage-2 re-review hang). Killed per run rails. **Monday action:**
re-run `docs/autofit/codex/stage5_bayesian_review_prompt.txt` — it targets
the free-energy math specifically (prior-volume cancellation in ΔF,
stepping-stone bias, CI honesty, and a suggested analytic-evidence test).
The Bayesian method is validated ONLY against the synthetic ground-truth
battery so far; treat its real-data outputs as unreviewed until this
review runs.

### Bayesian math review (2026-07-03 late session) — **COMPLETED: NO-GO → all 5 findings fixed**
The hung review ran clean under the gtimeout rails (~7 min). Verdict
archived at `docs/autofit/codex/stage5_bayesian_verdict.md`. **The core
math was CONFIRMED correct** (σ-marginal likelihood; stepping-stone
validity for p_β ∝ RSS^(−βn/2); β=0 replica normalizes the prior volume so
differing parameter counts DO flow into ΔF correctly; exchange sign;
post-burn detailed balance; bounded-uniform target). The NO-GO was honesty
machinery, all fixed same-session:
1. **BLOCKER** F reported with no MC error bar → split-half stepping-stone
   error per candidate (`free_energy_split_half_error`, documented lower
   bound), UNRESOLVED-selection warning when top-2 ΔF < 2×(sum of errors),
   `posterior_weight_reliable` flags. Motivating real-data case: U 4f
   seed flip (seed 0: U1b F=2803.2 < U2 2806.3; seed 1: U2 2800.1 <
   U1b 2806.6) — ΔF ≈ 3 vs seed spread ≈ 5, silently before this.
2. **BLOCKER** CI overclaim under low ESS → per-slot
   `sigma_stat.reliability` (ok|low_ess|stuck_chain) + note + per-interval
   `ess` in the confidence payload itself.
3. **MAJOR** stuck chain → ESS=n → zero-variance sampled param now ESS=0
   (stuck_chain), never n.
4. **MAJOR** tests could pass with wrong evidence math →
   `test_analytic_evidence_flat_model`: estimator vs quadrature evidence
   (Student-t kernel) at two prior widths incl. the log 4 prior-volume
   Occam factor; passes at |ΔF| ≤ 0.3.
5. **MINOR** `free_energy_is_relative: true` + docstring (same-data
   comparisons only).

**Re-check #1** (same session, ~7 min): all 5 code dispositions verified
closed line-by-line (verdict `docs/autofit/codex/stage5_recheck_verdict.md`),
NO-GO retained on two artifact gaps, both then fixed:
- **BLOCKER** validation JSONL predated the machinery + no U 4f gate →
  battery fully regenerated under the fixed method (records carry
  selection_warning / split-half / posterior_weight_reliable / per-slot
  CI reliability), and a NEW env-gated real-data gate pins the motivating
  case (below).
- **MAJOR** sigma_stat contract + stuck-chain ESS unpinned → pinned
  (`test_sigma_stat_reliability_contract`,
  `test_zero_variance_ess_is_stuck_not_perfect`).

**Deeper finding while building the U 4f gate** — the split-half proxy alone
CAN miss the flip: at 800 sweeps seed 0 reports ΔF=12.3 with split-half
errors 0.5+3.9 (looks resolved, U1b) while seed 1 flips to U2 — proof the
documented lower bound really is one. Fix: **`seed_replicates` method
option** — independent seeded evidence replicates; F reported as the
replicate mean with `free_energy_replicates` / `free_energy_replicate_spread`
/ `free_energy_mc_error` (= max(split-half, replicate half-range)) feeding
the UNRESOLVED warning. `tests/autofit/test_bayesian_u4f_unresolved_gate.py`
(env-gated, ~4 min) pins on the REAL B4C-UCl4 U 4f anchor that replication
flags the U1b/U2 selection UNRESOLVED and marks posterior weights
unreliable. PASSED 2026-07-03.

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

## Monday handoff — what to do first
*(updated end of the 2026-07-03 late session — items 2–3 of the original
list are DONE: both hung Codex reviews re-ran under the gtimeout rails
[Stage-2 re-review GO, Stage-5 NO-GO→fixed]; the baseline machine-tier
failure is FIXED; the suite is fully green, 322 passed.)*
1. Read this file top to bottom; then `git log main..feature-autofit-stage2`
   (every unit self-contained and pushed).
2. Run the suite: `venv/bin/pytest tests/ -q` (**expect fully green**) and
   the slow gates:
   `RUN_AUTOFIT_GATE=1 venv/bin/pytest tests/autofit/test_c1s_parity_gate.py
   tests/autofit/test_bayesian_real_gate.py
   tests/autofit/test_bayesian_u4f_unresolved_gate.py`.
3. Adjudicate the **Discrepancies** section above (8 items — RSF mis-tags,
   width conventions, Cl 2p ratio [now sharpened by the sensitivity sweep:
   interior ratio 0.611], B 1s assignments, U 4f satellite physics).
4. Hand-verify the machine-tier values marked UNVERIFIED (the per-value
   review table is `docs/autofit/fit-physics-coverage-report.md`; every
   value links to a sha256-pinned archived NIST snapshot) → promote or
   reject before any production exposure.
5. Check the Stage-6 (element DB) and Stage-5 re-check #2 Codex verdicts
   in `docs/autofit/codex/` and this file's verdict sections.
6. Nothing merges to main or deploys until human review (run rail).

## Remaining work (deliberately not attempted in this window)
- Production `/api/analyze` + results/confidence UI (spec §0/§8: later gate).
- Wiring region modules to read fit-physics.json (they keep their own
  cited constants for now; migration should follow human review of the
  machine-tier values).
- Per-candidate (vs region-wide) constants provenance; role-swap detection
  for overlapping symmetric components (B 1s).
- Methods 4–6 (sparse/MAP, multivariate, max-entropy) — stubs unless the
  stretch unit below got to them.
- CI infrastructure so the required gates cannot silently skip.
- Hour→interactive performance work (deferred per the run brief).
