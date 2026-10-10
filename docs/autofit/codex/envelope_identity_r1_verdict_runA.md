# Envelope identity — Codex round 1, run A (commit bf8a6c1)

1. **MAJOR — the FFT allowance is not derived for the implementations used.** [envelope_identity.py:21](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/envelope_identity.py:21) substitutes `u` for Higham’s twiddle-factor error `μ`. The page generates twiddles recursively; replaying that recurrence produced errors of approximately **164u at L=1024** and **603u at L=4096**. [Higham’s theorem](https://pages.stat.wisc.edu/~bwu62/771/hingham2002.pdf) requires an explicit bound on those errors. Likewise, `nTot ≤ L` does not extend a radix-2 theorem to pocketfft’s mixed-radix/Bluestein implementation. [Pocketfft documentation](https://github.com/mreineck/pocketfft#some-code-details)

   The derivation also omits the page’s linear-to-circular folding operation, treats complex multiplication as one rounding, and assumes normalization merely doubles the error. That last step requires accounting for `|conv(x)| / peakVal`, which can exceed one: I measured **1.03317** at permitted parameters.

   The probe itself reads the correct tapered `ds`, shifted normalized `ks`, and `peakVal`; sampled probe outputs were identical to the original evaluator. The problem is the allowance’s mathematical justification. Re-derive it for both implementations and add a DS+G mutation proof exercising this allowance.

2. **MAJOR — the “locked” test can pass with the locks removed.** [test_envelope_identity.py:79](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/test_envelope_identity.py:79) checks only numeric values explicitly present in `locks`. The amplitude/centre/width cases contain only `fix_*` flags, so their lock checks are empty.

   I removed those flags through an in-memory mutation of `_make_peak_params`. The Gaussian locked test **still passed**, with the first peak returning:
   
   - amplitude `8997.62`, requested `8000`;
   - centre `380.9033`, requested `381`;
   - width `1.58956`, requested `1.5`;
   - all three `vary=True`.

   Check every requested fixed parameter against its original specification and returned `vary` status, for both components. The [browser lock check:133](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/test_browser_envelope_identity.py:133) similarly omits amplitude and checks only the first peak.

3. **MAJOR — the page assertion can accept curves that violate the identity as drawn.** [test_browser_envelope_identity.py:54](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/test_browser_envelope_identity.py:54) discards every dataset’s x-coordinates and compares y-values by index. I executed the committed `DRAWN` reader against chart-shaped data, shifted one component horizontally by 10 eV, and obtained an **identical snapshot**. The identity check therefore cannot detect that drawing defect. Assert matching energy grids before summing, and include a horizontal-shift negative proof.

The ordinary summation coefficient has sufficient first-order headroom for the additional component-plus-background additions and background subtractions at the tested component count, **conditional on the claimed component-evaluation error bound**. However, the cited empirical one-ulp BLAS observation is not itself a general bound for arbitrary LA convolutions.

The existing mutations otherwise target real identity failures. I verified that `OLD_ASYMM_GL` reproduces the pre-`cf4938d` formula; holding asymmetry at `0.35` legitimately prevents the regression from disappearing in a symmetric fit. The dropped-component, default-mix, and stale-certificate-envelope mutations also break the claimed equality.

Coverage includes every registered server shape and every listed page shape after fitting and editing. The two documented omissions are transparent, but they are **absent cases, not executable skips**. They do not establish coverage of those bounds. The “each shape parameter … each bound” comment also overstates the matrix: examples include missing DS decay `0` and DS+G upper Gaussian width `4`. Use suitable fixtures for difficult bounds or narrow the claim.

Validation: **32 server tests passed in 69.97 seconds**, including about **34.63 seconds** for Nelder–Mead. The browser module adds 21 cases; I did not rerun it in this read-only environment, so total added browser runtime remains unverified. No files were changed.

**VERDICT: NO-GO.**
