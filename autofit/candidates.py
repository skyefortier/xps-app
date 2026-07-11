"""
Pluggable candidate-generation layer — detection proposes, selection judges.

This module generates an OVERCOMPLETE, provenance-tagged pool of peak-
candidate features from multiple detection sources.  It never decides what
the "true" peaks are: every feature carries its detection provenance and
gate outcomes, and the EXISTING fitting/model-selection machinery
(absent-slot classification, persistence, BIC* ranking, plausibility
filtering) prunes the pool.  Nothing here touches the manual Run Fit path
or the /api/fit contract.

Sources (provenance tags):
- ``local_max``            smoothed local maxima (the F1 dominant channel,
                           computed in engine.detect_out_of_grammar_dominants
                           and passed in — its reviewed behavior is unchanged)
- ``curvature_shoulder``   the CWT ridge detector below — the ONE new
                           detector (goal step 3).  Finds components that
                           produce NO local maximum (shoulders) and resolved
                           close pairs that blunt duplicate-suppression
                           discards.
- ``residual_gap``         the F2 residual-proposal pass (merged into the
                           pool payload post-fit by the engine)
- ``grammar``              region-cookbook windows (what the grammar already
                           expects, for a complete honesty surface)

Detector design (CWT ridge, Ricker wavelet):
A Ricker kernel is a band-limited negative-second-derivative probe; a
shoulder produces a local maximum of the CWT coefficient row at scales near
its own width even when the composite signal has no local maximum.  The
gate statistic is PROMINENCE-z: the coefficient local-max prominence
divided by the Poisson-propagated coefficient sigma sqrt((w^2 * y)), i.e. a
pure counting-statistics anomaly measure.  Because the kernel is exactly
zero-mean and symmetric, constant and linear backgrounds cancel
identically, and smooth-background curvature only enters through the
prominence (not the offset).  Raw derivatives are never used (extrema shift
under overlap/asymmetry/baseline/noise — goal rail).

CALIBRATION (anti-overfit rail): every tunable below was set on SYNTHETIC
batteries only — see scripts/calibrate_cwt_detector.py, which regenerates
the H0 false-positive battery (600 negative spectra across counts levels,
background families, and grid steps) and the shoulder/doublet sensitivity
maps.  The real held-out scans were NEVER a tuning target.  All tunables
are UNVERIFIED in the spec-§9 sense and are surfaced in the pool payload.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.signal import find_peaks, peak_prominences

# ── Detector tunables (synthetic-calibrated; surfaced in payloads) ──────────

# Prominence-z gate.  H0 battery (600 negative spectra: flat / linear-drift /
# sigmoid-step backgrounds x counts 100..50000 x steps 0.05/0.1, committed
# generator scripts/calibrate_cwt_detector.py, byte-identical regeneration):
# per-spectrum MAX prom_z q95 = 6.73, q99 = 8.32; measured POOL-level FP
# rate at 7.0 = 4.2% of spectra (tolerated by design — the pool is
# overcomplete; SEEDING-level FPs are separately pinned at zero under the
# compound gates).  Sensitivity battery: the HIGH-COUNT target shoulder
# regimes (sep >= 0.9xFWHM at ratio >= 0.3; sep >= 1.1 at ratio >= 0.15 —
# both at ~40k-count mains) measure prom_z >= 8.5 and detect 5/5; at low
# counts (~2k) the envelope shifts one step coarser (counting statistics).
# 7.0 sits above H0 q95 with >= 1.5 margin below the weakest high-count
# target regime.  UNVERIFIED tunable.
CWT_PROM_Z_MIN = 7.0

# Scale ladder, eV-anchored (grid-step independent): FWHM 0.3 eV (below any
# practical XPS instrumental width — nothing narrower is physical signal) to
# 2.4 eV (just above FWHM_MAX_ORDINARY_EV = 2.0, the engine's ordinary-
# component physical ceiling; broader structures are the dominant/local-max
# channel's regime).  8 geometric steps.  UNVERIFIED tunables.
CWT_FWHM_MIN_EV = 0.3
CWT_FWHM_MAX_EV = 2.4
CWT_N_SCALES = 8

# Ricker sigma floor in grid points — below ~2 points the kernel is
# undersampled and the row is pure grid noise (structural, not tuned).
CWT_SIGMA_MIN_PTS = 2.0

# Ridge linking: a ridge must persist across >= 2 adjacent scales (single-
# row maxima are numeric flukes); one missing scale row is tolerated
# (standard Du et al. 2006 ridge-linking practice, as in SciPy's
# find_peaks_cwt).  Structural constants, not sensitivity tunables.
CWT_MIN_RIDGE_LENGTH = 2
CWT_RIDGE_GAP_MAX = 1

_FWHM_PER_SIGMA = 2.354820045030949  # Gaussian FWHM / sigma


@dataclass(frozen=True)
class RidgeFeature:
    """One CWT ridge — a candidate feature, NOT a confirmed peak."""
    center_be: float          # position at the smallest scale on the ridge
    prom_z: float             # best prominence-z along the ridge
    scale_fwhm_ev: float      # FWHM implied by the best-z scale
    fwhm_est_ev: float        # width estimate (== scale_fwhm_ev, clipped)
    ridge_length: int         # number of scale rows the ridge persists

    def payload(self) -> dict:
        return {
            "center_be": round(float(self.center_be), 3),
            "prom_z": round(float(self.prom_z), 2),
            "scale_fwhm_ev": round(float(self.scale_fwhm_ev), 3),
            "fwhm_est_ev": round(float(self.fwhm_est_ev), 3),
            "ridge_length": int(self.ridge_length),
        }


def ricker_kernel(sigma_pts: float, radius_pts: int) -> np.ndarray:
    """Ricker (Mexican-hat) kernel, exactly zero-mean on the finite grid so
    constant AND linear signal components cancel identically."""
    t = np.arange(-radius_pts, radius_pts + 1, dtype=float)
    k = (1.0 - (t / sigma_pts) ** 2) * np.exp(-0.5 * (t / sigma_pts) ** 2)
    return k - k.mean()


def _cwt_scales_pts(step_ev: float) -> list[float]:
    lo = max(CWT_FWHM_MIN_EV / _FWHM_PER_SIGMA / step_ev, CWT_SIGMA_MIN_PTS)
    hi = CWT_FWHM_MAX_EV / _FWHM_PER_SIGMA / step_ev
    if hi <= lo:
        return [lo]
    return list(np.geomspace(lo, hi, CWT_N_SCALES))


def cwt_ridge_features(
    x: np.ndarray,
    y: np.ndarray,
    prom_z_min: float = CWT_PROM_Z_MIN,
    min_ridge_length: int = CWT_MIN_RIDGE_LENGTH,
) -> list[RidgeFeature]:
    """
    Ricker-CWT ridge detection on RAW counts.

    Raw counts (not background-subtracted) on purpose: the zero-mean kernel
    cancels constant/linear backgrounds exactly, while subtracting an
    iterative background from a low-structure window injects the background
    algorithm's own bridging artifacts into the curvature (measured on the
    calibration H0 battery: Shirley-subtracted negatives false-fire at
    prom_z 10-800; raw negatives stay below 8).

    Returns features sorted by center_be.  Detection only — every result is
    a candidate to prune, never truth.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) != len(y) or len(x) < 16:
        return []
    if x[0] > x[-1]:                       # real raw_be grids DESCEND
        x, y = x[::-1], y[::-1]
    steps = np.diff(x)
    if not np.all(steps > 0):
        return []
    step = float(np.median(steps))
    n = len(x)
    # a kernel longer than the signal makes np.convolve('same') return the
    # KERNEL's length (shape crash) and carries no information anyway —
    # oversized scales are skipped for short windows
    scales = [s for s in _cwt_scales_pts(step)
              if 2 * int(np.ceil(4.0 * s)) + 1 <= n]
    if len(scales) < CWT_MIN_RIDGE_LENGTH:
        return []
    nrow = len(scales)

    coef = np.zeros((nrow, n))
    var = np.zeros((nrow, n))
    margins: list[int] = []
    for si, s in enumerate(scales):
        radius = int(np.ceil(4.0 * s))
        w = ricker_kernel(s, radius)
        coef[si] = np.convolve(y, w, mode="same")
        var[si] = np.convolve(np.maximum(y, 1.0), w * w, mode="same")
        margins.append(radius + 2)         # 'same' zero-padding artifacts

    # Row-wise local maxima with prominence-z (prominence normalized by the
    # Poisson-propagated coefficient sigma at the maximum).
    row_max: list[list[int]] = []
    row_prom_z: list[dict[int, float]] = []
    for si in range(nrow):
        row = coef[si]
        m = margins[si]
        lo, hi = max(2, m), min(n - 2, n - m)
        if hi <= lo:
            row_max.append([])
            row_prom_z.append({})
            continue
        pk, _ = find_peaks(row)
        pk = [i for i in pk if lo <= i < hi]
        proms = peak_prominences(row, pk)[0] if pk else []
        pz = {i: float(p) / float(np.sqrt(max(var[si, i], 1e-12)))
              for i, p in zip(pk, proms)}
        row_max.append(pk)
        row_prom_z.append(pz)

    # Ridge linking, largest scale downward; new ridges may start at any
    # scale (shoulder ridges only exist at scales near their own width).
    ridges: list[list[tuple[int, int]]] = []
    active: list[tuple[list[tuple[int, int]], int]] = []
    for si in range(nrow - 1, -1, -1):
        window = max(2, int(round(scales[si])))
        claimed: set[int] = set()
        nxt: list[tuple[list[tuple[int, int]], int]] = []
        for line, gap in active:
            last_idx = line[-1][1]
            cands = [i for i in row_max[si]
                     if abs(i - last_idx) <= window and i not in claimed]
            if cands:
                i = min(cands, key=lambda i: abs(i - last_idx))
                claimed.add(i)
                line.append((si, i))
                nxt.append((line, 0))
            elif gap < CWT_RIDGE_GAP_MAX:
                nxt.append((line, gap + 1))
            else:
                ridges.append(line)
        for i in row_max[si]:
            if i not in claimed:
                nxt.append(([(si, i)], 0))
        active = nxt
    ridges.extend(line for line, _ in active)

    out: list[RidgeFeature] = []
    for line in ridges:
        if len(line) < min_ridge_length:
            continue
        best_z, (best_si, _best_i) = max(
            ((row_prom_z[si].get(i, 0.0), (si, i)) for si, i in line),
            key=lambda t: t[0])
        if best_z < prom_z_min:
            continue
        # center read at the SMALLEST scale on the ridge (least shift under
        # overlap — the reason raw-derivative extrema are banned)
        _si_small, i_small = min(line, key=lambda t: t[0])
        scale_fwhm = _FWHM_PER_SIGMA * scales[best_si] * step
        out.append(RidgeFeature(
            center_be=float(x[i_small]),
            prom_z=float(best_z),
            scale_fwhm_ev=float(scale_fwhm),
            fwhm_est_ev=float(scale_fwhm),
            ridge_length=len(line),
        ))
    out.sort(key=lambda f: f.center_be)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Candidate pool — overcomplete, provenance-tagged; seeding gates conservative
