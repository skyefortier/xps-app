
1. **Blocker closure fix: closed.** `closure=False` is default; `+1` only applies with `closure=True`; `n_centered_pcs`, `n_states`, and `closure_assumed` are separately reported. Direct check: non-closed fixture `rank=2`; 1-state `rank=1`; closed with claim `rank=2`; same closed data without claim `rank=1`.

2. **build_matrix behavior: implementation closed; one test pin weak.** Auto grid now uses `floor` and stays inside overlap; user grids outside overlap raise `ValueError`; descending grids are sorted before interpolation. The non-commensurate regression test needs tightening as above.

3. **NNDSVD sign orientation: closed.** [multivariate_mcr.py:161](/Users/skyefortier/xps-app/autofit/methods/multivariate_mcr.py:161) uses positive-vs-negative part norms, not sign counts.

4. **Dead-component reseed: closed with caveat surfaced.** [multivariate_mcr.py:178](/Users/skyefortier/xps-app/autofit/methods/multivariate_mcr.py:178) reseeds from finite positive residual and reports `dead_component_reseeds`. It can still repeat/oscillate on degenerate over-rank cases, but that is now visible through reseed count plus convergence/max-iter fields.

5. **ALS convergence surfacing: closed.** `als_tol=1e-3` is documented as the Jaumot GUI default but UNVERIFIED for XPS; `als_converged`, final relative delta, and max-iter hit are in `analysis`.

6. **Result contract: closed.** `result_kind="state_decomposition"` and `n_states` are present in both `analysis` and `diagnostics`; `peaks=[]` is explicitly contractual.

7. **Payload reconstruction and NNLS orientation pins: closed.** Direct check reproduced payload LOF exactly, and tests directly pin `_nnls_rows(S, D)` / `_nnls_rows(C, D.T)` orientation.

I did not modify anything. Full pytest could not run because the sandbox has no writable temp directory, but direct Python checks of the core pins passed.

VERDICT: GO
