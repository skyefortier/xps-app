# Design memo v4 — Background architecture: the sealed fit record

Status: DESIGN ONLY — no code. Review history: v1/v2/v3 → Codex ×2 NO-GO
each round; every round endorsed the architecture direction and produced
converging completeness findings. Rounds 1–2 were call-site enumeration;
round 3's findings ([R3-A#]/[R3-B#]) are all instances of ONE class — "a
fit artifact consumed in a different FRAME or SETTINGS context than it was
produced in." v4 therefore restructures per the project's own pattern-gate
rule (docs: stop patching the set; make the class impossible): a sealed,
self-contained fit record with exactly one producer path, plus a single
dirty-marking funnel enforced by a structural test. Enumerations from all
three rounds become the migration checklist, not the correctness argument.

Measured symptom table (S1–S8) unchanged from v3 — see task1/task4 reports;
one addition from round 2: JS `linearBackground` also flat-holds a narrowed
window where the backend extrapolates (S8b).

## Part 1 — The sealed fit record (replaces v3's 1a/1b)

**`fitResult.sealed`** is created at exactly one point per producing flow
and is the ONLY thing any "fit" consumer may read:

```
sealed = {
  frame:      { ccShift },                 // the corrected frame the arrays live in
  be, counts, bgIntensity, bgSubtracted, fittedY,   // wholesale from backendResult
  peakResults: [ { id, name, shape, rsfKey, rsf,    // frontend metadata at fit time
                   params,                          // backend refined params + stderr
                   y } ],                           // backend individual_peaks[].y
  statistics, settingsSnapshot,             // bg method/window/n_avg used
}
```

- Arrays come wholesale from the backend response (rounded session grid —
  `uploadToBackend` rounds BE/intensity, so mixing frontend-precision `be`
  with backend arrays reintroduces a small S3). `peakResults` merges
  backend `individual_peaks[].{params,y}` with fit-time frontend metadata
  (name/shape/RSF) — the normalized per-peak export record round 3 asked
  for [R3-A3, R3-B4].