# ─────────────────────────────────────────────────────────────────────────────

# Pool-entry floor for the local-max channel: pure-noise smoothed maxima sit
# at local_snr ~ 1/sqrt(smooth_points) ≈ 0.45, real sub-seed features well
# above.  Keeps the honesty payload overcomplete without transcribing noise
# chaff.  UNVERIFIED tunable (surfaced in the payload).
POOL_LOCAL_MAX_MIN_SNR = 2.0


@dataclass(frozen=True)
class PoolFeature:
    """One pool entry.  ``window`` is set only for grammar reference
    entries; detection entries carry the detector fields."""
    center_be: float
    provenance: tuple[str, ...]
    fwhm_est: Optional[float] = None
    amplitude_net: Optional[float] = None
    fraction_of_max: Optional[float] = None
    local_snr: Optional[float] = None
    prom_z: Optional[float] = None
    ridge_length: Optional[int] = None
    in_grammar_window: bool = False
    seeded_role: Optional[str] = None
    gate_fails: tuple[str, ...] = ()
    window: Optional[tuple[float, float]] = None       # grammar entries
    label: Optional[str] = None                        # grammar entries

    def payload(self) -> dict:
        rec: dict = {
            "center_be": round(float(self.center_be), 3),
            "provenance": list(self.provenance),
            "in_grammar_window": bool(self.in_grammar_window),
            "seeded_role": self.seeded_role,
            "gate_fails": list(self.gate_fails),
        }
        for key in ("fwhm_est", "amplitude_net", "fraction_of_max",
                    "local_snr", "prom_z"):
            v = getattr(self, key)
            rec[key] = round(float(v), 3) if v is not None else None
        rec["ridge_length"] = (int(self.ridge_length)
                               if self.ridge_length is not None else None)
        if self.window is not None:
            rec["window"] = [round(float(self.window[0]), 3),
                             round(float(self.window[1]), 3)]
            rec["label"] = self.label
        return rec


