**Findings**

- **BLOCKER** [autofit/methods/multivariate_mcr.py:131](/Users/skyefortier/xps-app/autofit/methods/multivariate_mcr.py:131): auto-rank unconditionally adds `+1 for closure`, but the ALS model does not enforce or validate closure. For non-closed two-state data with independently varying component amounts, centered PCA legitimately needs 2 PCs and this code reports 3 states. Fix: make closure an explicit option, default no `+1` unless closure is assumed/enforced, and report cumulative scree plus the selected PC count separately from state count.

- **MAJOR** [autofit/methods/multivariate_mcr.py:67](/Users/skyefortier/xps-app/autofit/methods/multivariate_mcr.py:67): `build_matrix` can generate grid points outside the overlap. If `hi-lo` is not near an integer multiple of the densest step, `np.arange(lo, hi + 0.5*step, step)` may include `> hi`; `np.interp` then silently edge-fills. Fix: construct `grid <= hi + eps` explicitly, optionally append `hi` only by policy, and validate user-supplied grids are inside the overlap.

- **MAJOR** [autofit/methods/multivariate_mcr.py:142](/Users/skyefortier/xps-app/autofit/methods/multivariate_mcr.py:142): SVD init sign-flips by sign count, then clips. A PC with fewer high-magnitude negative channels and many tiny positive/noisy channels can be kept in the wrong orientation and clipped into a near-degenerate atom. Tests use an easy two-component path and miss this. Fix: use NNDSVD-style positive/negative norm splitting, residual-based seeds, or multi-start deterministic initializations.

- **MAJOR** [autofit/methods/multivariate_mcr.py:155](/Users/skyefortier/xps-app/autofit/methods/multivariate_mcr.py:155): dead-component reseeding to uniform `1e-12` makes the next NNLS design nearly singular and can create huge arbitrary spectra in the dead column, especially after over-ranked auto-rank. It can also hide component death as a “state.” Fix: drop/flag dead components or reseed from a finite-scale positive residual pattern, and surface reseed counts/warnings.

- **MAJOR** [autofit/methods/multivariate_mcr.py:164](/Users/skyefortier/xps-app/autofit/methods/multivariate_mcr.py:164): convergence is reported only by LOF history length; hitting `max_als_iter` still returns success with no `converged` flag, final delta, monotonicity check, or factor-stability check. Fix: report `converged`, `final_lof_delta`, max-iteration warning, and ideally assert block updates do not increase RSS except after explicit reseeding.

- **MAJOR** [autofit/methods/base.py:26](/Users/skyefortier/xps-app/autofit/methods/base.py:26) / [autofit/methods/multivariate_mcr.py:208](/Users/skyefortier/xps-app/autofit/methods/multivariate_mcr.py:208): `MethodResult.peaks` is documented as the winning decomposition components, but MCR returns `success=True` with `peaks=[]`. The message says “states,” which is good, but generic consumers can still read empty peaks as “no result.” Fix: add an explicit `result_kind: "state_decomposition"` / `n_states` contract or extend `MethodResult` with non-peak components.

- **MAJOR test gap** [tests/autofit/test_multivariate_mcr.py:42](/Users/skyefortier/xps-app/tests/autofit/test_multivariate_mcr.py:42): current tests would pass with a rank estimator that always returns 2. They also do not reconstruct `D_hat = C_payload @ S_payload.T`, so wrong payload scaling could pass. Add pins for a closed 3-state mixture, a non-closed 2-state matrix, reconstruction LOF from payload, direct `_nnls_rows` orientation on known `D=C S.T`, descending-grid interpolation, and the overlap endpoint case above.

**Checked OK**

- `_nnls_rows(S, D)` and `_nnls_rows(C, D.T)` have the right orientation for row-wise NNLS.
- Unit-max normalization is algebraically correct: `C*scale` and `S/scale` preserve `C @ S.T`.
- Descending grids are sorted correctly before `np.interp`; the bug is endpoint generation, not sort order.
- Rotational ambiguity language is adequate: it says feasible, not unique, and warns against chemical claims without constraints.

I did not modify files. I also could not run pytest in this sandbox because package import hit the read-only temp-dir restriction through `lmfit`/`dill`.

VERDICT: NO-GO (blockers: auto rank overcounts non-closed data)
