# Sealed fit record v5 design — Codex gate round 1, run B (commit 3cc5fa0)

**NO-GO.** The design conflates the request’s starting model with the fitted model, leaves statistics outside its proof, and applies an insufficient numerical bound to lineshape evaluation.

Reviewed HEAD `3cc5fa0` against `90651e6`; only documentation differs. No files changed. Below, **D** means the design memo, **IH** means `templates/index.html`, and **F** means `fitting.py`.

1. **VERIFIED claims: several need correction.**

   I checked every V5.1 row and V5.2 gap against the cited code.

   | Claim | Audit result |
   |---|---|
   | V5.1 window fix | Confirmed: preview and both request paths use `_bgWindowIndices`; requests convert its inclusive end to exclusive. IH:5125, 8171, 8734. |
   | Background twins | Supported **on tested cases**, not established universally. The strict test covers five integral methods; linear has separate coverage, and manual’s strict parity test is in another file. `tests/js/background_parity.test.js:82,164`; `tests/js/manual_background_statement.test.js:53`. |
   | Shirley iterations retired | Correct for numerical consumption. “Never read” is literally too broad: the DOM value is still read and passed through, as well as saved/keyed. IH:3851, 5187. |
   | `shirley_linear` off-menu but loadable | Confirmed. `tests/js/background_parity.test.js:171`; IH:3868. |
   | Key, canonicalisation, in-flight discard, statistics states | Confirmed at the cited locations. The in-flight guard inherits the key’s omissions; it does not capture every request change. |
   | Minimum certificate and scattered starts | Confirmed. F:1868–1917, 2044–2082, 2482. “Local methods” here means the three local **server solvers**, not necessarily the JavaScript engine. |
   | Background verdict and HTTP 422 | Confirmed. F:1016, 1286; `app.py:153`. |
   | Seed derivation and reported seed | Confirmed. F:1951–2024, 2810. |
   | Full-precision upload | Confirmed for valid page-generated numeric CSV. IH:6861; `parser.py:168`. |
   | Legacy restore rule | Substantially correct, but abbreviated: acceptance includes `BG_REL_TOL * envScale`, Voigt compatibility, and matching the live key—not merely background difference within `BG_RESTORE_REL`. IH:10056–10058, 8420–8422. |
   | Support verdict binding | Confirmed. IH:7637–7658. |
   | Envelope identity tests | These are under-review worktree files, absent from `90651e6` and this HEAD. They are a dependency, not established main-branch evidence. |

   V5.2 gaps **1–5 and 7 are substantiated**: seed/request/version/verdict persistence is missing as described; Auto-Fit and local producers differ; Batch Fit invokes the local engine.

   **MAJOR — Gap 6 overstates rounding.** Project saves round `be`, `bgIntensity`, and `bgSubtracted`, but preserve `fittedY` directly at full precision. D:478–480 versus IH:11852, 11858–11860. This distinction matters when deriving a reconstruction error bound.

   **MAJOR — Gap 8 overstates the loader claim.** Core `chi`, `chiReduced`, and `rmse` are copied unconditionally; selected metadata and `rFactor` use truthiness. `statisticsState` is read, but `statisticsNote` is only written, not read. IH:12104–12113; its only occurrence is IH:8450.

   **MAJOR — V5.3’s cosmetic-field VERIFIED claim is false.** `peakToBackendSpec` explicitly includes `name`. Seed hashing ignores names; that does not mean the request omits them. A literal request comparison would invalidate a rename, violating the retained Round-6 requirement. D:528–530; [IH:6883](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/templates/index.html:6883), F:1983–1994.

