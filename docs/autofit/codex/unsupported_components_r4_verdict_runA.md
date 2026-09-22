No BLOCKER found. Two findings remain.

1. **MAJOR — Restoring a centre manually exposes a currently unsupported value.** [templates/index.html:5983](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:5983): increment an unsupported peak’s centre, then restore its exact fitted value. Suppression returns, but the inline `oninput` continuation overwrites the sidebar’s dash with the numeric centre. Reproduced with extracted production handlers: `_isUnsupported === true`, header `282.25 eV`, Results suppressed and Quantify excluded. Subsequent refreshes cannot repair it because the badge IDs already match.

2. **MINOR — Verdict invalidation interrupts numeric editing.** [templates/index.html:7358](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:7358): with a current unsupported component, select a peak’s amplitude and type a replacement. The first keystroke invalidates support and calls `renderPeakList`, which replaces the focused input during `oninput`. Continued typing requires refocusing. Preserve the input node or restore focus and editing state.

The Round 3 sidebar/Results and chart-label fixes hold for the inspected paths. No render cycle found.

Validation: **123 tests passed**; one Python-backed parity test was blocked by read-only temporary-directory restrictions. Reproduction used extracted functions, not a browser. No files changed.

**VERDICT: NO-GO.**
