Reviewed HEAD `f75db7a` against `35b950e`, read-only.

- **BLOCKER:** None found.
- **MAJOR:** None found.
- **MINOR / fault-injection-only:** No additional findings.

Both round 9 reproducers now return successful fits. With `n_perturb=0`, their complete responses equal direct least-squares, including χ² **0.000114071** and **0.000028518**. Three perturbations retain or improve those results.

Validation: **54 regression tests passed**; one upload test excluded to preserve read-only execution. Another **28 checks across all seven shapes** and **four real DE evaluation-budget failures** passed candidate-retention and response-consistency checks, without modifying solver outputs.

No new reachable defect found under (a)–(c). Full suite not independently rerun. No files changed.

**VERDICT: GO**
