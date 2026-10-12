# Q10 0c — a linked child shows the values the server fitted (owner, 2026-10-11)

Owner: "Q10: yes to all three, each its own small unit, BEFORE any seal build … measured, Codex
x2." The second of three; found by the sealed-fit v6 design gate (round 2, both runs).

## The defect

The server derives a linked component's centre, amplitude, width and shape parameters from its
parent by expressions, whatever the child's lock flags (`fitting._make_peak_params` sets the
expression before any held value). The page's `_applyBackendParams` skipped every LOCKED field, so
a linked child with a lock kept the page's own value: the sidebar, Results and the drawn curve
showed a model the server did not fit (the gate's probe: child centre 299 shown, 287 fitted;
amplitude 10 / 50; FWHM 3 / 1). The "other solutions" preview (`_altPeaks`) did the same.

## The fix

- `_applyBackendParams`: a locked field keeps its value EXCEPT one the server reports with an
  expression — then the server's value is taken. Shape guards unchanged (a Voigt's mix is still
  never written back; a Voigt child of a GL parent is Q10 0c′).
- `_altPeaks`: a linked component's alternative values are marked as expression values (the server
  fitted them from the parent), so the same rule applies in the preview.

## Measured

Committed models (`autofit.reference.load_project_tabs` over docs/autofit/test_data): 67 linked
children, 12 with a lock. Every one of the 12 already holds its parent-derived centre, amplitude,
width and active shape parameters; the only differences are the `glMix` of 9 Voigt children
(4-GTA UCl4-BN U 4f₅/₂ satellites), which a Voigt never reads and the apply step never writes. So
no committed result changes.

## Tests

`tests/js/lineshape_roundtrip.test.js`: for GL, asym-GL, DS, DS+G and LA, a linked child with its
linked fields locked at stale values, fitted by the real `run_fit` through the page's own builder
and applied by `_applyBackendParams`, is drawn exactly as fitted (≤ 1e-6 of amplitude, the file's
parity bound) and carries the server's centre and amplitude; all five fail with the old rule.
`tests/js/scattered_starts.test.js`: a linked child's alternative preview takes the alternative's
values despite its locks, an unlinked locked field keeps its own; fails with the old preview.

## Codex round 1 (NO-GO ×2) — fixed

Both runs confirmed the page fix (expressions only from links; Voigt guard intact; every apply
path; the measurement reproduced: the 12 locks are inactive `fixCaM` flags on GL / Voigt peaks).

| finding | fix |
|---|---|
| MAJOR the Python write-back twin (`autofit.reference.apply_backend_params`, used by `autofit.parity.refit_record`) kept the old rule, and its equivalence test fed only `expr: null` (both runs) | the twin takes an expression-valued locked field; a plain-value record (expressions lost) counts a linked peak's fields as expressions — the page's `_altPeaks` rule; the equivalence test adds locked linked peaks with real expressions and with plain values, and unlinked locked peaks whose locks hold |
| MAJOR the LA case locked no `caM`, so restoring the old rule for `m` alone passed (run A) | the LA child's stale `caM` is locked; every locked shape field is asserted to carry the server's expression value |
| MINOR the alternative fixture was not a solution the server could return (run A) | the child's offset and ratio now make the alternative's child its parent's through the link (and one lineshape) |

Mutation-checked: the old rule for LA's `m` alone, and the old rule in the twin, each fail a test.

## Codex round 2 (GO ×2) — one MINOR fixed

Both runs: no BLOCKER or MAJOR; round 1's findings fixed; every added test fails with the old
rule; the committed-data measurement reproduced (67 linked children, 12 with locks — all inactive
`fixCaM` flags — no active-parameter difference). The same MINOR from both: the alternative-
preview fixture gave the LOCKED parent centre 284.45, which the server would report at its locked
284.40, so the previewed child did not sit at parent + offset. Fixed in the test: the alternative
reports the parent at 284.40, the child's offset is taken from it, and the test asserts child =
parent + offset and amplitude = parent × ratio; the unlinked-lock assertion keeps the 284.45
alternative.
