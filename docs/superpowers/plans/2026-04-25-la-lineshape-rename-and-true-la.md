# LA Lineshape Rename + True CasaXPS LA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct a long-standing mislabeling — our current "LA (α,β,m) [CasaXPS]" lineshape is actually a Doniach-Šunjić core convolved with a Gaussian. Rename it to "DS+G (DS core × Gauss conv)" everywhere, then add a NEW lineshape that implements the *actual* CasaXPS LA(α,β,m) formulation (asymmetric base Lorentzian raised to piecewise α/β exponents, then Gaussian-convolved with integer-point kernel). Existing saved fits auto-migrate from the old shape to DS+G with no user action.

**Architecture:** Three layers of change:

1. **Backend (`fitting.py`):** rename `_la_casaxps` → `_ds_g_dscore_gauss` (math unchanged); register under new id `ds_g`. Add new `_la_casaxps_true` function under id `la_casaxps`. Both registered in `_SHAPE_FUNCS` dict.

2. **Frontend (`templates/index.html`):** rename `peak.shape === 'LA'` → `peak.shape === 'DSG_LA'` (not `DS+G` because plus-signs are awkward in JS string identifiers; the *display label* is "DS+G (DS core × Gauss conv)"). Add new `peak.shape === 'LACX'` for true CasaXPS LA, with new field names `caAlpha`/`caBeta`/`caM` to prevent unit confusion against DS+G's existing `laAlpha`/`laBeta`/`laM` (which retain their HWHM-eV semantics).

3. **Migration (JavaScript only — NOT `parser.py`):** the `.fit.json` and `.proj.json` formats are loaded entirely in JS via `_applyFitJSON` (line 6566) and `_loadProjectJSON` (line 6632). Add a `_migrateLineshapeAliases(peaks)` helper called at the top of both functions. Maps `'LA'` → `'DSG_LA'` (frontend enum). Backend doesn't need migration because the `/api/fit` request is built fresh on each fit; if peak.shape is `'DSG_LA'` after migration, `peakToBackendSpec` emits `spec.shape = 'ds_g'` and the backend dispatch finds `_ds_g_dscore_gauss`. Both are equivalent because the math is identical and we keep all DS+G parameters identical to the old LA.

**Tech Stack:** Python/Flask + lmfit for backend; single-file JS frontend; numpy/scipy for the new LA convolution. New unit tests run via inline `venv/bin/python -c "..."` or `/tmp/` scripts (no `tests/` dir).

---

## Critical design decisions surfaced for review

These deviate from the spec or fill gaps. **The plan assumes these decisions are accepted; flag any disagreement before execution.**

### D1. Migration lives in JavaScript, not `parser.py`

