# A1 round 3 — run B (commit c5278eb; codex exec, reasoning high; transcript had 3 reconnect lines, run completed)

No BLOCKER, MAJOR, or MINOR findings.

Round-2 fixes held under adversarial probes:

- Worker cleanup stopped heartbeats on completion, `_AnalyzeError`, ordinary exceptions, `SystemExit`, and `KeyboardInterrupt`, including payload-construction failures.
- Both forced lock orderings prevented heartbeat writes after terminal publication. Failed final publication stopped the heartbeat, leaving the stale-record detection path effective.
- Polling bounded persistent missing/non-finite heartbeat evidence, tolerated intermittent missing ages, and completed healthy 1,050-second jobs. Transport failures rejected correctly.
- Certificate exit branches, restart exhaustion, lowest-point retention, and the clock test through screening passed.

**Validation:** 22 targeted Python tests and 12 JavaScript tests passed. The new Python regression passed against HEAD and failed against `4ff9829` using in-memory storage. Persistent-null polling stopped on HEAD; the old loop continued until the harness limit.

Independent full-grammar **Scan_6 returned MG2+preseed**, with 30 candidates and no truncation.

Disk-backed API tests and the heavy-load matrix were not rerun under this read-only review. Section 4’s screen alternative remains an owner decision. Workspace unchanged.

**VERDICT: GO**
