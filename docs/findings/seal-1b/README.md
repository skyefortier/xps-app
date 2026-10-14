# Seal 1b: what the seal's states rest on, measured (2026-10-14, run v2)

Branch `seal-1b-measure`. Design memo V6.11 1b, V5.4 / V6.5 (option (b)).

**This run supersedes the first write-up.** The first run (commit db50327) used a fit-target file built before A03. In that file every frontend "Voigt" component (180, across 90 targets) started at η = 0.3, and 171 of the 180 were free (both reviews, from the first run's raw records). Today's page sends η = 0.5, fixed. The file also lacked `frontend_shape`. That run's evidence is kept in `v1-superseded/`, with its own `summary.txt`, and none of its numbers are used below. The two Codex round-1 reviews (both NO-GO) were made against that version.

**Sources.** Every number below is in `v2/summary.txt`, which is `python scripts/seal_1b_summarise.py docs/findings/seal-1b/v2`, unless a line names another command. The run's commit, cleanliness, software identity, commands and file digests are in `v2/MANIFEST.md`. The generators are `scripts/seal_1b_measure.py` (record, record-synthetic, verify, sizes, replay, index) and `scripts/seal_1b_background_twin.js`. Medians are true medians: with n = 202, a median is the mean of the two middle values.

## The corpus (`v2/records_index.jsonl`, `v2/MANIFEST.md`)

The corpus is 328 records. All 328 returned HTTP 200 with `success: true`. All 328 were recorded, verified and replayed on one clean commit, a46cd3f (`dirty=0` before the first phase). All 328 carry one software identity, the one `/api/verify-fit` gates on: Python 3.12.13, NumPy 2.4.4, SciPy 1.17.1, lmfit 1.3.4.

- **202 committed targets: Run Fit's request as today's page builds it.** The 7 committed projects in `docs/autofit/test_data` hold 121 tabs (`seal_1b_tabs.py`). `optimizer_disagreement_targets.js` turns those tabs into 202 targets, using the page's own `peakToBackendSpec` and `_bgWindowIndices`, extracted verbatim. 107 targets are a tab's own saved model. The other 95 are a region's first model propagated onto another tab, the way `runPropagation` does it: a start that is not yet a solution. Rebuilding both files at a46cd3f gives the same sha256 (MANIFEST).
  - Each request is what Run Fit sends: the data uploaded at full precision through `/api/upload`, explicit window indices and averaging, Trust-Region, `n_perturb` 3, and `n_starts` 3 when there are at least 2 unlinked components (304 records; the other 24 have 0).
  - The page's Method menu is assumed to be at its default. Only Trust-Region is measured.
  - All 180 Voigt components now go out at `gl_ratio` 0.5 with `fix_gl_ratio: true`, and every spec carries `frontend_shape`.
  - Committed lineshapes, by component: GL 374, Voigt 180, LA 178, asym-GL 108, Gaussian 25. There are no Lorentzian, DS or DS+G components.
  - Committed backgrounds: Shirley 69, Smart 109, smart_exp 24, at averaging 1, 2, 6, 25 and 31.
- **126 synthetic records: hand-written API requests, NOT the page's.**
  - Every backend lineshape (Gaussian, Lorentzian, pseudo-Voigt, asym-GL, DS, DS+G, LA) is crossed with six background methods (Shirley at averaging 3, Smart, Tougaard, linear, none, and manual with two anchors) on three Poisson spectra with two components each. Those spectra are on 0.1, 0.1 and 0.05 eV grids, 280–295 eV.
  - These requests differ from the page's. They have no `frontend_shape`, numeric ids and no lock flags. No window indices are sent, so the whole region is the window. No averaging is sent except Shirley's, so the server's default of 1 applies.
  - The pseudo-Voigt starts with a free η of 0.3, which corresponds to the page's GL, not its Voigt.
  - **LA's m is HELD at 6.0.** The request omits `fix_m`, and the server's default holds m. The page sends `fix_m: false` for an unlocked LA peak. The synthetic LA fits therefore exercise LA's convolution (σ = 2 points) but not a fitted m.
  - DS+G's m was fitted free, landing at 0.63–1.30 eV, so the FFT broadening is exercised.
- The verbatim records (18 MB) are not committed. Each line of `records_index.jsonl` describes one record: identity, request settings, the lineshape specs these findings rest on, the fit's χ²ᵣ and the commit. It also carries sha256 digests of the record line and of R and O.

## 1. Cross-process bit-stability per lineshape (Q7)

**Method.** `/api/verify-fit` checked every record in four settings other than the producer's process:
- two fresh processes;
- a process with shaken memory. Between checks it allocated and kept a random number of random-size arrays. This changes the allocation history, but it does not establish which alignments the evaluators actually received.
- a four-worker gunicorn reached over HTTP. Its log shows four workers. The `pid` in that file is the HTTP client's, and nothing records which worker answered which request.

**Result** (`v2/verify_*.jsonl`), as consistent / unconfirmed:

| setting | committed (202) | synthetic (126) |
|---|---|---|
| fresh process 1 | 199 / 3 | 126 / 0 |
| fresh process 2 | 190 / 12 | 126 / 0 |
| shaken memory | 199 / 3 | 126 / 0 |
| gunicorn, 4 workers | 164 / 38 | 118 / 8 |

- **No verification of these 328 records read `mismatch`.** That covers 1,312 verifications: 1,248 consistent and 64 unconfirmed. This is an observation on this corpus and these settings, not a guarantee.
- **Every one of the 64 `unconfirmed` is a record holding LA (`la_casaxps`).** The failed check is always `components`, and the reason names `la_casaxps`. The 221 records without LA verified `consistent` in all four settings, which is 884 verifications.
- **An LA record is unconfirmed only when that process's evaluation of LA differs from the producer's.** Holding LA does not make a record unconfirmed by itself.
  - Of the 107 LA records (89 committed, 18 synthetic), 54 were consistent in all four settings. The other 53 (45 committed, 8 synthetic) were unconfirmed in at least one.
  - The 10 committed LA records whose every LA component fitted m below LA's 1e-3 no-convolution threshold were never unconfirmed. The threshold is `fitting.py`, `m_cont < 1e-3`; 20 of the 178 LA components fitted m below it.
- **How many records come back unconfirmed is not a stable rate.** Here it was 3, 12, 3 and 46 across the four settings. The superseded run's settings gave 27, 25, 23 and 41 (`v1-superseded/summary.txt`), on other targets and another commit. What held in both runs is which lineshape fails, not how often.
- **Read by evaluator, not by record.** The summary's "records holding each backend lineshape, by verdict" counts are per RECORD. A GL or asym-GL record counted unconfirmed there is a mixed record whose LA component failed. Its GL and asym-GL evaluations passed, because the verifier judges every stable component before an unstable one can answer, and a stable one that differs reads `mismatch`.

**So Q7's set stays `NOT_BIT_STABLE_SHAPES = {la_casaxps}`.** It is the one evaluator observed to evaluate differently across processes, through its `np.convolve`. DS+G's FFT verified consistent in all 72 of its verifications, but that is bounded evidence:
- 18 synthetic fits, all with m_gauss between 0.63 and 1.30 eV;
- one family of spectra;
- one machine and one NumPy/BLAS build.

It is not proof across grids, parameter ranges or platforms. The committed targets hold no DS, DS+G or Lorentzian component.

What an LA record's verification means for the seal: it may come back `consistent` or `unconfirmed` depending on the verifying process. It is never `mismatch` here. "Unconfirmed" is a property of one verification, not of LA fits as such. Making LA's evaluator deterministic is the separate unit the owner set out in Q7.

## 2. The page's background is the server's (V5.4.4 / V6.5 step 4)

**Method.** The page's own `computeBackgroundCore` and every helper it calls are extracted verbatim (`tests/js/_page_background_source.js`, plus `manualAnchorBackground`). They are run on each record's own inputs (`scripts/seal_1b_background_twin.js`), and the output is compared with `O.background_y` element by element, with `!==`.

The window is given as the page's form would give it. An explicit window becomes its two edge energies as text, `String(v)`. A request without indices becomes blank fields, meaning the whole region. `_bgWindowIndices` must recover the request's indices exactly, or the record is reported as such rather than compared. Averaging is the request's. A manual request's anchors are given as the page holds them, `{x, y}`.

This is a numerical adapter. It does not recover the text the student typed: request indices cannot recover it (V6.5's `context0`).

**Result** (`v2/background_twin.jsonl`): **bit-identical on 328 / 328**. In every record the window was recovered exactly and the page's result was marked converged.
- Committed: Shirley 69, Smart 109 (averaging 1, 2 and 6), smart_exp 24 (averaging 1, 25 and 31).
- Synthetic: Shirley at averaging 3, Smart, Tougaard, linear, none and manual, 21 each, all on the whole region.

**Not covered by these records:**
- `shirley_linear`. It is off the menu but still loads and fits from saved files. Its page/server parity is covered separately, not by these records, in `tests/js/background_parity.test.js`:
  - The test "every background is bit-identical to the server" requires a relative difference of exactly 0. It covers `shirley_linear` at averaging 1, 3 and 10, on synthetic spectra, a real U 4f scan (ascending and descending) and 200 randomised spectra.
  - A further test checks both grid directions to within 1e-6 of the span.
  - `node --test tests/js/background_parity.test.js`, run in this worktree on 2026-10-14 (page, fitting.py and test unchanged since a46cd3f), passed 22 of 22.
- Tougaard, linear, none and manual on an explicit window or at averaging above 1. They appear here only in the synthetic whole-region requests.

The binding "the page's certified background equals the recorded one" can be exact on what was tested, as the plan requires.

## 3. The seal's size, PARTIAL

**Method** (`v2/sizes.jsonl`). The bytes of R = {request, energies, counts} and of O = the `/api/fit` reply, as `json.dumps` gives them, raw and gzip-compressed separately.

**Result**, per committed fit (n = 202):

| | median | min | max | total |
|---|---|---|---|---|
| R, JSON | 9,607.5 B | 5,019 B | 15,479 B | 2,267,723 B |
| O, JSON | 52,704.5 B | 17,714 B | 76,720 B | 11,126,673 B |
| R, gzip | 3,222 B | 1,858 B | 5,159 B | 764,915 B |
| O, gzip | 23,819 B | 6,516 B | 35,283 B | 5,042,760 B |

R + O per fit has a median of 62,323 B raw and 27,035 B gzipped. Thirty such fits come to 1,869,690 B raw and 811,050 B gzipped. A committed fit has a median of 191 data points (max 350) and 4 components (max 7).

**This is NOT the size of the designed seal, and NOT a measured project increment:**
1. The design's R also holds `idx`, `ccShift`, `roi`, `pageModel`, `context0` and `producer`, and the seal holds a digest D. None of these were measured.
2. R's energies and counts are a subset of the tab's `rawBE` / `rawIntensity`, which a project already saves, so a `.proj.zip` may compress the pair better than this.
3. Gzipping R and O separately is not what a zip of a whole tab's JSON adds.

The "30 tabs" line is arithmetic on these partial records. No 30-tab project was saved and measured.

## 4. "Re-run this fit" (REPLAY-CHECKED, 1d)

**Method** (`v2/replay.jsonl`). Each record's request was re-uploaded at full precision and re-run through `/api/fit` in a fresh process, with O's `random_seed` passed as the caller's `seed`. The result was compared with O by `tests/fit_equality.py`: the same fit within rounding, uncertainties and certificate history not compared. Before comparing, `seed_source` was removed from both, because a replay changes it by construction ("request" becomes "caller").

**Result.**

| | records | reproduced | of those, equal as sorted JSON* | differ |
|---|---|---|---|---|
| committed | 202 | 200 | 113 | 2 |
| synthetic | 126 | 121 | 88 | 5 |

\*Equal as `json.dumps(…, sort_keys=True)` once the original `seed_source` is put back. This is not the verbatim response bytes.

Every replay reported `success: true`, as did every record.

**All 7 differences are in the scattered-starts evidence only. The fit itself reproduced in every one of the 328.** No differing field is outside `starts.*`, and no diagnostic reached the generator's 400-character truncation.
- **Committed U4f Scan_2** (`5326f6646fca`, LA + Voigt): one not-better solution's χ²ᵣ differs by 2.1e-7 relative.
- **Committed U4f Scan_4** (`03540b1537f7`, LA + Voigt): one not-better solution's χ²ᵣ differs by 1.2e-7 relative.
- **Synthetic DS+G** (all five on the DS+G model):
  - `syn-3-ds_g-5`: one start moved from "same as the fit" into a not-better solution. `n_same_as_fit` went 3 → 2, `n_not_better_elsewhere` 0 → 1 and the not-better list's length 0 → 1. The comparator lists every field that differs, and `n_converged` is not among them.
  - The other four differ in one not-better χ²ᵣ: `syn-4-ds_g-1` by 3.5e-6, `syn-4-ds_g-3` by 1.6e-6, `syn-4-ds_g-5` by 2.1e-5 and `syn-5-ds_g-5` by 6.9e-4 relative.

The DS+G evaluator verified bit-stable across processes (§1), so these differences come from somewhere else. That fits the Trust-Region arithmetic jitter CLAUDE.md records, which acts on where a scattered start lands, but it was not investigated here.

The superseded run reported two fit-level differences, on U4f Scan_1 and Scan_3. They were on the pre-A03 targets, and they did not recur here. That does not show they cannot happen: CLAUDE.md documents LA U 4f fits whose minimum depends on arithmetic.

**For 1d.** The re-run verdict should judge THE FIT, meaning success and certificate as well as the values compared within rounding. It should report the scattered-starts evidence separately and visibly: the counts, a start that moved, and alternatives that changed. Otherwise the 7 reproduced fits above would read "different". A fit-level difference must still read "a different solution". This corpus did not produce one, but nothing here shows that it cannot.

## What this does and does not show

**Shown, on this corpus, on one machine and one software identity:**
- no false `mismatch` in 1,312 cross-process verifications;
- `unconfirmed` occurs only on records holding LA;
- the page's background is bit-identical to the server's on 328 / 328 records over six methods (`shirley_linear` aside);
- a re-run with the recorded seed reproduces the fit on 328 / 328, with the starts evidence differing on 7.

**Not shown:**
- Other platforms, BLAS builds or NumPy versions.
- The public URL, or concurrent load.
- Which gunicorn worker verified which record.
- Any fit method other than Trust-Region.
- The other producers: "Use this solution" and Auto-Fit.
- A DS, DS+G or Lorentzian component in a real request.
- A fitted LA m in the synthetic set. The committed set has 79 components with m free.
- The page's Voigt in the synthetic set. The committed set has 180.
- The full seal's size.
- Q5 (areas) is not re-measured. It was measured and switched before this unit (`docs/findings/q5-area`).

## Notes

- `scripts/seal_1b_background_twin.js` was corrected during the first run. It had handled only requests with explicit window indices and no anchors. Run v2 used the corrected version, the one at a46cd3f.
- After the run, `scripts/seal_1b_measure.py` gained an `index` phase, which writes `records_index.jsonl`; the measuring phases are unchanged. `scripts/seal_1b_summarise.py` now computes true medians, reports per-evaluator and per-LA-record verdicts, the request facts from the index and the replay classification, and defaults to `docs/findings/seal-1b/v2`. The superseded folder is still read with `python scripts/seal_1b_summarise.py docs/findings/seal-1b/v1-superseded`.