@dataclass(frozen=True)
class CurvatureSeed:
    """A pool feature accepted by the curvature-channel SEEDING gates —
    consumed by the engine as an additional pre-seeded slot (role prefix
    ``preseed_curvature_``, region-unassigned, absent-eligible: the
    selection layer prunes a seed that carries no real signal)."""
    role: str
    center_be: float
    fwhm_init: float
    amplitude_net: float
    fraction_of_max: float
    local_snr: float
    prom_z: float

    def payload(self) -> dict:
        return {
            "role": self.role,
            "center_be": round(float(self.center_be), 3),
            "fwhm_init": round(float(self.fwhm_init), 2),
            "amplitude_net": round(float(self.amplitude_net), 1),
            "fraction_of_max": round(float(self.fraction_of_max), 3),
            "local_snr": round(float(self.local_snr), 1),
            "prom_z": round(float(self.prom_z), 2),
            "provenance": "curvature_shoulder",
        }


@dataclass
class CandidatePool:
    features: list[PoolFeature]
    curvature_seeds: list[CurvatureSeed]
    sources_run: list[str]
    tunables: dict

    def payload(self) -> dict:
        return {
            "sources_run": list(self.sources_run),
            "features": [f.payload() for f in self.features],
            "curvature_seeds": [s.payload() for s in self.curvature_seeds],
            "tunables": dict(self.tunables),
            "note": ("OVERCOMPLETE detection pool — features are candidates "
                     "to prune, not truth; selection (absent-slot / "
                     "persistence / BIC*) judges.  All gate constants are "
                     "UNVERIFIED engine tunables."),
        }


