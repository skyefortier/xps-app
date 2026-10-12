# Q10 — the three link units combined for one deploy (2026-10-12)

Owner 2026-10-11: "Q10: yes to all three, each its own small unit … stop for my deploy approval on
each (or batch them if you prefer, but say so)." Batched: each unit was reviewed on its own branch
against main 8cc3750 until Codex GO ×2; this branch merges the three (merge commits keep each
unit's reviewed history) for one deploy.

| Unit | Branch | Plan | Codex |
|---|---|---|---|
| 0b — the local engine resolves links in dependency order | `fix-local-link-order` | `2026-10-12-local-link-order.md` | GO ×2 at round 5 |
| 0c — a linked child shows the values the server fitted | `fix-linked-child-values` | `2026-10-12-linked-child-values.md` | GO ×2 at round 2 |
| 0c′ — a link the server cannot fit as drawn is refused | `fix-link-graph` | `2026-10-12-link-graph-refusal.md` | GO ×2 at round 4 |

## What the merge changed

- **Text conflicts:** only the CI JS floor and the end of `tests/js/local_lm_descent.test.js`,
  where 0b and 0c′ each appended tests (both kept). `templates/index.html` merged cleanly.
- **0b's malformed-graph tests.** On its own branch 0b proved that a malformed graph (shared or
  unmatchable ids, a missing parent, a self-link, a cycle — with or without a reversed chain)
  commits exactly what main committed, by running main's engine beside its own. With 0c′ the
  local engine refuses every such graph at its start, so none is fitted at all: the comparison
  and the self-link test are replaced by one test that runs 0b's malformed cases through the
  combined engine and requires a refusal with nothing changed. 0b's peak-order fallback stays as
  written (reviewed) but is no longer reached through `runFitLocal`.
- **`scripts/local_link_order_identity.js`** extracts 0c′'s `_linkGraphFailure` where the page
  has it (main's does not).

## Measured on the combination

- Identity (local engine, 121 committed tabs, against main 8cc3750): 121 bit-identical.
- Link census (the page's check on every committed tab): 121 tabs, 530 peaks, 67 links, none
  refused.
- 0c's committed-data measurement (no committed locked linked child differs on a parameter its
  shape reads) is unaffected by the other two.

## Codex on the combination (round 1, GO ×2)

Both runs: no BLOCKER, MAJOR or MINOR. Each merged function equals its branch's version
(`runFitLocal` = 0b's plus 0c′'s early refusal; `_applyBackendParams` / `_altPeaks` = 0c's; the
builder, validator, family switch and guards = 0c′'s); the floor 610 + 6 + 6 + 8 − 1 = 629;
82 944 and 287 496 adversarial graph cases found no malformed graph reaching 0b's fallback
unrefused; the replacement test fails with the refusal removed; family switches with locked
children pass real backend fitting and write-back; identity 121 / 121 and the census reproduced.
Suites on the combination: pytest 1404 passed / 7 skipped, JS 629 passed. READY for the owner's
deploy approval.
