Reviewed **HEAD `253ec2a`**. **No BLOCKER or MAJOR findings; three MINOR findings remain.** Working files changed externally during review, so findings and line numbers below refer to that commit. I made no changes.

Both **`check.txt` and `check.json` reproduce byte for byte**, running the committed generator with output captured in memory. Checks cover **275 VGDs / 145,875 points** and seven projects.

| Round-1 disposition | Verification |
|---|---|
| Survey maxima | Fixed: sample restrictions, window-maximum wording, medians and edge counts reproduce; only B has near-edge maxima, **10/50**. |
| Charge settings versus charging | Major issue fixed: residuals remain hypotheses with alternatives acknowledged. **36/72** and **11/40** reproduce. Provenance wording needs the minor qualification below. |
| Floating point / sidecars | Fixed: maximum error from −4.58 is **1.5454×10⁻¹³ eV**; **275/275** XML endpoints match. Property names and float32 values check out. |
| ISO attribution | Fixed: stated values match Table 2 of [ISO 15472:2010](https://previewnorm.com/iso/ISO%2015472-2010%20PDF.pdf) and [ISO 17974:2002](https://standards.iteh.ai/catalog/standards/iso/d87d8fde-7ec1-46c2-bd17-a20bc19fc981/iso-17974-2002). |
| Carbon wording | Fixed: four sample medians **284.40**, individual apexes **284.30–284.40**, and both 50% sample medians **283.10** reproduce. |
| Inventory / citations | Fixed: both upload paths, frontend conversions, legacy cancellation, filtering and cited locations check out. |
| Displayed shift sign | Fixed: display negates the stored shift. The example needs narrower scope below. |

1. **MINOR — −4.74 is an example, not the graphite-project shift generally.**  
   [README.md:93](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/docs/findings/vgd-energy-axis/README.md:93)

   Summing the committed charge-correction rows gives **20/72** graphitic-reference tabs with stored shift −4.74. The full range is **−4.83 to −4.65**, displayed **+4.65 to +4.83**; corresponding Avantage-axis corrections are **+0.07 to +0.25**. Label −4.74 → +0.16 explicitly as an example. The other reported measurement summaries match the outputs at their stated precision.

2. **MINOR — An out-of-range setting does not establish that it was carried over.**  
   [README.md:79](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/docs/findings/vgd-energy-axis/README.md:79), [vgd_energy_axis_check.py:168](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/scripts/vgd_energy_axis_check.py:168)

   The range test establishes incompatibility with that tab’s spectrum, not entry provenance. Reproduction: `4-GTA UCl4-BN.proj.zip`, `spectrum_9_U4f_Scan_3.json`, has observed **274.67**, reference **280.67**, and raw range **365.42–400.42**. Transfer and mistyping remain possible. Use “possibly carried over.”

3. **MINOR — Corrected-position invariance needs its condition stated.**  
   [README.md:91](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/docs/findings/vgd-energy-axis/README.md:91)

   Positions remain unchanged **when the corresponding charge shift is recomputed consistently**. Reproduction using `corrected = raw − shift`:
   - Original: `279.76 − (−4.74) = 284.50`.
   - New axis with old shift: `284.34 − (−4.74) = 289.08`.
   - New axis with updated shift: `284.34 − (−0.16) = 284.50`.

The central offset and evidence favoring Avantage’s physical axis survive review. The two original major overclaims are resolved.

VERDICT: GO
