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
- What this establishes, and what not (Codex round 1): `np.convolve` is the one step observed to evaluate
  differently, and with it replaced nothing a verification recomputes was seen to differ (the matrix below, 428
  verifications). That is bounded evidence on this machine and build, not a proof that every operation a
  verification recomputes (`power`, `exp`, the backgrounds, DS+G's FFT, the statistics) is bit-stable on every
  platform. A failed evaluation identity on a stable lineshape reads MISMATCH, so a second unstable step would show
  itself rather than hide.

## Fix

`fitting._convolve_same_fixed_order`: every output the sum over the kernel taps in increasing order, accumulated
from 0 by elementwise numpy operations — no reduction, no BLAS. Same length and offset as `np.convolve(…,'same')`
trimmed to the grid (bit for bit on integer-valued inputs, every grid and kernel length 1-64, odd and even, the
kernel longer than the grid too); differs from it by rounding only (≤ 2.4e-15 relative over 3,000 random sizes).
Its order and association are fixed by the code, so neither alignment nor the BLAS build can change a bit; what can
is the floating-point environment itself (a different rounding mode or flush-to-zero setting), which nothing in the
application changes — the claim is reproducibility under the same, default, floating-point environment. The page's
`laTrueCasaXPS_array` already sums in this order (it still differs by rounding in exp / pow, inside its parity
tolerance; the JS suite's parity harnesses pass). `NOT_BIT_STABLE_SHAPES` is empty: an LA curve that differs under the
same numerics now reads MISMATCH like every other lineshape (the UNCONFIRMED mechanism kept, tested with LA marked
unstable). `NUMERICS_VERSION` 2026-10-15, recorded in tests/fixtures/numerics_manifest.json (no seal is deployed, so
no deployed record is affected; a 1b record made before reads "other numerics").

## The acceptance matrix: seal 1b's 107 LA requests in its four settings (`matrix/`)

The logged criterion: the 107 LA records of seal 1b, in all four settings. 1b's records were made with np.convolve,
so their curves are not the fixed-order sum's; the REQUESTS are the corpus. `scripts/seal_la_matrix.py` re-fits each
of the 107 (89 committed, 18 synthetic) through the real `/api/fit` route with its own request (a fresh
full-precision upload of its own data) and verifies the new record exactly as 1b did: two fresh processes, a
process with shaken memory, and a 4-worker gunicorn over HTTP. Run twice from the same script and the same 1b
records (`matrix/run.sh`): BEFORE on 5fad7de (seal-1d, np.convolve) and AFTER on 1d2b255 (this unit), each a clean
detached checkout (`dirty=0`, `matrix/run.log`), one software identity per side (numerics 2026-10-13 / 2026-10-15,
`matrix/*/provenance.json`, which also holds every record's R and O sha256), four gunicorn workers each
(`matrix/*/gunicorn.log`). Every fit on both sides HTTP 200 with success true. `matrix/summary.txt`
(`python scripts/seal_la_matrix.py summarise <dir>`):

| setting | before: consistent / unconfirmed | after |
|---|---|---|
| fresh process 1 | 94 / 13 | **107 / 0** |
| fresh process 2 | 104 / 3 | **107 / 0** |
| shaken memory | 66 / 41 | **107 / 0** |
| gunicorn, 4 workers | 43 / 64 | **107 / 0** |
| all four | 307 / 121; 70 records unconfirmed at least once (59 committed, 11 synthetic) | **428 / 0** |

No verification on either side read `mismatch`; every unconfirmed one failed the `components` check (an LA curve).
Every LA record that was unconfirmed is confirmed, in every setting. (1b's own run, at a46cd3f, had 53 of its 107
unconfirmed at least once; the count per run varies with which processes differ, as 1b recorded — the fix is the
difference between 121 and 0 on the same requests under the same harness.)

## Measured through the page (`scripts/seal_la_confirm_measure.py`, `confirm_before.json`, `confirm_after.json`)

The 121 committed fits: Run Fit on every tab, its own check, then five more checks each ("check again") — on a
4-worker gunicorn like production, the same script against seal-1d (87679b1, np.convolve) and this branch (3cc562e):

| | before | after |
|---|---|---|
| LA fits CURRENT right after Run Fit | 37 / 54 (17 unconfirmed: components) | **54 / 54** |
| LA re-checks confirmed | 190 / 270 | **270 / 270** |
| fits without LA | 67 / 67; re-checks 335 / 335 | 67 / 67; re-checks 335 / 335 |

Every unconfirmed fit becomes confirmed. (The step-8 save-size run had seen 10 unconfirmed of 121 with 2 workers; with
4 workers there are more processes to differ, hence 17.)

The servers' own logs for this browser run were not kept with it (the page records each tab's states, not the
server's identity); the matrix above is the measurement with full provenance.

Tests: tests/test_la_deterministic.py (numpy's semantics: to rounding over 3,000 random sizes, odd and even kernels,
and exactly on every length 1-64 — each offset mutant fails it; the same bits at every alignment and in five fresh
processes; LA fits verify consistent in four fresh processes — m free from 0.6 / 6 / 40 (the fit moves it to ~13.4)
and m HELD at 0.6 / 6 / 40 / 499, so those kernels are the ones verified — restoring np.convolve fails the
cross-process tests); tests/test_seal_1a_verify.py (the empty set; the mechanism with LA marked unstable).
tests/envelope_identity.py no longer allows an LA component an extra rounding margin (it allowed for the BLAS dot).

## Speed

Per evaluation the fixed-order loop is slower than `np.convolve` (0.31 vs 0.02 ms at 450 points and m = 50, 119
taps; 3.9 vs 0.14 ms at the maximum m = 499, 1,167 taps). On whole fits it is small: 12 committed LA Run Fit
requests (seal 1b's, `scripts/seal_la_fit_time.py`, in process) took median 1.16 s before and 1.38 s after
(0.80–3.87 s before, 1.05–3.19 s after).
