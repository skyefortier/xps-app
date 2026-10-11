# Sealed fit record v6 design — Codex gate round 4, run B (commit 2e44780)

**Revision 4 is not ready for approval.** The expired-session issue and original/final background-context contradiction are resolved, but link validation, the new two-fit proof, and canonicalisation remain incomplete.

Reviewed HEAD `2e44780` against `c643c5f`; changes are documentation only. Validation was read-only source inspection and bounded Python/JavaScript probes. No files changed.

1. **BLOCKER — cross-lineshape refusal does not complete the link/display proof.**

   [V6.3’s representability rule](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:773) leaves a reachable dangling-link case:

   - Start with `1 ← 2 ← 3`.
   - Remove peak 1. [`removePeak`](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:6400) removes 1 and its immediate child 2, leaving peak 3 with `linked: 2`.
   - [`peakToBackendSpec`](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:6983) silently omits `constrain_to` when it cannot find the parent.

   An extracted-function probe reproduced this exactly. The server fits an independent component while the page retains its linked designation. Step 0 passes because it reproduces that same omission; O’s roles match the request; projection retains the dangling link. Nothing in the stated cross-lineshape refusal explicitly rejects this model.

   The server-side refusal also lacks a necessary input: **Voigt and GL both arrive as `pseudo_voigt_gl`**, [IH:6929](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:6929). Comparing backend shape names cannot enforce the promised frontend-shape rule. A production-function probe again accepted the GL→Voigt request and returned the child’s expression-valued mix as `0.2`.

   **Required:** validate the complete graph before request construction and during seal verification: every link resolves, IDs are unambiguous, and cycles are rejected. Specify how the server receives and validates the frontend representation—or define an equivalent representability contract it can actually enforce.

   For valid same-shape families, I found no additional inactive-parameter hole: DS, DS+G, LA and asym-GL have mappings for their expression-controlled parameters. Voigt→Voigt preserves `0.5`; a reversed three-level chain resolved in the server probe. The local `LINK_SYNC_KEYS` covers those shape fields, with centre/amplitude/FWHM handled separately, but its missing-parent branch also silently skips the link, [IH:9285](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:9285).

2. **BLOCKER — the new anchor-fit evidence is not explicitly bound to the spectrum being charge-corrected.**

   [V6.3’s two-fit contract](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:795) requires deriving `R₂.context0` and `R₂.pageModel` from R₁/O₁, rerunning the anchor gate, and authenticating O₁. But [V6.4’s sample bindings](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:824) operate on the seal’s R—now R₂.

   An authentic anchor fit from another spectrum can therefore supply the charge shift unless R₁ independently receives the raw-data, selection, context and request bindings. Authenticity establishes that the server fitted R₁; it does not establish that R₁ belongs to this tab.

   Likewise, “O₁ is attested like any O” does not explicitly require its positive acceptance predicates. Today Auto-Fit checks `success === true` before applying its anchor gates, [IH:8267](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:8267). The revised protocol must preserve that distinction: an authenticated failure remains a failure.

   **Required:** make R₁/O₁ a fully checked prerequisite, bound to the same raw spectrum under its original context, with successful acceptance and the existing anchor/required-component gates. Include that evidence in the immutable seal and verification-cache identity. Deriving R₂ from unbound evidence does not repair the missing binding.

3. **MAJOR — the two-fit transaction and its terminal outcomes are underspecified.**

   The mathematical direction is coherent: fit in the provisional frame, derive the shift, rebuild inputs from raw samples in the final frame, lock centres, then fit again. This avoids translating O₁’s arrays.

   However, [the operative paragraph](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:795) does not define:

   - What the student sees between fits, including statistics, support, saving and history.
   - The complete R₂ construction: projection of O₁, centre/anchor migration, conditional endpoint rounding, overlay handling, request settings and fresh sample selection.
   - What happens when the final fit fails, is cancelled, or returns an unsupported charge-reference component.
   - How operation ownership spans both fits and verification.

   Reusing today’s `applyAutoFitResult` is insufficient: it immediately writes statistics, announces completion and snapshots the result, [IH:7824](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:7824). Today’s failure paths restore the previous state, subject to supersession ownership, [IH:8283](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:8283).

   **Required:** specify the two-stage transaction and commit/restore rules. Distinguish an unsupported component from a failed fit, and explicitly decide what an unsupported **final anchor** means for the retained charge correction.

   The consequence **without 0d** is now correctly stated: nonzero Δ cannot be current under this contract; zero Δ requires only the derived centre-lock change. The `delta !== 0` rounding branch is correctly preserved.

