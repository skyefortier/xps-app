# The app's VGD energy axis is 4.58 eV below Avantage's — which is right? (read-only, 2026-10-28; revised after the round-1 review)

**Answer.** On the evidence below, Avantage's axis is the physical one: BE = hν − KE with hν = 1486.68 eV. The app's
VGD reader puts every point of every committed VGD **4.58 eV lower** than that. The evidence:

- the files' own energy-calibration record, which states binding energies on the hν − KE scale;
- the high-resolution C 1s apex of the four graphite-rich samples, which sits at graphite's position on Avantage's
  axis.

The survey window maxima and the lab's own charge-correction settings are consistent with this, but are weaker (§2).

**Nothing in the app was changed.** A fix touches saved projects, the reference lines and their tests (§3), so it is
the owner's decision.

**Labels.** **VERIFIED** means file:line or a committed output: `check.txt` and `check.json` from
`scripts/vgd_energy_axis_check.py`, read on main at a887f02. The property reader is `scripts/vgd_properties.py`, the
same file as on branch unit-b-noise-estimator. **HYPOTHESIS** means not established here, including every literature
value. Corrections from the round-1 review (`docs/autofit/codex/vgd_energy_axis_r1_verdict_run*.md`) are marked
"round 1".

## 1. The offset (VERIFIED, `check.txt`)

- **Avantage's axis.** Computed from each file's own start KE and step (`VGSpaceAxes`) as 1486.68 − KE, in the
  reader's own point order. On every point of all 275 committed VGDs, app BE − Avantage BE = (1486.6 − 4.5) − 1486.68
  = −4.58 eV, within floating point (at most 1.6e-13 eV from −4.58; round 1: "exactly" was too strong).
- **The chart sidecars** title their x axis "Binding Energy (eV)". Its Minimum and Maximum equal this axis's ends in
  all 275 files. The sidecars hold the axis range only, not per-point values (round 1).
- **The file records** `SourceEnergy` (property 105) = float32(1486.68) and `ChamberWorkFunction` (406) = 4.2,
  named so by each file's own property dictionary.
- **The app** computes BE = 1486.6 − KE − 4.5 (`vgd_parser.py:33-34`, `:107`). Both upload paths apply those defaults:
  - `/api/parse-vgd` — the page sends only the file (`templates/index.html:4077-4079`, `:5451-5454`), so the route's
    defaults apply (`app.py:1013-1014`);
  - `/api/upload` (`app.py:934`, `:956`) → `parser.py:60-67` → `vgd_parser.parse_vgd`, with its defaults (round 1).
    `parser.py`'s older heuristic VGD reader is bypassed by `parse_file`.

## 2. Which axis is physical

1. **The calibration record** (VERIFIED: the strings, identical in all 275 files).
   - Property 981, "Calibration Energy Scale": "12:43:52 March 11, 2026, Ag3d = 368.209eV, Cu2p = 932.587eV,
     Au4f = 83.9537eV, CuLVV = 567.997eV".
   - These are binding energies on the instrument's scale, calibrated on metals, which do not charge.
   - The Cu L₃VV Auger line is stated as a binding energy too. Under BE = hν − KE with the file's hν that is
     KE = 1486.68 − 567.997 = 918.683 eV.
   - Reference values (HYPOTHESIS, as the round-1 reviews read them; not checked by me):
     - ISO 15472:2010 Table 2, monochromated Al Kα: Au 4f₇/₂ 83.96, Ag 3d₅/₂ 368.21, Cu 2p₃/₂ 932.62 eV; and Cu L₃VV
       as an apparent binding energy of 567.93 eV for unmonochromated Al Kα;
     - ISO 17974:2002 Table 2: Cu L₃VV at 918.69 eV kinetic energy, Fermi-referenced. That is within 0.007 eV of the
       record's 918.683.
     - Round 1: my first version mixed standards and source-specific values from memory.
   - **What this shows:** the instrument's binding-energy scale is hν − KE, calibrated. **What it does not:** it is
     not an independent measurement of the stored KE.
   - HYPOTHESIS: the stored KE is already on the calibrated, Fermi-referenced scale, so subtracting another 4.5 eV for
     a work function counts it twice.
