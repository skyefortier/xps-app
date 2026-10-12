# Q10 0c′ — a link the server cannot fit as drawn is refused (owner, 2026-10-11)

Owner: "Q10: yes to all three, each its own small unit, BEFORE any seal build … measured, Codex
x2." The third; found by the sealed-fit v6 design gate (rounds 3-4).

## The defect

- **Across lineshapes.** A linked peak takes its parent's lineshape (CLAUDE.md "Linked
  (Multiplet) Peaks"), but the page allowed a child of another shape. A Voigt child of a GL parent
  was sent `gl_ratio` 0.5 fixed; the server overrode it with the parent's mix (expression
  `p1_gl_ratio`) while the page drew the child at 0.5 (round 3's probe: up to 2.06 counts apart,
  success and certified). The server could not even see it: Voigt and GL are one backend shape.
- **A link to a peak that is gone.** Removing a chain's root deletes only its immediate children
  (`removePeak`); a grandchild stays linked to a deleted peak. The request builder silently drops
  its `constrain_to` and the local engine silently skips it: the peak is fitted free while the page
  shows it linked.
- Self-links and cycles were already refused by the server (audit F11) — but only when the fit
  ran, so `/api/fit/start` accepted the job and failed it later.
- **Two peaks sharing an id** (a project load keeps the ids it reads). The server's route refuses
  them ("Duplicate peak ids"); Batch Fit and the local engine fitted them, finding each link's
  parent as the FIRST peak with that id (found while reviewing 0b, Codex 0b round 2).

## The fix

- Page `_linkGraphFailure(peaks)`: a link to a missing peak (ids matched exactly, as `getPeak` and
  the local engine match them), a self-link, a cycle, or a link across lineshapes is refused in
  plain words, naming the peaks; so are two peaks sharing an id ("delete both and add them
  again": `removePeak` removes every peak with the id). Run Fit (incl. "Use this solution", on its start model) before the
  background, the undo entry and any request; Batch Fit before any target is touched; the local
  engine at its start.
- The request carries each peak's page lineshape, `frontend_shape` (additive; the seed and the fit
  ignore it — tested). Server `_validate_constraint_graph` refuses a link whose two
  `frontend_shape`s differ, or, without them, whose backend shapes differ; and it now runs in the
  shared request preparation, so `/api/fit/start` answers with the same immediate 400 as `/api/fit`.
  The Python twin `autofit.reference.peak_to_backend_spec` sends the field too.

## Measured

`scripts/link_graph_census.js` runs the page's `_linkGraphFailure` on every committed tab
(`docs/findings/link-graph/census.json`): 121 tabs, 530 peaks, 67 links in 57 tabs — none across
lineshapes, none to a missing peak, none self-linked, none in a cycle, no shared id. Nothing a user
has saved is refused, and no fit changes.

## Changed for direct server callers

A request made without the page (a script, a test, a Python twin) that links two different
BACKEND shapes is refused before the fit, HTTP 400, in plain words. Until now it reached lmfit:
a GL child of a Gaussian master referred to a `p1_gl_ratio` that does not exist and failed inside
the fit as RuntimeError (422, "Fit failed — see server log"); an asymmetric-GL master with a
pseudo-Voigt child fitted the expressions the two shapes share. Two existing tests built such
links: `test_a_broken_constraint_is_still_a_solver_failure_not_a_crash` now expects the earlier
refusal (still not a crash, the test's point), and the transitive-removal test in
`tests/test_component_required.py` gives its linked chain the parent's lineshape (its subject is
the chain, not the shapes). Nothing else on the server builds links: Find Peaks' engine has none,
and the scripts copy them from page models, which the census shows all share one lineshape.

## Tests

