# Sealed fit record v5 design — Codex gate round 1, run A (commit 3cc5fa0)

The design is **not ready for owner approval**. Its central comparison confuses the original optimization request with the fitted model, and its proof does not establish that the stored statistics belong to the displayed result.

I reviewed HEAD `3cc5fa0`; its changes from `90651e6` are documentation only, so the code line references below apply to main. No files were changed.

**1. VERIFIED-claim audit**

Here, **D** means the [design document](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:423), **IH** means `templates/index.html`, and **F** means `fitting.py`.

| V5.1 claim | Audit |
|---|---|
| Inclusive background window | Correct: shared helper, with the request converting its inclusive end to exclusive. IH:5125, 8171, 8734–8752. |
| Every background twin bit-identical | **Overstated as a universal claim.** The cited exact test covers five integral methods and averaging 1/3/10; linear has separate coverage, manual lives in another test file. This is evidence for tested cases, not every request/platform/frame. |
| Shirley iterations hidden, “never read” | Hidden and numerically ignored, but literally still read by `computeBackground`, `_captureUI`, serializers and key canonicalization. IH:2060, 3851, 5187, 8375. |
| Fit-key fields and producer stamps | Correct at the cited locations. |
| Field-specific key canonicalization | Correct, but deliberately incomplete: defaults are not folded in. IH:8367–8369. |
| In-flight discard | Correct for changes represented by that key; it inherits gap 2. |
| Statistics states | Correct. IH:8418–8426. |
| Minimum certificate | Correct; “improvement” is **relative** improvement. F:1898–1900. |
| Scattered starts | Correct: third seed stream and reported counts/alternatives. |
| Background verdict/failure | Correct. |
| Input-derived seed | Correct. |
| Full-precision upload | Correct for the page’s finite CSV values; parsing still filters nonfinite rows. `parser.py:159–165`. |
| Legacy restore rule | Substantially correct, but the tolerance includes **`BG_REL_TOL * envScale`**, and background agreement alone does not establish current model/key agreement. IH:10058, 8420–8422. |
| Support verdicts | Correct. |
| Identity tests | Explicitly under review, **not available in main or the committed `test-envelope-identity` branch HEAD**. I inspected the additional files in that branch’s working directory; those are provisional evidence. |

V5.2 gaps:

| Gap | Audit |
|---|---|
| 1: seed unsaved; override unavailable over HTTP | Correct. |
| 2: missing request settings/key fields | Correct. `_captureUI` also omits the fit method, IH:3846. |
| 3: certificate discarded | Correct as a persistence claim; the full certificate remains in runtime `backendResult`. |
| 4: no software version | Correct for executable provenance. |
| 5: successful background verdict unstored | Correct. `backgroundFailure` is actually serialized as `null` on success, rather than omitted. |
| 6: project curves rounded | **False as written:** `be`, `bgIntensity`, `bgSubtracted` are rounded; **`fittedY` is preserved directly**, IH:11852–11860. |
| 7: producer differences | Correct, including local certificate count returned but unstored and Batch Fit using the local engine. |
| 8: loader differences | Partly overstated: only the listed metadata fields use truthiness; χ²/RMSE are assigned directly. **`statisticsNote` is not read by the spectrum loader**—only `statisticsState` is. IH:12104–12120. |

**MAJOR — false VERIFIED assertion in V5.3:** D:528 says cosmetic names are absent from requests, citing seed construction. `peakToBackendSpec` explicitly sends **`name: p.name`**, IH:6885. A seed ignoring a field does not mean the request omits it. Colour and visibility are absent from this builder.

The caller-seed citations in V5.4 are correct. V5.5’s keyless rule is correct; its keyed-save description needs the qualifications above and those in item 5 below.

**2. Record completeness: `sealed` alone is not yet sufficient**

**BLOCKER — the proposed digest/index alternative is not self-contained.** D:502–503 and Q4 leave the input arrays outside the record. A digest cannot reconstruct them.

The “identical to raw arrays” hypothesis is also false for energies when charge correction is nonzero: `_roiSelect` uploads **`rawBE[i] - ccShift`**, not `rawBE[i]` (IH:5513–5525). It returns an explicit index list; on accepted interleaved data that need not be one contiguous range. The parser additionally removes nonfinite pairs.

For a server fit, the necessary computational inputs are all visible in [request preparation](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/app.py:65) and F:2274–2287:

- Exact **parsed session arrays**, in their original order and fit frame.
- Complete peak specifications, including initial values, locks, links, splitting, ratios and bounds.
- Background method, actual exclusive indices, endpoint averaging and manual anchors.
- Method, `n_perturb`, `n_starts`, `require_component`, caller seed and effective solver settings.

The schema can carry most of these, but its placeholders are not a resolved contract:

- Auto-Fit adds bounds **outside** `peakToBackendSpec`, IH:8183–8188.
- Linked-peak construction reads global `getPeak`, IH:6954–6960; the existing builder is not a pure function of its argument.
- HTTP sends `fit_method` and `session_id`; the proposed record has `method` and arrays. Step 7 needs an explicit upload/session reconstruction adapter.
- HTTP always passes `charge_shift_ev=0`, because the page already corrected the energies. Treating recorded `chargeShift` as that backend argument would apply correction twice.
- Defaults remain implicit: default centre bounds depend on the **starting centre**, F:1559–1564; certificate tolerance comes from installed SciPy, F:1868; solver defaults are inherited through F:2504–2506.

**MAJOR — app commit is insufficient numerical provenance.** `requirements.txt:9–11` permits changing NumPy/SciPy/lmfit versions under the same app commit. `CLAUDE.md:491–493` explicitly warns that NumPy upgrades can change random streams. Record the resolved numerical environment/effective defaults, or identify a recoverable immutable execution environment. `git rev-parse HEAD` identifies repository HEAD, not necessarily dirty source, loaded worker code or the browser’s code.

The local-engine variant is also underspecified. `runFitLocal` consumes frontend peak objects, exact background/subtracted arrays and `options.maxIterations`; it holds LA’s `caM` even when the server would vary it (IH:9057–9080, 9111–9117). A server request with `engine:'local'` attached does not define a local replay.

**3. Proof soundness**

**BLOCKER — step 2 ordinarily rejects the fit immediately after success.**

The original request contains starting parameters, IH:6886–6888. Applying the response changes them, IH:6969–6985. The current implementation therefore stamps its key **after application**, IH:8854.

Rebuilding the request from that live state produces different starting values—and potentially different default centre bounds. This is explicitly documented in `CLAUDE.md:495–498`. Auto-Fit additionally changes the charge frame and locks all centres, IH:7774–7776, 7825.

You need two distinct, linked facts:

- The immutable request that produced the result.
- The applied output model/context that the live display must match.

Calling both “the request” cannot close gap 2 by construction. Overwriting the original request with fitted values would instead destroy replay provenance.

**BLOCKER — steps 1–6 do not bind statistics to data and curves.**

They check curve identities and stored flags, but never recompute or verify χ², degrees of freedom, R-factor, RMSE, uncertainties or support statistics. Replacing only `statistics.chi_square` leaves every mandatory step unchanged.

Step 4 also evaluates **response parameters**, not the live applied peaks. It establishes response self-consistency, not that the page actually draws those parameters. No proof step validates `page.appliedPeaks` against the response.

Even running **all seven steps** does not prove uncertainties: `tests/fit_equality.py:70,235` explicitly skips `stderr`. An incorrect finite uncertainty can survive the entire proposed proof.

**MAJOR — step 5 omits global-method acceptance.** DE/basinhopping have no certificate, but their `success` still matters. F:2780–2788 can mark DE unsuccessful when generated search bounds remain unverified. The proposed response omits `success`, while the current page explicitly requires it, IH:8812. Stored background convergence alone must not admit such a result.

**Step 3: exact background equality is defensible only under a narrower contract.**

The current implementations provide substantial parity evidence, including both directions, averaging, manual anchors and Tougaard. However:

- `background_parity.test.js:55–56` uses blank windows; its exact integral-method test is at lines 82–94.
- Manual exactness is tested separately in `manual_background_statement.test.js:53`.
- The page dispatcher consumes UI bounds and `{x,y}` anchors; the sealed request has indices and `[x,y]` anchors. An explicit shared adapter is required.
- ROI extending past the data is already handled by `_roiSelect`; verification must use those selected samples, without selecting again in another frame.

**MAJOR — exact equality conflicts with transforming the replay record.** R4-A1’s mathematical rigid translation is not universally bit-invariant. A read-only probe of the existing linear background on energies `[255.9,256,256.1,256.2]`, counts `[100,110,160,180]`, shifted by `0.04`, changed the second background value from `126.66666666666667` to `126.66666666666919`. Preserve the original computational frame and represent display translation separately.

**MAJOR — step 4’s proposed identity bound is insufficient.**

The provisional [identity helper](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/envelope_identity.py:9) derives a **summation** bound and adds an FFT term. It is not a general bound for independently evaluating every lineshape.

I compared the unchanged JS evaluator with Python functions extracted directly from main, on `x=370+0.05i`, 601 points, amplitude `17794`, centre `391.8`, FWHM `1.83`. Against the helper’s single-component, zero-background bound `12u|y|`:

| Shape | Parameters | Maximum bound ratio |
|---|---|---:|
| LA | α=1.4, β=0.8, m=50 | **1.49** |
| DS | α=0.22, γ=0.05 | **3.72** |
| Gaussian | — | **85.33**, in the far tail |

Ratios above one fail. LA and DS failures occurred at approximately 286 and 89 counts, respectively. Existing shape tests use `1e-6` of amplitude (`lineshape_parity.test.js:126`), which does not establish this much tighter condition.

