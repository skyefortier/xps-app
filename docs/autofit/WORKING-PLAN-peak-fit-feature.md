# Working Plan & Scope Anchor — XPS Peak-Fit Feature

*Living doc. Check it at the start of each session. Anything that doesn't serve the North Star goes to **Parked** — that's the context-creep catcher.*

---

## ★ North Star (the goal)
Build the **Peak Fit "method" feature**: a user-selectable menu of *mathematical treatments* for decomposing an XPS spectrum into component peaks — scXRD-style (choose the method, set its parameters, solve). **Get the feature and its math correct**, using the Fable 5 window. Ship to production via the staged plan.

---

## In scope
- The **method dropdown** and its treatments (see `peak-fit-methods-decision-matrix.md`).
- The **math** behind each treatment, and the noise model (empirical, from repeat sweeps — data is processed, not raw counts).
- **Element/material-aware lineshape physics** — the algorithm must encode *why* a peak has its shape: uranium → intrinsic multiplet asymmetry (LA envelope + modeled satellites); metals → metallic-screening asymmetry (Doniach-Šunjić); insulators → symmetric + charge correction. This is the material×element layer (spec §2–3).
- **Multiple, overlapping element-regions per window.** The element/region input is *multi-valued* — more than one element can occupy a window (e.g. in U-in-BN the U 4f satellites overlap N 1s ~398 eV, and N 1s overshadows a U 4f satellite). The engine composes multiple element grammars and fits them **jointly**, with overlap handling. "Region" is never assumed to be a single element.
- Per-peak **confidence**; **multi-phase** samples; **C 1s + U 4f** as exemplars.
- **Staged delivery**, opt-in, Codex-gated.

## ⛔ Parked / Out of scope (context-creep catcher)
- **Oxidation-state determination / assignment** (satellite→state diagnostics). Real topic, *not* our goal. Satellites still get **modeled as peaks**; interpreting them is downstream. → parked 2026-07-02.
- **Frontend overhaul** (campaign Phase 2). Later.
- **Production UI / hour→interactive perf**. Later gate.
- **Auto material detection**. Designed-in, deferred.
- Cross-validation, RJMCMC, nested sampling as fit methods. Deferred (unproven on XPS).

---

## Decisions locked
- **Staged scope (Codex GO):** Stage 1 constants/stats audit → Stage 2 resolver + C 1s parity + schema round-trip → Stage 3 U 4f. Production UI is a later gate.
- **U 4f = LA asymmetric main lines + explicitly modeled satellites, one fit.** No oxidation-state machinery, no forced multiplet decomposition.
- **Composable grammar:** material class × element/region × oxidation-state; **multi-phase `phases[]`** with per-slot `phase_id`; phase disambiguation required when a region spans phases.
- **Confidence:** separate `σ_stat` and `reference_sensitivity_range` (no quadrature); typed `uncertainty_kind`; empirical detection floor.
- **Model selection:** `BIC*` is a heuristic tie-breaker; the criteria panel is a *diagnostic* ("not independent tests"); trust order = parity → stability/persistence → residual → BIC*.
- **Method menu (ranked value-vs-effort):** least-squares → IC/model-comparison → **Bayesian exchange-MC (flagship, new math)** → sparse/MAP → multivariate (multi-spectrum) → max-entropy.
- **Schema:** stay on v3; per-peak fields ride the peak-spread channel; candidate-set data needs a whitelisted `analysis` key (build-and-test in Stage 2); human decisions stored durably.

## Major Fable deliverables (big, high-leverage)
- **Comprehensive element-physics reference database** — *Skye's call: Fable builds it broadly, NOT per-element as-needed.* Cover **as many elements / core levels as authoritative XPS data exists** — this is what makes the feature broadly usable for external users, not just Fortier-Lab elements. Per entry: lineshape family (symmetric / DS-metallic / multiplet-asymmetric), spin-orbit splitting + area ratio, satellite structure, core-hole width β, BE windows. **Extends the app's existing tiered periodic-table reference system.**
  - **Non-negotiable — provenance discipline (reuse the existing anti-confabulation tier system):** every value tiered and sourced (NIST SRD 20, primary literature); **machine-generated entries flagged unverified-until-reviewed**; Codex/NIST-adjudicated; no confabulated constants. A comprehensive DB is only an asset if honestly sourced — a confidently-wrong element entry is worse than a missing one.
  - C 1s + U 4f are the **validated pattern/exemplars**; Fable then scales the pattern across the periodic table under the same verification gate.
- **Joint multi-element overlap fitting** (see In scope) — compose and co-fit overlapping element grammars (e.g. U 4f + N 1s).

## Open threads (next actions)
1. Fold the **`PeakFitMethod` selector** into spec v2.1 (methods 1–2 in Stage 2; Bayesian as window flagship).
2. Simplify the spec **U 4f section** to "asymmetric mains + modeled satellites, one fit."
3. Add **multi-element overlap** + **element-physics DB** as design requirements in the spec.
4. Then: **Stage 2 kickoff prompt** for Fable (resolver + C 1s parity + schema round-trip).

---

## Artifacts (where things live)
- `WORKING-PLAN-peak-fit-feature.md` — **this file** (scope anchor)
- `fable5-xps-campaign-brief.md` — overall campaign
- `phase1-grammar-architecture-spec-v2.md` — build spec (v2.1)
- `peak-fit-methods-decision-matrix.md` — the treatment menu + literature
- `spec-addendum-model-selection.md` — pluralistic-criteria detail
- `codex-reconciliation.md` — Codex review dispositions
- `codex-rereview-PASTE-THIS.md` — Codex re-review prompt (paste-ready)
