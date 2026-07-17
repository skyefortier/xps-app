# Codex review — reference_bridge.py VERIFIED-mechanism fix — RUN A (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/reference_bridge_mechanism_review_prompt.txt (commit 1ed297a)

**Findings**

None blocking.

**Verified**

`_curated_status()` correct: explicit `False` returns CONDITIONAL; absent or
True returns VERIFIED. `_add_position()` applies the helper only for
`tier == "curated"`; machine and legacy still use `BRIDGE_TIER_STATUS[tier]`
unchanged. Schema placement correct in both transition definitions;
`additionalProperties: false` remains in force; `jq empty schema.json`
passed. The per-record flag is justified: `_citation()` resolves `source_id`
through `sources`, and "nist-srd-20" is a real citation in sources.json;
current C 1s uses 284.44 with that same source, proving source resolution
alone would not have caught the old 284.5 bug. No real data records set
`independently_verified` — grep found only the schema declarations, so
every currently-curated record still defaults to VERIFIED. New tests import
the real `_curated_status` helper (not a copy) and use the actual field
names. Consumers (coverage.py, coverage_index.py) are generic enough,
passing status through / building a sorted set. Direct `_curated_status`
checks returned CONDITIONAL, VERIFIED, VERIFIED for the three intended
cases. CONDITIONAL is an acceptable downgrade target; a future dedicated
status would need broader UI/provenance vocabulary work, not required here.

VERDICT: GO