DS+G needs its convolution/normalization-specific analysis; LA needs convolution and evaluation error accounted for. An envelope sum test cannot simply become a universal component-evaluator test.

**Step 6 is unresolved:** identical app commits do not establish identical software; different commits passing steps 1–5 establish neither replay compatibility nor unchanged statistical semantics. Step 7’s “proof complete” therefore describes a different property from step 6’s CURRENT.

**4. Regeneration and “within rounding”**

**MAJOR — re-run disagreement is not evidence that the saved fit is stale.**

`tests/fit_equality.py` is a useful **same-minimum comparison**, with deliberately documented exclusions. It is not a proof of artifact currency.

The [two-basin fixture §2](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-10-09-two-basin-fixture.md:21) explicitly removes perturbed restarts from its robust fixture because identical production requests can reach different minima. The owner accepted and disclosed this behaviour. Turning it into automatic STALE conflates “different valid optimization outcome” with “statistics no longer describe this saved result.”

Nor do three scattered starts guarantee that every nonunique fit will already have a warning.

**The fraction of committed targets failing this exact proposed gate is unmeasured.** The historical 202-target measurements in `CLAUDE.md:499–538` report byte identity and area movement under earlier configurations; they are not a census of v5’s whole-response comparator. Do not present their percentages as that failure rate.

Keep replay outcome separate from artifact validity, and measure the exact proposed comparator across processes and the actual production requests before claiming its reliability.

**5. Legacy policy**

The keyless recommendation matches the owner’s 2026-10-05 rule and shipped implementation: stale/unconfirmed if reconstructible, otherwise peaks-only. I independently counted **121 saved fits across seven committed project archives; none carries `startsModelKey`**.

Two corrections:

- A keyed save is not necessarily current merely because its background passes. Key equality and Voigt checks still apply; IH:8420–8422, 10056–10058.
- **MAJOR — “they were fitted by a version with the fit key and the certificate” is false as a blanket assertion.** The key predates A2’s 2026-09-29 certificate. The design itself records earlier key availability at D:344–347.

Q1’s recommendation—never claim a complete seal proof for an unsealed save—is sound. It is a deliberate tightening for keyed legacy saves, so acceptance tests cannot simultaneously require all previous currency behaviour unchanged.

**6. Migration and remaining bindings**

**MAJOR — mixed consumers can recreate exactly the inconsistency the seal is intended to remove.**

Examples:

- Plotting still reads top-level frozen `be`, `bgIntensity`, `bgSubtracted`, IH:10940–10965.
- Uncertainty display reads `backendResult.individual_peaks`, IH:9461–9465.
- `_computeRFactor` can fall back to live `state.peaks`, IH:13073.
- Legacy restore mutates arrays and clears evidence, IH:10069–10084.
- Existing save whitelists omit `sealed`, IH:11753–11777, 11850–11879.

Thus partial migration can display one result, report another’s statistics, lose uncertainties, discard the seal on re-save, or mutate compatibility fields independently.

The retirement inventory should additionally account for:

- `sealed.page.fitKey` itself: it retains the old incomplete field-list mechanism unless explicitly non-authoritative.
- `_historyPreview.altKey`, IH:8501.
- `p._backendParams`, IH:6995, and its legacy evaluator use at IH:10423.
- `beShift`, `beExact`, `uploadFull`, `_modelBe`, `fitCounts`, `restoredStale` and the legacy reconstruction predicates.
- History’s shallow result copies, IH:15517, 15665.
- **`chosenAlternative`**, required as seal content by Round 6, D:374–378, but absent from V5.3.

Concurrency ownership tokens should remain; they answer which operation may apply a result, a different question from evidence currency.

Shipping 1b–1d on one branch helps, but the actual release must switch authoritative reads together or provide compatibility views derived exclusively from the seal.

**7. Design rules**

**MAJOR — “no magnitude tolerance anywhere” is false.** `fit_equality.py:62–63` defines `1e-3` and `1e-7` relative tolerances; subsequent comparisons scale them by component height, width, parameter bounds and objective magnitude. These are existing, owner-documented comparison rules—not machine-rounding identity bounds. Reusing them as a production CURRENT predicate introduces that tolerance into currency decisions.

A derived arithmetic error bound is a different category and can be justified, but the proposed lineshape bound needs correction.

The “two readings” problem remains in several forms:

- Starting parameters versus fitted parameters, both called `request`.
- UI background settings versus request indices/anchors.
- Original fit frame versus transformed display frame.
- `response.certificate` versus `verdicts.certificate`, with no required consistency check.
- The new request comparison versus retained `page.fitKey`.
- Default-bearing request JSON versus the server’s resolved parameter/solver configuration.

Resolve those contracts before implementation. The essential revision is to preserve an immutable replay input, bind its actual output and statistical evidence, and distinguish display currency from replay reproducibility.

**VERDICT: NO-GO.**
