# Find Peaks — math-first architecture

Design direction set by Skye Fortier, 2026-07-20. This supersedes the curated-grammar-driven design for peak *detection*.

---

## Plain-language summary

Today, Find Peaks decides what peaks are *allowed* to exist based on hand-written models of where each element's peaks "should" be. Those models came from a handful of spectra — in some cases literally one. If your sample charges, or has a chemical state the model author didn't anticipate, the feature fails, and it fails quietly.

The new design inverts this. **The math finds the peaks.** The periodic-table selection contributes only physics that is true regardless of anyone's sample: how many spin-orbit partners a level has, how far apart they sit, their area ratio, whether the element's open d/f shells cause multiplet asymmetry, and the core-hole lifetime. All of that comes from quantum numbers and cited tables. None of it comes from anyone's spectra.

Reference positions don't disappear — they move to the end, where they belong. After the math has found the peaks, the app can *suggest* what chemistry they might correspond to. A suggestion, clearly labeled, that cannot change what was found.

**Consequence worth stating up front:** this removes the difference between "curated" and "uncurated" elements. Fe 2p and U 4f get the same treatment, because treatment no longer depends on whether someone wrote a model for that element. It also retires the provenance concern that started this work — the fitting engine stops depending on Fortier Lab spectra entirely, rather than depending on them with an honest label.

---

## The three layers that currently limit the math

All three are marked UNVERIFIED in the app's own records. All three cap what can be found, and they compound.

**1. Position windows gate admissibility.** `N1S_WINDOW = (396.5, 400.0)`. A real N 1s peak outside that range cannot be fit by the curated model at all. The observed failure: a charging BN sample put N 1s at 392.4 eV, four eV outside the window, so the region silently dropped to detection-only fallback.

**2. Component width caps.** `FWHM_MAX_ORDINARY_EV = 2.0`, and per-region ranges like `N1S_FWHM_RANGE = (0.7, 2.5)` sourced to "a single labeled exemplar."

**3. The detector itself is capped.** `CWT_FWHM_MAX_EV = 2.4`, with the comment "just above FWHM_MAX_ORDINARY_EV = 2.0; broader structures are the dominant/local-max channel's regime." **The ridge detector cannot see a feature broader than 2.4 eV.** This is the layer neither of us had named, and it likely explains the observed N 1s case directly: a broad shoulder wider than 2.4 eV is invisible to the primary detector, so nothing proposes a peak there, and the leftover gets absorbed by a generic filler pegged at its 2.0 eV ceiling.

A chemistry-derived number (2.0 eV "ordinary" width) propagated into the signal-processing layer. That is the coupling to break.

## What the element selection may supply

Only quantities derivable from quantum numbers or citable to published tables. The app already has the derivation module: `autofit/coverage.py`, which covers Z = 1–96 and enforces "nothing here emits a binding energy, spin-orbit splitting magnitude, RSF, FWHM, or any other empirical value." Today it is used only as a last-resort fallback. **It becomes the primary source of physics constraints for every element.**

| Constraint | Source | Status |
|---|---|---|
| Singlet vs doublet; component labels (4f7/2, 4f5/2) | j = l ± 1/2 — exact bookkeeping | derivable |
| Area-ratio expectation (p 1:2, d 2:3, f 3:4) | (2j+1) degeneracy | derivable, **expectation only — relaxable** |
| Multiplet-prone flag (open d/f shell) | Madelung configuration | derivable, advisory |
| Spin-orbit splitting magnitude | cited tables where they exist (e.g. U 4f 10.8 eV, Ilton & Bagus DOI 10.1002/sia.3836 — already VERIFIED) | cited; **free parameter where no citation exists** |
| Core-hole lifetime → Lorentzian width | cited (e.g. C 1s Campbell & Papp DOI 10.1006/adnd.2000.0848 — already VERIFIED) | cited; omit where absent |
| Asymmetric-lineshape admissibility | multiplet/final-state physics (e.g. U 4f 5f² — already VERIFIED, Ilton & Bagus) | cited rationale |

The provenance audit already did the sorting work: for U 4f, precisely the spin-orbit splitting, area ratio, and asymmetry origin are VERIFIED, while every position window and FWHM range is UNVERIFIED. **The VERIFIED set is the physics to keep. The UNVERIFIED set is the gating to remove.**

Where no cited splitting exists for an element, the doublet *structure* is still enforced (two components, ratio expectation, shared width) while the splitting itself becomes a fitted parameter. That is strictly more honest than substituting a guess, and it still constrains the fit far more than treating the peaks as independent.

## What the math owns

**Detection** determines candidate peak positions and count from the data. Its limits must derive from the measurement, not from chemistry:

