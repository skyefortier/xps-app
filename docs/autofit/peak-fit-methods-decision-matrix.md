# Peak-Fit "Method" Dropdown — Decision Matrix

**Purpose:** specify a user-selectable *mathematical treatment* for Peak Fit — the way scXRD makes you choose Direct Methods / Patterson / charge-flipping before solving. Built from a multi-source, DOI-verified literature sweep (deep-research). Every treatment below is a genuinely different mathematical approach, not a re-skin of one.

**Headline finding:** your instinct is correct and the literature backs it — there is a real menu of distinct treatments, each better on different data, and there is even a **purpose-built published XPS method family** (Japanese "Bayesian measurement" school: Nagata, Okada, Tokuda, Akai, Shinotsuka) that does fitting *and* peak-count selection in one pipeline. Two treatments are genuinely mature for XPS off-the-shelf; two more are published-but-specialist; the rest are adjacent-field and would need Fable to adapt the math.

---

## The matrix

| # | Treatment | What it decides | Best on | Weak on | XPS maturity | Off-shelf vs new math | Cost |
|---|---|---|---|---|---|---|---|
| 1 | **Classical constrained least-squares** (current) | parameters, given *your* model | high S/N, known component count, separated peaks | can't choose #peaks; overfits; local minima | **mature, universal** (CasaXPS etc.) | off-shelf (exists) | ~ms |
| 2 | **Grammar + information criteria** (BIC/AICc/F-test) | # of components | unknown peak count; guarding overfit | shares Gaussian assumption; "not independent tests" | **published for XPS** (NIMS group) | mostly off-shelf math (= fitalg engine) | low |
| 3 | **Bayesian — exchange Monte Carlo + Bayes free energy** | parameters **+ #components + noise level**, with calibrated uncertainty | overlap, shoulders, honest error bars, meV precision | cost; component-exchange multimodality | **published for XPS** (Nagata/Akai/Tokuda) | **new math** (Fable implements) | minutes–hours |
| 4 | **Sparse / MAP** (L1 dictionary, auto-prune) | # of components (via λ) | fast, high-throughput/imaging, few separated peaks | grid mismatch splits peaks; amplitude bias; overlap | **one emerging XPS source** (STAM 2024) | needs XPS dictionary (light new math) | low–moderate |
| 5 | **Multivariate — PCA / MCR-ALS / NMF** | # of chemical states + pure spectra + concentrations | **multi-spectrum sets** (depth profiles, imaging, your repeat scans) | needs a data matrix; rotational ambiguity; not single-spectrum | **mature** (PCA/MCR in CasaXPS) | off-shelf | low |
| 6 | **Maximum-entropy** | a sharpened lineshape (resolution enhancement) | single spectrum, known broadening, **high S/N** | amplifies noise; artifact peaks; doesn't quantify | mature but niche (since 1981) | off-shelf-ish (needs kernel) | low |
| 7 | *Cross-validation for #peaks* | # of components | assumption-light, works on processed data | **naive CV over-selects peaks** (correlated channels) | **not established for XPS** | needs block+buffer CV (new for XPS) | moderate |
| 8 | *RJMCMC / nested sampling* | joint #components + params / model evidence | transdimensional, multimodal posteriors | mixes poorly on overlap; unproven on XPS | adjacent-field only | new math | high |

Items 7–8 are listed for completeness but are **not** recommended for a first release (see shortlist).

---

## The two hard cases (your data)

### U 4f actinide multiplet — an important refinement to flag
The literature is unambiguous and it **partly revises the asymmetric-envelope plan**, so it's worth your eyes:

- A single Doniach-Šunjić/LA asymmetric shape is the accepted model for **metallic conduction-electron screening** — **not** for an actinide **multiplet** manifold. Actinide 4f multiplets are discrete theory-derived final states (Bagus/Nelin/Ilton computed them ab initio); best practice fits **explicit, theory-constrained multiplet + satellite components with fixed separations and area ratios**, not one free asymmetric peak. [Ilton & Bagus 2011; Bagus et al. 2016; Morgan 2023]
- **Oxidation state is read from the shake-up satellite separation, not the main-peak BE** (main-line shifts are small vs. linewidth). Diagnostic satellite-to-main separations: **U(IV) ≈ 6.8–7.1 eV, U(V) ≈ 8 eV, U(VI) ≈ 3.5–4 and ~10 eV.** [Ilton & Bagus 2011; Schindler 2009]
- The "asymmetric tail swallows a minor high-BE oxidation state" risk Codex raised is **explicitly documented**, and careful studies avoid it by: fixing lineshape from a pure standard, constraining satellites from theory, cross-checking with U 5d or synchrotron HERFD-XANES, and using difference spectra. [Ilton 2017; Kvashnina 2013]

