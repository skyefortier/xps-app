# Optimiser disagreement — frequency measurement

Targets with all three methods completed: **202** of 202 (own-model starts 107, batch starts 95).

Disagreement criterion: χ²ᵣ spread > 0.001 (relative) OR area-fraction difference > 0.5 pp.

## 1. How often

| | count | share |
|---|---:|---:|
| the three methods disagree | 61 | 30.2 % |
| the UI default (Trust-Region) is NOT the best (χ²ᵣ > best by > 0.001) | 18 | 8.9 % |
| the UI default is the WORST of the three | 7 | 3.5 % |
| Trust-Region (UI default) not the best | 18 | 8.9 % |
| Levenberg-Marquardt not the best | 39 | 19.3 % |
| basin-hopping not the best | 18 | 8.9 % |
| any method reports success=false | 4 | |

Threshold ladder (share of targets disagreeing):

| fraction tolerance | 0.1 pp | 0.5 pp | 1 pp | 5 pp | 10 pp |
|---|---:|---:|---:|---:|---:|
| targets | 61 (30.2 %) | 49 (24.3 %) | 39 (19.3 %) | 15 (7.4 %) | 12 (5.9 %) |

By kind of start and region:

| group | targets | disagree | default not best | default worst |
|---|---:|---:|---:|---:|
| batch / B1s Scan | 18 | 0 | 0 | 0 |
| batch / C1s Scan | 33 | 20 | 8 | 1 |
| batch / Cl2p Scan | 2 | 0 | 0 | 0 |
| batch / U4f Scan | 42 | 15 | 3 | 2 |
| own / B1s Scan | 20 | 0 | 0 | 0 |
| own / C1s Scan | 37 | 19 | 4 | 1 |
| own / Cl2p Scan | 3 | 0 | 0 | 0 |
| own / U4f Scan | 47 | 7 | 3 | 3 |

## 2. How large, when they disagree

| among disagreeing targets | median | 90th pct | max |
|---|---:|---:|---:|
| area-fraction spread (pp) | 1.58 | 19.62 | 23.58 |
| component-area spread, components ≥ 1 % (%) | 14.0 | 152.9 | 200.0 |
| χ²ᵣ spread (%) | 8.97 | 317.65 | 2455.28 |

In 1 of 61 disagreeing targets the BEST solution drives a component to zero amplitude (vs 0 of 141 agreeing targets).

## 3. Is it predictable in advance?

AUC = probability that the predictor is larger for a disagreeing target than for an agreeing one (0.5 = no information; computed from the START model and the data only).

| predictor (known before fitting) | median, disagree | median, agree | AUC |
|---|---:|---:|---:|
| n_peaks | 5 | 4 | 0.71 |
| n_points | 190 | 200 | 0.50 |
| min_gap_over_fwhm | 0.27 | 0.97 | 0.34 |
| weakest_amp_ratio | 0.0265 | 0.099 | 0.31 |
| max_counts | 6.71e+04 | 3.16e+04 | 0.69 |
| has_voigt | 0 | 0 | 0.44 |
| has_lacx | 0 | 0 | 0.44 |
| is_batch_start | 1 | 0 | 0.57 |
| n_unlinked | 5 | 3 | 0.72 |

## 3b. What the UI default costs a student (Trust-Region's answer vs the best of the three)

| start | targets | default's fractions off by > 1 pp | > 5 pp | > 10 pp | default χ²ᵣ worse than best by > 1 % | > 10 % |
|---|---:|---:|---:|---:|---:|---:|
| own | 107 | 2 (1.9 %) | 0 (0.0 %) | 0 (0.0 %) | 6 (5.6 %) | 0 (0.0 %) |
| batch | 95 | 10 (10.5 %) | 8 (8.4 %) | 8 (8.4 %) | 11 (11.6 %) | 7 (7.4 %) |
| all | 202 | 12 (5.9 %) | 8 (4.0 %) | 8 (4.0 %) | 17 (8.4 %) | 7 (3.5 %) |

Independence caveat: 155 distinct spectra across 6 projects (several projects share raw spectra with different models, and scans within a project are repeats of one sample).

