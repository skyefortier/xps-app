# XPS Fitting Studio

Flask-based web application for XPS (X-ray Photoelectron Spectroscopy) peak fitting.

## Stack

- **Backend:** Python/Flask with gunicorn (planned — not yet implemented)
- **Fitting engine:** lmfit (>=1.3) (planned for backend; browser currently uses JS LM)
- **Numerics:** numpy, scipy, pandas
- **Frontend:** Single-file HTML (`xps-fitting-tool.html`)
- **File I/O:** openpyxl for .xlsx; browser-side XLSX.js for client parsing
- **Charting:** Chart.js 4.4 (CDN)

## Project Layout

```
xps-fitting-tool.html   # entire frontend — CSS + HTML + JS in one file
requirements.txt        # Python dependencies (Flask, lmfit, numpy, scipy, etc.)
venv/                   # virtualenv (do not commit)
```

The Flask backend (when present) will serve the HTML and expose fitting endpoints consumed by the frontend via fetch/XHR. Currently the app is fully client-side.

## Frontend Architecture

### State

All runtime state lives in a single global `state` object:

```js
state = {
  rawBE, rawIntensity,   // full spectrum as loaded
  ccShift,               // charge-correction rigid shift (eV)
  peaks[],               // array of peak objects
  nextId,                // auto-increment peak ID
  chart,                 // Chart.js instance
  fitResult              // last fit diagnostics
}
```

### Peak Object Schema

```js
{
  id, name, color,
  center,      // eV
  fwhm,        // eV
  amplitude,   // counts/s
  shape,       // 'Gaussian'|'Lorentzian'|'Voigt'|'GL'|'asym-GL'|'DS'
  glMix,       // 0–100 (0 = pure Gauss, 100 = pure Lorentz)
  asymmetry,   // asym-GL asymmetry index
  dsAlpha,     // DS α parameter (0–0.5)
  dsGamma,     // DS exponential tail cutoff
  linked,      // id of parent peak (null if primary)
  linkOffset,  // eV offset from parent center (linked peaks only)
  linkRatio,   // amplitude ratio relative to parent (linked peaks only)
  visible
}
```

### Lineshapes Currently Implemented

