**Findings**

- **BLOCKER** [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:1478): `_bound_fixed_refit` copies `absent_slots` from the pre-refit report, and [line 1511](/Users/skyefortier/xps-app/autofit/engine.py:1511) then uses that stale absent-slot-adjusted BIC* for dominance. Scenario: a C 1s boundary-limited candidate has a contaminant/satellite classified absent before fixing a bound; the bound-fixed refit changes area or persistence, but BIC* still subtracts the old removed params and exported peaks still omit the old absent slot. The “honest k” claim is not reliable.

- **BLOCKER** [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:1474): the bound-fixed refit is allowed to return with fresh `outcome.boundary_hits`, but [line 1511](/Users/skyefortier/xps-app/autofit/engine.py:1511) still treats its BIC* as decisive. Scenario: fixing Cl ratio at 0.55 causes FWHM/offset/center to peg a different bound; the promoted `+bfix` model is still a boundary-constrained fit with an invalid interior-Laplace comparison.

- **MAJOR** [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:1471): override refits inherit free-fit stability and never run stability on the fixed-bound model. Scenario: the free boundary model is stable because the pegged parameter absorbs degeneracy, but once fixed, another slot becomes unstable; the override can still promote it and confidence reports stale persistence/MAD.

- **MAJOR** [autofit/grammar.py](/Users/skyefortier/xps-app/autofit/grammar.py:327), [autofit/methods/ic_model_comparison.py](/Users/skyefortier/xps-app/autofit/methods/ic_model_comparison.py:219): provenance is runtime-visible now, but it is region-wide rather than candidate/winner-specific and is returned by reference. Scenario: running only `A0_graphite_asym_satellite` still reports unused C 1s contamination constants as “uses”; mutating `res.analysis["constants_provenance"]` also mutates the reused `grammar.provenance`.

- **MAJOR** [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:1505): the override refits only the best pre-refit conditional candidate by stale free-fit BIC*. Scenario: candidate A has the best free boundary BIC* but fails after bound-fixing; candidate B’s bound-fixed refit would dominate clean, but is never tried.

- **MINOR** [tests/autofit/test_b1s_cl2p_parity_gates.py](/Users/skyefortier/xps-app/tests/autofit/test_b1s_cl2p_parity_gates.py:91): the Cl 2p gate is no longer tautological, but it does not assert `winner_boundary_hits == []` or ΔBIC* > 10 for the fixed-vs-clean comparison. It will miss the fresh-boundary and weakened-dominance regressions above.

I could not run the targeted pytest gate because `pytest` is not installed in this environment.

VERDICT: NO-GO (blockers: stale absent-slot-adjusted BIC* in bound-fixed refit; bound-fixed override can promote refits with fresh boundary hits)