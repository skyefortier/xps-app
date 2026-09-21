Reviewed HEAD `f75db7a` against `35b950e`, read-only.

- **BLOCKER:** None found.
- **MAJOR:** None found. Round 9’s finding is resolved.
- **MINOR / fault-injection-only:** No additional findings.

Both archived reproducers now return `success=true`. With `n_perturb=0`, their complete responses equal direct least-squares, with χ² **0.000114071** and **0.0000285177**. Three-perturbation runs with DE seed 0 retained or improved those fits.

Response consistency also passed for a linked doublet through the in-memory API, including curves, statistics, bounds, expressions, and uncertainties.

Validation: **54 focused tests passed**, plus **28 additional real-solver cases** across all seven lineshapes. The upload test was excluded to preserve read-only execution. No files changed.

**VERDICT: GO.**
