# Seal 1a′ — the server side of the sealed fit record (option (b))

Design: `2026-09-02-background-architecture-sealed-fit-record.md` V6.2, V6.5 step 2, V6.6,
V6.7, V6.11 1a′, as amended by V6.22 (option (b): no key, no keyring, no attestation). Branch
`seal-1a-server` off main ef750f6 (+ the design branch merged for the memo). Additive on the
server; the page is not changed in this unit except the provenance meta tag it is served.

## What ships

1. **`fitted_sub`** in every fit response: the model sum, lmfit's `best_fit` (a fresh composite
   evaluation at the returned parameters, lmfit model.py:1587). `fitted_y` is unchanged and is
   `fitted_sub + background_y` exactly (that association, as today).
2. **Statistics formed from the returned arrays** (V6.6) — `y_sub = counts − background_y`,
   `w = 1/√max(counts, 1)`, `n_data = len(energy)`, `n_varys` = parameters with `vary` and no
   `expr`:
   `chi2_raw = Σ(((y_sub − fitted_sub)·w)²)` (NumPy's pairwise sum, as lmfit's
   `(residual**2).sum()`); `reduced_chi_square = chi2_raw / max(1, n_data − n_varys)`;
   `chi_square = max(chi2_raw, 1e-250·n_data)`; `aic`, `bic` by lmfit's formulas from that
   `chi_square`; NEW `rmse = √(Σ residuals² / n_data)`; `r_factor` as today. lmfit formed χ² from
   the residual of the minimiser's last evaluation; the reported value can therefore move.
   MEASURED on the 202 committed targets in one process (same fit, lmfit's value beside the
   array-formed one): `scripts/seal_1a_statistics_measure.py` → `docs/findings/seal-1a/`.
   Every internal decision (perturbed-restart ranking, the certificate, scattered starts, the
   required refit's `chi2_with`) keeps its own value — only the REPORTED statistics change.
3. **One background assembly** `_assemble_background(...)`: the window normalisation, every
   method, the flat hold, the effect — moved verbatim out of `_run_fit_impl`; `run_fit` and the
   verification call it. Also `_build_model(peak_specs)` and `_normalise_fit_kws(fit_kws)`, the
   same way, so the verifier builds the parameters and the seed's inputs with the fit's code.
4. **`_normalise_fit_request(body, energy, counts)`** in app.py: `_prepare_fit_request`'s
   validation with the arrays explicit; the fit routes call it after loading the session
   (every 400 / 404 word for word as before), the verification with the request's inline arrays.
   `session_id` is transport only.
5. **Provenance** (V6.7): `software.env_sha256` = SHA-256 of the sorted `name==version` lines of
   the installed distributions; `software.git_dirty` counts UNTRACKED files too. Per rendered
   page, `<meta name="xps-page">` = `{page_sha256, reference_sha256}`: the SHA-256 of the
   template source Jinja compiled for that render (recorded by a loader wrapper, so a cached
   template reports the source it was compiled from, never a later file on disk) and of the
   reference data injected (canonical JSON). `NUMERICS_VERSION` → "2026-10-13" (the reported
   statistics can change).
6. **`POST /api/verify-fit {R: {request, energies, counts}, O}`** — recomputes and compares,
   EXACTLY (no tolerance anywhere), never fits:
   - `software`: O's equals the verifier's, else `unconfirmed` "different software";
   - `schema`: O's keys, per-component ids / order / shapes / parameter names, arrays of the
     right length and finite;
   - `request`: R.request normalises (else `mismatch`, with the route's own message);
   - `data`: O.energy = energies + the shift, O.counts = counts;
   - `method`, `shift`, `seed` (the caller's, or `_request_seed` recomputed; `seed_source`);
   - `roles`: every parameter's `vary`, `expr`, `min`, `max` as the request builds it;
     `held`: a parameter with no expression and `vary` false has its held value; `expressions`:
     every expression evaluates, from O's free values, to O's value;
   - `determinacy`: n_varys < n_data;
   - `background`: `_assemble_background` on R's arrays = O.background_y, its verdict =
     O.background_verdict;
   - `components`: each `y` re-evaluated from O's parameters on O's energies, each `area`;
   - `fitted_sub`, `fitted_y`, `residuals` in their associations; `statistics`; `support` (with
     the linked-root rule).
   Answer: `{state: consistent | mismatch | unconfirmed, check, reason, software}`. NOT
   recomputed — shown as recorded (option (b)): `success`, `message`, σ, `certificate`,
   `starts`, `required`. Bit-stability per lineshape is 1b's measurement; a shape that is not
   bit-stable reads `mismatch` here until 1b / Q7 decide.

## Not in this unit

The page's R / O / D, `project`, `sealedState`, the labels and "Re-run this fit" (1c, 1d); 1b's
measurements.

## Also in this branch

The logged refusal-wording fix (Q10 0c′ Codex round 4, run B): a link across two backend shapes
both labelled "GL" now names the backend shapes (bfca83a).