`tests/test_link_graph_refusal.py` (server: Voigt child of a GL parent refused; backend-shape
mismatch refused without the field; one lineshape fits with the same seed and curve with and
without the field; `/api/fit` and `/api/fit/start` both 400). `tests/js/link_graph.test.js` (the
page check's table; the builder's field; every call site). `tests/js/local_lm_descent.test.js`
(the local engine refuses, nothing changes). `tests/test_browser_link_graph_refusal.py` (real
page: the Voigt-under-GL case and a chain orphaned by `removePeak` are refused with nothing sent;
Batch Fit leaves the target untouched). Mutation-checked: removing the Run Fit or the Batch Fit
check fails the browser tests.

## Codex round 1 (NO-GO ×2) — fixed

- **`linked: false` (and 0) was read as a link.** The loader keeps `false` for an unlinked peak,
  and the request builder, the peak controls and the local engine read any falsy value as no link;
  the check searched for a parent with id `false` and refused a valid model. It now reads a link
  as they do: a truthy `linked`.
- **Two builders erased the evidence.** The page's `peakToBackendSpec` and its Python twin dropped
  `constrain_to` when the parent was gone, so Find Peaks' "Refit my current peaks" (`/api/analyze`,
  no page check) and the twin's refit path fitted an orphan free and reported success. Both now
  send the link whatever the parent; the server refuses it. The Find Peaks refit also runs the
  page check before any request.
- **The server's shared check** (`_validate_constraint_graph`, every route and `run_fit`) now
  refuses a constraint naming no peak in the request and two peaks sharing an id (compared as the
  parameter prefix spells it: 1 and "1" are one `p1_`): `/api/fit/start` answers 400 at once
  instead of starting a job that fails, and `/api/analyze` answers 400 instead of "Internal
  analyze error" (500). The page compares ids the same way and refuses a peak its own lookup
  cannot find (an id of NaN).
- **A lineshape switch reached only the parent and its immediate children,** so switching a
  three-level chain left the grandchild on the old shape — a model the new check refuses, which
  the switch could not repair (switching the grandchild returned early because its parent already
  had the shape). `_switchPeakShape` now switches the whole family — the root and every peak
  linked to it at any depth, from any member — and completes a family left mixed.
- Both runs noted that the same-lineshape rule is stricter than "cannot fit as drawn": some
  cross-shape links (a GL child of a Voigt parent) fit and draw identically. The rule is the
  owner's (a linked peak takes its parent's lineshape, CLAUDE.md), stated as such.
- Census re-run: 121 tabs, 67 links, none refused. Tests: each new case fails on 1dc2c87.

## Codex round 2 (NO-GO ×2, the same MAJOR) — fixed

- **The Python twin joined a link the page cannot resolve.** A root with id 1 and a child linked
  to "1": the page's exact lookup finds no parent and refuses; the twin turned both ids into text
  and sent a valid constraint, and `autofit.parity.refit_record` reported a successful fit of
  another model. The twin's builder now looks the parent up as the page does (`_page_same_id`:
  two numbers of equal value or two equal strings; a boolean never matches) BEFORE the ids become
  text, and refuses a link it cannot resolve. Tested both mixed-type directions and the boolean
  ones; all-number and all-string graphs still link. (A float id such as 1.0 is written "1.0" by
  the twin and "1" by the page — an old twin difference no saved file reaches, page ids being
  whole numbers; its only effect is that the twin refuses such a model, the safe side.)
- **MINOR (run A): `/api/analyze/start` admitted an invalid graph** and refused it inside the job.
  The analyze request preparation now runs the shared check, so the start route answers 400 at
  once like `/api/analyze`; a malformed `peak_specs` list is still left to the method's own
  validation. Added to the every-route test.

## Codex round 3 (A GO, B NO-GO on one MINOR) — fixed

Run A: no findings (24 route probes, the page paths, the twin, the census). Run B, MINOR: when
both peaks carried `frontend_shape`, the server compared only those labels, so a request
labelling a gaussian parent and a pseudo_voigt_gl child both "GL" — which the page cannot build
(it derives the backend shape from its own) — was admitted by the start routes and failed inside
the fit (`p1_gl_ratio is not defined`). The check now compares the backend shapes always and the
page's shapes too when both are named. Added to the shared-check and every-route tests.
