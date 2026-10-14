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
   `starts`, `required`. Every field is checked by its JSON TYPE (a numeric string, a flag for a
   number, a number for a flag are not a response's), never through a coercion. `unconfirmed`:
   other software; a non-finite number anywhere in O; or one of the two EVALUATION identities
   failing (a recorded curve / the model sum is this server's evaluation of the parameters) on a
   request with a lineshape that is not evaluated bit-identically (`NOT_BIT_STABLE_SHAPES` =
   LA(α,β,m), owner Q7 — never a tolerance; 1b measures the rest; every relation of the recorded
   arrays stays exact — round 2).

## Round-1 fixes (Codex NO-GO ×2)

- Parameter membership is EXACT (`_component_of`: the component model's own `param_names`) in
  the response, the support, the scattered starts, the required refit and the verifier — ids "1"
  and "1_x" no longer echo each other's parameters (a page's integer ids never overlapped).
  (Find Peaks' archived engine, `autofit/`, keeps its own prefix readers; not on a seal's path.)

## Round-2 fixes (Codex NO-GO ×2)

- O's arrays are never converted before comparison: each recorded number is compared EXACTLY with
  the computed float (two JSON integers beyond 2⁵³ no longer round into one); a curve holding a
  number no float represents is a schema mismatch.
- The non-bit-stable rule is scoped to the two EVALUATION identities only (a recorded curve is the
  server's evaluation of its parameters; the recorded model sum is the composite's). Every relation
  of the recorded arrays — areas, fitted_y, residuals, statistics, support — is computed from the
  recorded curves and stays an exact mismatch; a stable component's curve stays a mismatch.
- The recorded-only objects (`certificate`, `starts`, `required`), the statistics and the support
  have a typed schema: their truth is not recomputed (option (b)), their form is the producer's.
- Only a float can be non-finite (an id of 10**400 no longer answers 500).
- `_component_required` takes the removed components' own parameter names only.
- A link's splitting / ratio is written into its expression with −0.0 folded to 0.0 (a JSON
  writer spells −0 as 0); requests the page can send are unchanged.
- The verifier reads the parameters as the fitter holds them (Model.fit's deep copy orders
  reversed bounds and clips into them); the seed is still derived from the start.
- Every recorded value — free, held and expression — must be the value evaluated.
- The page digest is carried by the compiled template object, not keyed by name.

## Not in this unit

The page's R / O / D, `project`, `sealedState`, the labels and "Re-run this fit" (1c, 1d); 1b's
measurements.

## Also in this branch

The logged refusal-wording fix (Q10 0c′ Codex round 4, run B): a link across two backend shapes
both labelled "GL" now names the backend shapes (bfca83a).

## Round-3 fixes (Codex NO-GO ×2; no false `consistent` left in run B)

- One reading of a parameter's value: the float the fit evaluates and records (`float(par.value)`),
  for held, free and expression values alike (a held integer 10000000000000001 is evaluated and
  recorded as 1e16).
- The id schema is the producer's: any JSON scalar the fit routes accept (true, null, numbers, text).
- `_exact_float`: a recorded number no float represents, or one that overflows a float, is a
  mismatch — never a 500.
- Every stable component's evaluation is judged before an unstable one may answer `unconfirmed`.
- Tests on honest values beyond 2⁵³ (the integer equal to the honest float is consistent; the next
  integer, which rounds to it, is a mismatch) across every array family, parameters, areas,
  statistics and support.

## Round-4 fixes (Codex NO-GO ×2; no false `consistent` in either run)

- A free value is checked against its bounds as floats — the reading the producer records and the
  fit uses (an integer bound of 10000000000000001 is 1e16 to both).
- Parameters that cannot be evaluated (a modified fwhm of 1e308 overflows) are a mismatch: the
  producer evaluated its own parameters. Any other error inside the verifier answers `unconfirmed`
  ("error") — never a 500, never current.
- Inline R arrays beyond any float are refused with the route's 400.

## Round-5 fixes (Codex run A NO-GO, run B GO — the stricter governs)

- A NaN anywhere in the request's peaks or anchors (a JSON parser that reads the NaN token accepts
  it; a browser writes null) is `unconfirmed` ("non_finite"): differential evolution searched a NaN
  bound as open, and no range check holds against NaN.
- A body nested past the JSON parser's depth is the route's 400, not a 500.

## Round-6 fix (Codex run A NO-GO; run B failed on HTTP 429, no review)

- A request number with no exact reading is `unconfirmed`: a NaN anywhere, or ±Infinity anywhere
  but a bound key (`_min` / `_max`, where Infinity is an open side). An infinite start (also the
  JSON number 1e400) paired with a finite record had read consistent once the record's values
  replaced the start.

## Round-7b fixes (run A NO-GO on two MAJORs; no false consistent, no false stale, no 500)

- The non-finite request check runs before the parameters are built (an infinite centre was refused
  as a mismatch first).
- The docs say exactly what Q7 exempts: the two evaluation identities, not every curve-derived check.

## Round-7c fixes (both runs NO-GO, one MAJOR each; no false stale, no 500)

- R's saved arrays are read as saved: JSON numbers only (a numeric string is the route's 400), each
  exactly a finite float, else `unconfirmed` — never rounded into agreement with O.
- The verifier performs the fit's FIRST step, the evaluation of the START model on the fitter's copy
  (nothing fitted): a start whose evaluation RAISES (a Lorentzian fwhm of 1e160 overflows; HTTP 422)
  has no response — `mismatch / request`. (Superseded as the general rule by round 8's digest.)
- The verifier's docstring states Q7's exact scope.

## Round-8 fix (both runs NO-GO, the same class: a start the routes refuse, paired with an honest record)

The class is closed, not enumerated: every response reports `request_digest` — the full SHA-256 of
every input the fit started from, by effect (data, the background's effect, shapes, each parameter's
role with its start value and bounds, the method, solver options, n_perturb), the very digest the seed
is the first 32 bits of (seeds unchanged). The verifier recomputes it exactly, whatever the seed's
source, so a recorded response is bound to every starting number of its request: a changed start —
one the routes refuse (an amplitude of 1e308, a width of 0) or any other — is `mismatch /
request_digest`. Additive in the response (`RESPONSE_KEYS`).