2. **BLOCKER — V5.3 does not yet specify a self-contained regeneration record.**

   The inline-array option can carry the server’s explicit inputs, but the digest/index-range option cannot regenerate from `sealed` alone. A digest verifies data; it cannot supply missing data.

   The input inventory needs these precise contracts:

   | Input | What must be recorded |
   |---|---|
   | Uploaded arrays | The exact **parsed, ordered arrays used by `run_fit`**. Original file parsing options need not be replayed if these arrays are retained. CSV parsing can remove non-finite rows: `parser.py:159–165`. |
   | ROI and charge correction | Uploaded energies are **corrected**, not raw: `_roiSelect` subtracts `ccShift` before selection. The HTTP route then supplies `charge_shift_ev=0`. IH:5513–5525; `app.py:134`. D:502’s “identical to … raw arrays” is false for nonzero correction. |
   | Sample selection | An index **range** is insufficient for permitted interleaved/non-monotonic records: `_roiSelect` returns an explicit index list and skips samples. IH:5520–5525. |
   | Background | Preserve method, actual `start_idx`, exclusive `end_idx`, parsed `endpoint_avg`, and all `manual_bg` pairs in their original frame. The generic “bg spec sent” can cover these, but should enumerate them. `app.py:79–88`; F:2345–2426. |
   | Peaks and links | Preserve actual ordered specs, including IDs, `constrain_to`, splitting, ratio, locks and bounds—not reconstructed specs from fitted peaks. IH:6954–6960; F:1507–1565. |
   | Auto-Fit | Capture the bounds overlaid **after** `peakToBackendSpec`, `require_component`, and its effective `n_starts=0`. IH:8183–8210; `app.py:120`. |
   | Run settings and seed | Explicit `n_perturb`, `n_starts`, method, complete `fit_kws`, and effective caller/derived seed. These are represented conceptually in v5; their wire mapping is not specified. |
   | Local engine | Its request is not the server request: it reads frontend peaks, supplied background/subtracted arrays and `options.maxIterations`; it holds LA’s `m`. IH:9057–9080, 9111–9117. Define a separate engine-specific recipe. |
   | Defaults/runtime | Record or pin effective bounds, weighting, solver defaults and numerical-library versions. App commit alone does not identify them: `requirements.txt:9–11` permits upgrades, and `CERTIFY_FTOL` comes from installed SciPy. F:1868, 2504. |

   **BLOCKER — Auto-Fit’s frame transform conflicts with “EXACTLY what was sent.”** D:534 retains R4-A1’s transformation of energies, centers, bounds, windows and anchors. Transforming the saved request destroys the original floating-point inputs; retaining it without an explicit display transform leaves the final live state unequal to it. Auto-Fit additionally changes the charge correction, reselects ROI samples, recomputes background and locks centers after fitting. IH:7774–7803, 7825.

   Preserve an immutable execution request and a separately defined mapping to the displayed result. They have different purposes.

   Two HYPOTHESES can be settled now: both saves serialize raw arrays without rounding (IH:11783–11784, 11846), but those arrays are **not already the uploaded corrected energies**. Storage cost remains unmeasured.

