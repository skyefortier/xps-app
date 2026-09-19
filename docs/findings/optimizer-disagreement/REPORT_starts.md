# Optimiser disagreement — is a different START a better second opinion than a different local method?

Targets: **202**. Reference = lowest χ²ᵣ seen in any run of the target (best known, not ground truth). 'Default' = Trust-Region with the page's n_perturb: 3 (5 repeats). 'Scatter K' = best χ²ᵣ of K Trust-Region fits from seeded random starts.

## 1. How often the REPORTED fit is more than 5 pp (1 pp) from the reference

| start | default alone | better of default + LM | better of default + nudge | better of default + scatter 3 | + scatter 5 | + scatter 10 |
|---|---:|---:|---:|---:|---:|---:|
| all, > 5 pp (n=1010) | 42 (4.2 %) | 34 (3.4 %) | 42 (4.2 %) | 20 (2.0 %) | 20 (2.0 %) | 20 (2.0 %) |
| saved-solution re-fit, > 5 pp (n=535) | 5 (0.9 %) | 4 (0.7 %) | 5 (0.9 %) | 5 (0.9 %) | 5 (0.9 %) | 5 (0.9 %) |
| not-yet-fitted start, > 5 pp (n=475) | 37 (7.8 %) | 30 (6.3 %) | 37 (7.8 %) | 15 (3.2 %) | 15 (3.2 %) | 15 (3.2 %) |
| all, > 1 pp (n=1010) | 52 (5.1 %) | 39 (3.9 %) | 51 (5.0 %) | 27 (2.7 %) | 22 (2.2 %) | 20 (2.0 %) |
| saved-solution re-fit, > 1 pp (n=535) | 6 (1.1 %) | 5 (0.9 %) | 5 (0.9 %) | 7 (1.3 %) | 7 (1.3 %) | 5 (0.9 %) |
| not-yet-fitted start, > 1 pp (n=475) | 46 (9.7 %) | 34 (7.2 %) | 46 (9.7 %) | 20 (4.2 %) | 15 (3.2 %) | 15 (3.2 %) |

## 2. As a FLAG: when the default is more than 5 pp off, does the second opinion differ from it by more than 5 pp?

| start | default off (pairs) | LM flags | nudge flags | scatter-3 best flags | scatter-5 | scatter-10 | false alarms when default is fine: LM | nudge | scatter-3 | scatter-5 | scatter-10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 42 | 25 (60 %) | 12 (29 %) | 24 (57 %) | 24 (57 %) | 29 (69 %) | 2 of 968 (0.2 %) | 3 of 968 (0.3 %) | 0 of 968 (0.0 %) | 0 of 968 (0.0 %) | 0 of 968 (0.0 %) |
| saved-solution re-fit | 5 | 3 (60 %) | 0 (0 %) | 0 (0 %) | 0 (0 %) | 0 (0 %) | 0 of 530 (0.0 %) | 0 of 530 (0.0 %) | 0 of 530 (0.0 %) | 0 of 530 (0.0 %) | 0 of 530 (0.0 %) |
| not-yet-fitted start | 37 | 22 (59 %) | 12 (32 %) | 24 (65 %) | 24 (65 %) | 29 (78 %) | 2 of 438 (0.5 %) | 3 of 438 (0.7 %) | 0 of 438 (0.0 %) | 0 of 438 (0.0 %) | 0 of 438 (0.0 %) |

A scatter 'false alarm' needs care: the best of K scattered starts differing from a default that is within 5 pp of the reference means the scattered fit found a WORSE-or-equal χ²ᵣ solution elsewhere, or a better one that is the new reference.

## 3. Starting on a bound

Targets whose request starts a freely varying shape parameter within 1 % of a bound: **52** of 202 (24 not-yet-fitted, 28 re-fits).
Of the 9 targets where the default is ever > 5 pp off, 7 start on a bound; of the 193 others, 45 do.

Cost: 10 scattered Trust-Region fits took a median 1.8 s per target (90th percentile 4.1 s, max 48.9 s).

## 4. The targets where the default is ever > 5 pp off

| project | tab | start | default χ²ᵣ (5 repeats) | nudge χ²ᵣ | scatter-10 best χ²ᵣ | reference χ²ᵣ | scatter-10 best off (pp) |
|---|---|---|---|---:|---:|---:|---:|
| 1-GTA UCl4-graph | C1s Scan_0 | own | 4.6, 4.6, 4.6, 4.6, 4.6 | 4.62 | 4.62 | 3.53 | 11.3 |
| 1-GTA UCl4-graph | C1s Scan_4 | batch | 19.1, 19.1, 19.1, 19.1, 19.1 | 19.06 | 18.58 | 18.21 | 6.5 |
| 8-JT Graphite.pr | C1s Scan_1 | batch | 17.6, 17.6, 17.6, 17.6, 17.6 | 17.55 | 17.55 | 12.30 | 21.1 |
| 8-JT Graphite.pr | C1s Scan_3 | batch | 25.9, 26.9, 26.9, 26.9, 25.9 | 26.91 | 26.91 | 14.80 | 21.5 |
| 8-JT Graphite.pr | C1s Scan_5 | batch | 33.9, 33.9, 33.9, 33.9, 51.9 | 51.91 | 17.26 | 17.26 | 0.0 |
| 8-JT Graphite.pr | C1s Scan_6 | batch | 70.6, 18.5, 70.6, 38.3, 18.5 | 70.61 | 18.45 | 18.45 | 0.0 |
| 8-JT Graphite.pr | C1s Scan_7 | batch | 35.8, 64.2, 35.8, 15.5, 35.8 | 64.17 | 15.47 | 15.47 | 0.0 |
| 8-JT Graphite.pr | C1s Scan_8 | batch | 35.5, 32.3, 32.3, 35.5, 35.5 | 35.55 | 15.95 | 15.95 | 0.0 |
| Cl2p_projfit_tes | C1s Scan_4 | batch | 5.3, 5.3, 5.3, 5.3, 5.3 | 5.29 | 4.28 | 4.28 | 0.0 |