4. **MAJOR — the signed representation works for ordinary values, but its declared domain and absent/null rule are unsound.**

   The [signed-byte contract](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:885) is substantially more concrete. Probes passed for booleans, strings, nested objects, `None`, ordinary integers, NumPy scalars, negative zero, and an actual O round-tripped through browser JSON.

   `n_perturb` is also sound **when normalised before canonicalisation**: the existing normaliser maps `3`, `3.0` and `"3"` to integer 3, and `True` to integer 1. Signing their floating canonical representation need not change the executable argument’s integer type.

   Two problems remain:

   **Absent is not generally null.** The normaliser currently passes nested peak specs through, [app.py:91](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/app.py:91). In `_make_peak_params`, absent `fwhm_min` means `0.1`; explicit `None` leaves the lower bound unset, [fitting.py:1617](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1617). Both production probes succeeded and returned different bounds. Blanket null-filling either changes the executed problem or conflates distinct requests in the signed representation.

   **Finite integers are not necessarily representable by `_canonical`.** A request with numeric peak ID `10**400` passed the current normaliser and produced a successful fit. `_canonical` then raised `OverflowError` at its integer-to-float conversion, [fitting.py:1988](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1988). Smaller integers beyond binary64’s exact range can also collapse together; the probe confirmed that for `9007199254740992` and `9007199254740993`.

   **Required:** define a recursive, versioned schema with field-specific defaults/nullability and numeric domains. Preserve meaningful absence or expand it to the actual effective default. Require lossless identifier encoding and reject unsupported values before fitting. Canonicalisation should encode the validated recipe without changing its meaning.

The round-3 dispositions are:

| Round-3 finding | Revision-4 disposition |
|---|---|
| Expression/display representability | **Partial:** finding 1 remains |
| Original versus final Auto-Fit context; zero-delta branch | **Resolved directly**, but the replacement introduces findings 2–3 |
| Expiring session; missing reconstruction inputs | **Resolved:** explicit arrays, transport-only session, method/settings and full peak snapshots |
| Attestation payload and lifecycle | **Partial:** coverage, signer and threat statement resolved; finding 4 remains |
| Overbroad tolerance statement | **Resolved:** exact currency comparisons are scoped |

Other requested checks:

- **0b/0c/0d are correctly identified as substantive changes.** 0b can change optimisation trajectories and outcomes; 0c changes displayed linked values and refuses previously runnable models; 0d changes the fitted problem, reported numbers and possible acceptance outcomes. Their measurements must cover refusals/failures as well as numerical differences.
- **Statistics remain coherent.** Installed lmfit confirms denominator, floor and AIC/BIC ordering; `best_fit` is a separate evaluation. SciPy confirms the stated trapezoid association. Twelve additional `_npPairwiseSum` probes through 100,000 elements matched NumPy exactly. Universal evaluator/background identity remains unproved, appropriately gated by 1b.
- **Areas, local designation, provenance and migration:** no new defect found beyond the link and Auto-Fit issues above. The existing measurement requirements and simultaneous consumer migration remain necessary.
- **MINOR:** `O_CREAT | O_EXCL` chooses a single creator but does not publish fully written key contents atomically; specify reader readiness and crash recovery. Also update the section heading, which still says “revision 3.”

No full browser suite or 202-target census was run.

**VERDICT: NO-GO.**
