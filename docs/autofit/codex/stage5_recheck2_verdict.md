# Codex re-check #2 verdict — Stage 5 (Bayesian exchange-MC validation), 2026-07-03 late

Re-check of the re-check-#1 artifact dispositions (prompt:
`stage5_recheck2_prompt.txt`). Recovered from the session log 2026-07-04 —
the verdict was returned late 2026-07-03 but not archived before session end.
~168k tokens.

**Findings**

1. **BLOCKER** `docs/autofit/inventory/bayesian_real_validation_runs.jsonl`
   (+ `scripts/run_bayesian_real_validation.py:117`): the main validation
   JSONL was still not fully regenerated — mixed append/resume output: 28
   Bayesian rows lacked the newer `free_energy_mc_error` / replicate-key
   schema while only 4 appended duplicate rows had it; U 4f default seed 0/1
   and C 1s seeds 0/1 appeared twice with the same key (stale + newer); the
   summary doc exposed the mix. Failure scenario: consumers parse the
   committed JSONL and see a non-canonical mix of old/new schemas and
   duplicate runs — not a clean evidence record for the fixed method.
   Fix: delete/truncate and rebuild under the current method; one record per
   intended `(anchor, method, config, seed)`, uniform candidate schema.

2. **MAJOR** `autofit/methods/bayesian_exchange_mc.py:373,444` +
   `tests/autofit/test_bayesian_method.py:241`: `seed_replicates>1` reports
   `free_energy` as the replicate mean, but posterior peaks/confidence/σ
   diagnostics come from the base seed run — documented only in an internal
   code comment, and no test pinned `seed_replicates=1` ≡ omitting the
   option. Fix: consumer-visible metadata (`free_energy_is_replicate_mean`,
   `posterior_samples_seed`, `posterior_summary_replicated=false`) + identity
   and mean-F tests.

**Closed checks**: the U 4f env-gate exists and asserts replicated UNRESOLVED
on the real B4C-UCl4 anchor; the tuned U 4f replicated row resolves to U2
with ΔF ≈ 27.6 and replicate spreads within ±0.5; sigma_stat reliability and
zero-variance ESS→0 are pinned in tests and implemented with `ptp==0`.

Nothing modified. Targeted pytest could not run (read-only sandbox, no
writable temp directory).

VERDICT: NO-GO (blockers: stale validation JSONL not fully regenerated)

---

**Disposition (2026-07-03 late session, same session):** both findings fixed —
finding 2 by commit 82003db (consumer-visible replicate semantics + pins),
finding 1 by commit 9296cc3 (canonical single-generation battery JSONL, 33
records, uniform schema). Verified by re-check #3.
