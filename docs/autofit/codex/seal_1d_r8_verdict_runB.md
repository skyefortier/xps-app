**One MINOR finding remains. No BLOCKER or MAJOR found.**

1. **Round-7 finding: resolved.** `_LINK_GRAMMAR.fullmatch` rejects comments and other trailing tokens. Accepted expressions expose one master name to both validation and the comparator’s regex; exponent text cannot name a synthesized parameter. [app.py:1454](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1454), [same_fit.py:143](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:143)

2. **MINOR — parameter names can make a validated response return HTTP 500.** The form check permits arbitrary parameter names. Add three otherwise valid parameter records named `value`, `min`, and `expr`:

   ```python
   h = copy.deepcopy(valid_response)
   p = h["individual_peaks"][0]["params"]
   for name in ("value", "min", "expr"):
       p[name] = {**p["center"], "expr": None}
   # POST /api/compare-fits {"a": h, "b": h}
   ```

   **Reproduced:** form validation returns `None`; comparison returns **500**. At `individual_peaks[0].params`, the comparator mistakes the entire parameter map for parameter metadata. Its `expr` is then a dictionary, causing `re.findall` to raise `TypeError: expected string or bytes-like object, got 'dict'`. [fitting.py:193](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:193), [same_fit.py:247](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:247), [app.py:1576](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1576)

   Restrict metadata interpretation to actual parameter records, or refuse unsupported parameter names before comparison. Add a regression for this reproduction. I found no additional non-finite-scale or link-graph bypass.

3. **Real-fit compatibility:** no new refusal found beyond the documented extreme-arithmetic limit, including ±1e308 bounds. The producer’s direct, offset and ratio links fit the lexical grammar. All **328 stored records** and the **five real-fit offset cases** passed. [plan:69](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:69), [fitting.py:1730](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1730), [tests:206](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:206)

4. **New tests detect their named defects.** An in-memory mutation replacing `fullmatch` with `match` failed **seven grammar cases**, including both comments and subtraction. The new 500 path is uncovered. [tests:272](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:272)

Validation: **53 endpoint tests passed**, including the corpus check; **37 comparator tests passed**. Execution used in-memory sessions; no checkout files changed.

VERDICT: NO-GO
