# Unit B, next step — the counting time recorded in the VGD files (read-only, 2026-10-27)

**Question (owner, 2026-10-27):** decode the counting time from the VGD files, their XML sidecars and the parsers —
dwell, number of scans, channels / detector — and test whether CPS × effective time gives integer-like counts on the
committed files. If it does, Poisson noise becomes exact for raw (unsmoothed) data.

**Answer in one line:** the files record the dwell and the number of scans, and the acquisition was stepped point by
point. But **no common counting time T makes the stored values whole counts**: none of the 275 committed files admits
any T up to its own acquisition time, exactly or approximately, and none admits T = c × scans × dwell for any c ≤ 1024.
The noise also does not scale with the recorded counting time. So σ = √N cannot be recovered from these files.

Labels as in [README.md](README.md): **VERIFIED** (file:line or a committed output, read on main at a192f78; the
outputs are `counting_time.txt` / `counting_time.json`, generator `scripts/noise_counting_time.py`, property reader
`scripts/vgd_properties.py`, tests `tests/test_noise_counting_time.py`) or **HYPOTHESIS**.

---

## 1. What the files record

**Where the parameters are.** Every committed `.VGD` is an OLE compound file. The app reads three of its streams:
`VGData`, the stored intensities; `VGDataAxes`, the point count; and `VGSpaceAxes`, the start KE and the step
(`vgd_parser.py:75`, `:81`, `:88`). It reads nothing else. The acquisition parameters sit in a property-set stream
with undocumented numeric ids (VERIFIED: one stream of 72 or 73 properties per file, `counting_time.txt`). olefile's property reader misreads
that stream: several properties are vectors of variants, and its string reader runs past them. For example, it
returns property 6 as `'Nexsa_G2\x00\x00\x03\x00…'`. `scripts/vgd_properties.py` reads it by the MS-OLEPS format.
The XML sidecars are chart descriptions only: series, axes, titles. They hold no acquisition parameters (VERIFIED).
Neither does the one committed Avantage project file (`9 A to G.vgp`), which is a "Processing Document" of data
references and a chart grid (VERIFIED).

**The ids that matter.** Each identification below is by evidence, not documentation. Thermo does not publish the ids.

| id | value(s) in the 275 files | read as | label | evidence |
|---|---|---|---|---|
| 305 | 0.05 (202 files), 0.01 (73) | dwell time per step, s | HYPOTHESIS (the name), VERIFIED (the relation) | 0.01 on every survey and 0.05 on every high-resolution region; elapsed time follows points × p305 × p306 with slope 1.005 (row 303/304) |
| 306, 328 | 4 (202), 2 (73) | number of scans | as above | equal to each other in every file; same split as 305 |
| 404 | 50 (202), 200 (73) | pass energy, eV | HYPOTHESIS | 200 on surveys, 50 on high resolution: the usual pairing |
| 303 → 304 | e.g. 04:23:39 → 04:24:40 | acquisition start and end (FILETIME, whole seconds) | HYPOTHESIS (the name), VERIFIED (the relation) | **elapsed = 1.005 × points × dwell × scans + 20.95 s**, residuals −3.3 … +2.7 s over all 275 files; elapsed − points × dwell × scans = 17.8 … 23.8 s. So each energy point was given dwell × scans of acquisition, one after another, plus a fixed ~21 s |
| 105 | float32(1486.68) in every file | photon energy, eV (Al Kα) | HYPOTHESIS | see §4 |
| 406 | 4.2 in every file | unidentified (a work function would be one reading) | HYPOTHESIS | — |
| 331 | `C:\AvantageSystem\Signatures\18-10-2023\Detector.vgd` | a detector "signature" file on the instrument PC, not in the committed data | VERIFIED (the string), HYPOTHESIS (what it holds) | — |
| 981 | "12:43:52 March 11, 2026, Ag3d = 368.209eV, Cu2p = 932.587eV, Au4f = 83.9537eV …" | the energy-scale calibration | HYPOTHESIS | — |
| 6, 17 | `Nexsa_G2`, `v6.7.0 : Build 00086` | instrument, Avantage version | VERIFIED (the strings) | — |

**What the files do not say.** No property holds 128 or any other channel count (VERIFIED: no numeric property
equals 128 in any of the 275 files). The detector model is therefore not in the files. The Nexsa G2's detector has 128 channels
according to Thermo's datasheet as cited in the round-4 review (HYPOTHESIS, not checked here). Nor do the files
record whether, or how, Avantage combines the channels, corrects them (dead time, the detector signature), or bins
them onto the energy grid.

**Two acquisition settings cover every file** (VERIFIED, `counting_time.txt`). All 73 surveys: dwell 0.01 s,
2 scans, pass energy 200 eV, step 1 eV. All 202 high-resolution regions (B1s, C1s, Cl2p, N1s, U4f): dwell 0.05 s,
4 scans, pass energy 50 eV, step 0.1 eV.

