# Codex re-check #3 verdict — Stage 5 (Bayesian exchange-MC validation)

The same prompt (`stage5_recheck3_prompt.txt`) was independently run TWICE —
once late 2026-07-03 (completed but not archived before session end;
recovered from the session log 2026-07-04) and once fresh 2026-07-04. Both
runs verified the two re-check-#2 dispositions closed and surfaced the SAME
single residual finding, but rated it differently (MINOR/GO vs
BLOCKER/NO-GO). Both are recorded here; the stricter reading governs the
disposition.

## Run A — 2026-07-03 late (~117k tokens): VERDICT: GO

- **MINOR** `docs/autofit/inventory/bayesian_u4f_tuned_run.jsonl:2`: the
  tuned U 4f sidecar record with `seed_replicates: 2` has
  `free_energy_replicates` / `free_energy_replicate_spread` /
  `free_energy_mc_error`, but lacks the newer `free_energy_is_replicate_mean`
  flag now emitted by `bayesian_exchange_mc.py`. Failure scenario: someone
  auditing the tuned sidecar directly cannot see the explicit replicate-mean
  semantic flag, even though the canonical validation JSONL and live method
  payload are correct. Fix: regenerate this sidecar under the latest method,
  or add the missing flag to the sidecar record.
- No blocker findings. Canonical JSONL: 33 records, 33 unique
  `(anchor, method, config, seed)` keys, no duplicates, 28 Bayesian records,
  all 80 scored candidates carry the free-energy reliability fields; per-slot
  `sigma_stat.reliability` + per-interval `ess` present. Doc reflects
  Cl 2p/B 1s resolved, C 1s unresolved on both seeds, U 4f seed 1 flagged
  while seed 0 at k=1 is not.

## Run B — 2026-07-04 fresh (independent): VERDICT: NO-GO

- **BLOCKER** `docs/autofit/inventory/bayesian_u4f_tuned_run.jsonl:2`: the
  replicated tuned U 4f artifact still omits `free_energy_is_replicate_mean`
  on both candidates despite `seed_replicates: 2` and
  `free_energy_replicates` being present. Failure scenario: downstream
  consumers cannot reliably distinguish the reported `free_energy` as a
  replicate mean in the doc-linked tuned evidence, reopening the
  consumer-visible replicate semantics issue. Fix: regenerate this tuned
  JSONL with the current `bayesian_exchange_mc` output schema so replicated
  candidates carry `free_energy_is_replicate_mean: true` (and non-replicated
  current-schema records carry `false`).
- Checks that passed: identical to Run A's closed checks (canonical JSONL
  schema/uniqueness, reliability fields, doc honesty picture).

Both runs: nothing modified; targeted pytest blocked by the read-only
sandbox (no writable temp directory).

---

**Disposition (2026-07-04):** treated at Run B's severity. The tuned
artifact was regenerated from scratch under the current method schema by the
new COMMITTED generator `scripts/run_bayesian_u4f_tuned.py` (the original
was ad hoc — no committed script — which is how it went stale); same two
records (full candidate set @ 16 replicas/4000 sweeps seed 0; U1b-vs-U2
head-to-head with `seed_replicates=2`), resumable-JSONL harness reused from
the battery runner. See PROGRESS.md for the regenerated numbers vs the
originals.
