# A2 round 5 — run A (commit 68fbf47; codex exec, reasoning high)

1. **MAJOR — DS+G alternatives still borrow the returned fit’s width, accepting distinct minima above the stated resolution.** [tests/fit_equality.py:154](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:154)

   `alternative_widths()` overrides the inherited width only for components containing `params.fwhm`. DS+G has `beta` and `m_gauss`, so the round-4 failure remains.

   Reproduced with complete `run_fit` responses, seed **123**, using controlled scattered starts; fitting, certification and reporting remained real. Construction: 50,001 points over −500…500, a held Gaussian of height 1e6/FWHM 1e9, and two height-10 DS+G lines at ±0.25 (`alpha=0`, `beta=0.05`, `m_gauss=0`). The fitted DS+G component starts at centre 1000 with bounds ±2000; its returned sampled width is **621.32 eV**.

   The listed alternatives certify at **−0.249257525 and +0.249257636 eV**. Profiling amplitude gives χ² **0.000424077** at either minimum versus **0.000849854** at centre zero; nearby displacements also increase χ².

   **`assert_same_fit` accepts both complete responses.** Their **0.498515 eV** separation exceeds the alternatives’ own sampled-width allowance, **0.00012 eV**, by over **4,000×**. The inherited allowance is **0.62132 eV**. Derive widths from each alternative’s actual shape and parameters.

2. **MAJOR — Bound inheritance stops after one link, falsely rejecting equivalent fits with linked chains.** [tests/fit_equality.py:96](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:96)

   `bounds_of` contains only directly bounded parameters. For `p4_m → p3_m → p2_m`, looking up `p3_m` fails because it is itself linked.

   Reproduced with real certified three-component LA fits: centres **380, 390.9, 401.8**, FWHM **2**, α **1**, β **2**, successive amplitude ratios **0.75**, seed **123**. Changing only the root’s starting `m` from **0.3 to 0.001** produces **identical component curves and χ² = 0.817751820897525**.

   The root and first child pass against the root’s **0–499** span. **Only the grandchild fails**, receiving a relative allowance of **0.0003** instead of **0.499**. This reproduces with the root both free and fixed. Resolve dependency chains to their underlying scale.

Validation: **59 battery tests, 122 JavaScript tests, and four targeted regression/order tests passed**. A broader Python run reached **43 passes** before a budgeted stop. Certificate exit/cap and restart-cancellation probes passed. Replayed parameter/curve comparisons passed for **398 recorded pairs** whose objectives agree within tolerance, including the four round-4 failures. Production code matches the recorded final hash; displacement counts remain **0/202** for both methods. No files changed.

The accepted finite-resolution ruling stands; finding 1 substantially exceeds that resolution.

**VERDICT: NO-GO**
