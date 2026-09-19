# Optimiser disagreement — correction: the shipped request (n_perturb = 3)

Targets analysed: **202** (own-model re-fits 107, not-yet-fitted starts 95); Trust-Region and LM each run 5 times with the page's `n_perturb: 3` (random, unseeded). Reference = lowest χ²ᵣ seen in any run of the target (best known, not ground truth).

## 1. The UI default, as shipped, versus the earlier n_perturb = 0 measurement

Share of Run Fit outcomes (Trust-Region) whose area fractions are further than the threshold from the reference. For n_perturb = 3 the rate is averaged over the 5 repeats; 'ever' = in at least one repeat, 'always' = in all five.

| start | threshold | n_perturb=0 | n_perturb=3 (mean of repeats) | ever (of 5) | always (of 5) |
|---|---|---:|---:|---:|---:|
| all (n=202) | > 1 pp | 14 (6.9 %) | 5.1 % | 13 (6.4 %, Wilson 3.8–10.7) | 8 (4.0 %) |
| all (n=202) | > 5 pp | 9 (4.5 %) | 4.2 % | 9 (4.5 %, Wilson 2.4–8.2) | 7 (3.5 %) |
| saved-solution re-fit (n=107) | > 1 pp | 3 (2.8 %) | 1.1 % | 2 (1.9 %, Wilson 0.5–6.6) | 1 (0.9 %) |
| saved-solution re-fit (n=107) | > 5 pp | 1 (0.9 %) | 0.9 % | 1 (0.9 %, Wilson 0.2–5.1) | 1 (0.9 %) |
| not-yet-fitted start (n=95) | > 1 pp | 11 (11.6 %) | 9.7 % | 11 (11.6 %, Wilson 6.6–19.6) | 7 (7.4 %) |
| not-yet-fitted start (n=95) | > 5 pp | 8 (8.4 %) | 7.8 % | 8 (8.4 %, Wilson 4.3–15.7) | 6 (6.3 %) |

Same, by reduced chi-square (default's χ²ᵣ above the reference by more than 1 %):

| start | n_perturb=0 | n_perturb=3 (mean of repeats) | ever | always |
|---|---:|---:|---:|---:|
| all (n=202) | 18 (8.9 %) | 5.8 % | 16 (7.9 %) | 7 (3.5 %) |
| saved-solution re-fit (n=107) | 7 (6.5 %) | 3.0 % | 5 (4.7 %) | 1 (0.9 %) |
| not-yet-fitted start (n=95) | 11 (11.6 %) | 9.1 % | 11 (11.6 %) | 6 (6.3 %) |

Run Fit is not repeatable on **8** of 202 targets (4.0 %): the five Trust-Region repeats of the identical request differ from each other by more than 1 pp of area fraction, because the perturbation is random.

Levenberg-Marquardt with n_perturb = 3: success=false in 25 of 1010 runs; Trust-Region: 0 of 1010.

## 2. What a Trust-Region / LM cross-check would catch (both as shipped, n_perturb = 3)

Each of the 5 repeats pairs one Trust-Region run with one LM run of the same request. 'Flag' = the two differ by more than the threshold in area fraction (or LM did not converge). 'Default is off' = the Trust-Region result is further than the same threshold from the reference.

| start | threshold | pairs | default off | of those, flagged (sensitivity) | default fine | of those, flagged (false-alarm rate) | flagged overall |
|---|---|---:|---:|---:|---:|---:|---:|
| all | > 1 pp | 1010 | 52 | 33 (63 %) | 958 | 33 (3.4 %) | 66 (6.5 %) |
| all | > 5 pp | 1010 | 42 | 25 (60 %) | 968 | 27 (2.8 %) | 52 (5.1 %) |
| saved-solution re-fit | > 1 pp | 535 | 6 | 4 (67 %) | 529 | 3 (0.6 %) | 7 (1.3 %) |
| saved-solution re-fit | > 5 pp | 535 | 5 | 3 (60 %) | 530 | 0 (0.0 %) | 3 (0.6 %) |
| not-yet-fitted start | > 1 pp | 475 | 46 | 29 (63 %) | 429 | 30 (7.0 %) | 59 (12.4 %) |
| not-yet-fitted start | > 5 pp | 475 | 37 | 22 (59 %) | 438 | 27 (6.2 %) | 49 (10.3 %) |
| not-yet-fitted, ≥ 2 peaks | > 1 pp | 430 | 46 | 29 (63 %) | 384 | 30 (7.8 %) | 59 (13.7 %) |
| not-yet-fitted, ≥ 2 peaks | > 5 pp | 430 | 37 | 22 (59 %) | 393 | 27 (6.9 %) | 49 (11.4 %) |

When the pair disagrees by more than 1 pp, which of the two has the lower χ²ᵣ (ties within 1e-3 relative):

Trust-Region better 24, LM better 16, tie 1.

After taking the better of the pair (the proposed behaviour), how often is the REPORTED fit still off the reference:

| start | threshold | reported fit off (mean of repeats) | of those, the pair had flagged |
|---|---|---:|---:|
| all | > 1 pp | 39 of 1010 (3.9 %) | 20 (51 %) |
| all | > 5 pp | 34 of 1010 (3.4 %) | 17 (50 %) |
| saved-solution re-fit | > 1 pp | 5 of 535 (0.9 %) | 3 (60 %) |
| saved-solution re-fit | > 5 pp | 4 of 535 (0.7 %) | 2 (50 %) |
| not-yet-fitted start | > 1 pp | 34 of 475 (7.2 %) | 17 (50 %) |
| not-yet-fitted start | > 5 pp | 30 of 475 (6.3 %) | 15 (50 %) |

## 3. Targets where the shipped default is ever more than 5 pp from the reference

| project | tab | start | peaks | repeats off (of 5) | worst pp | n_perturb=0 pp |
|---|---|---|---:|---:|---:|---:|
| 8-JT Graphite.proj.zip | C1s Scan_7 | batch | 5 | 4 | 23.6 | 23.6 |
| 8-JT Graphite.proj.zip | C1s Scan_6 | batch | 5 | 3 | 23.1 | 23.1 |
| 8-JT Graphite.proj.zip | C1s Scan_5 | batch | 5 | 5 | 21.8 | 21.8 |
| 8-JT Graphite.proj.zip | C1s Scan_3 | batch | 5 | 5 | 21.5 | 21.5 |
| 8-JT Graphite.proj.zip | C1s Scan_1 | batch | 5 | 5 | 21.1 | 21.1 |
| 8-JT Graphite.proj.zip | C1s Scan_8 | batch | 5 | 5 | 20.8 | 20.8 |
| 1-GTA UCl4-graphite one set of | C1s Scan_4 | batch | 6 | 5 | 15.2 | 15.2 |
| 1-GTA UCl4-graphite one set of | C1s Scan_0 | own | 6 | 5 | 11.3 | 11.3 |
| Cl2p_projfit_test.proj.zip | C1s Scan_4 | batch | 6 | 5 | 11.1 | 11.1 |
