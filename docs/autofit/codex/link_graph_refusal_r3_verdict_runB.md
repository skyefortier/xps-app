**One MINOR gap remains in the promised immediate refusal. No BLOCKER or MAJOR found.**

[The shared validator](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/fitting.py:1501) stops comparing backend shapes when both `frontend_shape` fields exist. A Gaussian parent and pseudo-Voigt child, both labelled `frontend_shape: "GL"`, therefore pass.

Reproduced:

- `/api/fit/start` and `/api/analyze/start`: **202** with those labels; **400** without them.
- Actual fitting fails with `p1_gl_ratio is not defined`.

Compare backend shapes regardless of the additional labels, then check frontend shapes too. Add this contradictory-metadata case to the route tests.

**Non-physical inputs:** No abnormal spectra or parameters required, but this requires inconsistent, manually supplied API metadata. The page builder cannot produce it. No wrong fitted result was demonstrated.

The round 2 fixes hold: actual twin refits refuse both mixed-type orphan directions, while valid numeric and string IDs fit. Normal invalid graphs returned immediate 400s in all **24 route probes**. Run Fit and Batch Fit guards precede their fitting mutations.

Validation: **132 JavaScript checks and five focused Python tests passed**, including pinned twin parity. Census: **121 tabs, 530 peaks, 67 links, zero refusals**. The complete tested fit result, including seeded restarts, was unchanged by `frontend_shape`. Browser fixtures were not rerun under read-only restrictions.

The blanket cross-shape ban exceeds mathematical necessity, but follows the explicit owner policy. No files changed; sibling units excluded.

The remaining gap violates the stated every-route immediate-refusal requirement.

VERDICT: NO-GO.
