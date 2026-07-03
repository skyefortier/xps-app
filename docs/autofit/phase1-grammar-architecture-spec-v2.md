# Phase 1 — Grammar Architecture Spec **v2**

**Supersedes** `phase1-grammar-architecture-spec.md` (v1). **v2 incorporates the full Codex reconciliation** (`codex-reconciliation.md`): multi-phase model, verified schema fix, BIC\*-heuristic relabel, separated uncertainties, empirical detection floor, the U 4f resolution, and the staged scope. Changes from v1 are marked **[v2]**. **v2.1 incorporates the Codex re-review — GO for Stage 2 with two preconditions:** the `analysis` namespace reworded as a Stage 2 *build-and-test* task (not yet in code), a phase-disambiguation requirement, a mandatory U 4f minor-oxidation-state candidate, durable storage for human decisions, two distinct selection flags, and the criteria panel labeled diagnostic (not independent corroboration). Changes marked **[v2.1]**.
**Grounded in:** current `main` (`0dc2308`, re-verified serialization), the `xps-app-fitalg` design docs, and Skye's real v3 fits.

> **Stance (unchanged):** an evidence engine, not an oracle. Output is an *educated fit* — best-evidenced proposal(s) + honest uncertainty — for a chemically-knowledgeable human to adjudicate. **Every numeric constant is UNVERIFIED until lit-cited; §9 now carries Codex's independent verdicts.**

---

## 0. Scope **[v2 — staged]**

**This window delivers (and only this):**
1. **Stage 1 — Science + statistics audit.** Reconcile §9 constants; U 4f model **decided** (below); sensitivity-test every threshold. No app code.
2. **Stage 2 — Resolver skeleton + C 1s parity + schema round-trip.** Build `resolve(phases, region, oxstate)` and the multi-phase model; prove C 1s reproduces existing fits (parity gate); land the `analysis`-namespace round-trip test.
3. **Stage 3 — U 4f module**, per the decided model (§3.2).

**Explicitly a later gate, NOT this window:** production `/api/analyze`, the results UI, the confidence surface, and the hour→interactive perf work ship only once runtime and serialization are independently proven. The window's win is **proven foundations + a validated C 1s slice + a decided, implemented U 4f model** — the base that makes B 1s / N 1s / Cl 2p cheap afterward via the region cookbook (§7).

**Stage 2 preconditions [v2.1] (Codex GO conditions — both mandatory):** (1) the `analysis` serialization namespace must be **added and round-trip-tested**, not assumed to exist (§1); (2) `resolve()` must **require phase disambiguation** when a region appears in multiple phases (§2). No production UI, no U 4f module, and no publication claims in Stage 2.

---

## 1. The v3 project schema — verified serialization behavior **[v2]**

The engine consumes/emits the existing `.proj.zip` v3 format. **Serialization was re-verified on `0dc2308`** and is *not* freely additive:

- **Save (`buildTabData`) whitelists every field.** `fitResult` is written as exactly `{chi, chiReduced, rmse, fittedY, be, bgIntensity, bgSubtracted, roiRange}`. A `confidence_vector`/`diagnostics` placed *inside* `fitResult`, or a tab-level `candidates[]`, is **dropped at save**.
- **Load rebuilds tabs from a whitelist** — unknown top-level fields vanish on load.
- **`peaks` are spread-copied** (`p => ({...p})`) on **both** save and load — so **unknown *peak-level* fields survive** (this is how `_backendParams.stderr` already round-trips).
- **Version gate rejects `manifest.version !== 3`** — a v4 bump breaks the current loader outright.

