# Codex review — Unit R2 exhaustion certification (commit 324b793) — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 155,435.
Prompt: docs/autofit/codex/refpop_unit2_exhaustion_prompt.txt

1. BLOCKER [scripts/acquire_nist_archive.py](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:90) / [docs/autofit/PROGRESS.md](/Users/skyefortier/xps-app/docs/autofit/PROGRESS.md:1547) - The re-probe still uses the same failure-collapsing CDX path. `cdx_snapshots()` catches any CDX/http/json exception and returns `[]`; `acquire()` then records that as `no archive snapshot`. A Wayback timeout, 503, rate-limit, or malformed CDX response for both `asp` and `aspx` would produce the same fresh `fetch_utc` and the same committed summary as true absence. The tests only pin the resulting counts/reasons, so they would not catch this. This leaves the central “NO Wayback snapshot” / “boundary is the archive” certification unproven.

VERDICT: NO-GO