**The parsers.** `vgd_parser.py` reads only the three streams above (`:75-88`). For an overlay file it averages the
scans (`:98`); no committed file has one. No other parser reads a unit or a counting time: CSV, TSV, TXT, XY and XLSX
intensities are "counts or CPS" (`parser.py:47`) and nothing is stored about them (VERIFIED).

## 2. Is the stored value counts / T for one effective time T?

**The test is exact and complete within its stated error model; there is no search heuristic.** It assumes one
common T for every point of a file. A different T for each point (for instance, edge points seen by fewer channels)
cannot be tested without a detector model the files do not record.

If y_i = N_i / T, rounded when stored, there are integers N_i with |y_i − N_i / T| ≤ δ_i. Here δ_i = 2 ulp(y_i),
which allows up to four half-ulp roundings in Avantage's division. For each value, the admissible T form a union of
intervals [N / (y + δ), N / (y − δ)]. The test intersects these sets in exact rational arithmetic (`fractions.Fraction`):

1. First each gap between neighbouring distinct values. A gap must be a positive multiple of 1/T, which narrows T cheaply.
2. Then each value, which pins the lattice at 0.

An empty result proves that no such T exists in the range. A non-empty one lists every admissible T, including the
multiples of the true T, which are always admissible.

`tests/test_noise_counting_time.py` (8 tests; the mutations that matter are caught) checks that it:

- **finds** both counterexamples the round-3 review gave against the earlier heuristic search (counts / 10 000 s and
  counts / 1000 s with 1e8-count values), and Poisson counts / 0.2 s together with their multiples;
- **refuses** a 1 % smooth correction, round 3's near-grid {1, 2, 3 + 4e-15}, an offset lattice whose gaps are all
  multiples of 1/T, and negative values.

**Ranges tested, with results (VERIFIED, `counting_time.txt`; no constraint deferred in any file):**

- **(a) Every T from 1e-9 s up to the file's own elapsed time + 1 s.** One energy is counted for at most as long as
  the acquisition lasted, whatever the detector does in parallel. Only one channel can sit at a given energy at any
  instant (HYPOTHESIS: a dispersive analyser; the elapsed time is property 303 → 304, read as above).
  **Admissible in 0 of 275 files.** The gap bound alone (T ≥ 1 / (smallest gap + δ)) already exceeds the elapsed
  time in 158 files; the value constraints exclude the remaining 117.
- **(b) Every decoded candidate T = c × scans × dwell, c = 1 … 1024,** whatever its length. c stands for a channel or
  pass count: c = 128 gives 25.6 s for high-resolution regions and 2.56 s for surveys. Each candidate is tested in a
  band covering the float32 dwell and its decimal. **Admissible in 0 of 275 files.**

**"Integer-like", approximately.** At each candidate in (b), the test uses the Rayleigh statistic
R = |mean exp(2πi y T)| over the points with y·T ≤ 1e5. Near-integers give R ≈ 1; with no structure,
p = exp(−m R²). The 1024 candidates form one family per file, judged by Bonferroni. Results (VERIFIED):

- **Integer-like at the 1 % family level in 0 of 275 files.** The smallest family p over the 275 files is 0.014,
  about what chance gives across that many files.
- At c = 1 (T = dwell × scans), R ≤ 0.142 in every file.
- The control: Poisson counts / 0.2 s give R > 0.999, and the same counts with a 1 % correction give m·R² < 9 (tests).

**So the stored CPS are not whole counts over any common time.** That includes T = dwell × scans, which is what
"CPS × effective time" would most naturally mean, and any multiple of it up to 1024. The physical bound caps the
search at the acquisition's own length, about 50–90 s per file. The usual way to undo a CPS conversion therefore
does not work on these files.

**What would explain it** (HYPOTHESIS, not tested; nothing in the files settles it). Avantage might combine the
detector's channels with non-integer weights: a per-channel gain or efficiency from the detector signature (id 331),
dead-time correction, or rebinning of channel energies onto the 0.1 / 1 eV grid. Any of these would leave no lattice.
Rebinning would also correlate neighbouring points.

## 3. Does the noise follow the counting time anyway?

Suppose the stored value is counting noise over T_eff = f × dwell × scans, with the same detector factor f in every
region, and any smooth correction factor. Then the variance scale k (variance = k·y) obeys k × dwell × scans = 1/f
in every region. Measured with the two estimators of [README.md](README.md) §3 that do well on independent noise
(VERIFIED, `counting_time.txt`, all 275 files):

