# Unit B, next step — the counting time recorded in the VGD files (read-only, 2026-10-27; revised after the round-1 review)

**Question (owner, 2026-10-27):** decode the counting time from the VGD files, their XML sidecars and the parsers —
dwell, number of scans, channels / detector — and test whether CPS × effective time gives integer-like counts on the
committed files. If it does, Poisson noise becomes exact for raw (unsmoothed) data.

**Answer.**

- **What the files record.** The dwell time and the number of scans, under the files' own property names. They also
  record that two corrections were set for every acquisition: `SignatureCorrected = True` and
  `Acq_TXFN_Correction = True`. A transmission correction is one reading of the second name. The correction
  algorithms themselves are not in the files.
- **The exact test.** Two ranges were tested, under the error model |y − N/T| ≤ 2 ulp(y) with one common T per file:
  (a) every T up to the acquisition's own elapsed time + 1 s, and (b) every T = c × scans × dwell with c ≤ 1024.
  **No such T exists in any of the 275 committed files**, so the stored values are not whole counts over any of these
  times. Range (a) holds on the condition stated in §2: each output energy is collected by at most one channel at a
  time.
- **The approximate test.** At the decoded candidates of range (b) where enough points qualify, no candidate
  survives a correction across all files and candidates. Two files pass the per-file 1 % level, both weakly.
- **Is this a surprise?** Not necessarily. A correction that varies from point to point would remove a lattice
  (HYPOTHESIS). The flags alone do not show that: a constant correction would keep one at a rescaled T (§2).
- **Conclusion.** σ = √N cannot be recovered from these files within what was tested. Recovering it would need the correction algorithms,
  and probably the uncorrected counts, which the files do not store.

Labels as in [README.md](README.md): **VERIFIED** (file:line or a committed output, read on main at a192f78; the
outputs are `counting_time.txt` / `counting_time.json`, generator `scripts/noise_counting_time.py`, property reader
`scripts/vgd_properties.py`, tests `tests/test_noise_counting_time.py`) or **HYPOTHESIS**. Corrections from the
round-1 review (`docs/autofit/codex/unit_b_counting_time_r1_verdict_run*.md`) are marked "round 1".

---

## 1. What the files record

**Where it is.**

- **What the app reads.** Every committed `.VGD` is an OLE compound file. The app reads three streams: `VGData`, the
  stored intensities; `VGDataAxes`, the point count; and `VGSpaceAxes`, the start KE and the step
  (`vgd_parser.py:75`, `:81`, `:88`). It reads nothing else.
- **Where the parameters are.** In a property-set stream of 72 or 73 properties per file (VERIFIED,
  `counting_time.txt`). olefile's property reader returns its strings running past their own end (its LPWSTR branch,
  `olefile.py:2286-2293` in the installed 0.47); property 6 comes back as `'Nexsa_G2\x00\x00\x03\x00…'`.
  `scripts/vgd_properties.py` reads the stream by the MS-OLEPS format instead. Round 1: the first version blamed
  vectors of variants, but the committed files hold no vector properties.
- **The names (round 1).** The stream carries its own **dictionary**, property 0, mapping ids to names. In every one
  of the 275 files it names every id used here exactly as listed below (VERIFIED: 57 or 58 entries,
  `counting_time.txt`). The first version had decoded the values but discarded the dictionary, and labelled every
  name a HYPOTHESIS.
- **What is not there.** The XML sidecars are chart descriptions with no acquisition parameters (VERIFIED). So is the
  one committed Avantage project file, `9 A to G.vgp`, a "Processing Document" (VERIFIED).

**The values** (all VERIFIED, `counting_time.txt`). The names are the files' own; what a name means beyond its
wording is HYPOTHESIS.

