# A2 round 4 — run A (commit 711da78; codex exec, reasoning high)

1. **MAJOR — Scattered-start alternatives borrow the returned fit’s width, accepting distinct minima above the stated resolution.** [tests/fit_equality.py:82](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:82), [line 124](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:124).

   Reproduced with two complete `run_fit` responses, seed **123**, using controlled scattered starts to select two basins. Fitting, certification, and report construction remained real.

   Construction: 50,001 points over −500…500; a held Gaussian of height **1e6**, FWHM **300**; data additionally contain a broad Gaussian of height **0.05**, FWHM **300**, and two narrow Gaussians of height **10**, FWHM **0.04**, centred at **±0.12**. The second fitted component starts broad, with centre bounds ±500, width bounds `[0.02,499]`, amplitude bounds `[0,100]`. LM, no background or perturbations, one scattered start.

   The returned component’s sampled width is **291.62 eV**. The two certified alternatives have centres **−0.12 and +0.12 eV**, FWHM **0.040261 eV**, and equal χ²ᵣ ≈ **3.85640856e−9**. Profiling amplitude and width gives χ² **0.000192813** at either minimum versus **0.000268213** at centre zero; nearby displaced centres also score worse.

   **`assert_same_fit` accepts the complete responses.** It allows **0.29162 eV** for alternative centres because `width` contains only `individual_peaks` from the returned fit. The alternatives’ own sampled-width allowance is approximately **0.00006 eV**. Their **0.24 eV** separation exceeds that by **4,000×**.

   Derive each alternative’s centre scale from that alternative’s component; apply it consistently to centre and displacement fields.

2. **MAJOR — Linked parameters reject recorded same-minimum repeat presses because their master’s bounds are lost.** [tests/fit_equality.py:127](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:127), [line 144](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:144).

   The committed [first press, line 63](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/docs/findings/runfit-certificate/data/V3_least_squares.jsonl:63) and [repeat, line 63](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/docs/findings/runfit-certificate/data/rep_V3_least_squares.jsonl:63) for **4-GTA UCl4-BN / U4f Scan_4** share seed **3861813319** and both certify.

   LA `m` changes **0.4769747758 → 0.0010740077**. Its master passes using bounds `[0,499]`, which allow **0.499**. The linked component reports `expr="p2_m"`, `min=None`, `max=None`; its duplicate value instead receives a relative allowance of only **0.000476975** and fails.

   Reconstructing the recorded fields with the current parameter schema reproduces that rejection. Component curves differ by only **5.08e−7** of their height; relative χ² change is **8.07e−11**. Three other recorded Trust-Region pairs exhibit the same failure. Linked values need the scale implied by their constraint.

**Proportionality ruling:** **Yes**, the expressly stated finite resolution satisfies the owner’s rounding-tolerance requirement. I would not reject it merely because minima below every stated tolerance remain indistinguishable. Finding 1 exceeds that resolution substantially.

**Same-minimum ruling:** No false rejection appeared on the exercised test models, including the overlapping-component check. However, the committed repeat data establish the linked-parameter failure above; removing stderr comparisons did not eliminate all such failures.

Validation: **59 battery tests and 122 JavaScript tests passed**. Focused Python runs passed before budgeted stops at 40 and 8 tests; four additional targeted tests passed. Certificate exits, restart cancellation, V3 ordering, and displacement checks behaved correctly. Seed/draw assertions remain exact, and the revised rejection proofs pin their seeds. Production code matches the recorded final hash; displacement counts remain **0/202** for both methods. Full-suite completion was not attempted. No files changed.

**VERDICT: NO-GO**
