# Codex adversarial review — endpoint-averaging default 3 (feature-endpoint-avg-default-3) — round 5, RUN A (2026-09-08, reviewed at 395ada8 / code fb17b8b)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 63,849.
Prompt: docs/autofit/codex/endpoint_avg_default_unit_r5_review_prompt.txt
Evidence at review time: node 162 pass / 0 fail / 3 known-gap todo; browser endpoint_avg_default (10), find_peaks_full_window, batch_roi, overlay_zip_roundtrip: 19 passed together; full pytest on the branch worktree 773 passed, 7 skipped (6 env-gated + local-only {7,8}* datasets absent from the worktree).
Round 5: GO x2 — reopened-project identity and null-active-tab closed (both); same-object challenge (v1 fromJSON into the active tab) ruled coherent undo, not a defect (both); WeakMap audit clear (both). Unit passes after 5 rounds.

**Findings**

1. **MAJOR — CLOSED: reopened-project tab identity.** The guard compares runtime tokens of live objects, so preserving a saved tab ID cannot make an old entry match a reopened tab. `_loadProjectJSON` constructs new objects. The extracted-function harness confirmed undo leaves the reopened DOM and record at **9**.

2. **MINOR — CLOSED: null-active-tab mirror.** Without a live tab, snapshots carry no averaging metadata and restoration returns immediately. The harness confirmed close-last-tab → undo → set 9 → redo leaves **9**.

3. **MINOR — same-object challenge: no new defect established.** `setSpectrum` creates a new tab. The v1 `fromJSON` loader retains the same spectrum and replaces its fitting setup. Restoring earlier peaks together with their averaging is consistent with undo within that spectrum. Using the actual loader and undo functions, I verified import at 9 → undo restores earlier peaks/3 → redo restores imported peaks/9. The loader’s lack of its own undo checkpoint is pre-existing.

4. **MINOR — WeakMap audit: clear.** Entries retain integer tokens, not tab objects; closed tabs remain collectible. Stack objects receive distinct tokens, missing-tab lookups are guarded, and array metadata does not survive JSON serialization. No additional round-5 regression established.

Validation: **13 targeted Node tests passed**, plus the isolated behavioral checks above. The full Node attempt yielded 150 pass / 12 fail / 3 todo because backend-parity subprocesses lacked writable temporary storage. Browser results remain author-reported; the available pytest log was incomplete. Archived verdict files were not read. Current HEAD is `395ada8`, with only the review prompt added after `fb17b8b`.

VERDICT: GO