| region | files | dwell × scans | pass energy, step | k (scaled_d4), median [10–90 %] | k × dwell × scans | varmean k × dwell × scans | rho1_d4 (independent: −0.80) |
|---|---|---|---|---|---|---|---|
| B1s | 50 | 0.2 s | 50 eV, 0.1 eV | 0.727 [0.547, 0.884] | 0.146 | 0.192 | −0.784 |
| C1s | 73 | 0.2 s | 50 eV, 0.1 eV | 0.691 [0.491, 0.960] | 0.138 | 0.282 | −0.735 |
| Cl2p | 6 | 0.2 s | 50 eV, 0.1 eV | 0.637 [0.619, 0.671] | 0.127 | 0.140 | −0.725 |
| N1s | 40 | 0.2 s | 50 eV, 0.1 eV | 0.617 [0.479, 0.821] | 0.123 | 0.266 | −0.778 |
| U4f | 33 | 0.2 s | 50 eV, 0.1 eV | 0.644 [0.532, 0.800] | 0.129 | 0.146 | −0.784 |
| Survey | 73 | 0.02 s | 200 eV, 1 eV | 1.008 [0.908, 1.114] | 0.020 | 0.022 | −0.748 |

**Reported, not concluded.**

- **The prediction fails.** The surveys had a tenth of the counting time per point, but their estimated k is only
  about 1.5 times the high-resolution k, not 10 times. k × dwell × scans differs between the two settings by a factor
  of about 6.5.
- **A detector factor proportional to pass energy / step does not rescue it.** That form predicts a factor of 25
  between the two settings.
- **What this does not show.** It does not show the noise is not counting noise. The estimators assume independent
  points, and §4 of the README measured lag-1 difference estimators underestimating correlated noise 4–30×. rho1_d4
  is slightly short of the independent −0.80 in every region (−0.725 … −0.784). The two settings could be correlated
  differently, and that diagnostic cannot measure how much (README §4: it misses a 3-point moving average). A noise
  floor, such as electronic or dark counts, would also break the proportionality (README §5 measured varmean's intercept: median 0, 90th percentile 0.105 of
  the median intensity).
- **What it does show.** One counting-time model with one detector factor does not describe the measured noise of
  both settings. Recovering σ would need the acquisition and processing model that the files do not hold.

## 4. A by-product, not a noise question: the app's VGD energy axis is 4.58 eV below Avantage's

While decoding I compared the sidecars' axes with the app's reader. What I found (VERIFIED, `counting_time.txt`, all
275 files):

- **Avantage's axis.** Each chart sidecar titles its x axis "Binding Energy (eV)". Its Minimum and Maximum equal
  1486.68 − KE at the data's last and first points exactly, where KE comes from the file's own start and step
  (`VGSpaceAxes`) and 1486.68 is property 105.
- **The app's axis.** The app's VGD reader computes BE = hν − KE − work function with hν = 1486.6 and a work function
  of 4.5 (`vgd_parser.py:33-34`, `:107`). The page sends only the file (`templates/index.html:4031-4032`,
  `:5402-5404`), so the route's defaults apply (`app.py:1013-1014`).
- **The result.** Every VGD's energy axis in the app is **4.58 eV lower** than the axis Avantage draws for the same
  file.
- **The lab's saved projects** carry charge shifts of −4.65 to −6.0 eV, plus 46 tabs at 0 (VERIFIED, `counting_time.txt`, read
  from the committed `*.proj.zip`).

HYPOTHESES:

- The KE in `VGSpaceAxes` is already referred to the Fermi level by the instrument's calibration (id 981 names Ag 3d,
  Cu 2p and Au 4f positions), so subtracting a work function again is a double correction. On this reading, every
  charge correction saved in the lab's projects has absorbed this 4.58 eV.

Rigid shifts cancel in a charge-corrected fit, so the fitted chemistry is unaffected. Uncorrected binding energies,
the size of the displayed charge shift, and anything compared with absolute energies before correction (the
reference-line overlay, for instance) are not. **This is outside Unit B and nothing was changed.** It is reported
here for the owner's decision.

## 5. Limits

- Every property identification is HYPOTHESIS. The relations they enter (the elapsed-time regression, the
  sidecar-axis identity) are VERIFIED.
- The exact test assumes one common T per file and δ = 2 ulp. A larger rounding error (more than four half-ulp
  roundings) or a different T for each point is not tested.
- The physical cap in range (a) rests on the timestamps being the acquisition's start and end (HYPOTHESIS, supported
  by the regression).
- Range (b) covers c ≤ 1024 at any length.
- §3 uses estimates whose bias under correlation is not known for these data.
- Earlier figures: §2 and §5 of the README measured 230 of the 275 committed VGDs. The other 45, in
  `9 UCl4-graphite 4%, no kapton …/`, were outside the glob `test_data/*.DATA/*.VGD`. This step reads all 275. Its
  per-region k agree with README §5's medians where both exist (C1s 0.691 vs 0.709, U4f 0.644 vs 0.661, B1s and N1s
  identical, Survey 1.008 vs 1.008).