| project | targets | disagree | default not best | default off by > 5 pp |
|---|---:|---:|---:|---:|
| 1-GTA UCl4-graphite one set of U doublets.pr | 38 | 9 | 2 | 1 |
| 4-GTA UCl4-BN.proj.zip | 38 | 1 | 1 | 0 |
| 8-JT Graphite.proj.zip | 19 | 17 | 9 | 6 |
| B4C-UCl4.proj.zip | 38 | 2 | 1 | 0 |
| Cl2p_projfit_test.proj.zip | 31 | 15 | 4 | 1 |
| UCl4_on_graphite.proj.zip | 38 | 17 | 1 | 0 |

## 3c. Simple advance rules (target = fraction spread > 1 pp between methods)

Materially disagreeing targets: 39 of 202.

| rule (from the START model only) | flagged | recall | precision |
|---|---:|---:|---:|
| n_peaks >= 5 | 89 (44 %) | 77 % | 34 % |
| min gap/FWHM < 0.5 (overlap) | 89 (44 %) | 77 % | 34 % |
| weakest/strongest amplitude < 0.05 | 89 (44 %) | 77 % | 34 % |
| n_peaks >= 5 AND overlap < 0.5 | 89 (44 %) | 77 % | 34 % |
| n_peaks >= 4 OR overlap < 0.5 | 159 (79 %) | 100 % | 25 % |
| n_peaks >= 3 | 178 (88 %) | 100 % | 22 % |

success=false cases:

- 1-GTA UCl4-graphite one  U4f Scan_4 (batch): Levenberg-Marquardt — Tolerance seems to be too small. Could not estimate error-bars.
- 1-GTA UCl4-graphite one  U4f Scan_8 (batch): Levenberg-Marquardt — Tolerance seems to be too small. Could not estimate error-bars.
- UCl4_on_graphite.proj.zi U4f Scan_4 (batch): Levenberg-Marquardt — Tolerance seems to be too small. Could not estimate error-bars.
- UCl4_on_graphite.proj.zi U4f Scan_8 (batch): Levenberg-Marquardt — Tolerance seems to be too small. Could not estimate error-bars.

## 4. Worst cases

| project | tab | start | χ²ᵣ TR | χ²ᵣ LM | χ²ᵣ BH | fraction spread (pp) | best |
|---|---|---|---:|---:|---:|---:|---|
| 8-JT Graphite.proj.zip | C1s Scan_7 | batch | 64.171 | 93.538 | 15.470 | 23.6 | basin-hopping |
| 8-JT Graphite.proj.zip | C1s Scan_6 | batch | 70.606 | 97.590 | 18.451 | 23.1 | basin-hopping |
| 8-JT Graphite.proj.zip | C1s Scan_5 | batch | 51.907 | 64.929 | 17.259 | 21.8 | basin-hopping |
| 8-JT Graphite.proj.zip | C1s Scan_3 | batch | 26.906 | 26.906 | 14.796 | 21.5 | basin-hopping |
| 8-JT Graphite.proj.zip | C1s Scan_1 | batch | 17.553 | 17.553 | 12.298 | 21.1 | basin-hopping |
| 8-JT Graphite.proj.zip | C1s Scan_8 | batch | 35.545 | 36.043 | 15.952 | 20.8 | basin-hopping |
| 8-JT Graphite.proj.zip | C1s Scan_0 | batch | 16.123 | 140.178 | 16.123 | 19.6 | Trust-Region |
| 1-GTA UCl4-graphite one  | C1s Scan_4 | batch | 19.056 | 18.212 | 18.212 | 15.2 | basin-hopping |
| 8-JT Graphite.proj.zip | C1s Scan_4 | batch | 18.749 | 25.043 | 18.749 | 13.6 | Trust-Region |
| Cl2p_projfit_test.proj.z | C1s Scan_0 | batch | 10.470 | 20.724 | 10.470 | 12.6 | basin-hopping |
| Cl2p_projfit_test.proj.z | C1s Scan_3 | batch | 12.038 | 19.875 | 12.038 | 12.2 | basin-hopping |
| Cl2p_projfit_test.proj.z | C1s Scan_4 | batch | 5.291 | 86.444 | 4.284 | 11.1 | basin-hopping |
| 1-GTA UCl4-graphite one  | C1s Scan_7 | batch | 8.016 | 8.016 | 8.735 | 8.4 | Levenberg-Marquardt |
| UCl4_on_graphite.proj.zi | C1s Scan_6 | batch | 2.028 | 8.472 | 2.028 | 6.8 | Trust-Region |
| UCl4_on_graphite.proj.zi | C1s Scan_7 | batch | 6.149 | 8.405 | 6.149 | 5.4 | Trust-Region |