| ID | Description |
|----|-------------|
| `Gaussian` | Pure Gaussian |
| `Lorentzian` | Pure Lorentzian |
| `Voigt` | Pseudo-Voigt (Thompson et al.), fixed η = 0.5 |
| `GL` | Pseudo-Voigt with adjustable GL mixing (0–100) |
| `asym-GL` | GL with asymmetric FWHM broadening on high-BE side |
| `DS` | Doniach-Šunjić, params `dsAlpha` (0–0.5) and `dsGamma` |
| `DSG_LA` | DS+G — Doniach-Šunjić core convolved with Gaussian (formerly mislabeled "LA [CasaXPS]"). Frontend params `laAlpha`/`laBeta`/`laM`; backend id `ds_g` |
| `LACX` | True CasaXPS LA(α,β,m) — asymmetric base Lorentzian + integer-kernel Gauss conv. Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps` |

### Fitting Algorithm

Client-side Levenberg-Marquardt (in JS):
- Only parameters of non-linked peaks are free; linked peaks derive their values from their parent
- Numerical Jacobian (finite differences with adaptive step)
- Gaussian elimination with partial pivoting to solve the normal equations
- Max 500 iterations; stops when Δχ²/χ² < 1e-8 or λ > 1e8

### File Formats Supported

| Extension | Parser |
|-----------|--------|
| `.csv`, `.tsv` | `parseCSV` — whitespace/comma/tab/semicolon delimited |
| `.xlsx` | `parseXLSX` via XLSX.js |
| `.vgd` | `parseVGD` — Thermo Avantage binary (heuristic Float32 extraction) |

Spectrum columns: first = BE (eV), second = intensity (counts/s). Rows with
non-numeric or missing values are skipped.

### Background Methods

| Option | Notes |
|--------|-------|
| Shirley (iterative) | **Default.** Proctor & Sherwood, *Anal. Chem.* **1982**, 54, 13, 2438–2439 |
| Linear | Straight line between ROI endpoints |
| Tougaard | Simplified B·T²/(C+T²)² cross-section approximation |

Use Shirley for standard core-level regions. Linear only when the spectral window is very narrow and featureless.

### Quantification

Peak areas are integrated numerically (trapezoidal over BE grid). RSF (relative sensitivity factor) corrections are applied manually in the Quantify tab. Atomic percent = (area/RSF) / Σ(area/RSF) × 100.

---

## Lineshape Physics — Critical Rules

### DS (Doniach-Šunjić) Asymmetric Lineshape

The DS tail MUST always point toward **higher binding energy** (the left side on a standard inverted BE axis). Asymmetric broadening in metals arises from low-energy electron-hole pair excitations at the Fermi level, which produce intensity only on the high-BE side of the core-level peak.

**Never invert the DS tail toward lower binding energy.**

Current implementation note: `doniachSunjic` uses
`gammaFactor = Math.exp(-gamma_asym * dx)` where `dx = x − center`.
When `dx > 0` (x at higher BE than center) this factor decays, and when
`dx < 0` it grows — which means the exponential tail currently amplifies toward
**lower** BE. This is physically backwards. Keep `dsGamma` small (≤ 0.01) to
minimise the artefact until this is corrected. The power-law asymmetry from
`dsAlpha` is correct and dominates at typical parameter values.

### DS+G (formerly mislabeled "LA(α, β, m) [CasaXPS]")

The shape registered as `ds_g` in the backend (frontend enum `'DSG_LA'`,
dropdown text "DS+G") is a Doniach-Šunjić asymmetric core convolved with a
Gaussian. Despite its old label, this is NOT the CasaXPS LA formulation.
Frontend field names `laAlpha` / `laBeta` / `laM` are kept for save-state
compatibility:

| Parameter | Meaning |
|-----------|---------|
| α (`laAlpha`) | DS asymmetry index, dimensionless, 0 ≤ α < 0.5 |
| β (`laBeta`) | Lorentzian HALF-width (eV) of the DS core |
| m (`laM`) | Gaussian FWHM (eV) used in the convolution |

Tail points toward **higher** binding energy (DS physics: low-energy
electron-hole pair excitations on the high-BE side only).

Saved fits using the old `'LA'` shape value are auto-migrated on load to
`'DSG_LA'` — math is unchanged, only the label.

DSG shape removed; was a pre-existing bug where the frontend preview showed
DS ⊛ G but the backend fit DS-only. Saved fits using DSG are auto-migrated
to DS, which is the shape they were actually being fit against.

### LA(α, β, m) [CasaXPS] — true CasaXPS formulation

The shape registered as `la_casaxps` (frontend enum `'LACX'`, dropdown
"LA(α,β,m) [CasaXPS]") implements the genuine CasaXPS LA. Distinct field
names `caAlpha` / `caBeta` / `caM` so users do not confuse them with DS+G's
`laAlpha`/`laBeta`/`laM` (which have totally different units):

| Parameter | Meaning |
|-----------|---------|
| α (`caAlpha`) | High-BE-side exponent on the unit-amplitude Lorentzian; dimensionless, default 1.0, bounds 0.1–5.0 |
| β (`caBeta`) | Low-BE-side exponent; dimensionless, default 1.0, bounds 0.1–5.0 |
| m (`caM`) | Gaussian convolution kernel width in DATA POINTS (not eV); integer, default 50, bounds 0–499 |

α=β=1, m=0 reduces exactly to a pure Lorentzian. Increasing α **suppresses**
the high-BE tail; decreasing α extends it (BE-axis convention; sign-flipped
from CasaXPS's KE-axis description). m controls Gaussian broadening;
effective eV width ≈ (m/3) × dx where dx is the data step size.

When implementing new LA-related lineshape parameters, **always** add them
to:

- `defaultPeak` defaults block in `templates/index.html`
- `syncKeys` array (around line 4075)
- `renderShapeControls` LACX param row
- `peakToBackendSpec` LACX branch
- `applyBackendResult` LACX backend-param mapping
- `runFit` JS LM free-params block + per-param clamps + linked-peak sync
- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`)
- `_migrateLineshapeAliases` if backwards-compat alias needed

### UCl4 U 4f Asymmetric Broadening

The asymmetric broadening in the UCl4 U 4f spectrum is due to **5f² multiplet
coupling**, not metallic screening. Do not attribute it to Kondo screening or
Doniach-Šunjić metallic behaviour. Use multiplet-split component models, not
a single DS peak.

The demo data (`loadDemo('U4f')`) correctly uses `asym-GL` for the U 4f₇/₂
and 4f₅/₂ main lines, with separate symmetric GL peaks for the multiplet
satellites.

### Satellite Peaks

Satellite peaks (shake-up, shake-off, plasmon loss) use **symmetric**
lineshapes — Voigt or GL. Do not apply DS or LA lineshapes to satellites.

### Linked (Multiplet) Peaks

A linked peak derives its center, amplitude, and **all lineshape parameters**
from its parent:

| Parent param changes | Linked peak receives |
|----------------------|----------------------|
| `center` | `parent.center + linkOffset` |
| `amplitude` | `parent.amplitude × linkRatio` |
| `fwhm` | same value |
| `shape` | same value |
| `glMix` | same value |
| `asymmetry` | same value |
| `dsAlpha` | same value |
| `dsGamma` | same value |

When implementing new lineshape parameters, **always** add them to the sync
block in `updatePeakParam` (around line 1048) and the `applyParams` closure in
`runFit` (around line 1254). Failing to do so silently breaks spin-orbit
constraints during fitting.

---

## Charge Correction

Reference: **C 1s graphite at 284.8 eV**. Apply a rigid shift (`state.ccShift`)
to all binding energies before fitting. The corrected axis is produced by
`getCorrectedBE()`.

---

## Demo Spectra

| Demo | Region | Notes |
|------|--------|-------|
| Fe 2p | 700–740 eV | Fe(0) at 706.6, Fe(III) at 710.5, satellite at 713.5 |
| U 4f | 370–415 eV | UCl4-like U(IV); 4f₇/₂ at 380.9, 4f₅/₂ at 391.8 (offset 10.9 eV) |
| C 1s | 280–295 eV | sp², sp³, C-O, C=O, COOH components; charge ref at 284.8 eV |