**Reconciliation for the spec:** your asymmetric envelope stays valid as a fast/pragmatic main-line model, but the U 4f module should (a) treat the **satellite structure as the real oxidation-state fingerprint**, and (b) offer an **explicit multiplet/satellite treatment** as a selectable method, with the pure-U(IV)-vs-U(IV)+minor-oxidized-state enumeration (already in spec v2.1 §3.2) informed by those satellite separations. This is exactly the kind of "get the math right" item this feature exists for — worth a decision.

### Weak / low-S/N components (dilute B, etc.)
- Noise floor is **Poisson counting statistics** (σ=√N) on *raw counts*; your intensities are processed, so estimate noise from **repeat sweeps** instead. [Shard 2020]
- Near the detection limit, **background subtraction dominates** the uncertainty — collect ≥2× as much background as peak. [Hill/Faradzhev/Powell 2017]
- **ISO 19668** is the standard for reporting XPS detection limits (a ~3σ-style S/N criterion). BE uncertainty for a weak peak is set by counting statistics + correlation with neighbors, well above the ±0.1 eV instrument floor. [Shard 2018]

---

## Recommended dropdown — ranked by value vs effort

| rank | dropdown entry | why | effort | UI parameters to expose |
|---|---|---|---|---|
| 1 | **Least-squares (manual model)** | the baseline; already exists; the honest default | none | lineshape, background, constraints |
| 2 | **Auto — model comparison (IC)** | decides peak count; published for XPS; ≈ your fitalg engine | low (off-shelf math) | criterion (BIC default), max components, thresholds |
| 3 | **Bayesian (exchange MC)** | the crown jewel: calibrated uncertainties **+** peak count + noise, one pipeline, real XPS track record | **high (Fable builds)** | likelihood (Poisson raw / Gaussian processed), priors/constraints, #replicas, sweeps |
| 4 | **Sparse / MAP (fast auto)** | fast, scalable, auto-prunes peaks; one XPS source | moderate | λ (sparsity), dictionary lineshape, non-negativity |
| 5 | **Multivariate (PCA / MCR-ALS)** | *different job*: multi-spectrum decomposition — fits your depth-profile / repeat-scan data | low (off-shelf) | #components, constraints (non-neg, closure), preprocessing |
| 6 | **Max-entropy (resolution enhancement)** | single-spectrum sharpening when S/N is high and kernel known | low | broadening kernel, χ² target |

**Off-shelf vs new math:** 1, 2, 5, 6 are largely off-the-shelf (standard math, some in CasaXPS already). **3 (Bayesian exchange MC) is the one that needs real new implementation** — and it's the highest-value new capability, exactly the kind of long-horizon math work Fable is built for. 4 needs an XPS dictionary. 7–8 (CV, RJMCMC/nested sampling) are **deferred** — unproven on XPS and higher-risk.

**Scope note:** this is a *menu spec*, not a Stage-2 commitment. Stage 2 (resolver + C 1s parity + schema) already covers entries 1–2. Entry 3 (Bayesian) is the natural flagship for the Fable window *after* the foundation lands; 4–6 are region-cookbook-style additions.

---

## Cross-cutting rules (apply to every method)
- **Noise model is the load-bearing choice:** Poisson for raw counts, Gaussian for processed — and your data is processed, so estimate variance from repeat sweeps. Wrong noise model biases both uncertainties and (for Bayesian/IC) the chosen peak count.
- **Reduced χ² ≈ 1 is necessary, not sufficient** — a low χ² can hide an overfit or a wrong model; pair with the Abbe/serial-correlation residual check and the box-plot uniqueness test. [Major 2020; box-plot: Sivertsen/Fairley 2021]
- **Differential charging invalidates any method** — fix it before fitting, don't fit through it.
- **The IC panel is a diagnostic, not independent corroboration** (all share the Gaussian assumption) — already in spec v2.1 §6.

---

## Sources (verified DOIs; a few flagged below)

**Curve fitting / practice:** Major et al., *JVST A* 38, 061203 (2020), 10.1116/6.0000377 · Shirley, *PRB* 5, 4709 (1972), 10.1103/PhysRevB.5.4709 · Tougaard, *SIA* 11, 453 (1988), 10.1002/sia.740110902 · Doniach & Šunjić, *J. Phys. C* 3, 285 (1970), 10.1088/0022-3719/3/2/010 · Morgan, *SIA* (2023), 10.1002/sia.7215 · box-plot overfitting, *JESRP* 253, 147094 (2021), 10.1016/j.elspec.2021.147094.

