# The LA unit — LA(α,β,m) made bit-reproducible (2026-10-15)

Logged by the owner on 2026-10-15 ("LA lineshape not bit-reproducible — find and fix the source, likely
np.convolve/BLAS"); seal 1b had found every unconfirmed record held LA, and step 8 that about one fresh fit in twelve
read UNCONFIRMED after Run Fit, all LA. Branch `seal-la-deterministic`.

## Diagnosis

- `scripts/seal_la_recompute.py`: every recorded LA component of seal 1b's run-v2 records (214) recomputed from its
  recorded parameters in four fresh processes: four different digests; 6, 22, 64 and 66 components differed from
  the record.
- `scripts/seal_la_isolate.py`, five fresh processes: LA's base curve (`np.power`) and its kernel had ONE digest each;
  `np.convolve`'s output had FOUR; a fixed-order convolution of the same inputs had one.
- Within one process `np.convolve` was stable across 64 memory alignments of its inputs, so the variation is per
  process (BLAS ddot on Apple Accelerate), not per alignment.

## Fix

`fitting._convolve_same_fixed_order`: every output the sum over the kernel taps in increasing order, accumulated
from 0 by elementwise numpy operations — no reduction, no BLAS. Same length and offset as `np.convolve(…,'same')`
trimmed to the grid; differs from it by rounding only (≤ 2.4e-15 relative over 3,000 random sizes). The page's
`laTrueCasaXPS_array` already sums in this order (it still differs by rounding in exp / pow, inside its parity
tolerance; the JS suite's parity harnesses pass). `NOT_BIT_STABLE_SHAPES` is empty: an LA curve that differs under the
same numerics now reads MISMATCH like every other lineshape (the UNCONFIRMED mechanism kept, tested with LA marked
unstable). `NUMERICS_VERSION` 2026-10-15, recorded in tests/fixtures/numerics_manifest.json (no seal is deployed, so
no deployed record is affected; a 1b record made before reads "other numerics").

## Measured (`scripts/seal_la_confirm_measure.py`, `confirm_before.json`, `confirm_after.json`)

The 121 committed fits: Run Fit on every tab, its own check, then five more checks each ("check again") — on a
4-worker gunicorn like production, the same script against seal-1d (87679b1, np.convolve) and this branch (3cc562e):

| | before | after |
|---|---|---|
| LA fits CURRENT right after Run Fit | 37 / 54 (17 unconfirmed: components) | **54 / 54** |
| LA re-checks confirmed | 190 / 270 | **270 / 270** |
| fits without LA | 67 / 67; re-checks 335 / 335 | 67 / 67; re-checks 335 / 335 |

Every unconfirmed fit becomes confirmed. (The step-8 save-size run had seen 10 unconfirmed of 121 with 2 workers; with
4 workers there are more processes to differ, hence 17.)

Tests: tests/test_la_deterministic.py (numpy's semantics to rounding; the same bits at every alignment and in five
fresh processes; LA fits verify consistent in four fresh processes at m = 0.6 / 6 / 40 — restoring np.convolve fails
the cross-process tests); tests/test_seal_1a_verify.py (the empty set; the mechanism with LA marked unstable).

## Speed

Per evaluation the fixed-order loop is slower than `np.convolve` (0.31 vs 0.02 ms at 450 points and m = 50, 119
taps; 3.9 vs 0.14 ms at the maximum m = 499, 1,167 taps). On whole fits it is small: 12 committed LA Run Fit
requests (seal 1b's, `scripts/seal_la_fit_time.py`, in process) took median 1.16 s before and 1.38 s after
(0.80–3.87 s before, 1.05–3.19 s after).
