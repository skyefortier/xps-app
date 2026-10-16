**Three MINOR findings remain. No BLOCKER or MAJOR found.**

1. **The specific round-15 findings are resolved.** Bounds, method/seed-source domains, and scattered-start ID types are checked at [fitting.py:335](fitting.py:335), [fitting.py:343](fitting.py:343), and [fitting.py:372](fitting.py:372). Integer `1` versus boolean `true` now compares differently at [same_fit.py:294](same_fit.py:294). The real-fit matrix includes children retaining their own shape parameters at [tests/test_seal_1d_compare.py:428](tests/test_seal_1d_compare.py:428). The broader bounds invariant remains incomplete, as below.

2. **No: validation still accepts structures the producer cannot write.** Starting from a real response, each mutation below passes validation and returns **200 on a, b, and both**, with self-comparison reporting **`same: true`**.

   - **MINOR — effectively equal bounds remain accepted.** Set `individual_peaks[0].params.fwhm` to `value:1`, `min:1`, `max:1.00000000000001`. The validator checks only strict ordering at [fitting.py:340](fitting.py:340). lmfit rejects bounds that are sufficiently close, using `isclose` at [parameter.py:888](/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py:888). I reproduced `run_fit` failing with “min == max” for these bounds.

   - **MINOR — impossible random seeds remain accepted.** `random_seed:-1` and `random_seed:4294967296` pass the integer-type check at [fitting.py:176](fitting.py:176). The producer requires caller seeds in `[0,2**32)` at [fitting.py:2775](fitting.py:2775); request-derived seeds also occupy that range at [fitting.py:2998](fitting.py:2998).

   - **MINOR — unknown background methods remain accepted.** Set `background_verdict.effect.method` to `"not-a-method"`, retaining its window and averaging fields. The validator treats every unknown name as a windowed method at [fitting.py:3584](fitting.py:3584), whereas the producer rejects it at [fitting.py:2861](fitting.py:2861).

   I found no new producer-response rejection. I reconfirmed the documented exception: a successful fit with held FWHM bounds `[-1e308,1e308]` is refused at `individual_peaks[0].params.fwhm.min/max` because its span overflows. See [fitting.py:394](fitting.py:394) and [plan:118](docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:118).

3. **I did not reproduce a body-triggered 500.** The 3,000-mutation fuzz passed; malformed JSON, excessive nesting, oversized integers, and wrong-content-type probes returned 400. This does not establish “never”: unexpected comparison exceptions still return 500 at [app.py:1486](app.py:1486).

4. **The tests establish the reported regressions, but not complete validation.** I independently confirmed all four reported regression mutants are caught, all **42 real-fit matrix cases** pass, and widening each `_FIXED_BOUNDS` entry is caught—**12/12**. All **328 archived records** validate and self-compare successfully. The fuzz explicitly does not establish whether accepting a changed value is correct: [tests/test_seal_1d_compare.py:456](tests/test_seal_1d_compare.py:456).

Read-only verification: **326 passed, 2 skipped, 5 chain tests deselected**, using in-memory sessions. The long-chain run was interrupted during regex compilation. The full 641-test suite and browser tests were not rerun. No files changed.

VERDICT: NO-GO
