Reviewed HEAD `253ec2a`. **No BLOCKER or MAJOR findings; two MINOR wording issues remain.** Nothing was changed.

Both `check.txt` and `check.json` reproduce **byte-for-byte**, using `/Users/skyefortier/xps-app/venv/bin/python` with output captured in memory.

| Round-1 disposition | Verification |
|---|---|
| Survey maxima | Fixed. Element filtering, all six medians, and B’s **10/50** near-edge maxima reproduce. |
| Charge settings versus charging | Fixed substantively. **36/72** graphitic and **11/40** other settings are outside their tabs’ ranges; charging remains a hypothesis. |
| Floating point / sidecars | Fixed. Maximum error from −4.58 is **1.54543×10⁻¹³ eV**; **275/275** sidecar endpoints match. Property names and values check out. |
| ISO attribution | Fixed. Values match the reproduced standards’ tables: [ISO 15472](https://standards.iteh.ai/catalog/standards/iso/ac0216e1-da6c-4b1c-a8cc-0156f169e156/iso-15472-2010), [ISO 17974](https://standards.iteh.ai/catalog/standards/iso/d87d8fde-7ec1-46c2-bd17-a20bc19fc981/iso-17974-2002). |
| Carbon wording | Fixed. Four sample medians are **284.40**, individual apexes **284.30–284.40**, and the two 50% sample medians **283.10**. |
| Inventory / citations | Fixed. Both upload routes and the listed frontend/backend consumers match the cited code. |
| Displayed shift sign | Fixed. Stored **−4.74** displays **+4.74**; its corresponding adjustment becomes **+0.16** on Avantage’s axis. |

1. **MINOR — Outside-range detection does not establish provenance.**  
   [scripts/vgd_energy_axis_check.py:158](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/scripts/vgd_energy_axis_check.py:158), [README.md:79](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/docs/findings/vgd-energy-axis/README.md:79).

   The generator categorically labels every outside-range setting “carried-over.” It establishes only that the entered position is outside the tab. Reproduction: `4-GTA UCl4-BN.proj.zip → spectrum_9_U4f_Scan_3.json` contains observed **274.67**, reference **280.67**, and raw range **365.42–400.42**. No inspected in-range setting shares that reference. Propagation is possible; entry error remains possible too. Use “outside range; possibly carried over.”

2. **MINOR — Identify −4.74 as an example, not the graphite-wide value.**  
   [README.md:93](/Users/skyefortier/xps-app/.claude/worktrees/energy-axis/docs/findings/vgd-energy-axis/README.md:93).

   Only **20/72** graphitic settings have stored shift −4.74. The complete range is **−4.83 to −4.65**, corresponding to displayed adjustments **+0.25 to +0.07** after the axis correction. Reproduce by grouping the graphitic `charge_corrections` rows by `observed app − reference`, weighted by their final count. Adding “for example” resolves this.

The remaining numerical claims and arithmetic check out. The physical-axis conclusion is supported as an inference; the revised text appropriately distinguishes that evidence from an independent measurement of stored kinetic energy.

VERDICT: GO
