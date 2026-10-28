# The app's VGD energy axis is 4.58 eV below Avantage's — which is right? (read-only, 2026-10-28)

**Answer.** Avantage's axis, BE = hν − KE with hν = 1486.68 eV, is the physically right one. The app's VGD reader
puts every point of every committed VGD **4.58 eV too low**. Four pieces of evidence point the same way:

- the files' own energy calibration;
- graphite's C 1s line on the graphite-rich samples;
- the survey lines;
- the lab's own charge references.

**Nothing in the app was changed.** A fix touches saved projects, the reference lines and Auto-Fit (§3), so it is
the owner's decision.

**Labels.** **VERIFIED** means file:line or a committed output: `check.txt` and `check.json` from
`scripts/vgd_energy_axis_check.py`, read on main at a887f02. The property reader is `scripts/vgd_properties.py`, the
same file as on branch unit-b-noise-estimator. **HYPOTHESIS** means not established here; literature values are
labelled as such.

## 1. The offset

- **The app's axis is a constant offset from Avantage's** (VERIFIED, `check.txt`). On every point of all 275
  committed VGDs, app BE − Avantage BE = −4.580000 eV, with a largest deviation of 0. Avantage's axis is computed here
  as 1486.68 − KE, from each file's own start KE and step (`VGSpaceAxes`).
- **That axis is the one Avantage draws** (VERIFIED). Each chart sidecar's "Binding Energy (eV)" axis equals it
  exactly, on all 275 files: `docs/findings/noise-estimator/counting-time.md` §4, branch unit-b-noise-estimator.
- **Where the offset comes from** (VERIFIED). The app computes BE = 1486.6 − KE − 4.5 (`vgd_parser.py:33-34`,
  `:107`). The page sends only the file, so these defaults always apply (`templates/index.html:4031-4032`,
  `:5402-5404`; `app.py:1013-1014`). The difference is (1486.6 − 4.5) − 1486.68 = −4.58.
- **What the file itself records** (VERIFIED). `SourceEnergy` (property 105) is float32(1486.68).
  `ChamberWorkFunction` (406) is 4.2. Avantage subtracts no work function from the stored KE.

## 2. Evidence that Avantage's axis is the physical one

1. **The calibration record** (VERIFIED: the strings, identical in all 275 files). Property 981, "Calibration Energy
   Scale", reads: "12:43:52 March 11, 2026, Ag3d = 368.209eV, Cu2p = 932.587eV, Au4f = 83.9537eV, CuLVV = 567.997eV".
   - These are binding energies on the instrument's own scale.
   - The Cu L₃VV Auger line is the independent check. An Auger line's kinetic energy does not depend on the photon
     energy. Under BE = hν − KE with the file's hν, BE 567.997 eV means KE = 918.683 eV.
   - HYPOTHESIS (reference values quoted from memory, not checked here): ISO 15472 tabulates Cu L₃VV at about
     918.69 eV kinetic energy, and Au 4f₇/₂ 83.95, Ag 3d₅/₂ 368.21 and Cu 2p₃/₂ 932.62 eV binding energy for Al Kα.
   - The record therefore says the instrument's binding-energy scale is hν − KE, calibrated on metals that do not
     charge. Subtracting another 4.5 eV for a work function counts it twice (HYPOTHESIS: the stored KE is already on
     the calibrated, Fermi-referenced scale, which the identity above supports).
2. **Graphite's C 1s line.** The apex of the high-resolution C 1s scans (VERIFIED, `check.txt`):
   - **284.40 eV on Avantage's axis** in every graphite-rich sample: 1 UCl4-graphite, 5 B4C-BN-graphite, 9
     B4C-graphite, 9 UCl4-graphite; median 284.40, range 284.30–284.40.
   - 279.82 eV on the app's axis.
   - HYPOTHESIS, literature: graphitic carbon is near 284.4–284.5 eV, and no carbon species sits near 280 eV.
