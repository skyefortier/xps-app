# Codex review — reference_bridge.py VERIFIED-mechanism fix — RUN B (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/reference_bridge_mechanism_review_prompt.txt (commit 1ed297a)

**Findings**

None blocking.

**Verified**

`_curated_status()` returns CONDITIONAL only for explicit False, otherwise
VERIFIED. `_add_position()` applies the helper only when `tier == "curated"`;
machine and legacy call sites are separate and unchanged. Schema placement
correct in both transition definitions with `additionalProperties: false`
intact. The per-record flag is justified: `_citation()` resolves
`sources[source_id]["citation"]`, and "nist-srd-20" is a real source entry;
C 1s uses that source and now stores 284.44 — a citation-resolution check
alone would not have caught the old 284.5 value. `rg independently_verified
data/xps` finds only the schema entries; a direct JSON scan counted 21
curated transitions and zero real `independently_verified` fields, so all
currently loaded curated records still default to VERIFIED. Tests import the
real helper, not a reimplementation, using the actual field names. coverage.py
passes status through without enum logic; coverage_index.py treats statuses
as arbitrary strings via set/sort/join. Commit scope is exactly the three
requested files. CONDITIONAL is an acceptable downgrade target in the
existing vocabulary; a future dedicated status could be clearer but would be
a broader UI/provenance vocabulary change, not required for this fix.

VERDICT: GO