| id | name in the file | values over the 275 files |
|---|---|---|
| 305 | `DwellTime` | 0.05 (202 files), 0.01 (73) |
| 306 | `Scans` | 4 (202), 2 (73) |
| 328 | `Current Scan` | equal to `Scans` in every file (HYPOTHESIS: the last scan reached, so every scan completed) |
| 404 | `PassEnergy` | 50 (202), 200 (73) |
| 303, 304 | `AcquisitionStart`, `AcquisitionEnd` | FILETIME, whole seconds |
| 105 | `SourceEnergy` | float32(1486.68) |
| 406 | `ChamberWorkFunction` | 4.2 |
| 311 | `DetectorMode` | 2 (the meaning of the value: HYPOTHESIS, unknown) |
| 313 | `SignatureCorrected` | True in every file |
| 331 | `DetectorSignatureCorrectionPath` | `C:\AvantageSystem\Signatures\18-10-2023\Detector.vgd`, a file on the instrument PC, not in the committed data |
| 415, 416 | `Acq_TXFN_Correction`, `Acq_TXFN_CCorrectionType` | True, 3 in every file |
| 413, 417 | `NumberOfTXFNCoeffs`, `NumberOfPSFCoeffs` | 4, 8 |
| 100000–100003 | (no name) | four values, the same in every file. HYPOTHESIS: the 4 TXFN coefficients |
| 300000–300007 | (no name) | eight values in two sets, one for pass energy 50 and one for 200. HYPOTHESIS: the 8 PSF coefficients (point-spread function) |
| 981, 982 | `Calibration Energy Scale`, `Calibration Detector Efficiency` | "…Ag3d = 368.209eV, Cu2p = 932.587eV, Au4f = 83.9537eV…", "96.9937" |
| 850 | `DataStorageMethod` | 0 |

**Two acquisition settings cover every file** (VERIFIED):

- All 73 surveys: dwell 0.01 s, 2 scans, pass energy 200 eV, step 1 eV.
- All 202 high-resolution regions (B1s, C1s, Cl2p, N1s, U4f): dwell 0.05 s, 4 scans, pass energy 50 eV, step 0.1 eV.

**Timing** (VERIFIED, reproduced by the round-1 review):

- **The relation.** Elapsed (303 → 304) = 1.005 × points × dwell × scans + 20.95 s. The residuals are −3.3 … +2.7 s,
  and elapsed − points × dwell × scans = 17.8 … 23.8 s.
- **What it shows.** Each energy step got dwell × scans of acquisition, plus a fixed ~21 s.
- **What it does not show** (round 1: "stepped point by point" was stronger than this). Whether the detector's
  channels collect several energies at once while the analyser steps, or how much exposure each output bin
  accumulates.

**What the files do not say.**

- **The channel count.** No property is identified as a channel count (VERIFIED: no dictionary name says so, and
  no numeric property equals 128 in any file; round 2: that check cannot exclude a channel count encoded some other
  way). The Nexsa G2's detector has 128 channels according to Thermo's datasheet as cited in the earlier
  review (HYPOTHESIS, not checked here).
- **The corrections.** How the signature and TXFN corrections are computed is not recorded, and neither is any
  uncorrected count.

**The intensity unit** (round 1). The sidecars title the intensity axis `Counts / s` in 268 files and `Counts` in 7
(VERIFIED). All 7 "Counts" files store non-integer values at every point (VERIFIED), so their title does not make
them raw counts. Whether it is a stale display setting is not established. The README's "Counts / s" evidence
covered the 230 files it read; it does not extend unqualified to all 275.

**The parsers** (VERIFIED). `vgd_parser.py` reads only the three streams above (`:75-88`). For an overlay file it
averages the scans (`:98`); no committed file has one. CSV, TSV, TXT, XY and XLSX intensities are "counts or CPS"
(`parser.py:47`), and nothing about their unit or counting time is stored.

## 2. Is the stored value counts / T for one effective time T?

**The test and its error model.**

- **The model.** One common T per file (a different T at each point cannot be tested without a detector model the
  files do not record), and non-negative counts.
- **The equivalence.** y_i = N_i / T, rounded when stored, holds iff there are integers N_i ≥ 0 with
  |y_i − N_i / T| ≤ δ_i, where δ_i = 2 ulp(|y_i|) allows up to four half-ulp roundings.
- **The procedure** (`admissible_times`). Each value gives a union of T intervals, [N / (y + δ), N / (y − δ)]. The test
  intersects these in exact rational arithmetic (`fractions.Fraction`): first each gap between neighbouring distinct
  values, then each value. A gap must be a positive multiple of 1/T, which is implied by the value constraints and
  narrows the set sooner.
