# Background math implementation — Codex round 29, run B (commit dedeace)

Reviewed `bg-math-implement` at `dedeace`, read-only. **One MINOR finding; no demonstrated BLOCKER or MAJOR.**

1. **MINOR — The backward sum is not rigorously conservative at the RMSE boundary.** [templates/index.html:10249](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10249)

   The backward table adds squared residuals in a different order from `rmseVerdict`. Its maximum can round below the forward sum, pruning a reading that `tolOwn` accepts.

   Concrete helper-level reproducer:

   ```js
   const be = [280, 280.1, 280.2, 280.3, 280.4, 280.5];
   const rec = {
     rawBE: be,
     rawIntensity: [
       -87809067.2660619, 33063639.28131759,
       -94206236.07002199, 95697211.52074635,
       -9742030.92046082, 60016250.517219305
     ],
     fitResult: {
       fittedY: [
         19819426.350295544, 70811345.56792676,
         -98611670.26683688, -54457667.19058156,
         -80704812.00702488, -6804285.477846861
       ],
       rmse: 86675042.30314377
     }
   };
   _restoredFitGrid(rec, be, 0, 89769475.55784136, 0);
   ```

   This refuses the sole reading. Removing only the lower-bound prune accepts it: RMSE difference **5.2154064e−7**, versus `tolOwn` **5.2317658e−7**. The backward maximum falls one floating-point step below `ssMin`; the forward sum reaches it. Outward rounding bounds are needed for the backward accumulation and its addition to the partial sum.

   **Proportionality:** this deliberately places the stored RMSE at the tolerance boundary. I have not demonstrated an actual fitted record producing it or a realistic XPS failure. It disproves unconditional prune safety, but does not justify MAJOR. Neither search cap is involved.

Verification:

- Census and Python twin reproduce **0 current / 81 stale / 40 peaks-only**.
- All five measurement summaries and student-note figures reproduce.
- All **202** upload inputs, seeds, background arrays, and net areas match.
- **97 focused JS tests and 73 Python tests passed**, including the narrowed test’s actual four scattered draws.
- **15,000** generated search comparisons found the boundary discrepancy above.
- CI floor is exactly **566**. Full-suite validation remains incomplete under the read-only sandbox; browser/HTTP checks were not completed.

No files changed.

**VERDICT: GO**