3. **The survey lines** (VERIFIED, `check.txt`): the median apex in a window that holds the line on both axes.

   | line | Avantage's axis | app's axis | HYPOTHESIS: typical literature range |
   |---|---|---|---|
   | C 1s | 284.0 | 279.4 | 284–289 |
   | O 1s | 532.0 | 527.4 | about 529–534 |
   | Cl 2p | 198.0 | 193.4 | about 198–200 (chloride) |
   | U 4f₇/₂ | 380.0 | 375.4 | about 377–381 (U(0)–U(IV)) |

   Only Avantage's axis puts these lines where these elements appear.
4. **The lab's own charge references** (VERIFIED, `check.txt`, read from the committed `*.proj.zip`).
   - **Graphite.** Every tab corrected on graphitic C 1s (284.50) recorded the line at 279.67–279.85 eV on the app's
     axis, which is 284.25–284.43 on Avantage's. That is within 0.07–0.25 eV of the reference, the size of a small
     residual charge.
   - **The insulators.** The B 1s (BN 190.7, B₂O₃ 193.0) and U 4f (380.6) references sit 1.2–1.4 eV below their
     reference on Avantage's axis. HYPOTHESIS: plausible charging of insulating BN / UCl₄ under the flood gun.
   - **What the app's numbers mean.** The lab's charge shifts of −4.65 to −6.0 eV are this offset plus 0.07–1.4 eV of
     real charging.

## 3. What the offset reaches in the app (VERIFIED code; the consequences HYPOTHESIS where marked)

- **The VGD reader.** `vgd_parser.py:33-34` / `:107` holds the defaults. Its docstring calls them the "standard Thermo
  lab configuration". The route `/api/parse-vgd` (`app.py:1013-1014`) and the page (sends only the file) fix them.
- **Charge correction absorbs it.** A charge-corrected spectrum is shifted rigidly, so fitted chemistry
  (positions after correction, areas, shapes) is unaffected. Uncorrected binding energies, and the size of the shown
  charge shift (−4.74 instead of −0.16 for graphite), are not.
- **Saved projects** store the raw energies in the app's frame (`rawBE`, `templates/index.html:13709`) together with
  their charge shift. HYPOTHESIS: they stay self-consistent whatever the reader does later. A fixed reader would load
  the same VGD 4.58 eV higher, so an old project and a fresh load of its file would differ by that much (each correct
  with its own shift).
- **The reference lines.** `xps_reference.py:10-17`, `:26`, `:245-246` converts Auger kinetic energies to apparent
  binding energy as hν − KE − work function, "the same convention as vgd_parser". `tests/test_xps_reference.py:137`
  and `:313` pin the work function at 4.5.
  - HYPOTHESIS: if the tabulated Auger KEs are Fermi-referenced, as the calibration's Cu L₃VV entry is, the Auger
    markers on a charge-corrected axis sit 4.5 eV too low. This needs checking against the reference data's sources.
- **Other files.** HYPOTHESIS: CSV, TSV and XLSX files carry whatever binding energies were exported; an Avantage
  export would carry Avantage's axis. A VGD and its own Avantage export would then load 4.58 eV apart.
- **Auto-Fit C1s Graphite** derives its shift from the fitted graphite centre. Its gate (data midpoint 270–315 eV,
  `isC1sTab`) accepts either axis.

## 4. What a fix would involve (for the owner, not done)

- **The reader.** Read hν from the file (`SourceEnergy`, 105), or use 1486.68, with no work function: BE = hν − KE.
  The route's `work_function` parameter would become unused or need a new meaning.
- **Saved projects.** Leave old projects as saved (their `rawBE` and shift agree). Optionally say on load that a VGD
  loaded today sits 4.58 eV higher than one loaded before the fix.
- **The Auger reference conversion** and its pinned tests, after checking the source data's KE reference.
- **Students' notes and docs**: charge shifts will be about 4.6 eV smaller, and raw positions will match Avantage.

## Generator

`venv/bin/python scripts/vgd_energy_axis_check.py --json docs/findings/vgd-energy-axis/check.json > docs/findings/vgd-energy-axis/check.txt`
(about 20 s; all 275 committed VGDs, the seven committed projects).