2. **Graphite's C 1s line** (VERIFIED, `check.txt`).
   - **Avantage's axis:** the apex of each high-resolution C 1s scan has a **median of 284.40 eV in each of the four
     graphite-rich samples**: 1 UCl4-graphite, 5 B4C-BN-graphite, 9 B4C-graphite, 9 UCl4-graphite. Individual apexes
     run 284.30–284.40.
   - **The app's axis:** 279.82.
   - HYPOTHESIS, literature: graphitic carbon is near 284.4 eV; carbides lie lower (the B₄C / BN 50 % samples' apex
     median is 283.10 on Avantage's axis).
   - On the app's axis these apexes would sit near 280 eV, where these samples' composition gives no reason to expect
     a carbon line. Round 1: the first version said no carbon species exists there, which is too universal.
3. **Survey window maxima** (VERIFIED as measured; NOT peak identifications — round 1).
   - What was measured: the highest point of each survey in a window holding the line on both axes, for elements in
     the sample's designation only (C and O in every sample).
   - Medians, Avantage's / app's axis: C 1s 284.0 / 279.4, O 1s 532.0 / 527.4, Cl 2p 198.0 / 193.4 (UCl₄ samples),
     U 4f₇/₂ 380.0 / 375.4 (UCl₄ samples), N 1s 397.0 / 392.4, B 1s 189.5 / 184.9.
   - No maximum lies within 1 eV of its window's edge except B 1s (10 of 50).
   - Round 1: the first version counted a background maximum at the window edge (203 eV in a B4C sample) as Cl 2p, and
     reported U and Cl lines for samples without them.
   - HYPOTHESIS, literature: these maxima sit where these elements' lines are expected on Avantage's axis (O 1s about
     529–534, chloride Cl 2p about 198–200, U(IV) 4f₇/₂ about 380), and about 4.6 eV below that on the app's.
   - This is consistent with §2.1–2.2, not independent proof.
4. **The lab's own charge-correction settings** (VERIFIED as recorded; they are settings the user entered, not
   measurements — round 1).
   - **How they are read:** each tab stores the observed raw position (`ccObs`, app's axis) and the reference
     (`ccLit`), with shift = observed − reference (corrected BE = raw − shift, `getCorrectedBE`).
   - **Graphitic C 1s (284.50):** every observed position is 284.25–284.43 on Avantage's axis. The observed position
     lies outside the tab's own energy range — not read off that tab: possibly carried over, possibly mistyped
     (round 2) — in
     36 of 72 (and in 11 of the 40 other settings).
   - **The B 1s, B₂O₃ and U 4f references** leave residuals of −1.2 to −1.4 eV on Avantage's axis. One U 4f tab
     carries a 280.67 eV reference whose observed position (274.67) lies outside its range.
   - HYPOTHESIS: the residuals are charging of the insulating BN / UCl₄ samples; chemical shift, reference choice and
     entry error are not excluded.
   - On the app's axis, every setting is about 4.6 eV further off.

## 3. What the offset reaches in the app

- **The VGD reader and both routes** (VERIFIED, §1). The reader's docstring calls its defaults the "standard Thermo
  lab configuration".
- **Charge correction absorbs it, when the shift is found on the same axis.** A charge-corrected spectrum is shifted
  rigidly, so positions after correction, areas and shapes are unaffected, provided the shift was determined on the
  axis it is applied to. An old shift applied to a re-read VGD on a corrected axis would put every line 4.58 eV too
  high: 284.34 − (−4.74) = 289.08 instead of 284.50 (round 2). Uncorrected binding energies, and the size of the charge shift, are not. The
  lab's graphite shifts are stored as −4.83 to −4.65 eV and shown as +4.65 to +4.83 (the page displays −`ccShift`,
  `templates/index.html:5617-5618`). On Avantage's axis they would be +0.07 to +0.25; for example, −4.74 (20 of the 72)
  would be +0.16. Round 1 corrected the sign; round 2, the example.
- **Saved projects** store the raw energies in the app's frame (`rawBE`, `templates/index.html:13709`) with their
  shift. HYPOTHESIS: they stay self-consistent whatever the reader does later; a fixed reader would load the same VGD
  4.58 eV higher.
- **The reference lines use the same convention** (VERIFIED code, round 1: the frontend sites were missing):
  - `xps_reference.py:10-17`, `:26`, `:245-246`: Auger apparent BE = hν − KE − work function, "the same convention
    as vgd_parser"; the work function is pinned at 4.5 in `tests/test_xps_reference.py:137`, `:313`;
  - `templates/index.html:16385`: the Auger conversion itself;
  - `:16342-16344`: legacy apparent-BE markers converted to KE with the same work function. That subtracts and then cancels
    it, so it is unaffected as long as both ends agree.
  - `:17149`, `:17439`: photoelectron excitation filtering at hν − wf.
  - HYPOTHESIS: if the tabulated Auger KEs are Fermi-referenced, as the calibration's Cu L₃VV entry suggests, the
    Auger markers on a charge-corrected axis sit 4.5 eV too low. Fixing both Al Kα defaults would move them by
    +4.58 eV. Needs checking against the reference data's sources.
- **Other files.** HYPOTHESIS: CSV, TSV and XLSX files carry whatever binding energies were exported; an Avantage
  export would carry Avantage's axis. A VGD and its own export would then load 4.58 eV apart.
- **Auto-Fit C1s Graphite** derives its shift from the fitted graphite centre. Its gate (data midpoint 270–315 eV,
  `isC1sTab`) accepts either axis.

## 4. What a fix would involve (for the owner, not done)

- **The reader** (`vgd_parser.py`). Read hν from the file (`SourceEnergy`, 105), or use 1486.68, with no work
  function: BE = hν − KE. Both routes pass through it.
- **Saved projects.** Leave old projects as saved (their `rawBE` and shift agree). Optionally say on load that a VGD
  loaded today sits 4.58 eV higher than one loaded before.
- **The reference lines** (§3). Change the Auger conversion and excitation filtering together, after checking the
  source data's KE reference, and update their pinned tests.
- **Students' notes and docs:** charge shifts will be about 4.6 eV smaller, and raw positions will match Avantage.

## Generator

`venv/bin/python scripts/vgd_energy_axis_check.py --json docs/findings/vgd-energy-axis/check.json > docs/findings/vgd-energy-axis/check.txt`
(about 20 s; all 275 committed VGDs, their sidecars, the seven committed projects).