The spec said "In `parser.py` (or wherever `.fit.json` ingestion happens)". `parser.py` only handles raw spectrum binaries (.csv/.tsv/.xlsx/.vgd). The `.fit.json` and `.proj.json` formats are pure JSON loaded by JavaScript — there is no Python ingestion path. The migration helper goes in [templates/index.html:6566-6700 area](templates/index.html#L6566), called from both `_applyFitJSON` and `_loadProjectJSON`. The console.info log the spec asks for becomes a JS `console.info('[migration] …')` — visible in the dev console, not user-facing.

### D2. Backend ID rename per spec; frontend internal enum gets a new value too

Spec says rename backend `la_casaxps` → `ds_g`. Frontend `peak.shape === 'LA'` is touched at 12+ sites. To avoid leaving `'LA'` as the JS enum value while the backend says `ds_g`, we change the JS enum to `'DSG_LA'` (NOT `'DS+G'` — `+` is fine in strings but awkward as a code identifier). The DROPDOWN DISPLAY LABEL is the human-readable string the user sees; that becomes `"DS+G (DS core × Gauss conv)"`.

Three different strings live in different layers — be deliberate:

| Layer | Old | New |
|------|-----|-----|
| Backend `_SHAPE_FUNCS` key | `la_casaxps` | `ds_g` |
| Backend function name | `_la_casaxps` | `_ds_g_dscore_gauss` |
| Frontend `peak.shape` enum | `'LA'` | `'DSG_LA'` |
| Frontend dropdown `<option value>` | `"LA"` | `"DSG_LA"` |
| Frontend dropdown display text | `"LA (α,β,m) [CasaXPS]"` | `"DS+G (DS core × Gauss conv)"` |
| `peakToBackendSpec` emits | `spec.shape = 'la_casaxps'` | `spec.shape = 'ds_g'` |

For the NEW true-LA shape:

| Layer | New |
|------|-----|
| Backend `_SHAPE_FUNCS` key | `la_casaxps` (now points to new shape) |
| Backend function name | `_la_casaxps_true` |
| Frontend `peak.shape` enum | `'LACX'` |
| Frontend dropdown `<option value>` | `"LACX"` |
| Frontend dropdown display text | `"LA(α,β,m) [CasaXPS]"` |
| `peakToBackendSpec` emits | `spec.shape = 'la_casaxps'` |
| Frontend param fields | `caAlpha`, `caBeta`, `caM` (distinct from DS+G's `laAlpha`/`laBeta`/`laM`) |

### D3. Display-label collision with existing `DSG` shape

The repo already has a shape `'DSG'` whose dropdown label is `"DS × Gaussian (DS + instr. broadening)"` — backend `_doniach_sunjic_gauss`. The renamed-old-LA's new display label `"DS+G (DS core × Gauss conv)"` is visually similar but mathematically distinct (different DS parameterization, different Gauss-broadening implementation). Both stay in the dropdown.

If you want to consolidate (merge `DSG` and `DS+G` into one shape), that's a separate decision — flag now and we'll revise. Default plan: keep both, with disambiguating display labels.

### D4. New LA's parameter semantics

Per spec: α exponent (default 1.0, bounds [0.1, 5.0]) on **high-BE side** (BE-axis convention, sign-flipped from CasaXPS's KE-axis); β exponent same range on **low-BE side**; `m` integer 0–499 in **data points** (not eV). At α=β=1, m=0 the new shape is a pure Lorentzian — Task 4 unit test asserts equality to 1e-10.

Frontend `caM` field is rendered as integer-stepped input (`step="1" min="0" max="499"`). Tooltip on `caM` shows the effective eV width on the current dataset: `≈ (m/3) × dx` where `dx` is the data step size.

### D5. Backend β/m semantics differ between old DS+G and new LA — DO NOT share field names

DS+G's existing β is **HWHM in eV**. New LA's β is a **dimensionless exponent**. Same Greek letter, totally different meaning. If the user switches a peak from DS+G → LACX, sharing `laBeta` would make 0.3 eV become a 0.3 exponent, silently giving nonsense. Solution: distinct frontend fields per shape (`laBeta` vs `caBeta`); the lineshape switch in `updatePeakParam` is responsible for setting reasonable defaults when the shape changes.

### D6. `m` as integer in lmfit

lmfit Parameters are floats. We store `m` as float in lmfit and round-to-int inside `_la_casaxps_true(...)`. Default `vary=False` because users typically fix m and tune α/β; the `caM` UI field has a lock icon like other params (defaults to locked).

### D7. Backend constraint: this IS allowed under the round-2 backend freeze

The Auto-Fit C1s Graphite freeze [memory note](../../../.claude/projects/-home-skye-xps-app/memory/feedback_autofit_backend_freeze.md) explicitly carves out: *"This freeze applies specifically to the Auto-Fit C1s Graphite feature in its current iteration cycle. It does not preclude backend changes for unrelated features (e.g. a new fitter, a new file format, a bug in existing fitting code unrelated to Auto-Fit)."* This is a lineshape feature change, not Auto-Fit. The freeze does not apply.

---

## File map

| File | Action |
|------|--------|
| `backups/{fitting,parser,app}.py.backup47`, `backups/index.html.backup47` | Create (Task 1) |
| `fitting.py` | Rename `_la_casaxps` → `_ds_g_dscore_gauss`; add `_la_casaxps_true`; update `_SHAPE_FUNCS`, the docstring header, all string-id branches in `_make_peak_params` |
| `templates/index.html` | Rename `'LA'` → `'DSG_LA'` everywhere; rename param-row label; relabel dropdown text. Add `'LACX'` as new shape with new param fields `caAlpha`/`caBeta`/`caM`, new dropdown option, new param row, new sync-keys entry, new `peakToBackendSpec` branch, new `applyBackendResult` branch, new JS lineshape function `laTrueCasaXPS`, new evaluator branch in the per-peak `evalPeak` switch. Add `_migrateLineshapeAliases(peaks)` helper called at top of `_applyFitJSON` and `_loadProjectJSON`. |
| `parser.py` | **NO CHANGES** (does not handle .fit.json/.proj.json) |
| `app.py` | **NO CHANGES** (the `/api/fit` request shape isn't versioned by lineshape; renames pass through transparently) |
| `docs/superpowers/plans/2026-04-25-la-lineshape-rename-and-true-la.md` | Create (this file) |
| `CLAUDE.md` | Update the "LA(α, β, m) — CasaXPS Convention" section to describe BOTH shapes |
| `/tmp/test_la_reduces_to_lorentzian.py` | New — Task 5 |
| `/tmp/test_la_reduces_to_voigt.py` | New — Task 5 |
| `/tmp/test_dsg_alias_migration.py` | New — Task 7 (frontend migration logic Python-ported) |

No `tests/` directory; ad-hoc tests in `/tmp/` matching the established pattern.

---

## Tasks

### Task 1: Backups before any edits

**Files:**
- Create: `backups/fitting.py.backup47`
- Create: `backups/templates_index.html.backup47`
- Create: `backups/parser.py.backup47`
- Create: `backups/app.py.backup47`

- [ ] **Step 1: Copy current state to numbered backups**

```bash
cp /home/skye/xps-app/fitting.py /home/skye/xps-app/backups/fitting.py.backup47
cp /home/skye/xps-app/templates/index.html /home/skye/xps-app/backups/templates_index.html.backup47
cp /home/skye/xps-app/parser.py /home/skye/xps-app/backups/parser.py.backup47
cp /home/skye/xps-app/app.py /home/skye/xps-app/backups/app.py.backup47
```

- [ ] **Step 2: Verify backups exist and are non-empty**

```bash
ls -la /home/skye/xps-app/backups/*.backup47 | awk '{print $5, $NF}'
```

Expected: 4 lines, all sizes > 0.

(No commit — backups live in untracked dir.)

---

### Task 2: Backend — rename `_la_casaxps` → `_ds_g_dscore_gauss`, register under `ds_g`

**Files:**
- Modify: `fitting.py:5-15` (header docstring listing available shapes)
- Modify: `fitting.py:148-310` (function definition area; rename the function symbol but do NOT touch the math body)
- Modify: `fitting.py:541` (`_SHAPE_FUNCS` registry entry)
- Modify: `fitting.py:629, 641, 643, 663-669` (all `if shape == "la_casaxps":` branches in `_make_peak_params`)

- [ ] **Step 1: Rename the function definition**

In `fitting.py`, find the line:

```python
def _la_casaxps(
```

(currently at line 148). Replace with:

```python
def _ds_g_dscore_gauss(
```

Also update the docstring on the next non-empty lines: change the leading line from
```
    CasaXPS LA(α,β,m) lineshape — Doniach-Šunjić core convolved with Gaussian.
```
to
```
    DS+G lineshape (formerly mislabeled "LA(α,β,m) [CasaXPS]") —
    Doniach-Šunjić asymmetric core convolved analytically with a Gaussian
    instrument-broadening kernel. NOT to be confused with the true CasaXPS
    LA shape (see _la_casaxps_true), which uses a piecewise-asymmetric
    Lorentzian with point-domain Gaussian convolution.
```

Leave the rest of the docstring and all the math (`_ds_core`, FFT convolution, etc.) untouched.

- [ ] **Step 2: Update the `_SHAPE_FUNCS` registry**

In `fitting.py:541`, change:

```python
    "la_casaxps": _la_casaxps,
```

to:

```python
    "ds_g": _ds_g_dscore_gauss,
```

(For now we leave `la_casaxps` UNREGISTERED. It will be re-registered to the new true LA in Task 3. Tests that exercise `la_casaxps` between Tasks 2 and 3 will fail; that's expected — Task 3 follows immediately.)

- [ ] **Step 3: Update the header docstring**

In `fitting.py:5-15`, find:

```
  la_casaxps      – CasaXPS LA(α,β,m): DS core convolved with Gaussian
```

Replace with two lines:

```
  ds_g            – DS+G: DS core × Gaussian convolution (formerly "la_casaxps")
  la_casaxps      – TRUE CasaXPS LA(α,β,m): asymmetric base Lorentzian + integer-kernel Gauss conv
```

- [ ] **Step 4: Update all `if shape == "la_casaxps":` branches in `_make_peak_params`**

There are FOUR such branches in `_make_peak_params` (lines 629, 641, 643, 663). For each, change the comparison string from `"la_casaxps"` to `"ds_g"`. The bodies of those branches (which set `min_`/`max_` for `alpha`/`beta`/`m_gauss`) stay unchanged.

Run `grep -n '"la_casaxps"' /home/skye/xps-app/fitting.py` AFTER editing — expected output: zero matches (Task 3 will re-introduce the string for the new shape).

- [ ] **Step 5: Verify the renaming hasn't broken Python imports**

```bash
venv/bin/python -c "from fitting import _SHAPE_FUNCS, _ds_g_dscore_gauss; assert 'ds_g' in _SHAPE_FUNCS; assert 'la_casaxps' not in _SHAPE_FUNCS; print('OK')"
```

Expected: `OK`.

- [ ] **Step 6: Verify the math is byte-identical (numerical regression)**

```bash
venv/bin/python -c "
import sys
sys.path.insert(0, '/home/skye/xps-app/backups')
import importlib.util
spec_old = importlib.util.spec_from_file_location('fitting_old', '/home/skye/xps-app/backups/fitting.py.backup47')
fitting_old = importlib.util.module_from_spec(spec_old); spec_old.loader.exec_module(fitting_old)

import fitting as fitting_new
import numpy as np
x = np.linspace(280, 295, 1500)
y_old = fitting_old._la_casaxps(x, amplitude=1000.0, center=284.5, alpha=0.10, beta=0.30, m_gauss=0.5)
y_new = fitting_new._ds_g_dscore_gauss(x, amplitude=1000.0, center=284.5, alpha=0.10, beta=0.30, m_gauss=0.5)
diff = np.max(np.abs(y_old - y_new))
assert diff < 1e-12, f'numerical drift: {diff}'
print(f'OK — max abs diff {diff:.2e}')
"
```

Expected: `OK — max abs diff 0.00e+00` (or similarly tiny).

- [ ] **Step 7: Commit (intermediate — Task 3 will follow)**

```bash
git add fitting.py
git commit -m "$(cat <<'EOF'
refactor(fitting): rename _la_casaxps to _ds_g_dscore_gauss

The shape registered as 'la_casaxps' is actually a Doniach-Šunjić core
convolved with a Gaussian — defensible math, but mislabeled.

Rename the symbol and registry id to 'ds_g' to free up 'la_casaxps' for
a forthcoming TRUE CasaXPS LA implementation. Math body is unchanged
and a regression check confirms numerical byte-equivalence.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2.5: Disambiguate `DSG` vs `DSG_LA` (the two "DS+Gaussian" shapes)

**Context:** After Task 2 the repo has two backend functions both nominally producing "Doniach-Šunjić core with Gaussian broadening":

- `_doniach_sunjic_gauss` — registered as `DSG`, dropdown label "DS × Gaussian (DS + instr. broadening)"
- `_ds_g_dscore_gauss` — just renamed from `_la_casaxps`, registered as `ds_g`, dropdown label "DS+G (DS core × Gauss conv)"

We must not ship two near-duplicate entries with confusingly similar labels. This task investigates the actual difference and resolves to one of three cases. Cases 2 and 3 are HALT conditions — Skye must respond before Task 3 runs.

**Files:**
- Read: `fitting.py` (function bodies of `_doniach_sunjic_gauss` and `_ds_g_dscore_gauss`)
- Possibly modify: `templates/index.html` (dropdown labels) and `fitting.py` (one-line docstrings) — only in Case 1.

- [ ] **Step 1: Read `_doniach_sunjic_gauss` function body**

```bash
grep -n "_doniach_sunjic_gauss\b" /home/skye/xps-app/fitting.py
```

Then read the lines of the function definition (signature through return), capturing parameter names, defaults, and the math operation (analytical product, numerical convolution, FFT convolution, or something else). Record findings briefly.

- [ ] **Step 2: Read `_ds_g_dscore_gauss` function body**

```bash
grep -n "_ds_g_dscore_gauss\b" /home/skye/xps-app/fitting.py
```

Same as Step 1 — capture parameter names, defaults, and the math operation. (After Task 2 this is the function formerly called `_la_casaxps`.)

- [ ] **Step 3: Check git log for the two functions**

```bash
git log --oneline -p -S "_doniach_sunjic_gauss" -- fitting.py | head -60
echo "---"
git log --oneline -p -S "_la_casaxps\|_ds_g_dscore_gauss" -- fitting.py | head -60
```

Look for: which was added first, whether one was added "to replace" the other, whether either has a "deprecated" or "superseded" comment, whether one was historically broken.

- [ ] **Step 4: Categorize into one of three cases**

Compare findings from Steps 1-3. Decide:

- **Case 1 — Different math, both legitimate:** e.g., one is analytic DS × Gaussian envelope (pointwise multiply), the other is DS ⊛ Gaussian (numerical convolution). Both are real shapes; users may want either. → Continue to Step 5.
- **Case 2 — Same math, different parameterization:** the two functions produce the same curve given a parameter mapping. → STOP and report (Step 7).
- **Case 3 — One is broken / vestigial / clearly superseded:** dead code path, broken normalization, or git history shows one was meant to replace the other. → STOP and report (Step 8).

- [ ] **Step 5 (Case 1 only): Update dropdown labels for unmissable distinction**

In `templates/index.html`, update the two dropdown options:

- The existing `DSG` option: dropdown text changes from `"DS × Gaussian (DS + instr. broadening)"` to **`"DS × G (analytic)"`**. Find the `<option value="DSG"` line (currently around the DS option block before line 4250) and update its display text inside the `>...</option>` portion. Tooltip can stay or be edited to add "analytic pointwise product".

- The `DSG_LA` option (created in Task 4): dropdown text changes from `"DS+G (DS core × Gauss conv)"` to **`"DS ⊛ G (convolution)"`**. (Task 4 hasn't run yet at this point in the sequence — so update Task 4 Step 1 in this plan file IN PLACE before Task 4 executes, OR run a sed against `templates/index.html` after Task 4 completes. Easier to ALSO patch the plan: edit Task 4 Step 1's old/new option HTML to use `"DS ⊛ G (convolution)"` instead of `"DS+G (DS core × Gauss conv)"`.)

For Task 2.5 itself (which runs BEFORE Task 4), the only frontend change is the `DSG` option's display text. Find the existing `<option value="DSG"` block in `templates/index.html` and edit just the displayed-text portion.

- [ ] **Step 6 (Case 1 only): Add disambiguating docstrings**

In `fitting.py`, prepend a one-line summary to each function's docstring:

For `_doniach_sunjic_gauss`:

```python
    """
    Analytic DS × Gaussian product (pointwise multiplication, NOT convolution).
    Use for instrument broadening modeled as a Gaussian envelope.
    
    [rest of existing docstring unchanged]
```

For `_ds_g_dscore_gauss`:

```python
    """
    DS core convolved (FFT) with a Gaussian kernel.
    Use for combined intrinsic + instrument broadening when convolution
    semantics matter.
    
    [rest of existing docstring unchanged]
```

(Adapt wording to match what you actually find in Step 1-2; the goal is one unmissable line distinguishing the two.)

- [ ] **Step 7 (Case 1 only): Verify and commit**

```bash
venv/bin/python -c "from fitting import _doniach_sunjic_gauss, _ds_g_dscore_gauss; print('OK')"
grep -n 'DS × G (analytic)' /home/skye/xps-app/templates/index.html
```

Expected: `OK`, then one match for the relabeled dropdown.

```bash
git add fitting.py templates/index.html
git commit -m "$(cat <<'EOF'
docs(fitting): disambiguate DSG (analytic) from DSG_LA (convolution)

The two DS+Gaussian shapes in the dropdown were confusingly similar.
DSG is an analytic DS × Gaussian product (pointwise multiplication);
DSG_LA (formerly the mislabeled 'LA') is DS ⊛ Gaussian (FFT
convolution). Updated dropdown labels to 'DS × G (analytic)' and
'DS ⊛ G (convolution)' and prepended a one-line docstring to each
backend function so the distinction is unmissable.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

**Then proceed to Task 3.**

- [ ] **Step 8 (Case 2 or Case 3 only): STOP and report**

Do NOT modify any files in this case. Print a message to Skye summarizing:

- Which two functions you found to be equivalent (Case 2) or superseded (Case 3).
- For Case 2: the parameter mapping that makes them equivalent (e.g., "DSG's σ_g = DSG_LA's m_gauss / 2.355", or whatever you derive from reading the math).
- For Case 3: the evidence — git commit hash where one replaced the other, dead-code indicators, broken normalization, etc.
- A recommendation: which shape to keep, which to retire, and whether the retired one needs a migration alias in Task 6.

Wait for Skye's response. **Do not proceed to Task 3 until Skye answers.**

If Skye approves the recommendation:
- If a shape is to be retired by deletion or merge: ADD an entry to the `SHAPE_ALIASES` map in Task 6 Step 1. E.g., `'DSG': 'DSG_LA'` if the analytic version is being retired in favor of the convolution one. Document the choice in Task 6's commit message.
- Then continue to Task 3.

---

### Task 3: Backend — implement true `_la_casaxps_true` and register under `la_casaxps`

**Files:**
- Modify: `fitting.py:~310` (insert new function definition after the renamed `_ds_g_dscore_gauss`)
- Modify: `fitting.py:541` (re-add `la_casaxps` to `_SHAPE_FUNCS`)
- Modify: `fitting.py:_make_peak_params` (add `if shape == "la_casaxps":` branch with the new params)
- Test: `/tmp/test_la_true_lorentzian.py`

- [ ] **Step 1: Write the failing reduce-to-Lorentzian unit test**

```bash
cat > /tmp/test_la_true_lorentzian.py <<'EOF'
"""
With α=β=1 and m=0 the true CasaXPS LA shape must reduce to a unit-area
pure Lorentzian of FWHM `fwhm`. Asserts equality to 1e-10.
"""
import sys
sys.path.insert(0, "/home/skye/xps-app")
import numpy as np
from fitting import _la_casaxps_true

x = np.linspace(280, 295, 2001)
center = 284.5
fwhm = 1.2
amp = 1000.0

y_la = _la_casaxps_true(x, amplitude=amp, center=center, fwhm=fwhm,
                       alpha=1.0, beta=1.0, m=0)

# Reference: pure Lorentzian, peak normalized to amp
y_ref = amp / (1.0 + 4.0 * ((x - center) / fwhm) ** 2)

diff = np.max(np.abs(y_la - y_ref))
assert diff < 1e-10, f"reduction failed: max diff = {diff}"
print(f"OK — α=β=1, m=0 reduces to Lorentzian (max diff {diff:.2e})")
EOF
venv/bin/python /tmp/test_la_true_lorentzian.py 2>&1 | tail -3
```

Expected: `ImportError: cannot import name '_la_casaxps_true'` — confirms the function doesn't exist yet.

- [ ] **Step 2: Implement `_la_casaxps_true`**

Insert the following AFTER the closing of `_ds_g_dscore_gauss` (around line 310 after Task 2's edits — find the blank line before the `# ─── Charge correction helpers ───` comment block, or wherever the lineshape functions end). Place it right before the `_SHAPE_FUNCS` dict at line 539.

```python
def _la_casaxps_true(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    alpha: float,
    beta: float,
    m: float,
) -> np.ndarray:
    """
    True CasaXPS LA(α, β, m) lineshape.

    Built in two steps per the CasaXPS LA manual:

    1.  Asymmetric base Lorentzian. Start with a unit-amplitude Lorentzian
        of FWHM `fwhm` centered at `center`:
            L(x) = 1 / (1 + 4·((x − center)/fwhm)²)
        Apply piecewise exponents to introduce asymmetry. CasaXPS defines
        these on a kinetic-energy axis. We use a binding-energy axis, so
        the sides flip:
            LA_base(x) = L(x)^α   for x ≥ center  (high-BE side)
            LA_base(x) = L(x)^β   for x <  center  (low-BE side)
        Increasing α relative to β SUPPRESSES the high-BE tail; decreasing
        α extends it. (Empirical sign-convention check: Si 2p doublet with
        α<β should show the tail on the high-BE side.)

    2.  Gaussian convolution with an integer-point kernel of width `m`.
        m=0 means no convolution. For m>0, build a discrete Gaussian
        kernel of length 2m+1 with σ_pts = m/3 (so the 3σ tail just
        reaches the kernel edge). Convolve with mode='same' on the
        uniform x grid.

    With α=β=1 and m=0, this reduces exactly to amplitude × L(x) (a pure
    Lorentzian of peak height = amplitude, FWHM = `fwhm`).

    Parameters
    ----------
    fwhm  : Lorentzian FWHM in eV (must be > 0)
    alpha : high-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    beta  : low-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    m     : Gaussian convolution kernel width in DATA POINTS (not eV);
            integer 0–499. Stored as float in lmfit, rounded to int here.
    """
    fwhm = max(float(fwhm), 1e-9)
    alpha = max(float(alpha), 1e-3)
    beta = max(float(beta), 1e-3)
    m_int = int(round(float(m)))
    m_int = max(0, min(499, m_int))

    eps = x - center
    # Base unit-amplitude Lorentzian
    L = 1.0 / (1.0 + 4.0 * (eps / fwhm) ** 2)
    # Piecewise exponentiation. BE-axis: high-BE side is eps ≥ 0.
    high = eps >= 0
    base = np.where(high, np.power(L, alpha), np.power(L, beta))

    if m_int == 0:
        return amplitude * base

    # Build discrete Gaussian kernel of length 2*m+1, σ_pts = m/3.
    sigma_pts = m_int / 3.0
    k = np.arange(-m_int, m_int + 1, dtype=float)
    kern = np.exp(-(k ** 2) / (2.0 * sigma_pts ** 2))
    kern = kern / kern.sum()  # normalize to unit area

    # Convolve. The grid x is assumed uniform (the fit grid in run_fit is
    # always uniform because it's the spectrum BE axis).
    convolved = np.convolve(base, kern, mode='same')

    # The convolution preserves total area but NOT peak height. Renormalize
    # so the peak value at center == 1.0, then scale by amplitude. This
    # matches the m=0 branch's amplitude convention.
    peak_idx = int(np.argmin(np.abs(eps)))
    peak_val = convolved[peak_idx]
    if peak_val <= 0:
        peak_val = float(np.max(convolved))
    if peak_val <= 0:
        return np.zeros_like(x)
    return amplitude * convolved / peak_val
```

- [ ] **Step 3: Re-register `la_casaxps` in the dispatch dict**

In `fitting.py:541` (the `_SHAPE_FUNCS` dict, after Task 2's edit currently has only `"ds_g"`), add a new entry. Find:

```python
    "ds_g": _ds_g_dscore_gauss,
}
```

Change to:

```python
    "ds_g": _ds_g_dscore_gauss,
    "la_casaxps": _la_casaxps_true,
}
```

- [ ] **Step 4: Add `_make_peak_params` branch for the new shape**

Find the `if shape == "ds_g":` branch in `_make_peak_params` (the master-peak path around line 628 and the free-peak path around line 663). The new shape needs a corresponding branch — but its parameters are different (`fwhm`, `alpha`, `beta`, `m`, no `m_gauss`). Add the new branch in BOTH paths.

In the free-peak path (after the `if shape == "ds_g":` block ending around line 670), add:

```python
    if shape == "la_casaxps":
        _set("alpha", spec.get("alpha", 1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_alpha", False))
        _set("beta",  spec.get("beta",  1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_beta", False))
        _set("m",     spec.get("m",    50.0), min_=0.0, max_=499.0,
             vary=not spec.get("fix_m", True))
        # `fwhm` is set by the generic _set("fwhm", ...) call at the top
        # of the free-peak path; new shape uses the standard fwhm parameter.
```

In the master-peak (constrained) path (after the `if shape == "ds_g":` block around line 632), add the analogous block but with `expr=` for spin-orbit constraints — same pattern as the existing `ds_g` block:

```python
        if shape == "la_casaxps":
            fix = spec.get("fix_fwhm", True)
            _set("alpha", spec.get("alpha", 1.0),
                 expr=f"{m_prefix}alpha" if fix else None,
                 min_=0.1, max_=5.0)
            _set("beta",  spec.get("beta",  1.0),
                 expr=f"{m_prefix}beta" if fix else None,
                 min_=0.1, max_=5.0)
            _set("m",     spec.get("m",    50.0),
                 expr=f"{m_prefix}m" if fix else None,
                 min_=0.0, max_=499.0)
```

- [ ] **Step 5: Run the reduce-to-Lorentzian test**

```bash
venv/bin/python /tmp/test_la_true_lorentzian.py
```

Expected: `OK — α=β=1, m=0 reduces to Lorentzian (max diff X.XXe-XX)` with diff < 1e-10.

- [ ] **Step 6: Write and run the reduce-to-Voigt-like test**

```bash
cat > /tmp/test_la_voigt_like.py <<'EOF'
"""
With α=β=1 and m>0 the LA shape should be a symmetric, smoothed Lorentzian
(Voigt-like). Verify it is a) symmetric and b) broader than the m=0 case.
"""
import sys
sys.path.insert(0, "/home/skye/xps-app")
import numpy as np
from fitting import _la_casaxps_true

x = np.linspace(280, 295, 2001)
center = 284.5
fwhm = 0.8
amp = 1000.0

y_no_g  = _la_casaxps_true(x, amp, center, fwhm, alpha=1.0, beta=1.0, m=0)
y_with_g = _la_casaxps_true(x, amp, center, fwhm, alpha=1.0, beta=1.0, m=30)

# Symmetry check: Lorentzian + symmetric Gaussian = symmetric profile
center_idx = int(np.argmin(np.abs(x - center)))
left  = y_with_g[center_idx - 50 : center_idx]
right = y_with_g[center_idx + 1 : center_idx + 51][::-1]
asym = np.max(np.abs(left - right)) / np.max(y_with_g)
assert asym < 1e-3, f"not symmetric: {asym}"

# Broader than m=0
def fwhm_at_half(y):
    half = np.max(y) / 2.0
    above = np.where(y >= half)[0]
    return x[above[-1]] - x[above[0]]
fwhm_no_g  = fwhm_at_half(y_no_g)
fwhm_with_g = fwhm_at_half(y_with_g)
assert fwhm_with_g > fwhm_no_g, f"convolution didn't broaden: {fwhm_no_g} vs {fwhm_with_g}"

print(f"OK — symmetric (asym={asym:.2e}); m=30 broadens FWHM {fwhm_no_g:.3f} → {fwhm_with_g:.3f}")
EOF
venv/bin/python /tmp/test_la_voigt_like.py
```

Expected: `OK — symmetric (asym=X.XXe-XX); m=30 broadens FWHM A → B` with B > A.

- [ ] **Step 7: Sanity-check BE-axis sign convention**

```bash
cat > /tmp/test_la_be_sign.py <<'EOF'
"""
On a BE axis, alpha applies to the high-BE side, beta to the low-BE side.
With alpha < beta, the high-BE tail extends; the low-BE side decays faster.
Confirm by integrating intensity on each side of the peak.
"""
import sys
sys.path.insert(0, "/home/skye/xps-app")
import numpy as np
from fitting import _la_casaxps_true

x = np.linspace(280, 295, 2001)
center = 284.5
fwhm = 0.6
amp = 1000.0

# Asymmetric: smaller alpha → more high-BE tail
y_asym = _la_casaxps_true(x, amp, center, fwhm, alpha=0.5, beta=2.0, m=0)
center_idx = int(np.argmin(np.abs(x - center)))
high_be = np.trapz(y_asym[center_idx + 1:], x[center_idx + 1:])
low_be  = np.trapz(y_asym[:center_idx],     x[:center_idx])
# In our coordinates, increasing x = increasing BE, so x>center is high-BE side.
assert high_be > 1.5 * low_be, (
    f"high-BE tail not extended: high={high_be:.1f}, low={low_be:.1f}"
)
print(f"OK — α<β extends high-BE tail (high/low ratio = {high_be/low_be:.2f})")
EOF
venv/bin/python /tmp/test_la_be_sign.py
```

Expected: `OK — α<β extends high-BE tail (high/low ratio = X.XX)`.

- [ ] **Step 8: Verify lmfit Parameter integration**

```bash
venv/bin/python -c "
import sys
sys.path.insert(0, '/home/skye/xps-app')
from lmfit import Model
from fitting import _make_peak_params, _la_casaxps_true

spec = {
    'id': '1', 'shape': 'la_casaxps',
    'center': 284.5, 'amplitude': 1000.0, 'fwhm': 0.7,
    'alpha': 1.0, 'beta': 1.0, 'm': 50.0,
}
model = Model(_la_casaxps_true, prefix='p1_')
params = _make_peak_params(model, spec, 'p1_', [spec])
assert 'p1_alpha' in params and params['p1_alpha'].min == 0.1 and params['p1_alpha'].max == 5.0
assert 'p1_beta'  in params and params['p1_beta'].min  == 0.1 and params['p1_beta'].max  == 5.0
assert 'p1_m'     in params and params['p1_m'].min    == 0.0 and params['p1_m'].max    == 499.0
assert params['p1_m'].vary is False, 'm should default to fixed (vary=False)'
print('OK — params plumbed')
"
```

Expected: `OK — params plumbed`.

- [ ] **Step 9: Commit**

```bash
git add fitting.py
git commit -m "$(cat <<'EOF'
feat(fitting): add true CasaXPS LA(α,β,m) lineshape

Reuses the now-free 'la_casaxps' registry slot for the genuine CasaXPS
formulation: a unit-amplitude Lorentzian of FWHM `fwhm`, raised to
piecewise exponents α (high-BE side) and β (low-BE side) on a BE axis,
then convolved with a discrete Gaussian kernel of integer point width m
(σ_pts = m/3).

Reduces to a pure Lorentzian when α=β=1, m=0 (verified to 1e-10 by
unit test). Symmetric Voigt-like profile when α=β=1, m>0. α<β extends
the high-BE tail (BE-axis convention; sign-flipped from CasaXPS's
KE-axis description, verified empirically).

Default m=50 fixed (vary=False); users typically tune α/β only.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Frontend — rename `'LA'` → `'DSG_LA'` enum and dropdown label (DS+G rename, no new shape yet)

**Files:**
- Modify: `templates/index.html` at the following sites:
  - Line 4250: dropdown `<option>` (value + display text)
  - Lines 2855, 4265, 4266, 4267, 4270, 4377, 4424, 4504, 4541, 4542, 4543, 5268, 5285, 7115: `p.shape === 'LA'` (or `!== 'LA'`) comparisons
  - Line 4505: `spec.shape = 'la_casaxps';` → `spec.shape = 'ds_g';`
  - Line 4721 (Auto-Fit graphite peak comment): the comment mentions `'LA(α,β,m)'` — leave as historical reference; no functional change needed.

- [ ] **Step 1: Replace the dropdown option**

In `templates/index.html`, find:

```html
        <option value="LA" data-tip="CasaXPS convention asymmetric lineshape. Most versatile — works for metals, semiconductors, and materials with complex screening. A good general choice for transition metals and other core levels with non-trivial tail shapes." ${p.shape==='LA'?'selected':''}>LA (&alpha;,&beta;,m) [CasaXPS]</option>
```

Replace with:

```html
        <option value="DSG_LA" data-tip="Doniach-Šunjić core convolved with a Gaussian. A defensible asymmetric shape — good for metals and transition metals with complex screening. Distinct from the new LA(α,β,m) [CasaXPS] entry below; previously this entry was mis-labeled as 'LA [CasaXPS]'." ${p.shape==='DSG_LA'?'selected':''}>DS+G (DS core &times; Gauss conv)</option>
```

- [ ] **Step 2: Replace `peakToBackendSpec` LA branch**

Find:

```js
  } else if (shape === 'LA') {
    spec.shape = 'la_casaxps';
    spec.alpha   = Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10;
    spec.beta    = Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3;
    spec.m_gauss = Number.isFinite(p.laM)     ? p.laM     : 0.4;
    spec.fix_alpha   = !!p.fixLaAlpha;
    spec.fix_beta    = !!p.fixLaBeta;
    spec.fix_m_gauss = !!p.fixLaM;
  } else {
```

Replace with:

```js
  } else if (shape === 'DSG_LA') {
    spec.shape = 'ds_g';
    spec.alpha   = Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10;
    spec.beta    = Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3;
    spec.m_gauss = Number.isFinite(p.laM)     ? p.laM     : 0.4;
    spec.fix_alpha   = !!p.fixLaAlpha;
    spec.fix_beta    = !!p.fixLaBeta;
    spec.fix_m_gauss = !!p.fixLaM;
  } else {
```

- [ ] **Step 3: Replace all remaining `'LA'` enum references**

Run a single replace_all for the literal `=== 'LA'` and `!== 'LA'` and `'LA'` enum occurrences. Use `sed -i` or careful Edit with `replace_all=true`. The exact strings to replace:

```
"=== 'LA'"   →  "=== 'DSG_LA'"
"!== 'LA'"   →  "!== 'DSG_LA'"
"==='LA'"    →  "==='DSG_LA'"
"=== \"LA\"" →  "=== \"DSG_LA\""   (if any double-quoted variants exist; grep first)
```

DO NOT do a blind `'LA'` → `'DSG_LA'` substitution — the substring `LA` appears in many unrelated places (LA tooltips, LA in CSS class names, etc.). Only replace where it's the JavaScript shape-enum value.

Concretely, run these sed commands:

```bash
sed -i "s/=== 'LA'/=== 'DSG_LA'/g" /home/skye/xps-app/templates/index.html
sed -i "s/!== 'LA'/!== 'DSG_LA'/g" /home/skye/xps-app/templates/index.html
sed -i "s/==='LA'/==='DSG_LA'/g" /home/skye/xps-app/templates/index.html
```

Then verify:

```bash
grep -n "=== 'LA'\|!== 'LA'\|==='LA'" /home/skye/xps-app/templates/index.html
```

Expected: zero matches.

```bash
grep -nc "=== 'DSG_LA'\|!== 'DSG_LA'\|==='DSG_LA'" /home/skye/xps-app/templates/index.html
```

Expected: at least 12 (matching the prior count of `'LA'` checks).

- [ ] **Step 4: Verify structural integrity**

```bash
venv/bin/python -c "html = open('templates/index.html').read(); assert html.count('{') == html.count('}'); assert 'DSG_LA' in html; assert \"value='LA'\" not in html and 'value=\"LA\"' not in html; print('OK')"
```

Expected: `OK`.

- [ ] **Step 5: Reload gunicorn and confirm served HTML**

```bash
kill -HUP 9674 2>/dev/null; sleep 2
curl -s --connect-timeout 2 http://localhost:5000/ 2>/dev/null | grep -c 'DSG_LA'
```

Expected: > 12 (declarations + comparisons + dropdown option, all delivered).

- [ ] **Step 6: Commit**

```bash
git add templates/index.html
git commit -m "$(cat <<'EOF'
refactor(frontend): rename LA shape enum to DSG_LA, relabel as DS+G

The old 'LA (α,β,m) [CasaXPS]' dropdown entry is in fact a
Doniach-Šunjić core × Gaussian convolution — defensible math, but
mislabeled. Frontend enum 'LA' renamed to 'DSG_LA'; dropdown display
becomes 'DS+G (DS core × Gauss conv)'. peakToBackendSpec emits
spec.shape = 'ds_g' to match the renamed backend entry.

The frontend field names (laAlpha, laBeta, laM, fixLaAlpha/Beta/M) are
left unchanged because they appear in saved-state schemas and renaming
them would cascade through the save/load round-trip without numerical
benefit. The new TRUE LA shape (forthcoming) uses distinct field names
(caAlpha/caBeta/caM) so users won't confuse the two.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Frontend — add the new `'LACX'` shape with all its UI plumbing

**Files:**
- Modify: `templates/index.html` at multiple sites — see substeps. Estimated diff: ~120 lines added.

This is the largest task. The new shape parallels the existing GL/asym-GL/DS/DSG/DSG_LA ones in the seven hooks every shape touches:

1. `defaultPeak` defaults block (around line 3522)
2. `syncKeys` array (line 4075)
3. Dropdown `<option>` (after the DSG_LA option at ~line 4250)
4. `renderPeakControls` param row (parallel to the LA branch at line 4377)
5. `peakToBackendSpec` branch (parallel to DSG_LA at the post-Task-4 site)
6. `applyBackendResult` shape-specific param mapping (parallel to LA mapping at line 4541)
7. JS `evalPeak` switch — needs a JS implementation `laTrueCasaXPS(x, center, fwhm, alpha, beta, m)` matching the Python `_la_casaxps_true` (called for live-preview without backend roundtrip)
8. `runFit` (the JS LM fitter at line 5285) free-params block
9. CSV export row at line 7115

The plan walks through each hook explicitly.

- [ ] **Step 1: Add JS implementation `laTrueCasaXPS`**

Around line 2806 (after the existing `// LA(α, β, m) — CasaXPS convention` block), add a new function block:

```js
// True LA(α, β, m) [CasaXPS] — piecewise-asymmetric Lorentzian + integer-kernel Gauss conv.
// Mirrors fitting.py:_la_casaxps_true. BE axis: high-BE side (eps ≥ 0)
// gets exponent α; low-BE side (eps < 0) gets β. m is integer 0–499 in
// data-points; σ_pts = m/3.
function laTrueCasaXPS(x, center, fwhm, alpha, beta, m) {
  const F = Math.max(fwhm, 1e-9);
  const A = Math.max(alpha, 1e-3);
  const B = Math.max(beta,  1e-3);
  const mInt = Math.max(0, Math.min(499, Math.round(m || 0)));
  const eps = x - center;
  const L = 1.0 / (1.0 + 4.0 * Math.pow(eps / F, 2));
  const base = eps >= 0 ? Math.pow(L, A) : Math.pow(L, B);
  if (mInt === 0) return base;
  // For convolution, JS evalPeak is invoked per-point. The per-point
  // convolution would be O(m) per evaluation — acceptable for the live
  // overlay because the chart re-renders only on parameter changes.
  // But evalPeak only sees one x at a time; we need access to the grid.
  // Solution: register laTrueCasaXPS_array which evalPeak calls when the
  // shape needs grid-aware evaluation.
  return base;  // m=0 fallback; full conv handled by laTrueCasaXPS_array
}

// Grid-aware variant called from evalPeakArray (next step) for non-zero m.
function laTrueCasaXPS_array(xArr, center, fwhm, alpha, beta, m) {
  const N = xArr.length;
  const F = Math.max(fwhm, 1e-9);
  const A = Math.max(alpha, 1e-3);
  const B = Math.max(beta,  1e-3);
  const mInt = Math.max(0, Math.min(499, Math.round(m || 0)));
  const base = new Float64Array(N);
  for (let i = 0; i < N; i++) {
    const eps = xArr[i] - center;
    const L = 1.0 / (1.0 + 4.0 * (eps / F) * (eps / F));
    base[i] = eps >= 0 ? Math.pow(L, A) : Math.pow(L, B);
  }
  if (mInt === 0) return base;
  const sigma = mInt / 3.0;
  const klen = 2 * mInt + 1;
  const kern = new Float64Array(klen);
  let ksum = 0;
  for (let k = 0; k < klen; k++) {
    const dk = k - mInt;
    kern[k] = Math.exp(-(dk * dk) / (2.0 * sigma * sigma));
    ksum += kern[k];
  }
  for (let k = 0; k < klen; k++) kern[k] /= ksum;
  const out = new Float64Array(N);
  for (let i = 0; i < N; i++) {
    let s = 0;
    for (let k = 0; k < klen; k++) {
      const j = i + (k - mInt);
      if (j >= 0 && j < N) s += base[j] * kern[k];
    }
    out[i] = s;
  }
  // Renormalize so peak = 1
  let pkVal = 0, pkIdx = 0;
  for (let i = 0; i < N; i++) {
    if (Math.abs(xArr[i] - center) < Math.abs(xArr[pkIdx] - center)) pkIdx = i;
  }
  pkVal = out[pkIdx];
  if (pkVal <= 0) {
    let mx = 0; for (let i = 0; i < N; i++) if (out[i] > mx) mx = out[i];
    pkVal = mx;
  }
  if (pkVal <= 0) return out;
  for (let i = 0; i < N; i++) out[i] = out[i] / pkVal;
  return out;
}
```

(The two-function design is necessary because `evalPeak(x, p)` is called per-point and a true convolution needs the whole grid. Live preview for LACX uses `laTrueCasaXPS_array` invoked once per render; the per-point `evalPeak` falls back to the m=0 value, which is good enough for hover/tooltip evaluation.)

- [ ] **Step 2: Wire LACX into `evalPeak` and the per-grid evaluator**

Find `evalPeak` (the function that returns the peak value at a single x). Around line 2843-2855 there's a switch on `p.shape`. Add a new branch after the existing LA branch:

Current (post-Task 4) state has:

```js
  } else if (p.shape === 'DSG_LA') {
    y = laCasaXPS(x, center, p.laAlpha, p.laBeta, p.laM);
```

Insert AFTER that branch:

```js
  } else if (p.shape === 'LACX') {
    // Per-point fallback: m=0 base, ignores Gaussian conv. The grid-aware
    // path uses laTrueCasaXPS_array (called from updatePlot's series build).
    y = laTrueCasaXPS(x, center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
```

- [ ] **Step 3: Patch the chart per-peak series build to use `laTrueCasaXPS_array` for LACX**

Find the place in `updatePlot` (or wherever per-peak series are computed for the chart) that loops over peaks and computes y arrays. Search for `evalPeak(` in a loop context. The expected pattern:

```js
const yArr = beArr.map(x => evalPeak(x, p));
```

Wrap it to special-case LACX with non-zero m:

```js
let yArr;
if (p.shape === 'LACX' && Math.round(p.caM || 0) > 0) {
  yArr = laTrueCasaXPS_array(beArr, p.center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
  for (let i = 0; i < yArr.length; i++) yArr[i] *= p.amplitude;
} else {
  yArr = beArr.map(x => evalPeak(x, p));
}
```

Locate the exact site by `grep -n "evalPeak(x, p)\|evalPeak(be\|map(x => evalPeak" /home/skye/xps-app/templates/index.html | head -10` and apply the wrap to each call site that builds chart series. Hover/single-point evaluations don't need it.

- [ ] **Step 4: Add `defaultPeak` default fields**

Around line 3540 (where existing defaults like `laAlpha: 0.10` live), add new defaults:

```js
    caAlpha: 1.0,
    caBeta:  1.0,
    caM:     50,
    fixCaAlpha: false,
    fixCaBeta:  false,
    fixCaM:     true,    // m typically fixed by default per spec
```

- [ ] **Step 5: Add to `syncKeys`**

Find the `syncKeys` array at line 4075:

```js
  const syncKeys = ['center','amplitude','fwhm','shape','glMix','asymmetry','dsAlpha','dsGamma','dsGaussSigma','laAlpha','laBeta','laM'];
```

Replace with:

```js
  const syncKeys = ['center','amplitude','fwhm','shape','glMix','asymmetry','dsAlpha','dsGamma','dsGaussSigma','laAlpha','laBeta','laM','caAlpha','caBeta','caM'];
```

- [ ] **Step 6: Add the dropdown option for LACX**

Find the `'DSG_LA'` option (created in Task 4 at line ~4250) and IMMEDIATELY AFTER it, add:

```html
        <option value="LACX" data-tip="True CasaXPS LA(α,β,m). Asymmetric Lorentzian raised to exponents α (high-BE tail side) and β (low-BE side), convolved with a Gaussian of integer point width m. Reduces to a pure Lorentzian at α=β=1, m=0. Match this to CasaXPS by using the same α, β, m values." ${p.shape==='LACX'?'selected':''}>LA(&alpha;,&beta;,m) [CasaXPS]</option>
```

- [ ] **Step 7: Add the LACX param row in `renderPeakControls`**

Find the existing `'DSG_LA'` (formerly `'LA'`) branch in `renderPeakControls` (currently at line ~4377 after Task 4). After its closing `}`, add a new branch:

```js
  } else if (p.shape === 'LACX') {
    return `
      <div style="font-size:10px;color:var(--text3);margin-bottom:6px">
        True CasaXPS LA — α/β are exponents (BE convention: α applies to high-BE side)
      </div>
      <div class="field-row">
        <div class="field">
          <label data-xps-tip="High-BE-side exponent. CasaXPS-equivalent α. Smaller α extends the high-BE tail. Default 1.0 (symmetric Lorentzian). Bounds 0.1–5.0.">&alpha; (high-BE exp)
            ${!isLinked ? `<button class="lock-btn${p.fixCaAlpha ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaAlpha',this)" title="${p.fixCaAlpha ? 'Unlock' : 'Lock'} during fitting">${p.fixCaAlpha ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
          </label>
          <input type="number" value="${(p.caAlpha ?? 1.0).toFixed(3)}" step="0.05" min="0.1" max="5.0"
            oninput="updatePeakParam(${p.id},'caAlpha',parseFloat(this.value))">
        </div>
        <div class="field">
          <label data-xps-tip="Low-BE-side exponent. CasaXPS-equivalent β. Default 1.0 (symmetric). Bounds 0.1–5.0.">&beta; (low-BE exp)
            ${!isLinked ? `<button class="lock-btn${p.fixCaBeta ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaBeta',this)" title="${p.fixCaBeta ? 'Unlock' : 'Lock'} during fitting">${p.fixCaBeta ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
          </label>
          <input type="number" value="${(p.caBeta ?? 1.0).toFixed(3)}" step="0.05" min="0.1" max="5.0"
            oninput="updatePeakParam(${p.id},'caBeta',parseFloat(this.value))">
        </div>
      </div>
      <div class="field">
        <label data-xps-tip="Gaussian convolution kernel width in DATA POINTS (not eV). Integer 0–499. m=0 = no convolution. Effective eV width ≈ (m/3) × dx where dx is the data step size.">m (Gauss kernel pts)
          ${!isLinked ? `<button class="lock-btn${p.fixCaM ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaM',this)" title="${p.fixCaM ? 'Unlock' : 'Lock'} during fitting">${p.fixCaM ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
        </label>
        <input type="number" value="${Math.round(p.caM ?? 50)}" step="1" min="0" max="499"
          oninput="updatePeakParam(${p.id},'caM',parseFloat(this.value))">
      </div>
    `;
```

- [ ] **Step 8: Add LACX branch in `peakToBackendSpec`**

Find the `'DSG_LA'` branch (post-Task-4) in `peakToBackendSpec`. After its closing `}`, add:

```js
  } else if (shape === 'LACX') {
    spec.shape = 'la_casaxps';
    spec.alpha = Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0;
    spec.beta  = Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0;
    spec.m     = Number.isFinite(p.caM)     ? p.caM     : 50.0;
    spec.fix_alpha = !!p.fixCaAlpha;
    spec.fix_beta  = !!p.fixCaBeta;
    spec.fix_m     = !!p.fixCaM;
```

- [ ] **Step 9: Add LACX branch in `applyBackendResult`**

Find lines 4541-4543 (the LA backend-param mapping). After those three lines (which now use `'DSG_LA'` from Task 4), add:

```js
    if (par.alpha && p.shape === 'LACX' && !p.fixCaAlpha) p.caAlpha = par.alpha.value;
    if (par.beta  && p.shape === 'LACX' && !p.fixCaBeta)  p.caBeta  = par.beta.value;
    if (par.m     && p.shape === 'LACX' && !p.fixCaM)     p.caM     = par.m.value;
```

- [ ] **Step 10: Add LACX branch in `runFit` JS LM fitter free-params**

Find line 5285 (`if (p.shape === 'DSG_LA') {` after Task 4) and the analogous `freeParams.push(...)` block. After its closing `}`, add:

```js
      if (p.shape === 'LACX') {
        if (!p.fixCaAlpha) { freeParams.push(Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0); paramMap.push({id: p.id, param: 'caAlpha'}); }
        if (!p.fixCaBeta)  { freeParams.push(Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0); paramMap.push({id: p.id, param: 'caBeta'}); }
        if (!p.fixCaM)     { freeParams.push(Number.isFinite(p.caM)     ? p.caM     : 50);  paramMap.push({id: p.id, param: 'caM'}); }
      }
```

Also find the per-param clamp block around line 5306-5308 and add:

```js
      if (param === 'caAlpha')    v = Math.max(0.1, Math.min(5.0, v));
      if (param === 'caBeta')     v = Math.max(0.1, Math.min(5.0, v));
      if (param === 'caM')        v = Math.max(0,   Math.min(499, Math.round(v)));
```

And the linked-peak param sync block at line 5317:

```js
            param === 'laAlpha' || param === 'laBeta' || param === 'laM' ||
            param === 'caAlpha' || param === 'caBeta' || param === 'caM') linked[param] = v;
```

- [ ] **Step 11: Add LACX columns to CSV export**

Find line 7115. Currently it's:

```js
      areas[i].toFixed(2), p.shape, p.glMix ?? '', p.dsAlpha ?? p.laAlpha ?? '',
      p.laBeta ?? '', p.laM ?? '',
```

Change the trailing two values to also fall through to `caAlpha`/`caBeta`/`caM`:

```js
      areas[i].toFixed(2), p.shape, p.glMix ?? '', p.dsAlpha ?? p.laAlpha ?? p.caAlpha ?? '',
      p.laBeta ?? p.caBeta ?? '', p.laM ?? p.caM ?? '',
```

- [ ] **Step 12: Verify structural integrity**

```bash
venv/bin/python -c "html = open('templates/index.html').read(); assert 'LACX' in html; assert 'caAlpha' in html and 'caBeta' in html and 'caM' in html; assert 'laTrueCasaXPS' in html and 'laTrueCasaXPS_array' in html; assert html.count('{') == html.count('}'); print('OK')"
```

Expected: `OK`.

- [ ] **Step 13: Reload gunicorn and verify in browser via served HTML**

```bash
kill -HUP 9674 2>/dev/null; sleep 2
curl -s --connect-timeout 2 http://localhost:5000/ 2>/dev/null | grep -c 'LACX\|caAlpha\|laTrueCasaXPS'
```

Expected: > 15.

- [ ] **Step 14: Commit**

```bash
git add templates/index.html
git commit -m "$(cat <<'EOF'
feat(frontend): add true LA(α,β,m) [CasaXPS] lineshape

New peak.shape value 'LACX' with distinct field names (caAlpha, caBeta,
caM) so users don't confuse parameters with the renamed DSG_LA shape
(whose β is HWHM in eV, not an exponent; whose m is FWHM in eV, not
integer points).

Adds: dropdown option, defaultPeak defaults, syncKeys entry, param row
in renderPeakControls, peakToBackendSpec branch, applyBackendResult
branch, runFit free-params + clamps + link-sync, CSV export columns,
JS implementations laTrueCasaXPS (per-point) and laTrueCasaXPS_array
(grid-aware for live convolution preview).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Frontend — auto-migration for saved `.fit.json` and `.proj.json`

**Files:**
- Modify: `templates/index.html` near `_applyFitJSON` (line 6566) and `_loadProjectJSON` (line 6632)

- [ ] **Step 1: Add `_migrateLineshapeAliases` helper**

Insert this helper just BEFORE `_applyFitJSON` (around line 6560 — find the function and add the helper above it):

```js
// Migrate lineshape enum values in saved fits to the current naming.
// Round-2 (2026-04-25): old 'LA' (which was DS-core × Gauss conv,
// mislabeled as CasaXPS LA) → 'DSG_LA'. The new genuine CasaXPS LA
// shape uses 'LACX' (which never appeared in any pre-2026-04-25 save).
// Mutates `peaks` in place and logs a single console.info line if any
// peak was migrated. Backwards-compat with no user-facing message.
function _migrateLineshapeAliases(peaks) {
  if (!Array.isArray(peaks)) return;
  const SHAPE_ALIASES = {
    'LA': 'DSG_LA',
    // Add future aliases here.
  };
  let n = 0;
  for (const p of peaks) {
    if (!p || typeof p.shape !== 'string') continue;
    const dest = SHAPE_ALIASES[p.shape];
    if (dest) { p.shape = dest; n++; }
  }
  if (n > 0) console.info('[migration] Remapped ' + n + ' peak(s) from LA → DSG_LA (DS+G is the new label).');
}
```

- [ ] **Step 2: Call `_migrateLineshapeAliases` from `_applyFitJSON`**

Find the start of `_applyFitJSON`. The function takes `data` and applies it. Insert the migration call after `data` is parsed but BEFORE peaks are pushed to state. The exact insert point is at the top of the function body. Find:

```js
function _applyFitJSON(data) {
```

Then, on the very next non-empty line, insert:

```js
  if (data && Array.isArray(data.peaks)) _migrateLineshapeAliases(data.peaks);
```

- [ ] **Step 3: Call `_migrateLineshapeAliases` from `_loadProjectJSON`**

Find `function _loadProjectJSON(data, sessionFile) {` (line 6632). At the top of its body, before any further work on `data`, insert:

```js
  // Per-tab peaks live under data.tabs[i].peaks (v2+) and/or top-level
  // data.peaks (v1). Migrate both shapes.
  if (data && Array.isArray(data.peaks)) _migrateLineshapeAliases(data.peaks);
  if (data && Array.isArray(data.tabs)) {
    for (const t of data.tabs) {
      if (t && Array.isArray(t.peaks)) _migrateLineshapeAliases(t.peaks);
    }
  }
```

- [ ] **Step 4: Write the migration unit test (Python port)**

```bash
cat > /tmp/test_dsg_alias_migration.py <<'EOF'
"""
Python port of _migrateLineshapeAliases. Verifies the alias map applies
correctly and is idempotent.
"""

SHAPE_ALIASES = {'LA': 'DSG_LA'}

def migrate(peaks):
    if not isinstance(peaks, list):
        return 0
    n = 0
    for p in peaks:
        if not isinstance(p, dict):
            continue
        s = p.get('shape')
        if not isinstance(s, str):
            continue
        if s in SHAPE_ALIASES:
            p['shape'] = SHAPE_ALIASES[s]
            n += 1
    return n

# Case 1: simple alias
peaks = [{'id': 1, 'shape': 'LA'}, {'id': 2, 'shape': 'GL'}]
n = migrate(peaks)
assert n == 1
assert peaks[0]['shape'] == 'DSG_LA'
assert peaks[1]['shape'] == 'GL'

# Case 2: idempotent (running twice produces no further changes)
n2 = migrate(peaks)
assert n2 == 0

# Case 3: no peaks
assert migrate([]) == 0
assert migrate(None) == 0

# Case 4: mixed types tolerated
assert migrate([{'shape': 'LA'}, None, {'no_shape': True}, {'shape': 'LACX'}]) == 1

print('OK — migration is correct and idempotent')
EOF
venv/bin/python /tmp/test_dsg_alias_migration.py
```

Expected: `OK — migration is correct and idempotent`.

- [ ] **Step 5: Verify structural integrity and reload**

```bash
venv/bin/python -c "html = open('templates/index.html').read(); assert '_migrateLineshapeAliases' in html; assert html.count('_migrateLineshapeAliases') >= 3; assert html.count('{') == html.count('}'); print('OK')"
kill -HUP 9674 2>/dev/null; sleep 2
curl -s --connect-timeout 2 http://localhost:5000/ 2>/dev/null | grep -c '_migrateLineshapeAliases'
```

Expected: `OK` then count ≥ 3 (definition + 2 call sites).

- [ ] **Step 6: Commit**

```bash
git add templates/index.html
git commit -m "$(cat <<'EOF'
feat(frontend): auto-migrate saved fits with old 'LA' shape to 'DSG_LA'

.fit.json and .proj.json files saved before the LA→DSG_LA rename load
without errors. _migrateLineshapeAliases mutates peak.shape entries in
place at the top of _applyFitJSON and _loadProjectJSON; logs a
console.info per file. Idempotent (re-running produces no further
changes), and migration cases are unit-tested in
/tmp/test_dsg_alias_migration.py.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: End-to-end backend test — fit a synthetic LACX spectrum

**Files:**
- Test: `/tmp/test_la_e2e_fit.py`

- [ ] **Step 1: Write the end-to-end fit test**

```bash
cat > /tmp/test_la_e2e_fit.py <<'EOF'
"""
End-to-end: synthesize a noisy spectrum with a single asymmetric LA peak
(α=0.6, β=1.5, m=20), feed it to fitting.run_fit through the same code
path the /api/fit endpoint uses, and confirm:
  - The fit converges
  - The recovered α, β, m, fwhm, center are within tolerance
"""
import sys
sys.path.insert(0, "/home/skye/xps-app")
import numpy as np
from fitting import _la_casaxps_true, run_fit

rng = np.random.default_rng(42)
x = np.linspace(280, 295, 1500)
true_amp = 12000.0
true_center = 285.0
true_fwhm = 0.9
true_alpha, true_beta, true_m = 0.6, 1.5, 20

y_clean = _la_casaxps_true(x, true_amp, true_center, true_fwhm,
                           true_alpha, true_beta, true_m)
y_noisy = y_clean + rng.normal(0, np.sqrt(np.maximum(y_clean, 1.0)))

peak_specs = [{
    'id': '1',
    'shape': 'la_casaxps',
    'center': 284.7,
    'amplitude': 10000.0,
    'fwhm': 1.0,
    'alpha': 1.0,
    'beta': 1.0,
    'm': 20.0,
    'fix_m': True,        # m is integer-valued; keep fixed for the test
}]

result = run_fit(
    energy=x,
    counts=y_noisy,
    peak_specs=peak_specs,
    background_method='none',
)

assert result['success'], f"fit failed: {result.get('message')}"
ip = result['individual_peaks'][0]
got_alpha = ip['params']['alpha']['value']
got_beta  = ip['params']['beta']['value']
got_fwhm  = ip['params']['fwhm']['value']
got_center = ip['params']['center']['value']

assert abs(got_alpha - true_alpha) < 0.05, f"alpha drift {got_alpha} vs {true_alpha}"
assert abs(got_beta  - true_beta)  < 0.10, f"beta drift {got_beta} vs {true_beta}"
assert abs(got_fwhm  - true_fwhm)  < 0.05, f"fwhm drift {got_fwhm} vs {true_fwhm}"
assert abs(got_center - true_center) < 0.02, f"center drift {got_center} vs {true_center}"

print(f"OK — α={got_alpha:.3f} β={got_beta:.3f} fwhm={got_fwhm:.3f} center={got_center:.3f}")
EOF
venv/bin/python /tmp/test_la_e2e_fit.py
```

Expected: `OK — α=… β=… fwhm=… center=…` with values close to the synthesized truths.

(No commit — test verifies prior commits.)

---

### Task 8: Documentation — update `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md` — the "LA(α, β, m) — CasaXPS Convention" subsection of the Lineshape Physics rules

- [ ] **Step 1: Replace the LA(α, β, m) subsection**

Find in `CLAUDE.md`:

```markdown
### LA(α, β, m) — CasaXPS Convention

| Parameter | Meaning |
|-----------|---------|
| α | **Dimensionless** asymmetry index, 0 ≤ α < 0.5 |
| β | Lorentzian half-width at half-maximum (eV) |
| m | Gaussian FWHM for convolution (eV) |

These are **not** half-widths in eV. α controls the shape of the power-law
tail (identical role to `dsAlpha` in the Doniach-Šunjić formula). β is the
Lorentzian width (not a half-width of a BE-asymmetric window). m is the
Gaussian broadening applied by convolution.

The LA tail must also point toward **higher** binding energy (same physical
reason as DS).
```

Replace with:

```markdown
### DS+G (formerly mislabeled "LA(α, β, m) [CasaXPS]")

The shape currently registered as `ds_g` (frontend `'DSG_LA'`, dropdown
"DS+G (DS core × Gauss conv)") is a Doniach-Šunjić asymmetric core
convolved with a Gaussian. Despite its old label, this is NOT the
CasaXPS LA formulation. Parameters:

| Parameter | Meaning |
|-----------|---------|
| α | DS asymmetry index, dimensionless, 0 ≤ α < 0.5 |
| β | Lorentzian HALF-width (eV) of the DS core |
| m | Gaussian FWHM (eV) used in the convolution |

Tail points toward **higher** binding energy (DS physics: low-energy
electron-hole pair excitations on the high-BE side only).

Saved fits using the old `'LA'` shape value are auto-migrated on load
to `'DSG_LA'` — math is unchanged, only the label.

### LA(α, β, m) [CasaXPS] — true CasaXPS formulation

The shape registered as `la_casaxps` (frontend `'LACX'`, dropdown
"LA(α,β,m) [CasaXPS]") implements the genuine CasaXPS LA. Parameters:

| Parameter | Meaning |
|-----------|---------|
| α | High-BE-side exponent on the unit-amplitude Lorentzian; dimensionless, default 1.0, bounds 0.1–5.0 |
| β | Low-BE-side exponent; dimensionless, default 1.0, bounds 0.1–5.0 |
| m | Gaussian convolution kernel width in DATA POINTS (not eV); integer, default 50, bounds 0–499 |

α=β=1, m=0 reduces exactly to a pure Lorentzian. Increasing α
**suppresses** the high-BE tail; decreasing α extends it (BE-axis
convention; sign-flipped from CasaXPS's KE-axis description). m
controls Gaussian broadening; effective eV width ≈ (m/3) × dx where dx
is the data step size.

When implementing new LA-related lineshape parameters, **always** add
them to:
- `defaultPeak` defaults block in `templates/index.html`
- `syncKeys` array (around line 4075)
- `renderPeakControls` LACX param row
- `peakToBackendSpec` LACX branch
- `applyBackendResult` LACX backend-param mapping
- `runFit` JS LM free-params block + per-param clamps + linked-peak sync
- The `evalPeak` switch + per-grid `laTrueCasaXPS_array` evaluator
- `_migrateLineshapeAliases` if any backwards-compat is needed
```

- [ ] **Step 2: Verify the file is well-formed Markdown**

```bash
grep -nc "### DS+G\|### LA(α, β, m) \[CasaXPS\]" /home/skye/xps-app/CLAUDE.md
```

Expected: `2`.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs(claude.md): document DS+G rename and true CasaXPS LA shape

Replaces the old 'LA(α, β, m) — CasaXPS Convention' subsection (which
described the now-renamed DS+G shape) with two subsections: the renamed
DS+G entry plus a new section for the true CasaXPS LA formulation.
Lists every per-shape integration point a future implementer must wire
through.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 9: Browser verification checklist (handoff)

This task does not run automatically. After Tasks 1-8 are committed, the user walks the following.

**Verification scenarios:**

**A. Saved-fit migration — old `.fit.json` opens cleanly.**
- Find or create a `.fit.json` saved before today (or one of the demo fits in the repo if available). Open it. Confirm:
  - File loads without console errors.
  - Console shows `[migration] Remapped N peak(s) from LA → DSG_LA …`.
  - Peaks that were `LA` now show "DS+G (DS core × Gauss conv)" in the dropdown.
  - Numerical fit (chi², peak areas) is unchanged from before-rename if you re-fit.

**B. DS+G round-trip — re-save, re-load.**
- Open any spectrum, add a peak, set its shape to "DS+G (DS core × Gauss conv)", set α/β/m to non-defaults, run fit, save as `.fit.json`. Reload that file. Confirm:
  - No `[migration]` log (the new save uses `'DSG_LA'` directly).
  - Peak's shape, α, β, m are preserved.
  - Re-fit produces identical χ².

**C. New LACX shape — basic sanity.**
- Add a peak. Set shape to "LA(α,β,m) [CasaXPS]". Defaults α=1.0, β=1.0, m=50.
- Verify the param row shows three fields (α, β, m), each with a lock icon and bounds enforced (α/β step 0.05 in 0.1–5.0; m integer step 1 in 0–499).
- m field shows the integer 50 by default; lock icon should default closed.
- Drag α below β and confirm the live preview shows a high-BE tail extending visibly.
- Drag β below α and confirm the live preview shows a low-BE tail extending.
- Set α=β=1, m=0; the peak should be a pure Lorentzian (symmetric, narrow).

**D. New LACX shape — fit convergence on real data.**
- Load Au 4f or any metallic core-level if available. Place an LACX peak; run fit. Confirm:
  - Fit converges.
  - Reported α/β/m in the Results panel are within their bounds.
  - Visually plausible (fit curve overlays data well).

**E. CSV export.**
- Add one peak per shape (DSG_LA + LACX). Export results as CSV.
- Confirm the row for the LACX peak has α/β/m columns populated correctly (not blank).

**F. Linked-peak sync (regression).**
- Create an LACX peak; link a second peak to it as spin-orbit child. Change parent's α — confirm child's α follows. Repeat for β and m.

**G. Saved-state schema check.**
- Save a project (`.proj.json`) containing both DSG_LA and LACX peaks. Reload. Confirm both shapes restore correctly.

**Reporting back:**
- All green → push the 8 commits to origin/main.
- Anything red → paste the symptom + console output; I'll patch the specific failure.

(No commit — manual verification only.)

---

## Self-review

**Spec coverage:**

| Spec section | Task |
|--------------|------|
| Part 1 (rename old LA) | Tasks 2 (backend), 4 (frontend) |
| Disambiguate DSG vs DSG_LA collision (D3) | Task 2.5 |
| Part 2 (math: piecewise asymmetric Lorentzian) | Task 3 Step 2 |
| Part 2 (math: Gaussian convolution with integer m, σ_pts = m/3) | Task 3 Step 2 (`sigma_pts = m_int / 3.0`) |
| Part 2 (BE-axis sign flip from CasaXPS KE-axis) | Task 3 Step 2 (eps ≥ 0 → α; verified by Step 7 test) |
| Part 2 (params: amplitude, center, fwhm, alpha, beta, m, defaults & bounds) | Task 3 Step 4 |
| Part 2 (reduce to Lorentzian unit test) | Task 3 Step 1 |
| Part 2 (reduce to Voigt-like unit test) | Task 3 Step 6 |
| Part 2 (frontend dropdown + param row + tooltip) | Task 5 Steps 6, 7 |
| Part 2 (m as int via float-then-round) | Task 3 Step 2 (`m_int = int(round(...))`) |
| Part 3 (auto-migration on load) | Task 6 |
| Part 3 (alias map) | Task 6 Step 1 (`SHAPE_ALIASES`) |
| Part 3 (console.info, no user-facing warning) | Task 6 Step 1 |
| Part 4 (visual regression on UCl₄ fit) | Task 9 (browser checklist A) |
| Part 4 (save/load round-trip) | Task 9 (browser checklist B, G) |
| Part 5 (DS+G + LACX descriptions in docs) | Task 8 |
| Part 5 (note about prior label / migration) | Task 8 |
| Workflow: backups | Task 1 |

**Placeholder scan:** No "TBD", "TODO", "implement later", or "fill in" text in tasks. All code blocks are complete. The browser checklist is intentionally manual (Task 9).

**Type/identifier consistency:**
- `_la_casaxps_true` defined in Task 3 Step 2; called in `_SHAPE_FUNCS` in Task 3 Step 3; tested in Steps 1, 6, 7; lmfit-checked in Step 8.
- `_ds_g_dscore_gauss` defined in Task 2 Step 1; registered in Task 2 Step 2; numerically verified in Step 6.
- `'DSG_LA'` (frontend enum), `'ds_g'` (backend id), `"DS+G (DS core × Gauss conv)"` (display label) — all consistent across Tasks 2, 4.
- `'LACX'` (frontend enum), `'la_casaxps'` (backend id), `"LA(α,β,m) [CasaXPS]"` (display label) — all consistent across Tasks 3, 5.
- `caAlpha`, `caBeta`, `caM` field names + `fixCaAlpha`, `fixCaBeta`, `fixCaM` lock fields — used consistently in Task 5 Steps 4, 5, 7, 8, 9, 10, 11.
- `_migrateLineshapeAliases` defined in Task 6 Step 1, called in Steps 2, 3.
- `laTrueCasaXPS` and `laTrueCasaXPS_array` defined in Task 5 Step 1; called in Steps 2, 3.

No gaps detected.