def merge_residual_attempts(
    pool_payload: dict,
    attempts: list[dict],
    coincidence_ev: float,
    proposal_pass_ran: bool = True,
) -> None:
    """
    Merge the F2 residual-proposal attempts into a pool PAYLOAD (post-fit —
    residual proposals only exist per fitted candidate).  Each attempt is
    ``{"center_be": float, "accepted": bool}``; attempts within
    ``coincidence_ev`` of an existing detection entry annotate that entry
    (provenance += 'residual_gap'), others append a new pool entry.  Every
    annotated entry carries {n_attempts, n_accepted} bookkeeping under the
    ``residual_gap`` key.  Mutates ``pool_payload`` in place.
    """
    if proposal_pass_ran and "residual_gap" not in pool_payload["sources_run"]:
        pool_payload["sources_run"].append("residual_gap")
    features = pool_payload["features"]
    for att in attempts:
        c = float(att["center_be"])
        host = None
        best = None
        for f in features:
            if f.get("window") is not None:
                continue                       # grammar reference entries
            d = abs(float(f["center_be"]) - c)
            if d <= coincidence_ev and (best is None or d < best):
                host, best = f, d
        if host is None:
            host = {
                "center_be": round(c, 3), "provenance": [],
                "in_grammar_window": False, "seeded_role": None,
                "gate_fails": [], "fwhm_est": None, "amplitude_net": None,
                "fraction_of_max": None, "local_snr": None, "prom_z": None,
                "ridge_length": None,
            }
            features.append(host)
        if "residual_gap" not in host["provenance"]:
            host["provenance"].append("residual_gap")
        rg = host.setdefault("residual_gap",
                             {"n_attempts": 0, "n_accepted": 0})
        rg["n_attempts"] += 1
        rg["n_accepted"] += int(bool(att["accepted"]))
    features.sort(key=lambda f: f["center_be"])


