# Task 1 — Diagnosis: the low-BE ROI-edge background residual

**Verdict: fully explained. The residual is not a lineshape, grid, or precision
issue — it is the difference between TWO DIFFERENT BACKGROUNDS stored in the
same fitResult.** `fittedY` contains the backend's Python background;
`bgIntensity` is the frontend's JS background. They diverge, dominantly because
of an off-by-one in the background anchor window, and the divergence has
exactly the observed shape: max at the low-BE ROI edge, ~0 at the high-BE
edge, intermediate at the peaks.

## Evidence chain

1. **Provenance (code).** In `runFit`'s backend path,
   `templates/index.html:6793` computes `bgIntensity = computeBackground(be, inten)`
   — client-side JS, *before* the fit — and `index.html:6852-6854` stores that
   JS array as `state.fitResult.bgIntensity` while storing
   `fittedY: backendResult.fitted_y` — which the backend built as
   `result.best_fit + bg` from its own Python background (`fitting.py:1191`).
   The auto-fit path does the same (`index.html:6553`, `6562-6564`). The
   backend's own `background_y` array is returned but only kept inside
   `fitResult.backendResult`; the top-level `bgIntensity` the save file and
   all display paths use is the JS twin. So algebraically:
   `fittedY − (peaks_py + bgIntensity) = bg_python − bg_js` (+ FP noise).

2. **Reproduction (measured).** Sample 6.proj is not on this machine (user ran
   that check themselves), so I reproduced on the committed
   `docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip`,
   tab `U4f Scan_0` (350-pt descending ROI 405.06→370.2 eV, bg method `smart`,
   shirleyIter 50, endpointAvg 1, stored backend fit of 2×LACX + 2×Voigt).
   Reconstructed peaks with `fitting.py`'s own `_la_casaxps_true` /
   `_pseudo_voigt_gl` at the stored `_backendParams`; computed the JS
   background by extracting the *shipped* `computeBackgroundCore` chain from
   `templates/index.html` and running it in node; computed the backend
   background exactly as `run_fit` does. Results:

   | quantity | max | low-BE edge | high-BE edge | main peak | mean |
   |---|---|---|---|---|---|
   | `fittedY − (peaks_py + bgIntensity_js)` | 94.5 | 92.4 | 0.0 | +62.3 | 24.4 |
   | `bg_python − bg_js` | 94.5 | 92.4 | 0.0 | +62.3 | 24.4 |
   | difference of the two rows | **0.01** | 0.00 | 0.00 | — | 0.00 |

   Same signature as the user's Sample 6 numbers (119 / ~0 / +65 / 33): a
   smooth positive offset largest at the low-BE edge. The stored
   `bgIntensity` also matches a fresh JS recomputation to 0.05 counts —
   i.e. it is (rounded to 0.1 by `_roundIntensity` on save) the JS
   background, confirming provenance from the data side too.

3. **Mechanism decomposition (measured, same scan):**
   - **Off-by-one anchor window: 92.4 of the 94.5 counts.** The frontend
     sends `end_idx` = the index *nearest* bg-end (`index.html:6805`), and
     `run_fit` slices `counts[i0:i1]` — Python-exclusive (`fitting.py:1020`),
     then flat-holds `bg_inner[-1]` over the dropped last point. The JS
     window is inclusive (`slice(i0, i1+1)`, `index.html:4340`). So the
     backend Shirley/Smart anchors its low-BE endpoint at `counts[n−2]`
     instead of `counts[n−1]`. Shirley scales the whole curve between its
     two endpoint levels, so this single-point anchor shift produces an
     offset that is maximal at the low-BE edge (= the local point-to-point
     intensity step, here 92 counts) and tapers to ~0 at the pinned
     high-BE end — passing through the peak region at a fraction of the
     edge value (+62 here, +65 on Sample 6).
   - **Iteration/init differences: ≤7.9 counts mid-window here.** JS Shirley
     runs a fixed `shirley-iter` count (UI default 5; this tab used 50),
     zero-initialized, no convergence test (`index.html:4027`); Python runs
     n_iter=200 to tol=1e-6 from a linear init (`fitting.py:320`). The
     `shirley-iter` setting is never sent to the backend at all. On tabs
     with the default 5 iterations this term will be larger than here.
   - JS applies endpoint averaging by pre-averaging the intensity array
     (`_applyEndpointAveraging`) with the same replace-with-mean semantics
     as Python's internal `n_avg` — same convention (good), but note the
     n_avg=1 default means the off-by-one anchor lands on a *raw noisy
     point*, which is why the edge offset can be ~2σ of the local counts.

## Consequences (why this matters beyond cosmetics)

- **The subtracted view lies slightly:** `bgSubtracted` (`index.html:6794`)
  is data − JS bg, but the χ²/residuals the backend reports were computed
  against data − Python bg. Also the backend *fit itself* ran against a
  background anchored one point inside the window the user actually placed.
- Peak **areas/quantification** integrate frontend-evaluated peaks, not the
  background, so atomic % is unaffected by the bg twin divergence itself.
- Magnitude scales with the local intensity step at the bg-end anchor
  (noise + slope), so it varies scan-to-scan; observed 90–120 counts
  (~0.5–0.7% of peak height) on real U4f data.

## What a fix would look like (NOT done — judgment call for the morning)

Options, not decided: (a) frontend sends `end_idx + 1` (make backend window
inclusive — matches user intent of "anchor AT bg-end"); (b) backend treats
`end_idx` as inclusive; (c) stop storing the JS bg after a backend fit —
store `backendResult.background_y` as `bgIntensity` so fitResult is
self-consistent regardless of twin drift; (d) all of the above plus sending
`shirley-iter` to the backend or aligning iteration policy. Note (a)/(b)
change fit numerics slightly for every future fit; (c) only changes display/
save consistency. Saved projects contain the old JS bg arrays either way.

Full parity data for all six background twins is in the Task 4 report.
