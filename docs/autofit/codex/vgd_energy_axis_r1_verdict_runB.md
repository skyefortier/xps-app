Reviewed **commit `4f08103`**. The working files changed externally during review; findings below use the requested commit’s line numbers. I made no changes.

The central offset survives: both committed outputs reproduce exactly. Independently decoding all **275 files / 145,875 points** gives one offset, `−4.580000000000155 eV`, with correct intensity ordering. Every XML sidecar’s axis endpoints match `1486.68 − KE`. Property names and property 981 decode consistently in every file.

1. **MAJOR — Survey maxima are presented as identified elemental lines.**  
   `docs/findings/vgd-energy-axis/README.md:49–58`; `scripts/vgd_energy_axis_check.py:83–88`.

   The generator searches every elemental window in every survey, without establishing that the element or peak is present. It reports U 4f₇/₂ in **72 surveys**, including B₄C/graphite and BN/graphite samples, although only **33 surveys** have UCl₄ in their sample designation.

   Reproduction: `2 B4C-graphite 50%, …/XPS Survey_0.VGD`, `_5.VGD`, and `_7.VGD` all contribute **203 eV** as “Cl 2p.” The window is 195–204 eV, so these pass the endpoint rejection despite being outside the document’s chloride range.

   The numerical medians reproduce, but that does not verify the line identifications or justify “Only Avantage’s axis puts these lines where these elements appear.” Restricting U/Cl to UCl₄ samples still gives **380/198 eV**, so the supporting argument can be retained with appropriate qualification.

2. **MAJOR — Saved reference settings do not establish “real charging.”**  
   `docs/findings/vgd-energy-axis/README.md:59–66`; `scripts/vgd_energy_axis_check.py:125–133`.

   The arithmetic is correct, but line 66 promotes the explicitly hypothetical charging explanation into a conclusion. These are saved settings, sometimes propagated between regions; they do not exclude chemical shifts, reference selection errors, or entry errors.

   Reproduction across the seven archives:
   - 120 spectrum tabs have nonzero shifts; only **112** have parseable `ccObs`/`ccLit`.
   - All 112 satisfy `ccShift = ccObs − ccLit`.
   - The observed reference lies outside the tab’s spectrum in **36/72 graphitic-reference tabs** and **11/40 other tabs**.
   - `4-GTA UCl4-BN.proj.zip`, entry `spectrum_9_U4f_Scan_3.json`, records observed **274.67**, reference **280.67**, shift **−6**, while its raw spectrum spans **365.42–400.42 eV**.

   Report the residuals as recorded settings consistent with charging, not verified measurements of charging.

3. **MINOR — The ISO values mix standards and source configurations.**  
   `docs/findings/vgd-energy-axis/README.md:39–40`.

   ISO 15472:2010 Table 2 gives monochromated Al Kα values **Au 83.96**, **Ag 368.21**, **Cu 932.62 eV**. It lists Cu L₃VV as apparent BE **567.93 eV for unmonochromated Al Kα**, not 918.69 eV KE. [ISO 15472 text](https://previewnorm.com/iso/ISO%2015472-2010%20PDF.pdf).

   **918.69 eV**, explicitly Fermi-referenced, appears in **ISO 17974:2002 Table 2**. [ISO 17974 text](https://standards.iteh.ai/catalog/standards/iso/d87d8fde-7ec1-46c2-bd17-a20bc19fc981/iso-17974-2002).

   The HYPOTHESIS label correctly flags uncertainty, but the attribution needs correction.

4. **MINOR — “Exactly” and the sidecar evidence need narrower wording.**  
   `docs/findings/vgd-energy-axis/README.md:21–25`; `scripts/vgd_energy_axis_check.py:80`.

   The deviation from literal `−4.58` is **1.54543×10⁻¹³ eV**. The generator compares against its floating-point `APP_OFFSET`, then rounds the deviation. This is harmless numerically but does not establish literal decimal equality.

   Also, the XML files contain chart bounds, **no per-point data**. They independently corroborate the endpoints; the interior axis comes from the stored start/step and linear reconstruction. State that distinction.

5. **MINOR — The impact inventory omits active consumers, and two citations are stale.**  
   `docs/findings/vgd-energy-axis/README.md:27–28,70–87,91–95`.

   Add:
   - `/api/upload`, `app.py:934,956` → `parser.py:60–67` → the same strict VGD reader.
   - Actual frontend Auger conversion: `templates/index.html:16385`.
   - Legacy apparent-BE→KE conversion: `templates/index.html:16342`. Its work-function terms cancel when both conversions remain consistent.
   - Work-function-dependent photoelectron visibility checks, including `templates/index.html:17149,17439`, which also change if the shared default changes.

   The cited upload lines `4031–4032` and `5402–5404` are unrelated code at this commit. Correct locations are **4077–4079** and **5451–5454**. The older heuristic `parser.parse_vgd` exists but is bypassed by `parse_file`.

6. **MINOR — “Shown charge shift” has the opposite sign.**  
   `docs/findings/vgd-energy-axis/README.md:73–74`.

   Stored `ccShift` is negative here, and `getCorrectedBE` correctly subtracts it (`templates/index.html:5639–5641`). But the display explicitly uses **`−state.ccShift`** (`:5617–5618`). Thus the example is stored **−4.74**, displayed **+4.74 eV**.

7. **MINOR — Carbon wording exceeds the measurements.**  
   `docs/findings/vgd-energy-axis/README.md:45–48,53`.

   **284.40 eV is each listed sample’s median**, not every individual apex; some are 284.30. All seven sample summaries match `check.txt`, and the folder-based sample labels are correct, including the nested ninth-sample files.

   The 284–289 eV range is not general to all carbon: carbides occur lower, relevant to these B₄C samples. Thermo lists metal-carbide C 1s around **283 eV**. [Thermo carbon reference](https://www.thermofisher.com/de/de/home/materials-science/learning-center/periodic-table/non-metal/carbon.html). “No carbon species sits near 280 eV” is an unsupported universal claim.

The remaining checks pass with limits: survey endpoint rejection works; translated windows select corresponding points. High-resolution scans bypass that rejection, but **none of their maxima is an endpoint**. The Cu arithmetic, **1486.68 − 567.997 = 918.683 eV**, is correct. An external Auger KE provides an independent physical consistency reference; the metadata conversion is not an independent measurement of stored KE. The Fermi-reference explanation and Auger-marker consequence appropriately remain hypotheses. Corrected spectra remain invariant only when their charge shifts are adjusted consistently.

VERDICT: NO-GO