3. **BLOCKER — V5.4 is neither sufficient for CURRENT nor reliable against false STALE.**

   **Step 1: envelope consistency is necessary, not a statistical proof.** Nothing recomputes or validates χ², reduced χ², degrees of freedom, R, support statistics, or their relationship to request counts. Replacing only `response.statistics` leaves steps 1–6 unaffected. The actual statistical definitions are at F:2430–2435 and 2768–2807.

   It also needs explicit request/response energy correspondence, component ID/shape correspondence, and parameter-role validation. Equal array lengths do not establish these.

   **Step 2: ordinary successful fits immediately fail.** The builder sends starting centers, amplitudes and widths; applying the response changes them. Therefore:

   `buildRequest(live fitted state) != original request`

   This is explicitly documented in [CLAUDE.md:495](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/CLAUDE.md:495), and implemented at IH:8740–8741, 8843–8854. Default center bounds are also derived from the starting center, so rebuilding them changes the optimization problem: F:1559–1565.

   **Conversely, restoring the original starting peaks can pass step 2 while showing the wrong model.** Step 4 evaluates the **response’s parameters**, never checking that the live/applied parameters equal them. `page.appliedPeaks` is stored but absent from the proof. Even a successful optional regeneration does not close this hole: it reproduces the stored response, not the edited live model.

   Existing chart code makes this consequential: it evaluates live components while separately choosing the stored envelope. [IH:10968](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/templates/index.html:10968).

   A shared builder is useful, but “closes gap 2 by construction” is false as written. There are different producer recipes, Auto-Fit-only overlays, alternative starting peaks, global `getPeak` access, and no saved/restored fit-method control. IH:3846–3877, 6955, 8183, 8740.

   **Step 3: exact background comparison is plausible, but its universal justification is unproven.** The implemented twins provide strong evidence for both directions, averaging, Tougaard and explicit backgrounds. The cited parity file alone does not cover manual anchors or the complete upload/ROI/window construction. Additional tests cover portions of those paths.

   I found no concrete unchanged-background counterexample here. Nevertheless, exact comparison requires identical parsed arrays, sample order, indices and frame—not merely mathematically equivalent settings. Reconstructing energies after the Auto-Fit transform breaks that premise. ROI past the data is already handled by inclusive selection; do not synthesize samples outside the actual upload.

   **MAJOR — Step 4’s bound demonstrably rejects correct evaluators.** The under-review identity helper derives a bound for **adding components**, plus a DS+G FFT term. It is not a general bound for evaluating every component.

   I compared the actual Python and extracted page evaluators on `linspace(386.8,396.75,200)`, center `391.8`, amplitude `17794`, FWHM `1.83`. Against the single-component bound `12u × local magnitude`:

   - Gaussian exceeded it by **2.805×**.
   - LA with `α=1.4, β=0.8, m=50` exceeded it by **1.496×**.

   These are tiny arithmetic differences, not changed shapes. Gaussian uses different arithmetic expressions: F:53 versus IH:4014–4015. LA uses sequential JavaScript convolution versus NumPy convolution: IH:4141–4162 versus F:1373–1394.

   The evidence is [the proposed bound](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/envelope_identity.py:9). DS+G needs its normwise FFT/normalization bound; LA needs convolution/evaluation error accounted for too. Existing roundtrip tests allow `1e-6` of amplitude, so they cannot establish this tighter requirement: `tests/js/lineshape_roundtrip.test.js:93`.

   **Step 5: verdict checks omit acceptance evidence.** The proposed response drops `success`, while DE/basinhopping have null certificates. Their acceptance cannot be inferred from a successful background and valid curves. Current code explicitly rejects `success !== true`, including DE’s failed bound-removal refinement. IH:8812; F:2780–2795. Define server-solver certification separately from the JavaScript engine’s certificate and “starting point” status.

   **MAJOR — Steps 6 and 7 prove different things.** Steps 1–5 cannot detect changed weighting, statistics, parameter defaults, certification rules or optimizer behavior. A different commit may remain display-compatible, but that does not establish regeneration compatibility. Even an equal commit does not identify NumPy/SciPy/lmfit versions.

   `git rev-parse HEAD` also cannot certify the loaded frontend/backend combination: deployment serves templates from disk while Python changes require a restart. `DEPLOY.md:31–37`. Record actual build/runtime identities and distinguish **current display**, **complete provenance**, and **regeneration checked**.

4. **MAJOR — Step 7 turns accepted nondeterminism into a currency failure without measuring its consequences.**

   `assert_same_fit` is an appropriate existing criterion for “this rerun reproduced the saved solution within the accepted precision.” It is not a criterion for “the saved statistics still describe the saved figure.”

   A basin-sensitive rerun can differ although the saved figure, data and statistics remain internally correct. That outcome should be reported as regeneration disagreement/non-uniqueness, not automatically equated with edited or stale evidence.

   The two-basin fixture explicitly removes perturbed restarts because candidates changed basins under `1e-9` start perturbations. [Two-basin memo:23](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-10-09-two-basin-fixture.md:23). Three scattered starts are a diagnostic, not a guarantee that every unstable case is exposed; Auto-Fit does not request them.

   **The fraction of committed targets failing the exact proposed whole-response check is unmeasured here and must be HYPOTHESIS.** Historical byte-identity counts, maximum area differences and selected-fixture passes are not that census. The accepted historical evidence includes repeated basin flips on a real target: `docs/findings/runfit-certificate/README.md:181–190`.

   The port also needs a defined comparison projection. `assert_same_fit` requires `counts`, compares dictionary key sets, and deliberately excludes stderr and most certificate details. V5.3 omits response `counts`, `residuals`, `success`, `message`, `charge_shift_applied` and `random_seed`. `tests/fit_equality.py:119–122,235–240`. A raw reply cannot simply be compared with the proposed response object, and equality cannot be advertised as proof of every saved uncertainty.

