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
| C 1s characterization battery + parity net | TODO | — | |
| Schema round-trip (`analysis` ns + `_confidence`) | TODO | — | |
| Resolver skeleton + PeakFitMethod seam | TODO | — | |
| C 1s parity gate | TODO | — | |
| Codex checkpoint: Stage 2 | TODO | — | |
| U 4f module | TODO | — | |
| B 1s / N 1s / Cl 2p cookbook | TODO | — | |
| Bayesian exchange-MC method | TODO | — | |
| Element-physics DB | TODO | — | |

## Codex checkpoint verdicts

*(none yet)*

## Discrepancies vs expert reference fits (for human adjudication)

*(none logged yet — see Data notes below for known-rough fits)*

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

## Next actions
1. Commit unit 0 (docs + data + inventory + this file), push with `-u`.
2. C 1s characterization battery (Task-1): parity harness reading the inventory,
   refitting with `run_fit` from saved peak specs, asserting reproduction within
   tolerance.
