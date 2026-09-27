# Public request ceiling (xps.fortierlab.org) — REPORT ONLY (2026-09-26)

Owner, during F2: "measure through the PUBLIC URL … verify it rather than
assume … Report which user-reachable paths exceed whatever the real public
limit is, and what the page shows when they do. Don't fold it into F2."

## 1. The ceiling

The tunnel (`~/.cloudflared/config.yml`) sets no `originRequest` timeouts, so
Cloudflare's edge defaults apply. Probes: one `/api/fit` each, from outside,
production code (main 07e8f46), basinhopping at `n_perturb` 0 on committed
targets (`scripts`-equivalent probe in the session scratchpad):

| target | request took | returned |
|---|---|---|
| 4e5388460b7b | 26.9 s | 200 |
| 005c6346813e | 88.3 s | 200 |
| fba7b6facc1a (168 s locally) | **125.1 s** | **HTTP 524** "error code: 524" |

So the public ceiling is between 88 s and 125 s (Cloudflare documents 100 s
for a proxied response; the 524 arrived at 125 s). Gunicorn's `--timeout 300`
is not the limit a student behind the public URL meets. The worker is not
told: it keeps computing a result nobody receives (up to 300 s, then it is
killed and restarted — one of four production workers is busy meanwhile).

## 2. What the page shows (no silent local fallback)

| failure | Run Fit (incl. "Use this solution") | Auto-Fit C1s Graphite |
|---|---|---|
| edge 524 (> ~100–125 s via the public URL) | "Fit failed: Fit request failed (HTTP 524). Previous peaks and result kept." — red, no local fallback (`resp.ok` false is a server error under A0) | main: "Fit failed to converge or produced an unphysical graphite position." (misleading); fixed in F2 (owner, 2026-09-27): Auto-Fit checks `resp.ok` before parsing, "Auto-fit failed: Fit request failed (HTTP 524)." |
| gunicorn worker timeout (> 300 s; direct :5050 or a slower edge) | "Fit failed: Fit request failed (HTTP 500)." — gunicorn answers 500 when it aborts a sync worker (reproduced with `--timeout 20`), no local fallback | the same unreadable-reply message |
| Auto-Fit's own 120 s `AbortController` | — | "Auto-fit exceeded the 2-minute timeout." (only reachable if the edge is slower than 120 s; the 524 at ≤ 125 s usually wins) |

The A0 concern ("a timeout is a transport failure → the local engine") does
not arise: both timeouts arrive as HTTP errors. Only a dropped connection
(network loss) reaches the local fallback, as designed.

## 3. User-reachable paths against the ceiling

| path | measured | vs ~100–125 s |
|---|---|---|
| Run Fit, basinhopping, page request (`n_perturb` 3), main | 16 multi-component targets: median 386 s, max 1066 s; 14 of 16 > 300 s | **exceeds** — always fails publicly on ≥ 3-component models |
| Run Fit, basinhopping, F2 (no restarts) | median 96 s, max 256 s; 5 of 16 > 125 s (the 6- and 7-component C 1s models, 183–256 s) | **still exceeds on the large models** — F2 fixes the 300 s case, not the public one |
| Run Fit, DS+G graphite + five GL (committed C1s Scan, Trust-Region, page request) | 78.7 s on the production page, 200 | under, little margin (was ~110 s under load in the DS+G unit; the "covered by 300 s" note there is wrong for public users) |
| Run Fit, differential evolution | 2–75 s (CLAUDE.md, committed targets, `n_perturb` 3) | under; the 75 s end is close |
| Auto-Fit C1s Graphite (Trust-Region) | 1.6–1.9 s | far under; its 120 s abort sits above the ceiling and is unreachable in practice |
| Find Peaks (`/api/analyze/start` → 202, poll `/api/analyze/progress`) | background thread; every request short | **unaffected** — the only long-running page path already built for this |
| Batch Fit | local engine only | unaffected |
| Upload, parse-vgd, reference, meta | short | unaffected |

## 4. Suggested unit (not decided)

Long fits on the Find Peaks pattern: `/api/fit/start` (202 + job id, a
background thread, the same poll file), poll for completion, the result read
from the progress record. It removes the edge ceiling for every method
without raising any timeout, lets the page show progress and cancel, and
frees the worker. Smaller interim options: Auto-Fit to check `resp.ok` and name
a 524 / 500 as a timeout; the Run Fit message to say "the server took longer
than the connection allows" for 524.