**Consequence for the design (fix, replaces v1's naïve "additive" claim). Status [v2.1]: this is a Stage 2 build-and-test task, NOT done — Codex confirmed `0dc2308` has the peak-spread channel but *no* `analysis` key in save or load yet.**
1. **Per-peak confidence rides the peak-spread channel.** Store it as a peak-level field (e.g. `_confidence {…}`, mirroring `_backendParams`). It round-trips **today, zero migration** (verified: save spreads peaks at `index.html:8514`; load re-spreads via `_normalizePeaksCRef` at `8856`/`4533`).
2. **Candidate-set-level annotations** (`analysis: {candidates[], ambiguous_pairs, criteria_panel}`) require a **new whitelisted `analysis` key added to *both* `buildTabData` and the load whitelist, in the same release, staying on v3.** Do **not** bump to v4 (loader rejects ≠3 at `8976`).
3. **Older clients that predate the change silently drop `analysis` on resave** — acceptable *only because* `analysis` is regenerable from `peaks` + `fitResult`. **[v2.1] Any human decision — a `reviewed by ___` acknowledgment, an analyst's candidate choice or override — is NOT regenerable and must be stored in a durable channel** (the peak-spread field or a separately-protected key), **never** in the losable `analysis` namespace.
4. **Task #1 of Stage 2 is a schema round-trip test:** save → load → save → diff every intended field; fail the build on any silent loss.

Peak object, `fitResult`, and `manifest` shapes otherwise as documented in v1 §1.

---

## 2. The composable grammar — **multi-phase** **[v2, B1 fix]**

v1's pairwise `mixed{analyte, matrix}` **cannot** represent a 3-phase sample (BN/B4C/graphite) — three materials would fight over one reference/shift. Replaced with an explicit phase list.

```
resolve(phases, region, oxidation_state?) -> CandidateGrammar

phases: [ { id, class ∈ {conductor, semiconductor, insulator},
            role ∈ {analyte, matrix, phase},
            reference,            # per-phase charge reference
            shift_model } ]       # per-phase differential-charge shift
```

- **Single-phase** (the general-use default) = a `phases` list of length 1; no differential-charging machinery instantiated.
- **Composite** = length ≥ 2; the UI's `mixed` selection builds the list.
- **Every `ComponentSlot` carries `phase_id`.** A C 1s slot belongs to graphite, a B 1s slot to B4C or BN, an N 1s slot to BN — each resolves its lineshape family, reference, and shift from *its* phase, not a global one.
- **[v2.1] Region is no longer a unique key (Codex precondition 2).** When the same region appears in multiple phases (B 1s in *both* BN and B4C), `resolve(phases, region)` must return **phase-scoped slot families** or **require a target `phase_id`** — never a single ambiguous B-1s grammar. Guard explicitly against `phase_id` leakage between slots; this is the primary implementation risk of the multi-phase model.
- **[Skye] Multiple element-regions per window — co-fit.** The region input is *multi-valued*: more than one element can occupy a window (in U-in-BN the U 4f satellites overlap N 1s ~398 eV, N 1s overshadowing a satellite). `resolve` composes the several element grammars and the engine fits them **jointly** in the shared window, with overlap handling. "Region" ≠ one element.

**Layers (unchanged conceptually):** Layer A = material class → lineshape family + charge strategy + reference (now *per phase*); Layer B = region/element module (doublet Δso/ratio, BE windows, element β, allowed lineshapes, satellites); Layer C = oxidation-state override (multiplet fingerprint, BE shift). Data structures as v1 §2, with `phase_id` added to `ComponentSlot`.

---

## 3. Worked exemplars (real fits)

### 3.1 C 1s — the parity anchor
As v1 §3.1 (A/B/M families; LACX graphitic, pseudo-Voigt adventitious; β 0.05 eV; refs 284.4/284.8). **Stage 2 parity gate:** the resolver must reproduce existing C 1s fits within tolerance before anything else proceeds.

### 3.2 U 4f — **asymmetric LACX is a first-class chemical model** **[v2, B2 resolved]**
**Decision (Skye, domain expert):** U(IV) 5f² is an open-shell final state whose multiplet manifold is an **unknown number of closely-spaced, individually unresolvable lines**. Fitting them as N discrete peaks is under-determined; **the asymmetric lineshape is the physically-correct envelope of that manifold**, and the asymmetric tail is *caused by* the multiplet (not metallic screening). Asymmetric LACX is therefore an **admissible chemical model** for U(IV) 4f — **no "diagnostic-only" label**, and the engine does **not** force a multiplet-peak decomposition.

Real fit (UCl₄/graphite, ccShift −4.739): 4f₇/₂ LACX 379.54 / 4f₅/₂ LACX 390.44 (Δso 10.90) + two Voigt satellites; amp σ ~0.4%.

**Retained safeguard (the one valid kernel of Codex's objection):**
- **Bound the asymmetry parameters physically** (α within the lit range for U 4f, §9) so the tail cannot silently absorb a *resolvable* phase.
- **The residual/proposal pass runs on the tail region** and flags unexplained structure — "possible separable feature (2nd oxidation state / satellite / contamination) beyond the intrinsic manifold" — **without** forcing over-parameterization. This preserves honesty about the one thing an asymmetric tail *could* hide.
- Doublet: Δso ≈ 10.90 eV; theoretical 4f₇/₂:4f₅/₂ = 4:3 (0.75); fitted 0.65 is a **relaxed empirical ratio, not a contradiction** (Codex). Default 0.75, bounded relaxation.

**[Skye — simplified] Satellites and overlaps are modeled as peaks, one joint fit.** Confirmed against the literature: the U 4f asymmetry is multiplet/many-body in origin (not metallic screening), and an **LA-type asymmetric main line is documented best-fit practice**; the ~7–8 eV (and ~15 eV) satellites are **explicit components in the same fit**, not a separate step. **Oxidation-state *assignment* is out of scope (parked).** Two safeguards the engine keeps, reframed as general (not oxidation-state) logic: (i) **bound the asymmetry physically** (α within the U 4f lit range) so the tail cannot silently absorb a genuinely *separable* overlapping feature; (ii) the **residual/proposal pass flags unexplained tail structure** as a possible separate component for the analyst. Multi-element case: in U-in-BN, **N 1s (~398 eV) overlaps a U 4f satellite**, so the U 4f and N 1s grammars are composed and co-fit (§2).

### 3.3 B 1s — the weak exemplar
As v1 §3.3 (B₂O₃ 192.54 / B–C 189.41 / B–B 187.39; symmetric GL; σ 3–6%; the `Zr 3d` RSF is a confirmed bug → quantification lint, §8).

### 3.4 Cl 2p — the doublet exemplar
As v1 §3.4 (2p₃/₂ 197.92 / 2p₁/₂ 199.52; Δso 1.60; ratio 0.5; shared FWHM; `stderr = None` → missing-σ path, §5). Cl 2p Δso/ratio **conditional** until a chloride-source primary fit is cited (§9).

### 3.5 N 1s — the charge-reference exemplar
Same 3-phase sample, two analysts/references, **same fit + different rigid shift**: GTA (N-ref) N 1s 398.31 / ccShift −5.51; JT (C-ref) 397.47 / −4.67. Δcenter 0.84 eV = ΔccShift exactly; amplitude and σ identical → **isolates the systematic term** (§4/§5). h-BN N 1s value **UNVERIFIED** until a primary table is pulled (§9).

---

## 4. Charge-reference model **[v2 — per phase; separated uncertainty]**

- **Per-phase reference** (Layer A, resolved through each slot's `phase_id`): conductor → internal (graphite C 1s / Fermi); insulator → adventitious C or deposited standard; semiconductor → internal-if-present else adventitious.
- **Differential charging** in a composite is a **per-phase rigid shift** (`shift_model`), a fit parameter — never assumed away. Single-phase samples keep the current single-shift behavior.
- **Uncertainty is reported as two separate fields, never combined [M2 fix]:** `σ_stat` (statistical, from the fit) and **`reference_sensitivity_range`** (the corrected-BE spread across *admissible* references for that phase). The 2-analyst 0.84 eV swing populates the latter. **No quadrature** — a systematic reference envelope is not a Gaussian 1σ. If a UI rollup is required, use a conservative interval and label it.

---

## 5. Confidence model **[v2 — typed, empirical noise]**

Per-peak, per-parameter vector; each signal reported separately with its **kind**:

1. **Statistical σ** with **`uncertainty_kind ∈ {covariance, stability_mad, unavailable}` [M3 fix].** `covariance` = lmfit `_backendParams.stderr`; `stability_mad` = derived from the perturbation refits when stderr is `None`; `unavailable` otherwise. **Never mix kinds in one numeric field**; after reload, read persisted values, don't recompute silently.
2. **Stability / persistence** — refit survival fraction + BE MAD.
3. **Detectability / S-N [M4 fix]** — amplitude vs a noise σ estimated from the **repeat sweeps** (or residual bands after background robustness), **not** `1/√counts`. The `5×` floor is a **tunable validation parameter** calibrated on the labeled set, not a fixed constant. Below the floor → "present but poorly constrained" / "not confidently detected."
4. **Identifiability** — boundary hits; correlation / near-degeneracy with a neighbor.

**BE reporting:** `σ_stat` and `reference_sensitivity_range` side by side (§4). Rollup band is a labeled heuristic. **[v2.1] The UI must not expose a single sortable/filterable "confidence" band that implicitly recombines `σ_stat` and `reference_sensitivity_range`** — they sort and filter separately. Calibration target: on the labeled set, band order matches expert reliability (strong U 4f high; weak B 1s low; the 0.84-eV-shifted N 1s flagged for reference sensitivity).

---

## 5A. PeakFitMethod — the solver selector **[Skye]**

The user picks **material class + element/region(s)** (the *rules* — which lineshapes, BE windows, constraints; §2–3) and a **PeakFitMethod** (the *solver* — how the plausible peak set is found), with pre-filled, user-adjustable defaults. This is the scXRD-style method choice (Direct Methods / Patterson / charge-flipping → here: least-squares / model-comparison / Bayesian / …). The full menu, per-method parameters, and when-each-wins are in `peak-fit-methods-decision-matrix.md`.

- **Stage 2 ships:** (1) classical constrained least-squares (baseline, exists) and (2) grammar + information-criterion model comparison (§6).
- **Window flagship (new math):** **Bayesian exchange–Monte-Carlo** — posterior + peak-count + noise estimate in one pipeline; published for XPS (Nagata/Akai/Tokuda).
- **Later / cookbook-style:** sparse/MAP, multivariate (multi-spectrum), max-entropy. CV / RJMCMC / nested-sampling deferred (unproven on XPS).
- The **per-peak lineshape** (Gaussian/Voigt/DS/LA…) is a **separate, existing** control — the grammar assigns it automatically in the auto run; the user can override any peak afterward.

## 6. Model-comparison + selection **[v2 — BIC\* heuristic; pluralistic criteria]**

Pipeline (fitalg): enumerate → primary fit → stability pass → absent-slot detection → filter-then-rank → ambiguity flag → residual-guided proposal. Ported onto main `fitting.py`; perf work deferred to the later gate.

**BIC\* is a heuristic, not exact [M1 fix].** The absent-slot parameter subtraction is exact only at *zero* amplitude; the implemented threshold is `<2%` area, so it is an approximation that can hand a candidate "the fit quality of the larger model and the penalty of the smaller." Therefore: **label it `BIC*` (heuristic)**, and **for finalists / ambiguous pairs, refit the reduced model** (or use the refit-distribution median for the area criterion), not the primary-fit area.

**Pluralistic criteria (from the model-selection addendum, now folded in).** From each candidate's shared `(RSS, k, n)` compute — near-free — a panel: weighted χ²ᵣ, `BIC*` (**ranking default, unchanged**), AICc, and a nested-model F-test. Report all; **raise `criteria_disagree`** when top-by-BIC\* ≠ top-by-AICc, or an F-test rejects a peak BIC\* keeps, or the leading gap < `τ_bic`. Route disagreement into the ambiguity layer — *criteria disagreeing is itself evidence of an underdetermined decomposition*. **Caveat encoded:** BIC\*/AICc/F-test share the Gaussian assumption, so on weighted-Poisson/processed data they are *relative* indicators; cross-validation (contiguous/block folds) is the assumption-light escape hatch, and MCMC (`emcee`) posteriors are the deferred high-rigor uncertainty mode. All thresholds are UNVERIFIED tunables (§9).

**[v2.1] Re-review refinements (Codex item 4):**
- **One likelihood convention throughout:** use fitalg's `BIC = n·ln(RSS/n) + k·ln(n)` (the addendum's `χ² + k·ln(n)` is a *different* convention — do not mix); apply the same discipline to AIC/AICc.
- **The panel is a *diagnostic*, not independent corroboration.** BIC\*, AICc, χ²ᵣ, and the F-test share the residual/noise assumptions and are correlated views of one fragile likelihood on processed (non-count) data. The output **must state "not independent tests."**
- **F-test only on genuinely nested pairs** (e.g. adding one peak); non-nested candidates and absent-slot-adjusted models are outside its validity.
- **Two distinct flags, never merged:** `bic_ambiguous` (|ΔBIC\*| < τ_bic) and `criteria_conflict` (top-by-BIC\* ≠ top-by-AICc, or an F-test rejects a BIC\*-kept peak).
- **No single scalar criterion is the decision.** Trust order for this data (Codex): **parity to expert fits → stability/persistence → residual structure → BIC\* as a relative tie-breaker only.**

---

## 7. Region cookbook
As v1 §7 — define Layer-B module + Layer-C overrides, lit-cite every constant, add ≥1 validation case + parity test, register in the resolver.

**[Skye] Comprehensive element-physics DB — a first-class Fable deliverable.** Rather than one element at a time, **Fable scales this pattern across as many elements / core levels as authoritative XPS data exists**, extending the app's **tiered periodic-table reference system** — per entry: lineshape family (symmetric / DS-metallic / multiplet-asymmetric), spin-orbit splitting + area ratio, satellite structure, core-hole width β, BE windows. **Provenance discipline is non-negotiable:** every value sourced (NIST SRD 20 / primary literature), machine-generated entries flagged unverified-until-reviewed, Codex/NIST-adjudicated — reusing the existing anti-confabulation gate. C 1s + U 4f are the validated pattern; broad coverage is what makes the feature useful beyond Fortier Lab. (This is a distinct workstream from the Stage 2 resolver build.)

---

## 8. Integration surface **[v2 — deferred to later gate]**

`/api/analyze`, the material selector UI, and the results/confidence surface are **specified but not built this window** (§0). Design, unchanged from v1 §8, with two additions: the **`analysis` serialization namespace** (§1) and a **quantification lint** (flag region-mismatched `_rsfKey` like `Zr 3d` on B 1s, and leftover default `linkOffset` on unlinked peaks — surface, don't auto-fix).

---

## 9. Constants — Codex-adjudicated verdicts **[v2]**

| constant | value | verdict | source |
|---|---|---|---|
| C 1s LA β | 0.05 eV | **VERIFIED** (high) | Campbell & Papp, DOI 10.1006/adnd.2000.0848 |
| graphite ref | 284.4 eV | **VERIFIED** (graphite) | Leiro 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 |
| adventitious ref | 284.8 eV | **CONDITIONAL** — convention, not universal | Biesinger 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 |
| advent. offsets | +1.5/+3.0/+4.0 | soft **priors/windows**, not exact | Biesinger 2022 |
| graphitic α cap | ≤ 0.3 | **UNVERIFIED** — tunable numeric guard | fitalg (no primary source) |
| U 4f Δso / ratio | 10.8–10.9 eV / 0.75 (fitted 0.65 relaxed) | **VERIFIED** (splitting + theoretical ratio) | Ilton & Bagus 10.1002/sia.3836; Bagus 10.1063/1.4846135 |
| U(IV) asymmetry origin | multiplet/final-state (not metallic) | **VERIFIED**; supports asymmetric-envelope model (§3.2) | Ilton & Bagus |
| Cl 2p Δso / ratio | 1.60 eV / 2:1 | **CONDITIONAL** (medium) until chloride-source fit cited | NaCl SSS 10.1116/1.1247741 |
| h-BN N 1s | ~398.0–398.3 eV | **UNVERIFIED** — pull a primary value | — |
| pipeline thresholds | 0.7, 2%, ΔBIC 2, 5×, 0.5×FWHM | **UNVERIFIED** tunables — sensitivity-test | fitalg |
| `1/√counts` weighting | — | valid **raw counts only**; use empirical repeat-sweep noise | fitalg LIMITATIONS §8 |

---

## 10. For the v2 Codex re-review
1. **Confirm each B1/B2/B3/M1–M5 fix closes the finding** — or say why it doesn't.
2. **Adversarially test the U 4f resolution (§3.2):** given that the 5f² manifold is genuinely unresolvable, is asymmetric-as-first-class now sound? Concede or give a concrete counterexample where the bounded asymmetric tail + residual-flag safeguard still misleads.
3. **New-risk check:** does the multi-phase `phases[]` model or the `analysis` serialization namespace introduce new failure modes (phase-id leakage, resolver ambiguity, round-trip loss)?
4. **Spot-check the still-open constants** (h-BN N 1s, Cl 2p chloride source, thresholds) if time permits.
5. **Go/no-go for the Stage 2 build** (resolver skeleton + C 1s parity + schema round-trip).