- **What it returns** (round 1: the first version could report a superset left by deferred constraints as
  "admissible"):
  - **excluded:** the set is empty, which proves no such T exists in the range;
  - **admissible:** every constraint was applied, and the result lists every admissible T, including the multiples
    of the true T, which are always admissible;
  - **unresolved:** some constraints would split the set too finely and were deferred, so the result is a superset
    only.
  - It also records which constraint emptied the set.

**The tests** (`tests/test_noise_counting_time.py`: 12 tests; dropping the value constraints and setting δ = 0 are
both caught). It:

- **finds** both counterexamples the earlier review gave against the heuristic quantum search (counts / 10 000 s and
  counts / 1000 s with 1e8-count values), and Poisson counts / 0.2 s with their multiples;
- **refuses** a 1 % smooth correction, the near-grid {1, 2, 3 + 4e-15}, an offset lattice whose gaps are all
  multiples of 1/T, and a value below −δ;
- **accepts** a negative value within its rounding as N = 0 (round 1: δ now uses |y|; `np.spacing` of a negative
  number is negative);
- **reports** {1, √2} over [1, 10⁶] and {1e8, 2e8 + 1} over [1, 2] as unresolved (the round-1 reviews' cases).

**Ranges and results** (VERIFIED, `counting_time.txt`; status "excluded" in every file, nothing unresolved):

- **(a) Every T from 1e-9 s up to the file's own elapsed time + 1 s** (timestamps are whole seconds).
  - **The cap.** One output energy is counted for at most as long as the acquisition lasted. This holds **on the
    condition that** at any instant at most one detector channel contributes to a given output energy bin
    (HYPOTHESIS, round 1). The timestamps' names are recorded; this exposure model is not.
  - **Result: excluded in 275 of 275 files.** The smallest gap empties the set in 158 files and the second-smallest
    in the other 117. No value constraint was needed. Round 1: the first version said the value constraints
    excluded the 117.
- **(b) Every decoded candidate T = c × scans × dwell, c = 1 … 1024,** whatever its length.
  - c stands for a channel or pass count: c = 128 gives 25.6 s for high-resolution regions and 2.56 s for surveys.
    Each candidate is tested in a band covering the float32 dwell and its decimal.
  - This range does not depend on the exposure model.
  - **Result: excluded in 275 of 275 files, all by the smallest gap.**

**"Integer-like", approximately: at the decoded candidates of range (b) only** (round 1: this test does not cover
range (a)'s continuum, where every phase concentrates trivially near T = 0).

- **The statistic** (round 1, run B). V = mean cos(2π y T) over the m points with y·T ≤ 1e5, which measures how far
  the phases align with the integers. The first version used the Rayleigh R = |mean exp(2πi y T)|. That ignores where
  the phases point, so a half-integer lattice also gave R = 1, and it needed at least 12 exact points to reach the
  family threshold. The y·T ≤ 1e5 cutoff keeps the phase error from the float32/decimal dwell difference below
  ~0.002 cycles (round-1 review).
- **Which candidates count.** A candidate is evaluated only where at least 10 points qualify.
- **The null.** For independent uniform phases, V·√(2m) is asymptotically N(0, 1), so p = Φ(−V√(2m)). This is not a
  calibrated null for correlated spectra.
- **The family.** The 1024 candidates of a file are judged by Bonferroni, which is conservative where candidates are
  skipped. A perfect lattice on 10 points reaches 1024·Φ(−√20) = 0.004, so the test has the power it claims (tests).
- **Coverage.** Between 58 and 1024 candidates evaluated per file; all 1024 in 113 files.
- **Results** (VERIFIED, `counting_time.txt`):
  - **2 of 275 files** pass the per-file 1 % level: 1 UCl4-graphite / XPS Survey (c = 107, V = +0.083 on 1361 points)
    and 5 B4C-BN-graphite / C1s Scan_6 (c = 60, V = +0.240 on 168 points).
  - **No candidate survives a global correction:** across all files (Bonferroni 275 × 1024) the smallest adjusted p
    is 1.
  - **What the 2 per-file flags mean** (round 2: the first version called them "what chance gives", which is not
    established). Bonferroni bounds each file's false-flag probability from above; it does not set it. Summed over the
    156 024 candidates actually evaluated, the expected number of per-file flags under the stated null is at most
    156 024 × 0.01 / 1024 = 1.52, and that null is not calibrated for these spectra. So the 2 flags are neither
    explained by chance nor evidence of a lattice.
  - Both alignments are weak (whole counts give V ≈ 1), and isolated: at the neighbouring c, V is 0.04/0.01 and
    0.01/0.03. The exact test excludes both candidates anyway.
  - At c = 1 (T = dwell × scans), V lies between −0.124 and +0.125 in every file.
- **The controls** (tests): Poisson counts / 0.2 s give V > 0.999, and with a 1 % correction p > 1e-4. Ten exact
  integers pass the family threshold; a half-integer lattice gives V ≈ −1, p > 0.5.

**So the stored CPS are not whole counts over any common time in the ranges tested, under the stated error model.**
That includes T = dwell × scans, which is what "CPS × effective time" would most naturally mean, and every multiple of
it up to 1024. The usual way to undo a CPS conversion does not work on these files. The bounds matter (round 2): every
stored float is a dyadic rational, so some enormous T always makes every value a whole number. For the first C 1s scan,
T = 2⁴¹ s does exactly that. Such a T has no acquisition meaning, and it lies far outside both ranges.

**Why, as far as the files say** (round 2: the first version stated the cause as recorded). Every file records that a
detector-signature correction and a TXFN correction were set (§1). It does not record the transformations, and the
two unnamed coefficient blocks are their coefficients only by HYPOTHESIS. A constant multiplicative correction would
keep a lattice at a rescaled T, so the flags alone do not explain the result. HYPOTHESIS: a correction that varies from
point to point would leave no common lattice — per-channel gains from the signature file, a transmission function in
KE and pass energy, or a point-spread correction — and rebinning channel energies onto the energy grid would also
correlate neighbouring points.

## 3. Does the noise follow the counting time anyway? (round 1: re-derived)

**The model.** Poisson counts N over T_eff = f × dwell × scans, multiplied by a deterministic correction a:
y = a·N / (f·d·s), so Var(y) = (a / (f·d·s))·E[y] and k·d·s = a/f. The same value in every region would follow only if
a/f were the same in every region. The files record corrections whose coefficients differ between the two settings
(§1), so a need not be. Round 1: the first version wrote 1/f, "with any smooth correction", which a constant
correction already contradicts.

Measured with the two estimators of [README.md](README.md) §3 that do well on independent noise (VERIFIED,
`counting_time.txt`, all 275 files):

| region | files | dwell × scans | pass energy, step | k (scaled_d4), median [10–90 %] | k × dwell × scans | varmean k × dwell × scans | rho1_d4 (independent: −0.80) |
|---|---|---|---|---|---|---|---|
| B1s | 50 | 0.2 s | 50 eV, 0.1 eV | 0.727 [0.547, 0.884] | 0.146 | 0.192 | −0.784 |
| C1s | 73 | 0.2 s | 50 eV, 0.1 eV | 0.691 [0.491, 0.960] | 0.138 | 0.282 | −0.735 |
| Cl2p | 6 | 0.2 s | 50 eV, 0.1 eV | 0.637 [0.619, 0.671] | 0.127 | 0.140 | −0.725 |
| N1s | 40 | 0.2 s | 50 eV, 0.1 eV | 0.617 [0.479, 0.821] | 0.123 | 0.266 | −0.778 |
| U4f | 33 | 0.2 s | 50 eV, 0.1 eV | 0.644 [0.532, 0.800] | 0.129 | 0.146 | −0.784 |
| Survey | 73 | 0.02 s | 200 eV, 1 eV | 1.008 [0.908, 1.114] | 0.020 | 0.022 | −0.748 |

**Reported, not concluded.**

- **What was measured.** The surveys had a tenth of the counting time per point; their estimated k is about 1.5
  times the high-resolution k. So k × dwell × scans differs by about 6.5 between the settings.
- **What it is consistent with.** Counting noise with a/f lower for the surveys by about that factor. That can come
  from the correction a, from the detector factor f, or both (round 2): equal corrections with f larger for the
  surveys by about 6.5 reproduce the measurement as well as equal f with a survey correction about 0.15 of the
  high-resolution one. The factors 10 and 25 follow only if a/f is equal in both settings, or if f is proportional to
  pass energy / step with equal a.
- **Why it decides nothing.** Neither the corrections' size nor the estimators' bias is known:
  - lag-1 difference estimators underestimated correlated noise 4–30× on the synthetic set (README §4);
  - rho1_d4 sits slightly short of the independent −0.80 in every region, and that diagnostic misses a 3-point moving
    average (README §4);
  - a noise floor would add a constant term (README §5 measured varmean's intercept: median 0, 90th percentile 0.105
    of the median intensity).

## 4. A by-product, not a noise question: the app's VGD energy axis is 4.58 eV below Avantage's

**The comparison** (VERIFIED, `counting_time.txt`, all 275 files):

- **Avantage's axis.** Each chart sidecar titles its x axis "Binding Energy (eV)". Its Minimum and Maximum equal
  1486.68 − KE at the data's last and first points exactly. KE comes from the file's own start and step
  (`VGSpaceAxes`); 1486.68 is the decimal that `SourceEnergy` (105) stores as a float32 (round 1: the stored value is
  1486.6800537…).
- **The app's axis.** The app's VGD reader computes BE = hν − KE − work function with hν = 1486.6 and a work function
  of 4.5 (`vgd_parser.py:33-34`, `:107`). The page sends only the file (`templates/index.html:4031-4032`,
  `:5402-5404`), so the route's defaults apply (`app.py:1013-1014`).
- **The result.** Every VGD's axis in the app is **4.58 eV lower** than the one Avantage draws for the same file.
- **The lab's saved projects** (166 spectrum tabs; the one stack tab has no charge shift): 46 have a shift of 0, and
  120 have shifts of −6.00 to −4.65 eV (VERIFIED, `counting_time.txt`, read from the committed `*.proj.zip`; round 1:
  the review counted 167 / 121, apparently including the stack tab).

**HYPOTHESES:**

- The file records a `ChamberWorkFunction` of 4.2 (406). Avantage's axis subtracts no work function from the stored
  KE, which suggests the stored KE is already referred to the instrument's calibrated energy scale (981 names Ag 3d,
  Cu 2p and Au 4f positions). If so, subtracting 4.5 eV again is a double correction.
- Every charge correction saved in the lab's projects has then absorbed this 4.58 eV.
- Which axis is physically right is not established here.

**What it affects.** Rigid shifts cancel in a charge-corrected fit, so the fitted chemistry is unaffected. Uncorrected
binding energies, the size of the displayed charge shift, and anything compared with absolute energies before
correction (the reference-line overlay, for instance) are not. **This is outside Unit B and nothing was changed.** It
is reported for the owner's decision.

## 5. Limits

- **Names and meanings.** The property names are the files' own; what they mean beyond their wording (`DetectorMode`
  2, `Acq_TXFN_CCorrectionType` 3, the unnamed coefficient blocks) is HYPOTHESIS.
- **The exact test** assumes one common T per file, non-negative counts and δ = 2 ulp(|y|). A larger rounding error,
  or a different T at each point, is not tested.
- **Range (a)'s cap** rests on the exposure model in §2. Range (b) does not.
- **The approximate test** covers only range (b)'s eligible candidates.
- **The reader** (`scripts/vgd_properties.py`) handles every type present in these files. Its vector and signed-I1
  branches are pinned by tests only (round 1: it padded each vector element and read I1 unsigned). Types it does not
  know raise an error.
- **§3** uses estimates whose bias under correlation is not known for these data.
- **Earlier figures.** README §2 and §5 read 230 of the 275 committed VGDs; the other 45, in
  `9 UCl4-graphite 4%, no kapton …/`, were outside the glob `test_data/*.DATA/*.VGD`. This step reads all 275. Its
  per-region k agree with README §5's medians where both exist: C1s 0.691 vs 0.709, U4f 0.644 vs 0.661, B1s and N1s
  identical, Survey 1.008 vs 1.008.