- **Producers (the only two):** (1) `runFit`'s backend path; (2)
  `applyAutoFitResult` — which seals AFTER its final programmatic charge
  correction, with `frame.ccShift` = the final shift and `be` + per-peak
  centers rigidly shifted by the final delta (exact — a cc change is a
  rigid BE relabeling; per-channel intensities, curves, widths, σ, and χ²
  are unchanged). This resolves the auto-fit frame contract both round-3
  runs rated BLOCKER [R3-A1, R3-B2]: the seal is always in the frame the
  UI shows at completion. The local-LM path seals its own record (its JS
  background IS what it subtracted — the invariant is "store what was
  fit," not "store Python output").
- **Consumers** (migration checklist, from rounds 1–3): `updatePlot`'s
  frozen-fit path incl. per-peak curves (post-fit, un-dirty: draw
  `peakResults[].y`, not evalPeakArray(state.peaks)) [R3-B3]; the
  Bkgrd-Sub view; `_computeRFactor`; `_doSaveSpectrum` / project save
  (persist the seal; `.spec.json` and project load restore it — the
  round-trip gap [R2-A4, R3-B4]); `exportResults` / `exportFitTable`
  (columns from `peakResults`, never live `state.peaks` — the cc-frame
  export invariant, now concrete) ; `exportFigure`; stack Path A (envelope
  AND per-peak curves from the source tab's seal) [R3-A2]; fit-history
  `_autoSnapshot` (snapshot = the seal; the history preview overlay draws
  a snapshot against its OWN be/bg/fittedY, not current plotBE/plotBG)
  [R3-B3]. Batch propagation and `runFitLocal` remain JS-background
  consumers by design (verified correct all three rounds); batch must
  additionally propagate `endpointAvg` (it is background-affecting)
  [R3-B5].

## Part 2 — The dirty funnel (replaces v3's 1c call-site map)

The class-killer for "some mutation path forgot to dirty the fit": all
background-affecting inputs are written through ONE funnel —
`_setBgInput(field, value)` for the DOM fields and `_mutateAnchors(fn)`
for anchors — and the funnel is the only place `fitResult.settingsDirty`
is set. Direct writes to bg-start/bg-end/bg-type/shirley-iter/
endpoint-avg/cc fields/manualAnchors outside the funnel are forbidden and
ENFORCED by a structural test that greps the source for rogue mutations —
the same mechanism that already guards evalPeak() callers in
tests/js/lineshape_parity.test.js (C) and has held for months. Known sites
to migrate (rounds 2–3, now a checklist, not the safety argument): the
five bg-field oninput handlers, `_onBgTypeChange`, `updateChargeCorrection`,
all four anchor mutations (add/remove/undo/clear), and `maxROI()` /
`autoSetROI()` — which rewrite bg-start/bg-end and were missed by every
hand enumeration until round 3 [R3-B1], which is exactly why the funnel +
structural test replaces enumeration.

Dirty semantics (unchanged from v3, now stated against the seal): dirty
mode draws the live JS preview background marked "preview (not fitted)";
the seal is retained untouched; stats/exports read the seal and carry an
"as fitted (settings changed since)" marker; the next fit replaces the
seal. Plain ROI typing stays non-dirtying (documented frozen-fit
invariant; it does not touch bg inputs — and if a future ROI helper does,
it must go through the funnel or the structural test fails).

## Part 3 — Window fix (unchanged; verified three rounds)

`_bgWindowIndices(be)`: `lo = min`, `hi = max`, send `(lo, hi+1)`;
blank/NaN endpoint → `(0, len)`; used by BOTH request builders (runFit +
auto-fit). Backend contract untouched → autofit/parity.py + battery
fixtures byte-stable. Helper unit tests: NaN endpoints, one-point ROI,
window outside ROI. Ship note: windowed-method fit numbers move by the S2
magnitudes (χ²ᵣ +0.03, centers ±10 meV, areas ±3.2%, fractions ±0.9 pp).

## Part 4 — Twin alignment + pinned parity (unchanged)

S4 (shirley signal clamp), S5 (smart clamp target), S8 (BE-based linear +
narrowed-window extrapolation semantics), JS convergence semantics (tol
1e-6 incl. smart_exp), committed parity suite from the Task-4 harness.

## Part 5 — shirley-iter removal (unchanged; sweep incl. batch_propagation.js)

Gated on Part 4's convergence semantics; decoupled from shirley_linear if
Q4 chooses de-listing. Sweep: DOM control, computeBackground deref,
_clampShirleyIter, _captureUI/_restoreUI, _onBgTypeChange, save metadata,
serializers accept-and-ignore, computeBackgroundCore accepts-and-ignores,
static/js/batch_propagation.js + its tests.

## Part 6 — shirley_linear (unchanged): scientific review first; user picks
interim (align JS→Python with ship note, or de-list until reviewed).

## Part 7 — /api/background shared constructor (contract completed)

Extract run_fit's background construction; method-specific contract:
integral → compute on [i0:i1), flat-hold outside; linear → extrapolate
across full ROI; manual → ignores window, `manual_bg` with ≥2 anchors
interpolates, and `manual_bg` empty/absent falls back to linear exactly as
/api/fit does today (documented, not a 400 — keeps the two endpoints
identical) [R3-B6]; none/flat → zeros. Response carries the full-ROI
embedded array.

## Ship order (Unit 1 split per review [R3-B6])

1a. **Seal + producers** (runFit, auto-fit incl. frame shift, local-LM),
    persistence round-trip (.spec.json + project save/load).
1b. **Consumer migration** to the seal (chart curves, sub view, R-factor,
    saves, all exports, stack Path A, history preview).
1c. **Window fix** (`_bgWindowIndices`, both builders).
1d. **Dirty funnel + structural test.**
    (1a→1d are one branch, separately committed; 1c is independent and
    could ship first if a smaller first unit is preferred.)
2.  shirley_linear decision (gated on Q4 choice).
3.  Twin alignment + committed parity suite.
4.  shirley-iter removal.
5.  /api/background shared constructor.

Verification per unit as in v3, plus: a structural test for the dirty
funnel; an auto-fit seal test (frame.ccShift equals the final displayed
shift and sealed graphite center = 284.50 exactly); battery suite
byte-stability run for 1c.

NOT in scope: DSG_LA/LACX lineshape parity (own branches; DSG_LA GO×2),
LACX kernel decision (parked pending CasaXPS empirical check).

## Round-4 amendments (GO ×2 — fold into implementation as written)

Round 4 approved the sealed-record architecture; both runs attached
amendments that are part of the approved design:

1. **Precise seal transform for the auto-fit final-cc shift** [R4-A1]:
   shift by the final delta: `sealed.be`, peak CENTER values (and any
   center-like bounds), `settingsSnapshot.bgStart/bgEnd`, ROI/range
   labels, and anchor x if captured. Do NOT shift: counts, bgIntensity,
   bgSubtracted, fittedY, per-peak y, amplitudes, areas, FWHM/width
   params, center stderr/σ, χ², RMSE, R-factor. `settingsSnapshot` is
   defined as "settings expressed in the sealed frame."
2. **Non-dirty hydration writer** [R4-A2, R4-B3]: project/spec load, tab
   activation, undo, and history restore go through the SAME allowlisted
   writer with `{dirty: false}` (`_writeBgInput(field, value, opts)`) —
   no raw restore writes "outside" the funnel, so a future mutator cannot
   hide behind the restore exception.
3. **Allowlist-based structural guard** [R4-A3]: the grep test guards the
   named write surfaces — the bg DOM fields, `tab.ui` bg fields,
   `state.ccShift`, `manualAnchors` — not just literal element ids, so
   dynamic helpers/dispatchEvent paths cannot evade it.
4. **Legacy adapter** [R4-A5, R4-B5]: one `normalizeFitResult(raw, peaks,
   ui, ccShift)` at every load/restore boundary converts old top-level
   fitResult shapes to a seal; old saves lacking peakResults become a
   flagged partial/"legacy reconstructed" seal, never silently
   authoritative.
5. **Local-LM seal contract** [R4-A4, R4-B4]: stores exactly what local
   LM fit (JS bg, JS per-peak y, final params, local stats; stderr
   explicitly absent); the parity suite must not expect a local-LM seal
   to match Python background output.
6. **Ship order confirmed**: 1a–1d one branch (mixed sealed/unsealed
   consumers are a transient hazard); 1c separable and may land first
   with its numeric-shift expectations documented.

## Round-5 amendment (2026-09-03) — Part 3 justified and made exact (Condition 2)

Approval of this memo carried two conditions. Condition 1: unit 1c ships
alone and first, as its own branch and its own deploy, because it is the
only unit that moves reported numbers. Condition 2: the window direction
is justified here, in plain terms, before 1c is built. This section is that
justification. Everything in it is reproducible with
`scripts/bg_window_pointsets.py` (prints the three-rule comparison table
below as its last line) and `scripts/bg_window_worked_example.py` (refits
at the exact precision `uploadToBackend` sends: BE to 4 decimals, counts
to 2) against the committed `.proj.zip` projects.

### The statement

The user draws a background window by typing two binding energies
(bg-start, bg-end). The on-screen preview (`computeBackgroundCore`) builds
its background from every grid point with lo ≤ BE ≤ hi — the last point the
user selected is in the window. The fit request converts each typed bound
to the nearest grid index and the backend slices `counts[i0:i1]` —
Python end-exclusive — so the fit anchors its background one grid point
INSIDE the window the user drew, on a raw single-channel value the user
never chose (endpointAvg = 1 is the default). End-exclusive slicing
silently drops the last point they selected; inclusive honours the stated
intent. That is the whole direction argument. Nothing about it depends on
which background algorithm is in use.

### The point-set contract (what 1c actually changes)

v4 said "send `(lo, hi+1)`" and left the index rule implicit. Measured
across all 166 fitted tabs in the seven committed `.proj.zip` projects,
the implicit rule matters:

| rule for the request | tabs where fit point set == preview point set |
|---|---|
| today: nearest grid index per bound, end-exclusive | 12 / 166 |
| v4 as written: nearest index, `hi+1` | 151 / 166 |
| **1c: inside-range (lo ≤ BE ≤ hi), `hi+1`** | **166 / 166** |

The 15 tabs where "nearest, hi+1" still disagrees with the preview are
all tabs whose typed bound falls off-grid *inside* the ROI: the nearest
grid point lies just OUTSIDE the typed bound (typed 279.2, grid 279.16)
and "nearest" would pull it in, while the preview excludes it. Inside-range
is also the rule `getROIData` already uses for the ROI itself, so 1c makes
the three windows in the app (ROI, preview background, fitted background)
obey one definition: a typed bound is an inclusive limit; no point outside
it is ever used; every grid point inside it is.

Concretely, 1c adds one helper and routes three callers through it:

```
_bgWindowIndices(be, bgStart, bgEnd) → { i0, i1 }   // inclusive indices
  lo = min(start, end), hi = max(start, end)
  i0 = first index with lo ≤ be[i] ≤ hi, i1 = last such index
  blank/NaN bound, or fewer than 2 points in range → { 0, be.length − 1 }
```

- `runFit` backend request: `start_idx: i0, end_idx: i1 + 1`
- `runAutoFitC1sGraphite` request: same
- `computeBackgroundCore`: takes `i0`/`i1` from the same helper (its
  current inline scan is the same rule; sharing the function makes the
  agreement structural rather than coincidental)

The backend contract is untouched (`end_idx` remains Python-exclusive, as
`/api/fit` and `/api/background` both document), so `autofit/parity.py`
and the battery fixtures stay byte-stable. `_parse_int` already clamps
`end_idx` to `[0, len]`, so `i1 + 1 == len` is legal.

Two contract edges, raised by Codex round 1 and documented on the helper:
the window is the contiguous span from the first to the last in-range
index, exact on a monotonic grid — which `createTab` guarantees by sorting
descending and which every project this app has written carries; a
hand-edited non-monotonic `rawBE` would make the span include
out-of-window rows, with preview and request still agreeing. And the
indices are computed on the frontend grid before `uploadToBackend` rounds
BE to 4 decimals; the backend only applies them to that same-length,
same-order session grid, so rounding cannot change which rows are used.

### Worked example on real data

Committed `docs/autofit/test_data/1-GTA UCl4-graphite one set of U
doublets.proj.zip`, tab `U4f Scan_0`: smart background, endpointAvg 1,
bg window 405.1 / 370.1 (= the ROI bounds, the default set by maxROI),
350-point descending grid at 0.1 eV, stored model 2 × LACX + 2 × Voigt
refit from its stored parameters. Both `least_squares` and `leastsq` give
the same numbers to 4 decimals.

| | points in the background window | last (low-BE) point | counts at that anchor |
|---|---|---|---|
| today | 349 — 405.06 … 370.26 | 370.26 | 5517 |
| after 1c | 350 — 405.06 … 370.16 | 370.16 | 5425 |
| preview | 350 — identical to "after 1c" | | |

The one point that moves in is the last point of the user's window. Its
intensity differs from its neighbour by 92 counts, and because Smart/Shirley
scale the whole curve between the two anchor levels, the fitted background
shifts by 92.4 counts at the low-BE edge tapering to 0.0 at the high-BE
edge — exactly the Task 1 residual signature (max at the low-BE ROI edge,
~0 at the high-BE edge).

| quantity | today | after 1c | shift |
|---|---|---|---|
| χ²ᵣ | 1.8293 | 1.9317 | +0.10 |
| U 4f₇/₂ centre | 379.574 | 379.590 | +16.5 meV |
| U 4f₅/₂ centre | 390.474 | 390.490 | +16.5 meV |
| U 4f₇/₂ area | 44 164 | 44 360 | +0.44 % |
| U 4f₅/₂ area | 28 126 | 28 279 | +0.54 % |
| Satellite 1 area | 5 450 | 5 679 | +4.2 % |
| Satellite 2 area | 3 114 | 3 164 | +1.6 % |
| atomic fractions | | | within ±0.23 pp |

Second example, same project, tab `C1s Scan` (shirley; window 298.2 / 279.2
typed INSIDE the ROI 279.0–298.5). The typed 279.2 is off-grid; the nearest
grid point is 279.16, outside the bound. Today's request (nearest, exclusive)
ends the window at 279.26; 1c's inside-range rule also ends it at 279.26 —
this fit is UNCHANGED by 1c, and equals the preview. Had 1c used "nearest,
hi+1" it would have pulled 279.16 in (2794 counts vs 2912 one channel up):
χ²ᵣ 4.97 → 3.32 and the graphite fraction +6.2 pp — a movement the user did
not ask for and the preview never showed. This is why the rule is stated
explicitly above.

### Ship-note magnitudes (supersede v4's Part 3 line)

v4 quoted χ²ᵣ +0.03, centres ±10 meV, areas ±3.2 %, fractions ±0.9 pp; the
measurement behind those figures is not archived in the repo. The worked
example above is the archived, reproducible basis: the size of the shift is
set by the intensity step between the two candidate anchor channels and by
how strongly the model leans on the background near that edge. State it as
a mechanism plus a measured range — χ²ᵣ up to ~0.1, centres up to ~20 meV,
areas up to ~4 % (satellites move more than main lines), atomic fractions
under 1 pp — not as a single number. Which fits move: every fit whose
dropped bound maps to a grid point inside the typed range, which is the
default configuration (window = ROI bounds); 154 of the 166 committed tabs
move. The 12 tabs whose point set was already the preview's — the
C1s-style off-grid-inside-ROI case — do not move at all.

The C1s example also shows, incidentally, how much a single-channel anchor
can matter when endpointAvg = 1 (graphite fraction ±6 pp from one channel).
That is an argument for endpoint averaging in the user guidance, not a
change for 1c.

### Known divergence left in place (logged, not fixed in 1c)

`autofit/reference.py::bg_indices` reconstructs stored expert fits for the
parity gates using the OLD frontend rule (nearest index; `parity.py` then
slices end-exclusive). It must stay that way in 1c: the committed fixtures
were produced by the old frontend and are required to stay byte-stable.
Expert fits saved AFTER 1c will have been made with the inclusive window,
and `reference.py` will reconstruct them one point short (its module
docstring now says so). The durable fix
is unit 1a's `settingsSnapshot` carrying the actual indices the fit used,
so reconstruction never re-derives them. Until then, any new parity
fixture must be generated with that caveat recorded.

## Round-6 note (2026-09-22, owner instruction) — binding by key is this memo's principle, and the seal must absorb it

Two units shipped before 1a–1d carry their own "does this evidence still
describe the fit?" mechanism, and both are local instances of Part 1's
invariant ("store what was fit", read only that):

- **Scattered starts (2026-09-22):** `fitResult.startsModelKey` — the
  JSON of every peak field the request reads plus the fit context
  (background type and window, endpoint averaging, Shirley iterations,
  ROI, manual anchors, charge shift) — taken after the result is applied.
  `_startsIfCurrent(fr, key)` compares it with `_startsLiveKey()` (active
  tab) or `_startsRecordKey(t)` (record) at every read; a mismatch means
  "no longer applies": nothing shown, applied, saved or exported. `runFit`
  also captures that key before its first await and discards a result
  whose model or context was edited while it ran.
- **Unsupported components (2026-09-22):** `p.support.fitKey`, the same
  key, on each peak's verdict; `_isUnsupported(p, key)` compares at every
  read; Auto-Fit re-stamps after its own locks and charge refinement
  (exactly Part 1's "seal AFTER the final programmatic charge correction").

Why it was done this way: hand invalidation in edit handlers was tried
first and lost the review rounds (a rename path deleted evidence, a lock
path missed it, an in-flight edit stamped a fresh key onto a mismatched
model). Comparison against a key derived from what the fit actually
consumed cannot forget an edit path. That is the seal's argument, made
twice more in the small.

**Instruction for 1a–1d:** absorb both into the seal; do not leave a second,
narrower binding mechanism beside it. Concretely:

1. `settingsSnapshot` + `peakResults` + `frame` ARE the key. The seal's
   identity is the request it was produced from; `_startsLiveKey()` and
   `_STARTS_MODEL_FIELDS` / `_STARTS_UI_FIELDS` become the definition of
   "the live state matches the seal" and should move into the seal's own
   `isCurrent()` (one function, one field list) rather than remain a
   parallel list that can drift from `settingsSnapshot`.
2. `fitResult.starts`, `fitResult.chosenAlternative` and each peak's
   `support` are seal contents (they were produced from the same request
   as the arrays), so they inherit the seal's currency test and its
   persistence, and the separate `startsModelKey` / `support.fitKey`
   fields are retired at migration.
3. The in-flight guard in `runFit` (key captured before the first await,
   result discarded if the live key changed) is the seal's producer-side
   rule: a seal is only ever created for the request that was sent.
4. Consumers already migrated to "read only the current evidence" — the
   starts panel, `_isUnsupported` at 15 sites, the CSV/XLSX status column,
   `_refreshStartsEvidence`'s per-consumer comparison — are the first
   consumers on the Part 1 checklist to switch to the seal, and their tests
   (`tests/js/scattered_starts.test.js`, `tests/js/unsupported_components.test.js`)
   are the acceptance tests for that switch: identical behaviour, one
   mechanism.
5. What must survive the absorption: cosmetic fields (name, colour,
   visibility) never invalidate; the sidebar is patched in place, never
   re-rendered under a typing student; each consumer is compared with its
   own rendering when currency changes.

## Round-7 note (2026-09-26, owner instruction) — legacy verification on load belongs in the seal's legacy adapter

Unit F1 (`docs/superpowers/plans/2026-09-25-f1-stale-statistics.md`) binds
χ², σ, RMSE, R and the stored fitted curve to their fit by the step (b) key.
A result saved before that key existed has none, so it reads `unverified`
("cannot be confirmed … Run Fit to confirm") — on EVERY tab of EVERY
project saved before 2026-09-26 (all 20 tabs of the committed UCl4-graphite
project). F1 deliberately does not try to recover those; the seal does.

The seal's legacy adapter, on load of a result with no key: recompute the
envelope from the SAVED peaks on the SAVED fit grid (`fitResult.be`) with the
saved background (`fitResult.bgIntensity`) and compare it with the SAVED
fitted curve (`fitResult.fittedY`). Where they agree, the statistics
demonstrably belong to that model, and the result is sealed with the loaded
model's key and reads `current`; where they disagree, or anything needed is
missing (no `fittedY`, no `be`, an older save's grid), it stays `unverified`.
Open questions for that unit, not decided here: the agreement criterion
(the design rule on data-scaled thresholds applies — prefer a comparison
with no magnitude tolerance, e.g. the same evaluator on the same grid
reproducing the saved curve to the precision the save rounded it to:
project saves round intensities to 6 significant figures); whether the
context half of the key (background type and window, ROI, anchors, charge
shift) can be taken from the saved `ui` at all, since the saved controls
are not proof of the fit's context; and local-engine results, which saved
no `fittedY`.


---

# v5 (2026-10-10, owner instruction) — the sealed fit record as a regeneration PROOF

Status: DESIGN ONLY — no code. Supersedes Parts 1–2 and the Round-6/7 notes where they
conflict; Parts 3–7 shipped or were overtaken (below). Owner, 2026-10-10: "a saved fit
carries everything needed to regenerate it and prove it current — inputs, settings, seed,
software version, background verdict, certificate verdict — and a loaded fit is current only
if that proof checks." Every statement about the CURRENT code is labelled **VERIFIED**
(`path:line` on main 90651e6) or **HYPOTHESIS** (not checked, or a claim about behaviour not
yet measured). Abbreviations: IH = templates/index.html, F = fitting.py, A = app.py,
P = parser.py.

## V5.1 What shipped since v4 (the pieces the seal must absorb)

| piece | what it is today | VERIFIED at |
|---|---|---|
| window fix (Part 3, unit 1c) | inclusive `_bgWindowIndices`, shared by preview and request | shipped 2026-09-03 (Round-5 above) |
| twins + parity (Part 4) | every background twin bit-identical to fitting.py | `tests/js/background_parity.test.js`; CLAUDE.md "Background Methods" |
| Shirley iterations retired (Part 5) | hidden, never read; kept in keys and saves | IH:8351 (`_STARTS_UI_FIELDS` still lists `shirleyIter`) |
| shirley_linear (Part 6) | off the menu, loads | CLAUDE.md "Background Methods" |
| the fit key (Round 6) | `fitResult.startsModelKey` = JSON `{p, u, s, a}` of the peak fields `_STARTS_MODEL_FIELDS`, the UI fields `_STARTS_UI_FIELDS`, the charge shift and the anchors | IH:8347-8358; stamped by runFit IH:8854, runFitLocal IH:9413, applyAutoFitResult IH:7803, re-stamped `_restampSupport` IH:7666 |
| comparison by key | `_sameFitKey` canonicalises each field through its reader (`_fitKeyCanon`, parseFloat / parseInt) | IH:8372-8393 |
| in-flight discard | key captured before the first await, result discarded if the live key changed | IH:8747, IH:8789, IH:8831 (Auto-Fit IH:8181, 8214, 8244) |
| statistics states (F1) | `_statsState`: none / stale / unverified (no key) / current | IH:8418-8426 |
| certificate (A2) | Trust-Region restarts until improvement < scipy's ftol, ≤ 50; response `certificate {certified, restarts, moved, optimiser_flag, centre_moves, largest_centre_move}`; DE / basinhopping `null` | F:1868-1870, F:1873-1917, F:2815, F:2825-2831 |
| scattered starts | third stream of the request seed; `starts {ran, n_run, n_converged, …, alternatives}` | F:2482-2483, F:2044-2082, F:2152-2161; page `n_starts` IH:8744, IH:8779 |
| background verdict | `background_certificate` → `{converged, residual, reason}`; `compute_background` raises `BackgroundNotConverged` → HTTP 422; page twins `_bgCertificate` / `_bgMark` / `_bgFailure` / `_certifiedBg` | F:1016, F:1286-1287, A:153-156, IH:4729, IH:5045-5068, IH:5178-5185 |
| input-derived seed (v2) | `_request_seed`: SHA-256 tag `xps-fit-seed-v2` over energies, counts, lineshapes, parameter roles by position, fit_kws, solver, n_perturb, the background BY EFFECT; reported `random_seed` | F:1951-2024, F:2810 |
| full-precision upload | `String(v)` per value; `parser._exact_columns` reads back bit for bit; `fitResult.uploadFull` | IH:6861-6862, P:168-195, IH:8850 |
| legacy restore rule | `_restoredFitBgFailure`: the background the fit used (stored envelope less its components) against today's certified background on the fit's own samples (`_restoredFitGrid`); within `BG_RESTORE_REL` = 1e-3 → current; beyond → stale `{pct}`; uncheckable → peaks only; **a fit without `startsModelKey` is never current** (`unconfirmed = !fit.fitFrame`) | IH:9956-10087 (rule IH:10053), IH:10126; loaders IH:12136-12146, IH:12323-12327 |
| support verdicts | `individual_peaks[].support`, bound by `p.support.fitKey` | CLAUDE.md "Not supported by the data"; IH:6988-6999 (`_applySupport(…, _startsLiveKey())`) |
| identity tests | envelope = background + Σ components, page and server, to rounding | branch `test-envelope-identity` (2026-10-10, under review) |

## V5.2 The gap between today and the goal (all VERIFIED unless marked)

1. **The seed is not saved.** `random_seed` is in the response (F:2810) and read nowhere on
   the page (no occurrence in IH); `backendResult` is kept in memory only (IH:8850) and not
   persisted by the project save (IH:11850-11878) or the spectrum save (IH:11753-11777). The
   caller-seed override exists in `run_fit` (F:2331-2338, F:2472-2473) but the HTTP route
   cannot reach it (A:135 passes `fit_kws={"method": fit_method}` only).
2. **The request is not fully recorded.** The fit method is read from the dropdown at request
   time (IH:8750; Auto-Fit IH:8173) and appears in neither key list (IH:8347-8351) nor the
   saved `ui` (`_captureUI` records `ccMethod` but no fit method). `n_perturb`, `n_starts`,
   `require_component` and Auto-Fit's `_afCenter*` / `_afFwhm*` bounds (IH:8185-8188) are not
   in the key either. Consequence: changing the method keeps a result "current".
3. **The certificate verdict is discarded.** Only a > 1 eV move survives, as
   `fitResult.certificateMove` (IH:8853, IH:8546-8549); `certified`, `restarts`,
   `optimiser_flag` exist only in the in-memory `backendResult`.
4. **No software version anywhere.** No app version, commit or `__version__` in F, A, P or IH
   (grep, NOT FOUND); the response has no version field (F:2791-2816). What exists: file
   format versions (fit file 1 IH:11649, spectrum 2 IH:11780, project 3 IH:11903), the seed
   tag (not in the response), timestamps.
5. **The background verdict is not stored for a successful fit.** The spectrum save writes
   `backgroundFailure` only on failure (IH:11779-11800); `fitResult` holds the page's own
   `bgIntensity` (IH:8849-8855), not the server's `background_y`, and no
   `{converged, residual}`.
6. **The saves round.** The project save writes `be` to 4 dp and the curves to 6 significant
   figures (IH:11826-11827); the spectrum save keeps full precision; the restore has to infer
   which (`beExact`, IH:10150). A sealed record must be lossless (HYPOTHESIS: the size cost is
   modest — to be measured on the committed projects before 1a).
7. **Producers differ.** Auto-Fit's fitResult has no `starts`, `certificateMove`, `engine` or
   `chosenAlternative` (IH:7795-7804); the local engine records no seed (it has none: it is
   deterministic, IH:9057-9430) and no certificate (its coordinate certificate's
   `certifyRestarts` is returned, IH:9429, not stored); Batch Fit is the local engine
   (IH:13747).
8. **Two loaders, two rules.** The spectrum loader copies statistics fields only when truthy
   (IH:12105); the project loader takes the record verbatim (IH:12290). `statisticsState` /
   `statisticsNote` are written to projects (IH:11878) and read only by the spectrum loader
   (IH:12112-12120). `restoredStale` is written by the spectrum save only (IH:11769).

## V5.3 The record

One object, `fitResult.sealed`, written by the producer at the moment the result is applied,
persisted LOSSLESSLY in both save formats, and the only thing a consumer of fit evidence reads:

```
sealed = {
  schema: 'xps-sealed-fit/1',
  software: { app: <version>, commit: <git sha>, seedTag: 'xps-fit-seed-v2', engine: 'server' | 'local' },
  request: {                       // EXACTLY what was sent, canonical JSON (the proof's anchor)
    energies, counts,              // as uploaded (full precision: identical to the tab's raw arrays
                                   //   in the ROI — stored as a digest + index range, HYPOTHESIS)
    peaks: [ <the peakSpecs sent> ], background: <the bg spec sent>, roi, chargeShift,
    method, n_perturb, n_starts, require_component | null, solver options
  },
  seed: <random_seed returned>,    // server only
  response: {                      // the server's own arrays, full precision
    energy, background_y, fitted_y, individual_peaks: [{ id, shape, params, y, support }],
    statistics, certificate, starts (counts AND alternatives' parameter sets), required
  },
  verdicts: {
    background: { method, converged, residual, reason },     // from the server (new response field)
    certificate: { certified, restarts, moved, optimiser_flag } | null,
    identity: <the envelope = background + Σ components check, run by the producer>
  },
  page: { fitKey: <_startsLiveKey() after apply>, appliedPeaks: <peak params as applied> },
  frame: { ccShift }                                          // as v4 Part 1 / R4-A1
}
```

Notes:
- `request` replaces v4's `settingsSnapshot` and is the key: "the live state matches the
  seal" means *the request the live state would send equals `sealed.request`* — built by the
  SAME builder the fit uses (`peakToBackendSpec`, the background spec, the ROI selection), so
  the key can never list fields the request does not read or miss ones it does (this closes
  gap 2 by construction; the Round-6 instruction "one function, one field list"). Cosmetic
  fields (name, colour, visibility) are not in a request (VERIFIED for name/colour: the seed
  hashes by effect, F:1967-2024; HYPOTHESIS for every builder field — to be checked
  field by field in 1a).
- The server adds `software` and the background verdict to the response (new fields; additive).
  HYPOTHESIS: `git rev-parse HEAD` at app start (the LaunchAgent serves the working tree,
  DEPLOY.md) gives the commit; a VERSION file written by the deploy step gives `app`.
- Auto-Fit seals after its final charge shift with v4's R4-A1 transform; the local engine and
  Batch Fit seal `engine: 'local'` records with no seed, no server certificate (its own
  coordinate certificate's verdict instead), and stay "a starting point".

## V5.4 "Current" is a proof, checked on every read and on load

A loaded (or live) fit is CURRENT only if ALL of these hold; otherwise it is STALE (statistics
withheld, F1's rules, with the failed step named) or, if the record is unusable, PEAKS-ONLY:

1. **Integrity:** `sealed.schema` known; the record's own arrays are finite and consistent
   (lengths; `fitted_y = background_y + Σ y` within the identity bound of
   `tests/envelope_identity.py`, incl. its FFT term).
2. **Same request:** the request the live state would send (same builder) equals
   `sealed.request` under the readers' canonicalisation (`_fitKeyCanon`'s rule). Covers the
   model, the locks, the bounds, the method and the run settings, the window, ROI, anchors,
   charge shift and the data.
3. **Same background:** today's certified background for `sealed.request` (the page twin, which
   is bit-identical to the server's on the tested cases — VERIFIED by
   `tests/js/background_parity.test.js`) equals `sealed.response.background_y` EXACTLY (no
   tolerance: same arithmetic, same inputs). Different → stale "background changed" with the
   size (today's message, `_bgStaleNote`).
4. **Same lineshapes:** the page's evaluators at `sealed.response.individual_peaks[].params`
   reproduce each `y` within the identity bound (the drawn curves are the fitted ones).
5. **Verdicts:** `verdicts.background.converged` and, for a local method,
   `verdicts.certificate.certified` are true.
6. **Software:** `sealed.software.commit` equals the running commit → steps 1–5 suffice.
   Different commit → steps 1–5 still decide, AND the record is marked "made by version X"
   (HYPOTHESIS for the owner: is a different version alone a reason to be stale? Steps 3–4
   already detect every change that alters what is drawn or the background; a change in the
   optimiser itself would not be detected without regeneration — see step 7).
7. **Regeneration (optional, explicit):** "Verify by re-running": the page sends
   `sealed.request` with `seed: sealed.seed` (a new, validated request field; the server
   already supports a caller seed in run_fit, F:2331-2338) and compares the reply with
   `sealed.response` WITHIN ROUNDING (`tests/fit_equality.py`'s rules, ported). Equal → the
   proof is complete; different → stale "a re-run gives a different result" with what moved.
   Trust-Region is not bit-reproducible (CLAUDE.md, owner 2026-09-21) — hence within rounding,
   never byte equality; a fit near a basin boundary can legitimately fail this step, and the
   scattered-starts line already says such a fit is not unique.

No magnitude tolerance is introduced anywhere (design rule "thresholds on data-scaled
quantities fail"): steps 2–3 are exact, 1 and 4 use the derived rounding bound, 7 uses the
existing fit-equality rules.

## V5.5 Legacy saves

- **No seal and no fit key** (every save before 2026-09-25, all 121 committed fits): NEVER
  current (owner 2026-10-05). The existing restore rule stays as the legacy adapter: stale with
  the reconstructed difference, or peaks only (VERIFIED IH:10053, IH:10072-10073). Unchanged.
- **Fit key but no seal** (saves 2026-09-25 → seal deploy): today the restore rule can make them
  current (VERIFIED: keyed, background within `BG_RESTORE_REL`). OWNER DECISION Q1: keep that
  (they were fitted by a version with the fit key and the certificate), or treat them like
  keyless saves (never current; "press Run Fit") because they lack the seed and the method
  (gap 1–2)? Recommendation: never current — the proof cannot be completed without the method,
  and the student note already tells students to re-run older saves.
- **Sealed:** V5.4.

## V5.6 Retired at migration (one mechanism, per the Round-6 instruction)

`startsModelKey`, `restoredKey`, `loadKey`, `p.support.fitKey`, `certificateMove`'s own binding,
`backgroundStale` / `voigtStale` as restore-time flags, `statisticsState` / `statisticsNote` in
saves, `_preFit`, `backendResult` in memory, the separate spectrum / project field lists
(gap 8): all become views of `sealed` and its proof. Acceptance tests that must pass unchanged
in behaviour: `tests/js/scattered_starts.test.js`, `tests/js/unsupported_components.test.js`,
`tests/js/stale_statistics.test.js`, `tests/js/certificate_move_notice.test.js`,
`tests/js/background_not_converged.test.js` (restore), `tests/test_browser_background_not_converged.py`,
and the new envelope-identity tests.

## V5.7 Owner decisions requested

- Q1 (V5.5): keyed-but-unsealed saves — current via the restore rule, or never current?
- Q2 (V5.4 step 6): is a different software commit by itself a reason for stale?
- Q3 (V5.4 step 7): regeneration on demand (a button), automatically on load (a server job per
  fit — cost: one fit per tab), or not at all?
- Q4 (V5.3): store the uploaded data in the seal (lossless, self-contained) or a digest + the
  tab's raw arrays (smaller; the raw arrays are already saved — HYPOTHESIS that they are always
  the uploaded values at full precision since 2026-10-03)?
- Q5: the alternatives' parameter sets — persist them (the panel survives a reload) or keep
  today's counts-only save (IH:8508-8517) and regenerate on demand (needs the seed, Q3)?

## V5.8 Ship order (after approval)

1a. Server: `software` + background verdict in the response; the request seed accepted over
    HTTP (validated, as `fit_kws.fit_kws.seed`). Additive; tests.
1b. Page producers write `sealed` (runFit, Use this solution, Auto-Fit, local engine, Batch
    Fit); both saves persist it losslessly; both loaders read it through ONE function.
1c. The proof (V5.4 steps 1–6) as the single currency test; consumers switch (V5.6 list).
1d. Retire the parallel mechanisms; the legacy adapter routes keyless / unsealed saves.
1e. (Q3) regeneration.
Each with Codex ×2; 1b–1d one branch (mixed consumers are a transient hazard, v4 R4-6).