def _smoothed_local_maxima(ys: np.ndarray, edge: int) -> list[int]:
    """The F1 detector's plateau-tolerant local-max condition."""
    idx = []
    for i in range(edge, len(ys) - edge):
        if (ys[i] >= ys[i - 1] and ys[i] > ys[i + 1]
                and ys[i] >= ys[i - 2] and ys[i] > ys[i + 2]):
            idx.append(i)
    return idx


def _half_height_fwhm(x: np.ndarray, ys: np.ndarray, i: int,
                      floor: float) -> float:
    half = 0.5 * ys[i]
    left = i
    while left > 0 and ys[left - 1] > half:
        left -= 1
    right = i
    while right < len(ys) - 1 and ys[right + 1] > half:
        right += 1
    fwhh = float(x[right] - x[left])
    return fwhh if fwhh > 0 else floor


def build_candidate_pool(
    x: np.ndarray,
    y: np.ndarray,
    background: np.ndarray,
    all_windows: list[tuple[float, float]],
    labeled_windows: dict[str, tuple[float, float]],
    dominant_seeds: list[dict],
    noise_floor: float = 1.0,
    min_fraction_of_max: float = 0.25,
    amplitude_snr: float = 5.0,
    prom_z_min: float = CWT_PROM_Z_MIN,
    coincidence_ev: float = 0.5,
    max_total_seeds: int = 2,
    smooth_points: int = 5,
    fwhm_clip: tuple[float, float] = (0.5, 2.0),
    local_window_ev: float = 0.5,
) -> CandidatePool:
    """
    Build the overcomplete candidate pool and apply the curvature-channel
    SEEDING gates.

    ``dominant_seeds`` is the local-max dominant channel's output (the
    reviewed F1 detector, unchanged upstream), as payload-shaped dicts with
    roles already assigned — the pool merges them by position and never
    re-gates them.

    Curvature-seed window blocking is CONTAINMENT-only (Stage-2
    recalibration, 2026-07-10): a feature is "expressible by the grammar"
    only if some slot window actually CONTAINS its center — the old
    window+margin test was measured blocking top-5 curvature detections
    (prom_z 107–273) sitting in inter-window cracks where NO slot could
    center a component ("covered by grammar" was a fiction).  Near-edge
    ambiguity — a seed just outside a window fighting the window's own
    slot for the same intensity — is deliberately left to SELECTION
    (absent-slot pruning / persistence / BIC*), which is the layer with
    the evidence to arbitrate it.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    background = np.asarray(background, dtype=float)
    tunables = {
        "prom_z_min": prom_z_min,
        "min_fraction_of_max": min_fraction_of_max,
        "amplitude_snr": amplitude_snr,
        "coincidence_ev": coincidence_ev,
        "max_total_seeds": max_total_seeds,
        "pool_local_max_min_snr": POOL_LOCAL_MAX_MIN_SNR,
        "cwt_fwhm_scale_range_ev": [CWT_FWHM_MIN_EV, CWT_FWHM_MAX_EV],
        "note": "UNVERIFIED engine tunables (synthetic-calibrated; "
                "scripts/calibrate_cwt_detector.py)",
    }
    if len(x) < max(smooth_points + 4, 8) or len(x) != len(y):
        return CandidatePool([], [], ["local_max", "curvature_shoulder",
                                      "grammar"], tunables)
    if x[0] > x[-1]:                       # real raw_be grids DESCEND
        x, y, background = x[::-1], y[::-1], background[::-1]

    y_net = y - background
    kernel = np.ones(smooth_points) / smooth_points
    ys = np.convolve(y_net, kernel, mode="same")
    global_max = float(np.max(ys)) if len(ys) else 0.0

    # Containment tolerance = HALF A GRID STEP: a feature center within half
    # a sample of a window edge is indistinguishable from the edge itself
    # (grid arithmetic also puts float epsilon on exact-edge centers).  This
    # is sampling resolution, NOT a coverage margin — the Stage-2 diagnosis
    # measured the old ±margin (~0.5 eV) fictitiously "covering" features
    # 0.2+ eV outside every slot's center bounds.
    step_tol = 0.5 * float(np.median(np.diff(x))) if len(x) > 1 else 0.0

    def in_any_window(be: float) -> bool:
        return any((lo - step_tol) <= be <= (hi + step_tol)
                   for lo, hi in all_windows)

    def local_sigma(be: float) -> float:
        mask = (x >= be - local_window_ev) & (x <= be + local_window_ev)
        if mask.sum() > 1:
            return float(np.median(np.sqrt(np.maximum(y[mask], noise_floor))))
        return float(np.sqrt(max(noise_floor, 1.0)))

    def net_height(be: float) -> float:
        return float(ys[int(np.argmin(np.abs(x - be)))])

    # ── channel 1: smoothed local maxima (pool entries; the seeding for
    #    this channel happened upstream in the dominant detector) ─────────
    entries: list[dict] = []
    edge = max(2, smooth_points // 2)
    for i in _smoothed_local_maxima(ys, edge):
        amp = float(ys[i])
        c = float(x[i])
        snr = amp / max(local_sigma(c), 1e-12)
        if snr < POOL_LOCAL_MAX_MIN_SNR:
            continue                       # noise chaff, not pool-worthy
        entries.append({
            "center": c, "prov": {"local_max"}, "amp": amp,
            "frac": amp / global_max if global_max > 0 else 0.0,
            "snr": snr,
            "fwhm": _half_height_fwhm(x, ys, i, fwhm_clip[0]),
            "prom_z": None, "ridge_len": None,
        })

    # ── channel 2: CWT ridges (merge into coincident local-max entries) ──
    for rf in cwt_ridge_features(x, y, prom_z_min=prom_z_min):
        host = min((e for e in entries
                    if abs(e["center"] - rf.center_be) <= coincidence_ev),
                   key=lambda e: abs(e["center"] - rf.center_be),
                   default=None)
        if host is not None:
            host["prov"].add("curvature_shoulder")
            host["prom_z"] = (max(host["prom_z"], rf.prom_z)
                              if host["prom_z"] is not None else rf.prom_z)
            host["ridge_len"] = rf.ridge_length
            host["fwhm"] = rf.fwhm_est_ev   # scale estimate beats the
            continue                        # half-height walk under overlap
        c = rf.center_be
        amp = net_height(c)
        entries.append({
            "center": c, "prov": {"curvature_shoulder"}, "amp": amp,
            "frac": amp / global_max if global_max > 0 else 0.0,
            "snr": amp / max(local_sigma(c), 1e-12),
            "fwhm": rf.fwhm_est_ev,
            "prom_z": rf.prom_z, "ridge_len": rf.ridge_length,
        })

    # ── mark upstream dominant seeds on their pool entries ───────────────
    seeded_centers: list[float] = []
    for seed in dominant_seeds:
        c = float(seed["center_be"])
        host = min((e for e in entries
                    if abs(e["center"] - c) <= coincidence_ev),
                   key=lambda e: abs(e["center"] - c), default=None)
        if host is None:                   # defensive: list it anyway
            host = {"center": c, "prov": {"local_max"},
                    "amp": float(seed.get("amplitude_net", 0.0)),
                    "frac": float(seed.get("fraction_of_max", 0.0)),
                    "snr": float(seed.get("local_snr", 0.0)),
                    "fwhm": float(seed.get("fwhm_init", fwhm_clip[0])),
                    "prom_z": None, "ridge_len": None}
            entries.append(host)
        host["seeded_role"] = str(seed["role"])
        seeded_centers.append(c)

    # ── curvature-channel seeding gates (conservative; every failure is
    #    surfaced so the pool stays honest about why) ─────────────────────
    accepted: list[dict] = []
    eligible = sorted(
        (e for e in entries
         if "curvature_shoulder" in e["prov"] and "seeded_role" not in e),
        key=lambda e: e["amp"], reverse=True)
    n_seeds = len(seeded_centers)
    for e in eligible:
        fails = []
        if in_any_window(e["center"]):
            fails.append("in_grammar_window")
        if any(abs(e["center"] - c) <= coincidence_ev
               for c in seeded_centers):
            fails.append("coincident_with_seed")
        if e["snr"] < amplitude_snr:
            fails.append("below_amplitude_snr")
        if e["frac"] < min_fraction_of_max:
            fails.append("below_fraction_of_max")
        if not fails and n_seeds >= max_total_seeds:
            fails.append("preseed_cap")
        e["gate_fails"] = tuple(fails)
        if fails:
            continue
        e["seeded_role"] = "pending"       # renamed by BE order below
        seeded_centers.append(e["center"])
        n_seeds += 1
        accepted.append(e)

    # stable role naming by ascending BE (matches the F1 convention)
    curvature_seeds_sorted = sorted(accepted, key=lambda e: e["center"])
    seeds_out: list[CurvatureSeed] = []
    for k, e in enumerate(curvature_seeds_sorted):
        role = f"preseed_curvature_{k}"
        e["seeded_role"] = role
        seeds_out.append(CurvatureSeed(
            role=role,
            center_be=float(e["center"]),
            fwhm_init=float(np.clip(e["fwhm"], fwhm_clip[0], fwhm_clip[1])),
            amplitude_net=float(e["amp"]),
            fraction_of_max=float(e["frac"]),
            local_snr=float(e["snr"]),
            prom_z=float(e["prom_z"]),
        ))

    # ── gate bookkeeping for the remaining (unseeded) entries: every
    #    unseeded detection must say WHY (honesty-surface completeness).
    #    For local-max-only entries the seeding decision happened upstream
    #    (the dominant channel); the diagnostics reconstruct which gate the
    #    entry fails, or mark it suppressed_upstream (the dominant
    #    channel's separation/cap rules — the pool cannot re-derive those).
    features: list[PoolFeature] = []
    for e in sorted(entries, key=lambda e: e["center"]):
        in_win = in_any_window(e["center"])
        fails = list(e.get("gate_fails", ()))
        if "seeded_role" not in e and not fails:
            if in_win:
                fails.append("in_grammar_window")
            if e["snr"] < amplitude_snr:
                fails.append("below_amplitude_snr")
            if e["frac"] < min_fraction_of_max:
                fails.append("below_fraction_of_max")
            if not fails:
                fails.append("suppressed_upstream")
        features.append(PoolFeature(
            center_be=float(e["center"]),
            provenance=tuple(sorted(e["prov"])),
            fwhm_est=float(e["fwhm"]) if e.get("fwhm") is not None else None,
            amplitude_net=float(e["amp"]),
            fraction_of_max=float(e["frac"]),
            local_snr=float(e["snr"]),
            prom_z=(float(e["prom_z"]) if e.get("prom_z") is not None
                    else None),
            ridge_length=(int(e["ridge_len"])
                          if e.get("ridge_len") is not None else None),
            in_grammar_window=bool(in_win),
            seeded_role=e.get("seeded_role"),
            gate_fails=tuple(fails),
        ))

    # ── grammar reference entries (species-level labeled windows) ────────
    for label, (lo, hi) in sorted(labeled_windows.items()):
        features.append(PoolFeature(
            center_be=0.5 * (float(lo) + float(hi)),
            provenance=("grammar",),
            in_grammar_window=True,
            window=(float(lo), float(hi)),
            label=str(label),
        ))

    return CandidatePool(
        features=features,
        curvature_seeds=seeds_out,
        sources_run=["local_max", "curvature_shoulder", "grammar"],
        tunables=tunables,
    )
