# Fable 5 Weekend Marathon — Unsupervised Autonomous Run

*Supersedes the Stage-2-only kickoff for this scenario: Fable expires ~Jul 7–8, and no human review is available until Mon Jul 6. Goal = extract maximum Fable value autonomously; clean up later with Sonnet 5 / Opus 4.8.*

---

## STEP 0 — before you launch (2 minutes)
1. In the tmux terminal, on branch `feature-autofit-stage2`, launch Claude Code: `claude`
2. Set model: `/model` → **Fable 5**
3. Make sure the doc it needs is in the repo: `docs/autofit/` contains `phase1-grammar-architecture-spec-v2.md`, `peak-fit-methods-decision-matrix.md`, `WORKING-PLAN-peak-fit-feature.md`, and **this file** (`fable-weekend-marathon-RUN-THIS.md`). Also let it clone the public `xps-app-fitalg` repo.
   - **Experimental data is pre-loaded** (raw C 1s / B 1s / N 1s / U 4f / Cl 2p spectra + `.json` fits + fitted `.proj.zip`). Just confirm it sits somewhere **under the repo** (e.g. `docs/autofit/data/`) so Fable can read it — and if the folder isn't obvious, name the path in the goal.
4. **Prevent your Mac from sleeping** (or the run dies when the machine sleeps). In a separate terminal tab: `caffeinate -dimsu &` — and keep the Mac plugged in and online.

## STEP 1 — paste this `/goal` (confirm flag spelling with `/goal` in-session first)

```
/goal "Build the XPS automatic peak-fit engine as far as you can, autonomously and UNSUPERVISED (no human review until Monday). Follow docs/autofit/fable-weekend-marathon-RUN-THIS.md and docs/autofit/phase1-grammar-architecture-spec-v2.md. Read both in full first, plus the current xps-app main and the public xps-app-fitalg repo.

HARD SAFETY RAILS (I am away all weekend):
- Work ONLY on the current feature branch. NEVER merge to main. NEVER deploy. NEVER git push --force. NEVER touch the existing /api/fit route or the manual-fit default path. The new engine is strictly additive and opt-in.
- Commit AND push the branch after every self-contained unit, so nothing is lost if you crash or top out.
- After every unit, run the full test suite; the existing manual-fit path must stay green (parity). If it goes red, fix before moving on.
- If a unit fails after 3 honest attempts, LOG it in docs/autofit/PROGRESS.md and move to the next INDEPENDENT unit — do not loop and burn tokens.
- Scientific integrity: never emit a binding-energy or RSF value from model memory; every physical constant is lit-cited or flagged UNVERIFIED; machine-generated element data is flagged unverified-until-reviewed.

DATA: real experimental files are pre-loaded in the repo — raw C 1s / B 1s / N 1s / U 4f / Cl 2p spectra, their .json fits, and fitted .proj.zip projects. Locate them and use them as the per-region validation and parity cases (build the Task-1 characterization battery from the C 1s set; validate each new region against its real fits). Treat the provided fits as EXPERT REFERENCE, not ground-truth-perfect — some are rough or contain known errors (e.g. a stray 'Zr 3d' RSF tag on a boron peak; weak-signal B4C fits; a Cl 2p fit with elevated reduced chi-squared). Where the engine disagrees with a provided fit, LOG the discrepancy in PROGRESS.md for human adjudication — do NOT silently force the engine to match a rough fit, and do NOT alter the source data files.

ORDER OF WORK (go as far as you get):
1. Stage 2: regression/parity safety net; schema round-trip (analysis namespace + per-peak _confidence); resolver skeleton with the PeakFitMethod seam (least-squares + IC implemented, others stubbed); prove C 1s parity.
2. Stage 3: U 4f module — asymmetric LA mains + explicitly modeled satellites, one joint fit; multi-element co-fit (e.g. U 4f + N 1s overlap); the bounded-asymmetry + residual-flag safeguard.
3. Additional regions via the region cookbook (C 1s, U 4f already; then B 1s, N 1s, Cl 2p).
4. The Bayesian exchange-Monte-Carlo method (per the decision matrix), as a selectable PeakFitMethod.
5. The comprehensive element-physics database across as many elements/core-levels as authoritative XPS data supports — tiered/sourced, extending the existing periodic-table reference system, machine entries flagged UNVERIFIED.

VERIFICATION (independent eyes, since no human is watching): in addition to your own test loop and the /goal supervisor's independent final check, at each STAGE checkpoint (end of Stage 2, end of U 4f, end of each new region, after the Bayesian method) invoke the Codex plugin (/codex) to adversarially review that stage's branch diff — run it as codex exec with inspection forbidden, high reasoning effort, and an explicit demand for findings. Fix any blocker/major findings before proceeding; log the rest in PROGRESS.md. If Codex hangs or errors (it has a history of hanging), wait briefly, log it, and proceed — NEVER let a Codex call stall the run.

HANDOFF: keep docs/autofit/PROGRESS.md updated continuously — what's done, what's tested, what's UNVERIFIED/suspect, what's next, any blockers, and every Codex checkpoint verdict. This is the handoff for a later Sonnet 5 / Opus 4.8 session. Stop only when you top out or exhaust the ordered work." --turns 600
```

*(Budget note: keep it loose — you WANT it to run long. A turn cap avoids infinite loops; skip a tight `--time` cap so it doesn't quit early Friday. It will likely stop when it hits your plan's Fable token limit; that's fine — everything is committed, and you can re-launch the same `/goal` to resume.)*

---

## Why this is safe to walk away from
- **Branch-only, no merge, no deploy, no touching `/api/fit`** → your live app is untouched no matter what it does.
- **Commit + push after every unit** → a crash, a sleep, or a token top-out loses nothing.
- **Full test suite + manual-fit parity after each unit** → it can't silently break existing behavior on the branch.
- **`PROGRESS.md` handoff log** → Monday-you (and Sonnet/Opus) can see exactly what's done, what's trustworthy, and what's next.
- **Three verification layers, no human needed:** (1) Fable's own test/debug loop, (2) `/codex` adversarial review at each stage checkpoint, (3) the `/goal` supervisor's independent final verification. Codex hangs are handled gracefully (log + proceed), so they can't stall the run.

## Monday (Jul 6) handoff checklist
1. Read `docs/autofit/PROGRESS.md` first — that's the map.
2. `git log`/`git diff main` on the branch; run the test suite.
3. Anything marked UNVERIFIED → adjudicate against NIST / primary literature before trusting.
4. Hand the diff to Codex for the implementation review.
5. Continue or fix with **Sonnet 5 / Opus 4.8** from where PROGRESS.md leaves off.
6. **Nothing merges to main or deploys until you've reviewed it.**

## Known reality
- Fable is token-heavy; it may top out or pause at plan rate limits and (during the included window) resume as limits reset. Commit-as-you-go makes any stop harmless.
- It will almost certainly NOT finish everything (the element-physics DB alone is huge). That's expected — "as far as it gets" is the goal, and lesser models finish the rest.