5. **Legacy: the keyless rule is consistent; Q1’s recommendation is sound, with a false rationale removed.**

   V5.5 correctly preserves the owner’s October 5 rule: keyless saves never become current; reconstructible ones remain stale/unconfirmed and unusable ones become peaks-only. IH:10053–10073; `CLAUDE.md:951–978`.

   **MAJOR — “They were fitted by a version with … the certificate” is false for the entire keyed interval.** F1 dates to September 25; the minimum certificate dates to September 29. D:582–585; `CLAUDE.md:615`.

   Recommend **never CURRENT for keyed-but-unsealed saves under the new proof contract**. They lack original starting requests and other provenance as well as method/seed. Preserve their reconstructible curves and explanation; do not manufacture missing evidence. This is an intentional tightening of the shipped keyed restore rule and requires updating corresponding behavioral expectations.

6. **MAJOR — Migration can leave old readers authoritative, and the retirement list is incomplete.**

   Merely adding `sealed` leaves old readers able to report current statistics from `startsModelKey` despite a failed seal. Removing old fields first makes other consumers lose uncertainties, choose reconstruction paths, or mislabel local fits.

   Concrete consumers include `_statsState` (IH:8418), `_buildStderrMap` (9461), `_validateUncertainties` (13172), and the chart’s `haveFit`/stored-envelope paths (10940–10976).

   Additional items requiring explicit ownership are:

   - **`sealed.page.fitKey` itself:** it preserves the old incomplete field list beside request equality.
   - Alternative preview’s **`_historyPreview.altKey`** and result ownership: IH:8501, 8670, 8856.
   - **`chosenAlternative`**, explicitly required by Round 6 but absent from the proposed schema: D:374–378; IH:8855.
   - Legacy reconstruction state: **`restoredStale`, `beShift`, `beExact`, `uploadFull`, `_modelBe`**, plus peak **`_backendParams`** used for legacy Voigt interpretation.
   - Engine/reportability metadata and history/stack/save/export readers from the earlier consumer checklist.

   Legacy-only fields may remain inside the adapter; they must not independently authorize sealed evidence. Operation tokens such as `_fitOpCurrent` should remain for cancellation and supersession—they solve request ownership, not fit currency.

   Keeping 1b–1d on one branch is sensible but insufficient. Require one authoritative accessor and complete the consumer migration before deployment.

7. **Design rules: distinguish existing precision rules from new proof claims.**

   **MAJOR — v5 introduces competing readings of identity.** Original request, post-apply `page.fitKey`, applied peaks, transformed frame and live request are different objects, yet the design treats them as interchangeable. The duplicated certificate under `response` and `verdicts` also needs one authoritative source and consistency checking.

   The existing `fit_equality` relative criteria are an explicitly accepted rounding policy; reusing them does not automatically violate the prohibition on arbitrary absolute floors. But D:573’s “no magnitude tolerance anywhere” is inaccurate: the helper explicitly compares differences against scale-dependent allowances. `tests/fit_equality.py:161–197`.

   The remedy is to name each comparison’s purpose and justify its bound. Do not widen the failing lineshape bound empirically or reuse a whole-envelope scale to hide discrepancies in small components.

The standard numerical suites could not run because the read-only sandbox blocked dependency temporary-directory discovery. The isolated evaluator probe completed without modifying repository files; its measured failures are reported above. No committed-target regeneration census was performed.

**VERDICT: NO-GO.**
