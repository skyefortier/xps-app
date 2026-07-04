# Codex re-check #4 (final) verdict — Stage 5 (Bayesian exchange-MC validation), 2026-07-04

Focused verification of the re-check-#3 closure — the regenerated tuned
U 4f artifact + committed generator, fixed in commit 7f6ec48 (prompt:
`stage5_recheck4_prompt.txt`).

Findings: none. No blocker, major, or minor issue found.

Verified:
- `scripts/run_bayesian_u4f_tuned.py:37` defines
  `TUNED = n_replicas=16, n_sweeps=4000`; `:47` emits the full seed-0 run;
  `:50` emits the U1b/U2 `candidate_filter` with `seed_replicates=2`; `:18`
  documents the resume-key caveat.
- `docs/autofit/inventory/bayesian_u4f_tuned_run.jsonl:1` has 4 current
  U 4f grammar candidates, winner `U2_mains_satfree`, seed 0, 16/4000, all
  `free_energy_is_replicate_mean: false`.
- `docs/autofit/inventory/bayesian_u4f_tuned_run.jsonl:2` has only U1b/U2,
  winner `U2_mains_satfree`, `seed_replicates: 2`, replicated F fields and
  `free_energy_is_replicate_mean: true` on both candidates.
- Both records have per-slot `confidence.*.sigma_stat.reliability`.
- Deltas match docs: record 1 ΔF(U1b−U2) = 28.2436; record 2 mean-F
  ΔF = 27.5572, spreads 0.5108 and 0.1756.
- `docs/autofit/PROGRESS.md:478` and
  `docs/autofit/bayesian-real-validation.md:10` remain consistent with the
  regenerated evidence.

No modifications made.

VERDICT: GO
