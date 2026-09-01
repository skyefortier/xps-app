# Codex review — Asymmetric GL frontend/backend mismatch — RUN B (2026-08-30)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/asym_gl_mismatch_review_prompt.txt

**Diagnosis**

Yes. The active backend and frontend implement different `asym-GL` functions.

Backend: [fitting.py](/Users/skyefortier/xps-app/fitting.py:72) clips asymmetry to `[0,1]`, then uses two fixed half-widths: `x <= center` uses `fwhm`, `x > center` uses `fwhm * (1 + asymmetry)` at [fitting.py](/Users/skyefortier/xps-app/fitting.py:90).

Frontend: [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:3834) uses `fwhm * (1 + alpha * abs(x-center) / fwhm)` on `x >= center`, so the high-BE width grows with distance and is unbounded.

The rendering consequence is also correct. `runFit()` stores backend `fitted_y` into `state.fitResult.fittedY` at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:6842). `updatePlot()` uses that as the red envelope at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:7951) and [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:8041), while individual peaks are recomputed through `evalPeakArray()` at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:7993). Independent U-like sweep gave `asym-GL max_abs=1703 counts`, `max_rel=9.57%`, consistent with the claimed ~10% failure mode.

**Canonical Direction**

For `asym-GL` specifically, frontend-to-backend is the right production fix. The backend produced the fit parameters and `fitted_y`; changing backend semantics would invalidate existing manual-fit/autofit parity and saved results.

Literature-wise: the frontend's distance-growing FWHM is not a CasaXPS/Fairley/Avantage form that could be substantiated. CasaXPS LA is a different model: a Lorentzian raised to side-specific exponents and convolved with a Gaussian, `LA(alpha,beta,m)`. CasaXPS also documents exponential-tail `GL/SGL T(k)` and Gelius forms, not this frontend width law. A 2021 XPS review (Major et al.) lists decaying exponential tails, DS, double-Lorentzian, and LX/LA/LF/LS as the main asymmetric approaches, and says DS is the only one with a theoretical basis, but has quantitative problems from infinite area.

So: backend `asym-GL` is defensible as an empirical split pseudo-Voigt, but it is not the CasaXPS LA definition. The better-founded alternatives are already separate shapes: DS/DS+G/LACX, or a true DL shape if added later.

**Derivative**

No value or first-derivative discontinuity at `x = center`. Both halves meet at amplitude, and centered Gaussian/Lorentzian/pseudo-Voigt derivatives are zero at the center regardless of width. There is a second-derivative jump when asymmetry is nonzero, because curvature scales with width. That is a kink, but not a first-order optimizer-breaking discontinuity.

**Bounds**

Backend has both lmfit bounds and function-level clipping: default `asymmetry_min=0`, `asymmetry_max=1` at [fitting.py](/Users/skyefortier/xps-app/fitting.py:923), plus `np.clip()` at [fitting.py](/Users/skyefortier/xps-app/fitting.py:90).

Frontend input declares `min="0" max="1"` at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:5761), but `updatePeakParam()` stores the raw parsed value without clamping at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:5494). Browser number inputs can still hold out-of-range values. Local LM clamps asymmetry to `0..0.9` at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:6918), which is another mismatch against backend `0..1`.

**Sweep**

Other mismatches exist, so this is not only an `asym-GL` bug class.

Representative max differences from extracted JS vs inspected Python formulas:

`Gaussian`, `Lorentzian`, `GL/pseudoVoigt`, fixed `Voigt`, `DS`: agreement to floating-point noise.

`asym-GL`: `1703 counts`, `9.57%`.

`DSG_LA/ds_g`: `231 counts`, `1.29%`. Backend FFT padded convolution [fitting.py](/Users/skyefortier/xps-app/fitting.py:149); frontend pointwise numerical convolution [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:3873).

`LACX/la_casaxps`: `14.6 counts`, `0.082%`. Backend uses continuous `m` and a `ceil(3.5*sigma)` kernel [fitting.py](/Users/skyefortier/xps-app/fitting.py:699); frontend rounds `m` and uses `2*m+1` kernel [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:3918).

**Blast Radius**

Changing frontend `asym-GL` changes individual peak curves, pre-fit previews, history previews, stack per-peak curves, exported PNG per-peak outlines/fills, `exportResults()` model/residual columns, saved `peakCurves`, local-LM fallback fitting, and displayed/exported area percentages. Backend `fittedY` for successful lmfit runs remains unchanged.

Tests do not pin JS/Python lineshape parity. `tests/js/shape_switch_roundtrip.test.js` extracts `evalPeakArray()`, but only checks round-trip curve preservation. Backend parity fixtures pin Python behavior, not frontend rendering.

Negative backend areas are confirmed: backend integrates with `trapezoid(peak_y, x)` at [fitting.py](/Users/skyefortier/xps-app/fitting.py:1204), so descending BE gives negative area. User-visible Results/Quantify use frontend positive-width integration via `Math.abs()` at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:7065), so percentages are mostly insulated. The negative values persist in backend JSON/fixtures and any downstream consumer of `backendResult.individual_peaks[*].params.area`.

VERDICT: NO-GO
