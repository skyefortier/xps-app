# Unit A1 — Find Peaks determinism (2026-09-29)

Owner: "Find Peaks' answer must not depend on server load or on the
optimiser's own termination flags. Count refits, not seconds … Judge
convergence by whether the refit actually reached the minimum … no new
magnitude threshold. Acceptance: identical output under light and heavy
machine load, and Scan_6 returns MG2." Scope check first:
`docs/findings/fit-termination-scope/README.md` (Run Fit shares the flag
problem; its step is A2).

## 1. What changed (`autofit/engine.py`)

| site | before | after |
|---|---|---|
| `run_stability_analysis` | refits stopped at a 25 s per-candidate deadline (shared with the primary fit) | exactly `n_refits` refits, always |
| `compare_models` screen | stopped at 60 % of a 240 s sweep budget | every candidate screened |
| `compare_models` sweep | stopped starting candidates when 240 s − 25 s had elapsed | every selected candidate evaluated |
| proposal pass | 60 s pass budget, 35 s stability budget, 15 s minimum-fit refusals (`insufficient_budget`) | none — counted work only (≤ 3 accepted rounds × ≤ 3 attempts) |
| bound-fixed refit | 25 s deadline | `n_refits` refits |
| `fit_candidate` convergence | `leastsq`'s `success` flag; on a failed fit ONE warm restart from the exit point whose flag was taken | the CERTIFICATE (`_certify_minimum`); warm restart removed |

Removed constants: `CANDIDATE_TIMEOUT_SEC`, `TOTAL_ANALYSIS_TIMEOUT_SEC`,
`PROPOSAL_CANDIDATE_TIMEOUT_SEC`, `PROPOSAL_STABILITY_TIMEOUT_SEC`,
`PROPOSAL_MIN_FIT_BUDGET_SEC`, `SCREEN_BUDGET_FRACTION`, `WARM_RESTART_MAX_NFEV`.
The clock is read only for the proposal pass's `wall_time_sec` telemetry
(`proposal_pass_timings`, not in the payload). `analysis_truncated` /
`timed_out` are never set (kept for the payload's shape).

**The certificate** (owner-accepted as proposed): after the `leastsq` fit,
restart from its end point with Trust-Region (`least_squares`, native bounds);
repeat from each improved point until a restart improves chi2 by less than
Trust-Region's own `ftol` (1e-8, read from scipy's signature — no new
constant; relative, so scale-free); at most `CERTIFY_MAX_RESTARTS` = 50
restarts (a count); out of restarts or a non-finite restart = not converged.
Trust-Region, not Levenberg-Marquardt, restarts: an LM restart from a stall
point reproduces the stall (the removed warm restart is exactly that).

## 2. Measurements

**What the old "~30-evaluation convergence" was.** 8-JT C1s Scan_7, MG2,
stability refit 0: `leastsq` stalls at chi2 5220 (18 000 evaluations, flag
False); the warm restart met MINPACK's xtol in 30 evaluations and reported
success there. That point is NOT a minimum (a descent still lowers chi2 — the
KKT check in `tests/autofit/test_fit_certificate.py`). The certified point is
chi2 5166, a genuine CONSTRAINED LOCAL minimum (free gradients ~0, all ten
parameters on bounds pushing outward) — a worse basin than the chi2r 5.21
least_squares reaches from the same start along another path. Correction to
the scope report: "37.6 vs 5.21" was a bad basin, not a point far from a
minimum; "converged" is the right verdict for it now.

**Restarts needed** (8 committed C 1s scans × the 4 gate candidates,
primaries + all refits, 208 fits): 1: 10, 2: 173, 3: 14, 4: 5, then one each
at 5, 6, 8, 9, 11, 21 (flat valleys). With 5 allowed four real minima went
uncertified (8-JT Scan_5's MG2 and MG3 primaries → AG2 at chi2r 42.5 won); 50
certifies all 208. 75 fits `leastsq` flagged as FAILED were certified (capped
at a minimum — the Scan_6 case), none of 208 left uncertified.

**Acceptance — Scan_6.** Gate options: MG2 (chi2r 2.03), as main with budgets
off; main under load had given AG2.

**Acceptance — load.** The page's own request (conductor, C 1s, proposals on,
n_refits 4, endpoint average 3; full grammar, 29–30 candidates screened, 6
deep) on 1-GTA Scan_6 and 8-JT Scan_7, idle, idle again, and with 8 CPU
burners (load average 11):

| | structural fields (winner, tier, candidate set, filter reasons, persistence, ranks, peak roles) | max Δcentre | max rel Δamplitude | max Δarea % |
|---|---|---|---|---|
| idle vs idle | identical (both scans) | 0.20 meV | 3.9e-4 | 7.6e-4 pp |
| idle vs heavy | identical (both scans) | 0.24 meV | 4.9e-4 | 9.4e-4 pp |

The residual numeric differences are Trust-Region's arithmetic jitter (the
BLAS alignment effect CLAUDE.md records; owner decision 2026-09-21 accept and
disclose), present idle-to-idle — not load. Find Peaks used only the
byte-reproducible Levenberg-Marquardt before; the certificate's Trust-Region
restarts bring the jitter in. Wall time (page request, idle): main 208–213 s,
A1 236–239 s; under load A1 342–350 s (main would have truncated).

**Screen interaction (found here).** With every screen fit certified to a
genuine local minimum, the screen now compares honest minima — and MG2's
single screen start on 8-JT Scan_7 lands in a poor one (BIC* 2277, as on main)
while most others improve, so MG2 ranks 19th of 28 and is screened out,
though its deep evaluation reaches the best BIC* of all. Page request: main
MG2 (BIC* 1776.8) vs A1 MG3 (1787.6). Measurement on six more scans: §3.

## 3. The page's own Find Peaks request: main vs A1 (7 distinct committed C 1s scans, idle)

4 of 7 winners identical (UCl4 Scan_8, UCl4 Scan_3, 1-GTA Scan, 1-GTA Scan_6 —
the last MG2 on both). 3 differ:

| scan | main (winner, BIC*) | A1 (winner, BIC*) | why |
|---|---|---|---|
| 8-JT Scan_5 | MG2, 1882.6 | MG3, 1901.5 | MG2 SCREENED OUT on A1 (screen rank 21 of 28) — its single screen start lands in a poor local minimum while the certificate carries most other screen fits to much better ones |
| 8-JT Scan_7 | MG2, 1776.8 | MG3, 1787.6 | the same (MG2 screen rank 19 of 28) |
| 1-GTA Scan_2 | MG3, 1803.9 | MG2, 1816.0 | MG3 deep-evaluated on both with the SAME chi2r 1.388; on main one MG3 slot was "absent" (BIC* drops its parameters) because refits the old flag called non-converged counted as empty; certified, the slot is populated in every refit — no credit. A1 is the honest one here |

The two screen cases pick a model with a WORSE BIC* than main's. The screen's
single-start ranking is pre-existing; the certificate changes which candidates
it happens to favour. OWNER DECISION (see the report).