**Information criteria / Bayesian XPS:** Kumazoe/Akai et al., *Sci. Rep.* 13, 13221 (2023), 10.1038/s41598-023-40208-3 · Nagata et al. (Poisson VMA), *JPSJ* 88, 044003 (2019), 10.7566/JPSJ.88.044003 · Nagata/Sugita/Okada (exchange MC), *Neural Networks* 28, 82 (2012), 10.1016/j.neunet.2011.12.001 · Tokuda/Nagata/Okada (noise+#peaks), *JPSJ* 86, 024001 (2017), 10.7566/JPSJ.86.024001 · Kashiwaya/Nagata (Hamiltonian selection), *JPSJ* 88, 034004 (2019), 10.7566/JPSJ.88.034004 · Machida et al. (multi-core-level), *STAM: Methods* 1, 123 (2021), 10.1080/27660400.2021.1943172 · Shinotsuka et al. (info compression), *JESRP* 239, 146903 (2020), 10.1016/j.elspec.2019.146903.

**Sparse / MAP:** MAP high-throughput XPS, *STAM: Methods* (2024), 10.1080/27660400.2024.2373046 · Tibshirani (LASSO), *JRSS B* 58, 267 (1996) · Green (RJMCMC), *Biometrika* 82, 711 (1995), 10.1093/biomet/82.4.711.

**Cross-validation:** Arlot & Celisse, *Statistics Surveys* 4, 40 (2010), 10.1214/09-SS054 · Roberts et al. (block CV), *Ecography* 40, 913 (2017), 10.1111/ecog.02881.

**Samplers/evidence:** Foreman-Mackey et al. (emcee), *PASP* 125, 306 (2013), 10.1086/670067 · Feroz et al. (MultiNest), *MNRAS* 398, 1601 (2009), 10.1111/j.1365-2966.2009.14548.x · Speagle (dynesty), *MNRAS* 493, 3132 (2020), 10.1093/mnras/staa278 · Skilling (nested sampling), *Bayesian Anal.* 1, 833 (2006).

**Multivariate / MaxEnt:** Mc Evoy et al. (PCA), *Anal. Chem.* 80, 7226 (2008), 10.1021/ac8005878 · Artyushkova & Fulghum, *JESRP* 121, 33 (2001), 10.1016/S0368-2048(01)00325-5 · Avval et al. (chemometrics guide), *JVST A* 40, 063206 (2022), 10.1116/6.0002082 · Jaumot et al. (MCR-ALS GUI), *Chemom. Intell. Lab. Syst.* 76, 101 (2005) · Vasquez et al. (MaxEnt XPS), *JESRP* 23, 63 (1981), 10.1016/0368-2048(81)85037-2 · Aspnes (MaxEnt deconvolution), *Entropy* 24, 1238 (2022), 10.3390/e24091238.

**Actinide / weak components:** Ilton & Bagus, *SIA* 43, 1549 (2011), 10.1002/sia.3836 · Bagus et al. (heavy-element multiplets), *Surf. Sci.* 643, 142 (2016), 10.1016/j.susc.2015.06.002 · Ilton et al. (shallow core level), *PCCP* 19, 30473 (2017), 10.1039/C7CP05805E · Schindler et al. (U 4f uranyl), *GCA* 73, 2488 (2009), 10.1016/j.gca.2009.02.008 · Kvashnina et al. (HERFD-XANES), *PRL* 111, 253002 (2013) · Shard (quantitative XPS), *JVST A* 38, 041201 (2020), 10.1116/1.5141395 · Hill/Faradzhev/Powell (detection limit), *SIA* 49, 1187 (2017), 10.1002/sia.6285 · Shard (ISO 19668), *SIA* 50, 906 (2018), 10.1002/sia.6339.

**Flagged / to re-verify before formal citation:** a handful of exact DOIs were reconstructed from search snippets (publisher pages were captcha-blocked) — notably some Surf. Interface Anal. / Appl. Surf. Sci. volume numbers in the multivariate and IC clusters, and two 2026 arXiv preprints (GPU-SMC Bayesian XPS; γ-ray unmixing). Nested sampling (MultiNest/dynesty) has **no** verified application to real XPS — it's inferred adjacent-field. Confirm these before they enter a grammar module (same UNVERIFIED discipline as spec §9).
