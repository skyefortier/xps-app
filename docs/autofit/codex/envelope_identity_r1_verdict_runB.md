# Envelope identity — Codex round 1, run B (commit bf8a6c1)

Reviewed `90651e6..bf8a6c1`. Three MAJOR findings:

1. **MAJOR — The advertised rounding bound is not derived for the implementations tested.**  
   [envelope_identity.py:18](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/envelope_identity.py:18)

   Higham’s theorem uses `η = μ + γ₄(√2 + μ)`, where `μ` bounds the computed twiddle errors. Setting `μ = u` is unjustified for the page’s recursive twiddle multiplication. Replaying that recurrence produced modulus errors of **165u, 174u, and 604u** at lengths 1024, 2048, and 4096. [Higham, Theorem 24.2](https://pages.stat.wisc.edu/~bwu62/771/hingham2002.pdf#page=482)

   Other missing steps matter:
   - The spectral product is complex arithmetic, not one real multiplication bounded by `u`.
   - The page folds two linear-convolution outputs together; that operation needs accounting.
   - Normalization does not simply double the error: it depends on `|conv(x)| / peakVal`. I measured **1.1121** for valid DS+G parameters with `α = 0.49`.
   - `nTot ≤ L` does not establish the same error bound for pocketfft’s different factorization. [Pocketfft implementation](https://github.com/mreineck/pocketfft)
   - The non-FFT derivation likewise assumes, without justification, that repeated LA convolution evaluations differ by at most one ulp. An inner-product bound depends on its length and arithmetic order; cross-language evaluation adds further differences.

   The probe does read the tapered `ds`, normalized/shifted `ks`, and actual `peakVal`; I verified its copied evaluator preserved output for a representative input. That does not repair the derivation. The summation margin can accommodate adding/subtracting component backgrounds, but the evaluator-error assumptions remain unsupported.

2. **MAJOR — The claimed amplitude/centre/width lock checks can pass with every lock ignored.**  
   [test_envelope_identity.py:77](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/test_envelope_identity.py:77)

   The assertion examines only numeric entries explicitly present in `locks`. The amplitude-only and Gaussian cases contain only `fix_*` entries, so they execute **no held-value assertions**.

   I removed those flags in memory before parameter construction and ran the Gaussian locked test. **It passed**, with all three parameters varying. Peak 1 moved from amplitude `8000`, centre `381`, width `1.5` to approximately `8997.62`, `380.9033`, `1.58956`.

   Check requested values and `vary=False` for both locked components. The page check also examines only the first component and omits the amplitude value. Its retained frontend values alone cannot establish what the server held.

3. **MAJOR — The page assertion ignores horizontal alignment of the drawn curves.**  
   [test_browser_envelope_identity.py:54](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/test_browser_envelope_identity.py:54)

   `DRAWN` discards every dataset’s x-coordinates and compares y-values by index. Shifting a component horizontally breaks the plotted identity but leaves every assertion unchanged. I confirmed that shifting component x-values produced an identical `DRAWN` result.

   Assert matching x-grids before subtraction/summation, and add a mutation proving a shifted component fails.

The existing mutations otherwise represent real identity violations. The historical asym-GL replacement matches the pre-`cf4938d` implementation; holding asymmetry at `0.35` makes it a meaningful asymmetric regression case despite the symmetric input spectrum. The normal page tests explicitly check server-backed/current and edited/stale states.

The LA and DS+G omissions are disclosed, but they remain omissions—not coverage. “Each shape parameter at each bound” overstates the matrix; other endpoints are absent too. A difficult or uncertifiable fixture warrants changing the fixture, rather than claiming exhaustive coverage. There is also no DS+G-specific negative control exercising its extra tolerance; I did not establish that it admits a substantial lineshape defect.

Validation: **32 server tests passed in 71.11 seconds**, including **35.30 seconds** for Nelder–Mead. The added 21 browser cases were not rerun under the read-only restrictions, so their runtime and full-suite timing remain unverified. No files changed.

**VERDICT: NO-GO.**
