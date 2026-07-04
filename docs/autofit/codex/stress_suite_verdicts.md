# Codex verdict trail — synthetic stress suite (run-brief item 2), 2026-07-04/05

Every round ran TWICE (severity-nondeterminism rail; stricter verdict
governs). Prompts committed alongside (`stress_suite_review_prompt.txt`,
`stress_suite_recheck_prompt.txt`, `stress_suite_recheck2_prompt.txt`;
round-4's factual prompt in the session scratchpad, quoted in the commit).
Full dispositions live in the PROGRESS.md stress section.

## Round 1 — unit review: NO-GO ×2
Blockers (converged): stale expectation evidence (JSONL rows carried
generation-time labels after measurement-arbitrated relabels); sparse
count-only PASS (0.7 eV position errors classified as recovery);
simpler_model classification laundering buried decisive alternatives.
Highs/mediums: Bayesian rows lacked n_emitted AND ran UNWEIGHTED on
Poisson data (the suite's own premise); nearest-neighbor truth matching
reused components; over-specified regime tested only empty flanking
windows; always-on pins froze measured-deficient behavior.
→ FIXED: library-as-single-source labels + battery REGENERATED (182
records; superseded generation in git history); sparse PASS requires
positions; buried_dominant_alternative classification; weighted Bayesian
(finding rewritten — the noise model, not the evidence machinery, was the
misdirection; 2 of 3 silent P3 overfits became true picks); one-to-one
matching; in-ROI decoy case added; conditional-invariant pins.

## Round 2 — re-check: GO + NO-GO (stricter governs)
Both runs caught an evidence misread: the in-ROI decoy is NOT pruned on
every draw — offset 2000 promotes the bound-fixed decoy via
decisive_override (P3_decoy+bfix, k=3, conditional-flagged but
structurally an invented component); the winner-stability section labeled
that prune failure "ambiguity evidence"; stale RELABEL prose remained.
→ FIXED: report/PROGRESS/pin docstrings state the per-draw truth; new
finding 8 (prune robustness is noise-draw-dependent —
criteria-calibration material); expectation-aware stability framing
(recover/prune flips = robustness FAILURES); prose scrubbed.

## Round 3 — re-check: GO + NO-GO (stricter governs)
One factual blocker left: finding 8 said the passing draws were
"χ²ᵣ ≈1.1" while offset-1000's P2 winner sits at 2.23.
→ FIXED: exact per-draw numbers (1.10 base / 2.23 offset-1000) in the
generator and PROGRESS; report regenerated.

## Round 4 — final factual re-check: **GO ×2**
Both runs verified the corrected per-draw numbers against the JSONL and
found no other numeric disagreement. The stress-suite unit is
review-complete: 14 ground-truth cases / 6 regimes, 182-record evidence
JSONL, generated report with encoded classification rules, 10 always-on
honesty pins, and a findings list whose every number survived four
adversarial rounds.
