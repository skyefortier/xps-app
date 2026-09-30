# A2 round 10 — run A (commit a06e2da; codex exec, reasoning high)

No BLOCKER, MAJOR, or MINOR findings reproduced at `a06e2da`.

Round-9 fixes hold: explicit shape resolves broad-component ambiguity, invalid shapes fail closed, and NaN/±Infinity reconstructions fail. The added field is harmless in the inspected page, Python, persistence, and export consumers. No above-resolution false acceptance or same-minimum false rejection reproduced. The accepted finite-resolution ruling stands.

Validation:

- **110 Python tests passed:** certificate, equality, and C 1s parity.
- **158 JavaScript tests passed:** 122 focused regressions and 36 lineshape round-trip tests.
- Additional certificate exit, evaluation-cap, and restart-cancellation probes passed.
- Recorded displacement notices remain **0/202 per method**.

Full suites were not rerun. Read-only Python setup required an in-memory temporary-directory bootstrap. No files changed.

VERDICT: GO
