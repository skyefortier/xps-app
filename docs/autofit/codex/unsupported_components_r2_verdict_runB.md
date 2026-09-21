No BLOCKER found. Four MAJOR findings remain.

1. **MAJOR — Auto-Fit invalidates its own verdicts.** [templates/index.html:6306](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:6306) stamps support before `applyAutoFitResult` refines charge correction and locks centres at line 7065. Both change the key. Reproduced with charge correction stubbed unchanged: an unsupported component becomes reportable solely because Auto-Fit locks its centre. Preserve valid evidence through Auto-Fit’s finalization.

2. **MAJOR — Importing parameters onto different data reuses the old verdict.** [templates/index.html:7302](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:7302) keys parameters/settings but excludes spectrum identity or data. `fromJSON` copies support and restores those settings. Reproduced importing a `.fit.json` onto different counts: `fitResult === null`, yet `_isUnsupported` remains true. Clear evidence on parameter-only import or bind it to the originating data.

3. **MAJOR — Key changes do not refresh all suppression consumers.** [templates/index.html:7327](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:7327) refreshes only the scattered-starts panel. Reproduced toggling a component’s centre lock: `_isUnsupported` becomes false, but Results remains unchanged and Quantify still omits its row. The key comparison works; already-rendered suppression survives. Refresh all affected presentations after such edits.

4. **MAJOR — Stale unsupported verdicts export as “supported.”** [templates/index.html:11015](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:11015) uses `p.support ? 'supported' : ''`. Once an edit invalidates an unsupported verdict, CSV/XLSX positively labels that component supported. Reproduced with a stale false verdict. Require a current, explicitly true verdict; otherwise leave status unestablished.

5. **MINOR — Stack labels compare against the wrong tab.** [templates/index.html:8800](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:8800) calls `_isUnsupported` on source peaks, but that helper compares against the active stack’s key. Reproduced an unsupported source component appearing simply as `ghost`, without its designation. Compare against the source record’s key.

6. **MINOR — “Your fit” percentages retain the unsupported area in their denominator.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:7418) prints the original `area_percent`. The committed test’s supported cells remain `60.0` and `39.7`, while Results renormalizes them over supported area. Renormalize the judged row; alternatives can retain their own percentages.

7. **MINOR — All-unsupported Quantify still totals 100%.** [templates/index.html:8441](/Users/skyefortier/xps-app/.claude/worktrees/feature-unsupported-components/templates/index.html:8441) hardcodes `100%`; recalculation never updates it. Reproduced an empty quantified body with that total. Show an unavailable total.

The local statistic’s weights and parameter counting match the intended engine-relative definition; I found no additional overclaim given the retained local caveat. The linked-ancestry and width-export fixes passed focused checks.

**Twin wording:** current `CLAUDE.md` correctly describes response-shaped inputs. The plan still says “for loaded files” at lines 141 and 280; change those to “for a response lacking the field.”

Validation: 110 focused JS tests passed; one Python-backed parity test was blocked by temporary-directory restrictions. Six Python support tests passed; the write-requiring upload test was excluded. Reproductions used extracted page functions. No files changed.

**VERDICT: NO-GO.**
