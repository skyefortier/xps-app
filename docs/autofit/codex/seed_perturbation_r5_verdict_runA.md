Reviewed HEAD `d98777d`, read-only.

- **BLOCKER:** None.
- **MAJOR:** None.
- **MINOR:** None newly introduced.

The Round 4 dispositions hold. In-memory `/api/fit` requests with IDs `1–5`, `2–6`, and `11/1/111/21/12` produced seed **4134790754** and byte-identical results after ID normalization.

Component order is **not a numerical no-op**. Using four-decimal energies, LM, zero perturbations, and caller seed 7, reversing the components changed the third component’s fraction from **5.17% to 8.76%**; both fits succeeded. Its seed may therefore change. Reordering across master/slave groups while preserving effective fitting order retained the seed and curve.

The [prefix rewrite](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1153) survived linked expressions, underscore IDs, and alias-like IDs. Regex metacharacters are rejected by lmfit before hashing. Overlapping underscore IDs expose a response-extraction defect already present on `main`, not a rewrite regression.

The [float64 conversion](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1216) also accepts numeric lists/object arrays that previously failed and strips masked-array masks. Masked samples were already mishandled on `main`; no production caller supplying masked arrays was found.

Validation: **41 passed, 2 upload-writing tests excluded**, plus the in-memory API and adversarial probes. No files changed.

**VERDICT: GO.**
