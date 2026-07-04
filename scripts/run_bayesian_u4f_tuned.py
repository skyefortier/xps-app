#!/usr/bin/env python
"""
U 4f tuned-budget Bayesian run — (re)generates
docs/autofit/inventory/bayesian_u4f_tuned_run.jsonl under the CURRENT
bayesian_exchange_mc output schema.

Provenance: the original artifact was produced ad hoc (no committed
script) BEFORE the consumer-visible replicate-semantics flags landed, so
its replicated candidates lacked `free_energy_is_replicate_mean` — the
Codex Stage-5 re-check #3 blocker. This script is the committed,
reproducible generator.

Two records, mirroring the original evidence (PROGRESS.md section
"U 4f Bayesian resolution at tuned budget"):
  1. the full U 4f candidate set at 16 replicas / 4000 sweeps, seed 0;
  2. the U1b-vs-U2 head-to-head at the same budget, seed_replicates=2.

Resumable: done (anchor, method, config, seed) tuples are skipped on
re-run — the same append-only JSONL harness as the main battery runner,
which this script reuses. NOTE: the stale pre-schema artifact carries the
SAME keys, so a regeneration must start from a removed/empty file.

Usage: venv/bin/python scripts/run_bayesian_u4f_tuned.py   (~30-50 min)
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import run_bayesian_real_validation as battery                     # noqa: E402
from autofit.grammar import resolve                                # noqa: E402

battery.OUT = os.path.join(battery.REPO, "docs", "autofit", "inventory",
                           "bayesian_u4f_tuned_run.jsonl")

TUNED = dict(n_replicas=16, n_sweeps=4000)


def main():
    spec = battery.ANCHORS["U4f_Scan"]
    rf = battery._anchor_rf(spec)
    grammar = resolve(spec["phases"], spec["region"])
    done = battery._done_keys()
    print(f"== U4f_Scan tuned budget ({len(grammar.candidates)} candidates) "
          f"-> {battery.OUT} ==", flush=True)
    battery.run_bayes("U4f_Scan", spec, rf, grammar, dict(TUNED), 0, done)
    battery.run_bayes(
        "U4f_Scan", spec, rf, grammar,
        dict(TUNED, candidate_filter=["U1b_mains_satpair_freesep",
                                      "U2_mains_satfree"],
             seed_replicates=2),
        0, done)
    print("done", flush=True)


if __name__ == "__main__":
    main()
