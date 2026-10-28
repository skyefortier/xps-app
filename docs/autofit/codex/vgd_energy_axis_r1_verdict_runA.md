The central −4.58 eV finding holds, but the write-up overstates two supporting arguments. **No BLOCKER; two MAJOR findings.** Nothing was changed.

I reproduced `check.txt` exactly and `check.json` structurally exactly. Independent binary decoding confirmed matching energy/intensity ordering in all 275 files. Property 981 and its dictionary name decode correctly and identically throughout.

1. **MAJOR — Survey window maxima are presented as verified elemental line positions.**  
   [scripts/vgd_energy_axis_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/scripts/vgd_energy_axis_check.py:59), [README.md:49](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/docs/findings/vgd-energy-axis/README.md:49).

   `apex()` rejects endpoints but performs no peak-presence, prominence, background, or identity check. The generator consequently reports U 4f maxima in 72/73 surveys, including 39 surveys from folders without U in their sample designation. That designation alone cannot exclude contamination, but neither does an interior maximum establish uranium.

   Concrete reproduction: `2 B4C-graphite 50%, …/XPS Survey_0.VGD` contributes a “Cl 2p” apex at **203 eV**. Intensities rise from approximately 600 at 195 eV to 893 at 203 eV, then 887 at 204 eV. The endpoint rule accepts this near-edge background maximum as a chloride line.

   The reported medians reproduce, but their elemental interpretation is not VERIFIED. Establish peak identity/presence before pooling, or describe these strictly as window maxima and qualify the conclusion at line 58.

2. **MAJOR — Saved charge-reference settings do not establish “real charging.”**  
   [README.md:59](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/docs/findings/vgd-energy-axis/README.md:59), especially line 65; [scripts/vgd_energy_axis_check.py:129](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/scripts/vgd_energy_axis_check.py:129).

   The arithmetic is correct: all 112 applicable records satisfy `ccShift = ccObs − ccLit`; `getCorrectedBE()` subtracts that shift. The graphite and insulator numbers reproduce.

   However, those fields record user settings, not independently validated line measurements. A concrete counterexample is:

   ```text
   4-GTA UCl4-BN.proj.zip
     spectrum_9_U4f_Scan_3.json
     ccObs = 274.67; ccLit = 280.67; ccShift = −6
     rawBE range = 365.42–400.42
   ```

   This appears in `check.txt:53`. It establishes a requested −6 eV correction, not a measured U reference or −1.42 eV of physical charging. Other settings can legitimately be transferred between regions, so out-of-range references are not automatically errors.

   Call the remaining differences **residuals relative to the chosen references**. Charging is a HYPOTHESIS; chemical shifts, reference choice, fitting, calibration uncertainty, and entry errors have not been excluded. The categorical “real charging” sentence exceeds the evidence.

3. **MINOR — “Exactly” and “largest deviation 0” conceal rounding; sidecars verify endpoints.**  
   [README.md:21](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/docs/findings/vgd-energy-axis/README.md:21), [scripts/vgd_energy_axis_check.py:80](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/scripts/vgd_energy_axis_check.py:80).

   The unrounded maximum error relative to −4.58 is **1.5454 × 10⁻¹³ eV**. The script rounds deviations to 12 decimal places before reporting zero. This is harmless floating-point error; say “within floating-point precision.”

   All 275 XML minimum/maximum BE values match the independently reconstructed axis exactly. The sidecars contain **no per-point data**, so describe the evidence as endpoint agreement plus the stored uniform step. The cited `noise-estimator/counting-time.md` is absent from this branch, and this generator never reads XML. Commit that validation, including properties 105/406 and their dictionary names, to make these VERIFIED claims reproducible here.

4. **MINOR — The remembered ISO attribution mixes source-specific values.**  
   [README.md:39](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/docs/findings/vgd-energy-axis/README.md:39).

   ISO 15472:2010 Table 2 gives monochromated Al Kα values **Au 83.96, Ag 368.21, Cu 932.62 eV**. Au **83.95** belongs to the unmonochromated columns. It tabulates Cu L₃VV as apparent BE **567.93 eV for unmonochromated Al Kα**, with no entry in the monochromated column—not the stated 918.69 eV KE entry. [ISO text, Table 2](https://www.standards.iteh.ai/catalog/standards/iso/ac0216e1-da6c-4b1c-a8cc-0156f169e156/iso-15472-2010).

   The arithmetic **1486.68 − 567.997 = 918.683** is correct. An ordinary Auger transition’s KE is independent of photon energy, making an externally sourced KE a useful physical cross-check. But this calculation is not an independent measurement of the stored KE. The Fermi-reference/double-subtraction interpretation is supported as an inference; retain its HYPOTHESIS qualification.

5. **MINOR — Sample wording and literature ranges need narrower scope.**  
   [README.md:45](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/docs/findings/vgd-energy-axis/README.md:45).

   Folder parsing is correct; I found no sample-name extraction error. The seven C 1s sample medians reproduce:

   | Sample | Avantage median |
   |---|---:|
   | 1 UCl4-graphite | 284.40 |
   | 2 B4C-graphite 50% | 283.10 |
   | 3 BN-graphite 50% | 283.10 |
   | 4 UCl4-BN | 283.70 |
   | 5 B4C-BN-graphite | 284.40 |
   | 9 B4C-graphite | 284.40 |
   | 9 UCl4-graphite | 284.40 |

   Say “the four listed samples,” rather than “every graphite-rich sample.” Also distinguish sample medians from individual apexes.

   The literature labels are present, and graphite around 284.4 eV is supported. However, **284–289 is not a general C 1s range**: carbides extend below it, relevant to these B4C-containing samples. “No carbon species” is unnecessarily universal. [Graphite study](https://www.nature.com/articles/s41598-020-71435-7), [Thermo carbon references](https://www.thermofisher.com/kr/ko/home/materials-science/learning-center/periodic-table/non-metal/carbon.html).

   Survey endpoint rejection works. High-resolution scans bypass that rejection at generator line 91, although none of the current 202 regional maxima falls at an endpoint.

6. **MINOR — §3/§4 omit another runtime entry and frontend convention consumers.**  
   [README.md:70](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/docs/findings/vgd-energy-axis/README.md:70).

   `/api/upload` also accepts VGD through `app.py:956 → parser.py:66 → vgd_parser.parse_vgd`. It inherits any default correction.

   The actual Auger conversion occurs in `templates/index.html:16385`; legacy apparent-BE-to-KE conversion occurs at `:16344`, and photoelectron excitation filtering also uses `hv − wf` at `:17149` and `:17440`. Include these in the fix inventory. Legacy conversion subtracts and subsequently cancels the same work function, so distinguish it from tabulated-KE markers.

   Leaving the Auger-reference consequence conditional is appropriate. With both Al Kα defaults corrected, the numerical marker change would be **+4.58 eV**, including the additional +0.08 photon-energy change.

The charge-correction sign, saved raw-energy storage, and Auto-Fit gate description check out. Uniformly adding 4.58 to both raw energies and their corresponding charge shift preserves corrected energies; that algebra does not certify the original reference choice. The page-upload citations are stale: the relevant file-only submissions are now at `templates/index.html:4077–4079` and `:5451–5454`.

VERDICT: NO-GO
