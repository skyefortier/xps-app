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
(`python scripts/seal_la_matrix.py summarise <dir> before after final xps2`):

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

### On the final code, and on the second machine (owner, 2026-10-16: the deploy goes to the i9 AND xps2)

The AFTER side was run again on the final LA code (55d99ca: the tap range below, on 1d's round-12 fixes ac2fda6), on
both machines, from the same 107 requests and the same script. (The branch was later rebased onto 1d's round-13 fixes;
those touch the compare endpoint's validator, the link walks and the comparator, not LA's evaluation — the LA code is
the same, and the full suite was rerun on the final stack.)

| machine | environment | fresh 1 | fresh 2 | shaken | gunicorn | all |
|---|---|---|---|---|---|---|
| i9 (`matrix/final/`) | macOS x86_64, Python 3.12.13, Apple Accelerate | 107 / 0 | 107 / 0 | 107 / 0 | 107 / 0 (4 workers) | **428 / 428** |
| xps2 (`matrix/xps2/`) | Linux 6.8 x86_64, 1 vCPU, Python 3.12.3, scipy-openblas 0.3.31 | 107 / 0 | 107 / 0 | 107 / 0 | 107 / 0 (2 workers) | **428 / 428** |

(consistent / unconfirmed; no mismatch anywhere; every fit HTTP 200 with success true.) On xps2 the requests were
re-fitted THERE and verified there, so each machine's matrix is that machine's own repeatability. xps2's run used production's virtualenv read-only
(/opt/xps-app/venv: numpy 2.4.4, scipy 1.17.1, lmfit 1.3.4, asteval 1.0.8, the i9's pins) from a separate clone of the
commit (`matrix/xps2/run_xps2.sh`, `provenance.json`: commit 55d99ca, clean, one software identity), at nice 19 beside
production; its temporary gunicorn had 2 workers, production's count on that 961 MB machine.

### Across the machines

A verification is a recomputation: a record made on one machine and checked on the other reads CONSISTENT when the
recomputation reproduces it exactly, and UNCONFIRMED — never `mismatch` — when it does not, because the two numerics
identities differ (Python 3.12.13 vs 3.12.3, the OS, the BLAS: `NUMERICS_IDENTITY_KEYS`). (Round 2 of this review
corrected an earlier statement here that a record could only be confirmed by its own identity.) Measured, every record
checked once on the other machine (`matrix/cross/`, `cross.sh`; Codex round 2 found the same counts independently):

| records | made on | checked on | consistent | unconfirmed | mismatch |
|---|---|---|---|---|---|
| the 107 LA fits of the final code | i9 | xps2 | 56 | 51 | 0 |
| the 107 LA fits of the final code | xps2 | i9 | 53 | 54 | 0 |
| seal 1b's 221 records WITHOUT LA (GL, asym-GL, Gaussian, DS, DS+G …) | i9 (a46cd3f) | xps2 | 119 | 102 | 0 |
| the same 221 — control | i9 (a46cd3f) | i9 (final code) | 221 | 0 | 0 |

So about half of the records made on one machine are unconfirmed on the other, LA or not: the elementwise arithmetic
the lineshapes use (exp, power, …) is not bit-identical between macOS and Linux's math libraries (Codex round 2: 55 of
214 xps2 LA curves evaluate to other bits on the i9), and the control shows it is the platform, not the code. This is
not something the LA unit can change — it fixes LA within each machine — and it matters for a deployment to both
machines: a fit saved on one site and re-checked on the other may read "unconfirmed" (shown as recorded), never wrong.

Across the machines as FITS (information, not verification — `python scripts/seal_la_matrix.py across`, the fit compared as
/api/compare-fits compares it, `matrix/across.txt`): of the 107 requests fitted on the i9 and on xps2, 106 are the same
fit within rounding and 101 have the same scattered starts; none is bit-identical (the optimiser's arithmetic differs
between the platforms, CLAUDE.md "Reproducibility"). The one fit that differs (f91e7b75720c, UCl4_on_graphite)
differs by 2e-6 of its χ² — the same record differs by the same amount on the i9 alone between np.convolve and the
fixed-order sum (before vs after), a fit whose minimum is flat to that level; five differ only in a "not better" scattered start's χ²ᵣ (≤ 2e-6) and one in a scattered start
that converged on one machine and not the other. These are optimiser outcomes on two platforms whose arithmetic
differs (the table above); they are not isolated to any one cause. Within each machine, every one of the 856
re-evaluations above reproduced its record bit for bit.

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

## Speed (owner 2026-10-16: accepted as is; no FFT convolution — repeatability on both machines first)

Per evaluation the fixed-order sum is slower than `np.convolve`'s BLAS dot (0.21 vs 0.007 ms at 150 points and 119
taps; with the tap range, 0.5 vs 0.04 ms at 150 points and m = 499). Whole fits, every seal-1b LA request (107) timed
in process on clean checkouts of both sides AT THE SAME TIME, so both saw the same load (`scripts/seal_la_fit_time.py`,
`matrix/time_before.json`, `matrix/time_after.json`; every response 200 with success true): median 1.26 s → 1.51 s,
total 520 s → 564 s (+8 %), median ratio per request 1.23. The fitted kernels in this corpus are short (the widest 33
taps). The largest increase is not the loop's cost: one request (5374a59f1c40) takes 17.5 s → 36 s reproducibly
(three timings each side) and reaches the same fit (χ²ᵣ, areas, certificate and starts identical); profiled, the
optimiser made 98,558 LA evaluations instead of 52,546 at the same cost each (0.11 vs 0.10 ms) — the new rounding sent
a minimisation along a longer path to the same minimum. Synthetic worst cases (two LA components on the 150-point
well-posed grid, Trust-Region, n_perturb 3, n_starts 3; three timings each): m held at the page default 50, about
20 s → 45 s; m held at 150, 3.7 s → 16 s; m held at 499 (1,167 taps on 150 points), 1.4 s → 18.5 s before the tap
range and ≈ 5 s with it; m free from 50, 1.6 s → 3.4 s. The tap range (only the taps that reach the window are summed)
changes no bit (4,000 random cases against the every-tap form; the numerics manifest records it as equivalent).
