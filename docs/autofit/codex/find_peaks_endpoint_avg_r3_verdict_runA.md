# Codex adversarial review — Find Peaks endpoint averaging (feature-find-peaks-endpoint-avg) — round 3, RUN A (2026-09-08, reviewed at 7cd67ec / code 916d3da)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 67,823.
Prompt: docs/autofit/codex/find_peaks_endpoint_avg_r3_review_prompt.txt
Round 3: A NO-GO / B GO — B1 bound CLOSED (both), A3 out of scope (both), no new defect (both). Run A caught a second evidence error: the author's 'on main checkout' isolation run never changed directory (all three invocations ran in the feature worktree), so the main reproduction was NOT established. Corrected in round 4 with a real main-checkout run (checkout identity printed, exit status, full log).

**Findings**

Reviewed `916d3da`; actual HEAD `7cd67ec` adds only the round-3 prompt. No new implementation defect found.

1. **MINOR — Evidence discrepancy remains unresolved.** The [logged isolation command](/Users/skyefortier/.claude/projects/-Users-skyefortier-xps-app/350bc509-8554-4eb2-8e01-0167f43c0b89.jsonl:1729) runs all three invocations in the feature worktree: printing “same test on main checkout” does not change directories. The [subsequent command](/Users/skyefortier/.claude/projects/-Users-skyefortier-xps-app/350bc509-8554-4eb2-8e01-0167f43c0b89.jsonl:1739) switches to main and prints `0a80288`, but runs no tests. Timing sensitivity is credible; reproduction on main is **not established**. Progress helpers and the entire spinner/upload/poll/cleanup sequence exactly match main. Synchronous metadata lookup and validation cannot reorder that sequence, although the intended averaging change can alter fitting duration. Supply an actual main run with checkout identity, full failure output and exit status before classifying this as pre-existing.

2. **MINOR — B1 fixed.** Backend and frontend enforce 1–50, closing the Advanced-JSON `1e21` divergence. The quarter-window cap is acceptable here: both implementations reduce 50 to 11 on the same 46-point window. `_fpLast` records the requested setting; each background calculation applies its window cap. All 17 background-affecting calls forward nonliteral `endpoint_avg`; default-1 arithmetic remains unchanged.

3. **MINOR — A3 remains acknowledged and outside scope.** `/api/fit` and `/api/background` retain their existing coercion. This does not bypass Find Peaks’ method validation.

Logs support 39 wiring/seam passes, 14 browser passes and Node 164/0. My focused JavaScript run passed 14/14; the full Node run encountered sandbox temporary-directory failures. Current full pytest was still running, and its parity gate had not completed when checked. Archived verdict files were not opened.

VERDICT: NO-GO — The claimed main-branch reproduction was actually another feature-branch run, leaving the required evidence discrepancy unresolved.
