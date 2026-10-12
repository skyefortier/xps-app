No BLOCKER, MAJOR, or MINOR findings. The round 3 gap is closed.

- All **28 probes across four HTTP routes** returned immediate 400s, including different backend shapes both labelled `"GL"`.
- Page guards cover Run Fit, alternative starting models, Batch Fit, and local fitting. Auto-Fit builds unlinked models. Valid chains, family switches, and ordinary numeric/string IDs remain supported.
- `frontend_shape` left the tested complete fit result unchanged: seed, restarts, curve, and record. Both Python/page parity checks passed; no saved-file format change found.
- Some cross-shape pairs are mathematically compatible. Refusing them follows the explicitly documented owner policy.
- Census reproduced **121 tabs, 530 peaks, 67 links, zero refusals**.

Validation: **104 distinct JavaScript checks and six focused Python tests passed**. HTTP probes mocked session loading. Browser fixtures were inspected but not rerun under read-only restrictions; source-pattern tests establish wiring, not complete behavioral proof.

No files changed. Sibling units 0b and 0c excluded.

VERDICT: GO