- lower width bound: grid step and instrumental resolution;
- upper width bound: a fraction of the ROI width, or unbounded — *not* a chemical "ordinary peak" constant;
- prominence threshold: the noise estimate.

`CWT_FWHM_MAX_EV` must be decoupled from `FWHM_MAX_ORDINARY_EV` and driven by ROI scale. Multi-scale detection should span the full physically-measurable range, so a 4 eV shoulder is a detection candidate like anything else.

**Peak count** is chosen by model comparison — build models with k = 1, 2, 3 … N components and let the information criteria and F-tests pick. The machinery already exists (`autofit/criteria.py`: AIC/BIC, nested F-test; `autofit/methods/ic_model_comparison.py`). What changes is that the ladder is generated by *math plus physics constraints*, not by enumerating a hand-written family list. This is what makes the approach element-agnostic.

**Width bounds within a fit** come from instrument resolution as a floor, and from degeneracy control as a ceiling — with the "pegged at ceiling" condition treated as evidence for an additional component, not as an acceptable answer. Per Skye: a component sitting at its maximum allowable width **is a detection signal**, and the engine should respond by testing k+1, not by returning the capped fit.

## What happens to the curated grammars

They are **not deleted** — they are demoted from gates to labels.

- Position windows and chemical-state definitions become a *post-fit labeling* layer: given a peak the math found at 397.3 eV, suggest candidate assignments from the reference tables, with tier/provenance shown.
- A suggestion can never move, add, remove, or constrain a fitted peak.
- Where the label comes from a lab-derived source, it says so — consistent with the provenance work already completed.
- The cited physics (splittings, ratios, lifetimes, asymmetry rationale) is extracted from the region modules into the constraint layer above, where it applies to all elements uniformly.

## Migration outline

Sequenced so each step is independently reviewable. Every step is analysis-affecting, so Codex ×2 per unit and parity gates re-run each time.

1. **Decouple the detector from the chemistry constant.** Drive `CWT_FWHM_MAX_EV` from ROI/grid scale rather than `FWHM_MAX_ORDINARY_EV`. Smallest change with the most immediate effect on the observed N 1s failure — a broad shoulder becomes visible to detection. Verify against the real UCl₄-BN N 1s spectrum.
2. **Promote `coverage.py` to the universal constraint source.** Every element/level gets derived structure (doublet/singlet, components, ratio expectation, multiplet flag) applied to candidate construction — not just the five curated regions.
3. **Extract cited physics from region modules into the constraint layer.** The VERIFIED entries only (splittings, ratios, lifetimes, asymmetry admissibility). Leave the UNVERIFIED windows/widths behind.
4. **Generate the candidate ladder from k = 1…N** with physics constraints applied, replacing hand-enumerated model families. This is the core change and the largest. Existing model comparison selects k.
5. **Treat ceiling-pegged widths as evidence for k+1** rather than a terminal state.
6. **Move curated windows/chemical states to a post-fit labeling layer**, suggestion-only, provenance-labeled.
7. **Retire or rewrite the parity gates.** They currently pin behavior against expert fits produced under the old architecture — see the honest caveat below.

## Honest caveats — flagged, not buried

**The parity gates encode the old design.** `test_c1s_parity_gate.py` and friends assert agreement with expert fits, which are Fortier Lab fits. Under the new architecture the engine will legitimately find different decompositions. These gates cannot be treated as pass/fail correctness for the new design without reintroducing exactly the circularity the provenance audit removed. They should be reframed as *comparison* diagnostics ("how does the math-first result differ from the expert fit, and why?") rather than gates.

**Unconstrained peak-finding is degenerate.** Adding components always reduces residuals; this is why information criteria and F-tests carry the load, and why their thresholds become the most safety-critical constants in the system. Expect these to need real sensitivity work. This is a genuine risk of the new design and should not be glossed: the old windows, whatever their provenance problems, did suppress absurd decompositions. Their replacement must be statistical rigor, not nothing.

**Some regressions are expected and correct.** Cases where the curated grammar produced a "nice" answer because it was told the answer will now depend on the data supporting it. Where the data doesn't, the honest output is fewer peaks, or wider uncertainty, or a flag.

**Speed.** A k = 1…N ladder with constrained variants is likely more expensive than the current fixed enumeration. Find Peaks is already 60–240 s. This needs measuring early, not at the end.

## Success criteria

- The observed UCl₄-BN N 1s spectrum yields a chemically sensible multi-component decomposition, driven by the data, whether or not charge correction has been applied.
- A charge-correction offset changes labels only — never which peaks are found.
- Fe 2p (no curated grammar) and U 4f (curated) receive the same quality of treatment.
- No fitted quantity traces to Fortier Lab spectra.
