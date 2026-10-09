# Two-basin fixture — Codex round 2, run B (commit 2171166)

No BLOCKER or MAJOR found. The round-1 MAJOR is resolved.

**MINOR:** [The fixture docstring](/Users/skyefortier/xps-app/.claude/worktrees/two-basin/tests/test_scattered_starts.py:53) still says perturbed restarts “land … near basin boundaries.” Change this to “can land,” matching the corrected plan.

Verification:

- Generator reproduced exactly: **75 candidates, 15 qualify, 7 robust, 4 with no alternative on a bound; selected: `1400.0|285.2|2`**.
- Gaps reproduce: selected **33.268040**; other eligible candidates **3.204912, 3.342593, 3.799111**; excluded candidates **38.202916, 33.342132, 29.242299**. The selection applies the documented rule.
- Fixture reproduced **46.931123 → 13.663083**, four alternative starts, one same, one not better; **1.490367 eV** centre shift and **11.016686 pp** area difference.
- **50 additional rounding probes passed**, including energy ulps and background edge levels.
- **112 Python tests passed** with reproducibility tests first. Eight API cases were excluded from that run; six affected API cases passed separately using in-memory storage. Full-precision CSV preserved both arrays and matched the direct whole-fit response.
- **32 JavaScript tests passed**. The continuation made one LM call capped at six evaluations, then two uncapped Trust-Region calls.
- Both legacy pins are removed; affected assertions retain coverage. The tolerance wording and historical certificate example are corrected.

Review remained read-only.

VERDICT: GO
