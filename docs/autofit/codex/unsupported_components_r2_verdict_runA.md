No BLOCKER found. **Three MAJOR findings remain.**

1. **MAJOR — Auto-Fit invalidates its own verdicts.** [templates/index.html:6306](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:6306) stamps support before `applyAutoFitResult` adjusts charge correction and [locks every centre](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:7065). Reproduced: an unsupported non-anchor component becomes `_isUnsupported === false` immediately after successful Auto-Fit, even with charge correction stubbed unchanged. Its centre, width and quantification reappear without any user edit.

2. **MAJOR — Stale verdicts become affirmative “supported” exports.** [templates/index.html:11015](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:11015) uses `p.support ? 'supported' : ''`. After editing an unsupported component’s amplitude, I reproduced an XLSX row labelled **supported**, although its stored verdict remains `supported:false` and no new fit occurred. Keyless older verdicts have the same problem. A stale verdict must yield an unestablished status.

3. **MAJOR — Key invalidation does not refresh existing suppression.** [templates/index.html:5804](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:5804) refreshes only scattered-starts evidence. Reproduced through the actual lock handler: `_isUnsupported` changes to false, but the existing Results row still suppresses values and the sidebar retains its badge. Quantify likewise retains its previously rendered exclusion. Refresh affected consumers when the key changes.

4. **MINOR — Stack annotations compare against the wrong tab.** [templates/index.html:8800](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:8800) calls `_isUnsupported` on source peaks, but that helper reads the active stack’s empty model. Reproduced a valid source verdict producing the plain dataset label `Unknown 2`. Compare against the source record’s key.

5. **MINOR — “Your fit” percentages retain the unsupported denominator.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:7418) prints original `area_percent` values. The committed-style fixture displays supported components as `60.0` and `39.7`, while hiding the unsupported `0.3`; normalization over supported components gives `60.2` and `39.8`. Alternatives correctly remain unaffected.

6. **MINOR — Empty Quantify still reports 100%.** [templates/index.html:8441](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:8441) hardcodes the total. Reproduced all components unsupported: empty body, normalized total zero, percentage total `100%`. This Round 1 finding remains.

No additional defect found in the local statistic’s weights/free-parameter accounting, root-verdict inheritance, or recovery from zero. The local starting-point caveat remains appropriate.

**Twin wording:** HEAD’s CLAUDE.md already describes recomputation from a response carrying the required arrays. “For a response lacking the field” would accurately replace the older “for loaded files” wording still in the plan.

Validation: **110 JS tests passed**, one Python-backed parity test blocked by read-only temporary-file restrictions; **six Python support tests passed**, upload/API test excluded. Additional reproductions used extracted production functions. No files changed.

**VERDICT: NO-GO.**
