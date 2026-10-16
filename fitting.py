"""
fitting.py – XPS peak fitting engine using lmfit.

Supported lineshapes
--------------------
  gaussian        – pure Gaussian (amplitude at peak max, FWHM parameterised)
  lorentzian      – pure Lorentzian
  pseudo_voigt_gl – linear GL mix: (1‑η)·G + η·L  (η = Lorentzian fraction)
  asymmetric_gl   – GL mix with independent left/right FWHM
  doniach_sunjic  – metallic asymmetric lineshape
  ds_g            – DS+G: DS core × Gaussian convolution (formerly "la_casaxps")
  la_casaxps      – TRUE CasaXPS LA(α,β,m): asymmetric base Lorentzian + integer-kernel Gauss conv

Backgrounds
-----------
  shirley         – iterative Shirley (Proctor & Sherwood 1982)
  linear          – straight‑line between endpoints
  none            – flat zero

Spin‑orbit constraints are handled via lmfit parameter expressions.
"""

from __future__ import annotations

import copy
import hashlib
import inspect
import json
import logging
import re
import threading
import time
import warnings
from typing import Any

import math
import numpy as np
from lmfit import Model, Parameters
from scipy.integrate import trapezoid
from scipy.optimize import least_squares as _scipy_least_squares


SEED_TAG = "xps-fit-seed-v2"                      # _request_seed's derivation tag (recorded with every fit)
# The version of the NUMERICS: bumped whenever a change can move a fitted number for the same
# request (the background arithmetic, the optimiser path, the certificate, the seed derivation) — and
# ONLY then (owner 2026-10-15): tests/test_numerics_version.py pairs it with a digest of the fitting math
# (tests/fixtures/numerics_manifest.json) and fails on a math change without a bump, or a bump without one.
# Recorded with every fit (owner 2026-10-10). History: "2026-10-09" — background math
# (levels-only averaging, certified backgrounds, full-precision upload, seed v2), deployed then;
# "2026-10-13" — the reported statistics formed from the returned arrays (seal 1a′, V6.6).
NUMERICS_VERSION = "2026-10-13"
# The fields of a software record that DECLARE the numerics a fit was computed with (owner 2026-10-15, consistent
# with Q4): the numerics version, the seed derivation, the numerical libraries (lmfit evaluates linked
# parameters through asteval), the machine architecture, the operating system release and numpy's BLAS backend
# (Apple Accelerate states no version of its own: the OS release names it). A declared compatibility identity,
# not a proof of identical arithmetic. The rest — the git commit, whether the checkout was clean, the
# environment digest — is recorded and shown as INFORMATION only: a seal is confirmed by recomputation,
# whatever commit made it. The identity decides only how a recomputation that DIFFERS reads (verify_fit).
NUMERICS_IDENTITY_KEYS = ("numerics", "seed_derivation", "python", "numpy", "scipy", "lmfit", "asteval",
                          "machine", "os", "blas")
# Declared since 2026-10-15: a record made before lacks them, and so reads as made under other numerics.
_NUMERICS_KEYS_SINCE_2026_10_15 = ("asteval", "machine", "os", "blas")
# The fields every fit response RECORDS (owner 2026-10-10); fit_record() copies them.
RECORD_KEYS = ("fit_method", "random_seed", "seed_source", "background_verdict", "certificate", "software")


def fit_record(res: dict) -> dict:
    """The record of a run_fit response: what computed it (RECORD_KEYS), for any caller that
    re-packages a fit (autofit's least-squares method, /api/analyze)."""
    return {k: res.get(k) for k in RECORD_KEYS}


def _git_state(here):
    """``(commit, dirty)`` of the checkout at ``here``: dirty when a tracked file differs from the
    commit OR an untracked file is present (seal 1a′, V6.7: an untracked module can be imported, so
    a checkout with one is not the commit). ``(None, None)`` when it is not a git checkout."""
    import subprocess
    try:
        commit = subprocess.run(["git", "-C", here, "rev-parse", "HEAD"], capture_output=True, text=True,
                                timeout=10, check=True).stdout.strip() or None
        dirty = bool(subprocess.run(["git", "-C", here, "status", "--porcelain"],
                                    capture_output=True, text=True, timeout=10, check=True).stdout.strip())
    except Exception:                                      # no git, not a checkout: said as null
        return None, None
    return commit, dirty


def _env_sha256():
    """SHA-256 of the installed distributions, one ``name==version`` line each, sorted — the
    environment's identity (seal 1a′, V6.7; a lockfile's, not an execution proof)."""
    import hashlib
    from importlib import metadata
    lines = sorted(f"{d.metadata['Name']}=={d.version}" for d in metadata.distributions())
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _software_identity() -> dict[str, Any]:
    """The code that computes a fit, read ONCE at import — so it names what this worker process
    loaded, not what is on disk later (fit recording, owner 2026-10-10): the git commit of
    this checkout and whether it differed from it (tracked or untracked files, seal 1a′), the
    numerical libraries and the installed environment's digest. Recorded; the verification
    (``/api/verify-fit``) compares it whole with the fit's."""
    import os
    import platform
    from importlib import metadata
    import lmfit
    import scipy
    commit, dirty = _git_state(os.path.dirname(os.path.abspath(__file__)))
    try:
        env = _env_sha256()
    except Exception:
        env = None
    try:
        asteval_v = metadata.version("asteval")
    except Exception:
        asteval_v = "unknown"
    try:
        b = np.show_config(mode="dicts")["Build Dependencies"]["blas"]
        blas = f"{b.get('name', 'unknown')} {b.get('version', 'unknown')}"
    except Exception:
        blas = "unknown"
    return {"git_commit": commit, "git_dirty": dirty, "python": platform.python_version(),
            "numpy": np.__version__, "scipy": scipy.__version__, "lmfit": lmfit.__version__,
            "asteval": asteval_v, "machine": platform.machine() or "unknown",
            "os": f"{platform.system()} {platform.release()}", "blas": blas,
            "numerics": NUMERICS_VERSION, "seed_derivation": SEED_TAG, "env_sha256": env}


def software_failure(sw):
    """None if ``sw`` is a software record as a fit records it, else why not (seal, owner 2026-10-15): an
    object; every numerics field declared since 2026-10-10 a string (the later ones a string when present);
    the information fields of their types — the commit a string or null, the checkout state a flag or
    null, the environment digest a string or null."""
    if not isinstance(sw, dict):
        return "the recorded software is not an object"
    for k in NUMERICS_IDENTITY_KEYS:
        if k in _NUMERICS_KEYS_SINCE_2026_10_15 and k not in sw:
            continue
        if not isinstance(sw.get(k), str):
            return f"the recorded software's {k} is not a text"
    if not (sw.get("git_commit") is None or isinstance(sw.get("git_commit"), str)) or "git_commit" not in sw:
        return "the recorded software's commit is not a text or null"
    if not (sw.get("git_dirty") is None or isinstance(sw.get("git_dirty"), bool)) or "git_dirty" not in sw:
        return "the recorded software's checkout state is not a flag or null"
    if not (sw.get("env_sha256") is None or isinstance(sw.get("env_sha256"), str)) or "env_sha256" not in sw:
        return "the recorded software's environment digest is not a text or null"
    return None


def response_form_failure(O, n):
    """None if ``O`` is of a fit response's FORM — what can be judged without reading its request: the fields and
    their JSON types, the software record, every array ``n`` numbers, each component's fields, parameters and area
    — else why not. A record not of this form is ``mismatch`` whatever numerics made it (owner 2026-10-15; Codex
    rule round 2: checked BEFORE the request is read, so an unreadable request cannot hide it)."""
    if not isinstance(O, dict):
        return "the recorded result is not an object"
    if set(O) != RESPONSE_KEYS:
        extra, missing = sorted(set(O) - RESPONSE_KEYS), sorted(RESPONSE_KEYS - set(O))
        return f"the recorded result's fields differ from a response's (extra {extra}, missing {missing})"
    why = software_failure(O["software"])
    if why:
        return why
    if not isinstance(O["success"], bool) or not isinstance(O["message"], str):
        return "success / message are not a flag and a text"
    if not _typed(O["background_verdict"], _BG_VERDICT_T):
        return "the recorded background verdict is not of a response's form"
    why = _bg_effect_form_failure(O["background_verdict"]["effect"])
    if why:
        return why
    for k, spec in (("starts", ("null", _STARTS_T)), ("required", ("null", _REQUIRED_T)),
                    ("certificate", ("null", _CERTIFICATE_T))):
        if not (_typed(O[k], spec) or (O[k] is not None and _typed(O[k], _NOT_RUN_T) and k != "certificate")):
            return f"{k} is not of a response's form"
    if not _typed(O["statistics"], _STATISTICS_T):
        return "the recorded statistics are not of a response's form"
    if not _is_number(O["charge_shift_applied"]) or not isinstance(O["random_seed"], int) \
            or isinstance(O["random_seed"], bool) or not isinstance(O["fit_method"], str) \
            or not isinstance(O["request_digest"], str) \
            or not isinstance(O["seed_source"], str) or not isinstance(O["background_verdict"], dict):
        return "a recorded field is not of its type"
    nums = lambda v: isinstance(v, list) and len(v) == n and all(_is_number(x) for x in v)   # noqa: E731
    for k in ("energy", "counts", "background_y", "fitted_y", "fitted_sub", "residuals"):
        if not nums(O[k]):
            return f"{k} is not {n} numbers"
    peaks = O["individual_peaks"]
    if not isinstance(peaks, list):
        return "the recorded components are not a list"
    for ip in peaks:
        if not isinstance(ip, dict) or set(ip) != _PEAK_KEYS or not isinstance(ip["params"], dict) \
                or not _typed(ip["support"], _SUPPORT_T) or not nums(ip["y"]) or not _typed(ip["id"], _ID_T) \
                or not isinstance(ip["shape"], str) or "area" not in ip["params"]:
            return "a recorded component's fields differ from a response's"
        for name, rec in ip["params"].items():
            if name == "area":
                if not isinstance(rec, dict) or set(rec) != {"value", "stderr"} or not _is_number(rec["value"]) \
                        or not (rec["stderr"] is None or _is_number(rec["stderr"])):
                    return "a recorded area is not of a response's form"
            elif not isinstance(rec, dict) or set(rec) != _PARAM_KEYS or not _is_number(rec["value"]) \
                    or not (rec["stderr"] is None or _is_number(rec["stderr"])) or not isinstance(rec["vary"], bool) \
                    or not (rec["expr"] is None or isinstance(rec["expr"], str)) \
                    or not (rec["min"] is None or _is_number(rec["min"])) or not (rec["max"] is None or _is_number(rec["max"])):
                return f"{name}: the recorded parameter is not of a response's form"
    return None


# The EXACT structure a fit response has (seal 1d, owner 2026-10-15: /api/compare-fits refuses anything else, before
# comparing). Every rule is what run_fit writes, checked on seal 1b's 328 records: a component's parameters are exactly
# its lineshape's arguments plus `area`; a link is `p<master>_<the same parameter>` — the centre `+ <number>`, the
# amplitude `* <number>` — on a parameter that does not vary, to another component; the scattered starts list every
# component, in order, an alternative's components carrying exactly their own parameters; every number one a float
# represents; every scale a comparison measures against finite (the energy span times the samples, the signal, every
# bound span).
_FLOAT_TEXT = r"[-+0-9.einf]+"                          # a candidate number; it must ALSO be str(float) of a finite float


def _float_spelling(t):
    """t is exactly how the fit writes a finite float into a link (f"{float}") — else False."""
    try:
        f = float(t)
    except ValueError:
        return False
    return math.isfinite(f) and str(f) == t and t != "-0.0"     # the fit folds −0 to 0 before writing


def _representable(v, depth=0):
    if depth > 64:
        return False
    if isinstance(v, dict):
        # an id (and the id a support follows) is a label the fit echoes, never a number it computes with
        return all(_representable(e, depth + 1) for k, e in v.items() if k not in ("id", "follows"))
    if isinstance(v, list):
        return all(_representable(e, depth + 1) for e in v)
    if isinstance(v, int) and not isinstance(v, bool):
        try:
            return float(v) == v                           # an integer a float holds EXACTLY
        except OverflowError:
            return False
    return True


# (shape, parameter, linked?) -> the bounds _make_peak_params always sets; None = either branch (keep in step with it:
# the real-fit tests over every lineshape, link and lock fail if these drift)
_FIXED_BOUNDS = {
    ("pseudo_voigt_gl", "gl_ratio", None): (0.0, 1.0), ("asymmetric_gl", "gl_ratio", None): (0.0, 1.0),
    ("doniach_sunjic", "alpha", None): (0.0, 0.5),
    ("doniach_sunjic", "gamma_asym", False): (0.0, 5.0), ("doniach_sunjic", "gamma_asym", True): (0.0, 1.0),
    ("ds_g", "alpha", None): (0.0, 0.49), ("ds_g", "beta", None): (0.05, 2.0),
    ("ds_g", "m_gauss", False): (0.05, 4.0), ("ds_g", "m_gauss", True): (0.0, 4.0),
    ("la_casaxps", "alpha", None): (0.1, 5.0), ("la_casaxps", "beta", None): (0.1, 5.0), ("la_casaxps", "m", None): (0.0, 499.0),
}


def response_structure_failure(O):
    """None if ``O`` has exactly the structure a fit response has (the rules above), else why not, in plain words."""
    if not isinstance(O, dict) or not isinstance(O.get("energy"), list) or not O["energy"]:
        return "it is not a fit response with energies"
    why = response_form_failure(O, len(O["energy"]))
    if why:
        return why
    if not _representable(O):
        return "it holds a number no float represents (or is nested too deeply)"
    sw = O["software"]
    allowed = set(SOFTWARE) | set(_NUMERICS_KEYS_SINCE_2026_10_15)
    if not set(sw) <= allowed:
        return "the recorded software holds a field no server records"
    peaks = O["individual_peaks"]
    if not peaks:
        return "it has no components (a fit has at least one)"
    # an id is one the server accepts: it builds every parameter name as f"p{id}_<name>", which must be an identifier
    ids = [f"{ip['id']}" for ip in peaks]
    if any(_id_failure(ip["id"]) for ip in peaks):
        return "a component id is not one a fit can have"
    if len(set(ids)) != len(ids) or len({ip["id"] for ip in peaks}) != len(peaks):    # by spelling AND by value
        return "two components share an id"
    by_id = {f"{ip['id']}": ip for ip in peaks}
    for ip in peaks:
        func = _SHAPE_FUNCS.get(ip["shape"])
        if func is None:
            return f"a component's lineshape ({str(ip['shape'])[:30]}) is not one a fit has"
        want = set(list(inspect.signature(func).parameters)[1:]) | {"area"}
        if set(ip["params"]) != want:
            return f"component {str(ip['id'])[:20]}: its parameters are not those of a {ip['shape']} component"
    # links, as the fit writes a component linked to a master M (_make_peak_params): its centre `p<M>_center + <number>`,
    # its amplitude `p<M>_amplitude * <number>` (the numbers spelt as the fit writes a float, −0 folded to 0), and every
    # other parameter either ALL `p<M>_<the same name>` or none (one flag, fix_fwhm); M a different component of the same
    # lineshape. An unlinked component has no expression at all.
    master, parent = {}, {}
    for ip in peaks:
        me = f"{ip['id']}"
        exprs = {name: rec["expr"] for name, rec in ip["params"].items() if name != "area" and rec["expr"] is not None}
        if not exprs:
            continue
        if any(ip["params"][name]["vary"] for name in exprs):
            return f"component {me[:20]}: a linked parameter varies"
        if any(ip["params"][name]["min"] is not None or ip["params"][name]["max"] is not None for name in exprs):
            return f"component {me[:20]}: a linked parameter carries bounds (a fit leaves it unbounded)"
        m_found = []
        for mid in ids:
            if mid == me or by_id[mid]["shape"] != ip["shape"] or by_id[mid]["id"] is None:   # constrain_to null = unlinked
                continue
            c = re.fullmatch(re.escape(f"p{mid}_center") + r" \+ (" + _FLOAT_TEXT + ")", exprs.get("center") or "")
            a = re.fullmatch(re.escape(f"p{mid}_amplitude") + r" \* (" + _FLOAT_TEXT + ")", exprs.get("amplitude") or "")
            if c and a and _float_spelling(c.group(1)) and _float_spelling(a.group(1)):
                m_found.append(mid)
        if len(m_found) != 1:
            return f"component {me[:20]}: its links are not as a fit writes them"
        mid = m_found[0]
        rest = [name for name in ip["params"] if name not in ("area", "center", "amplitude")]
        linked = [name for name in rest if name in exprs]
        if linked and (len(linked) != len(rest) or any(exprs[name] != f"p{mid}_{name}" for name in rest)):
            return f"component {me[:20]}: its links are not as a fit writes them"
        if not linked and not all(ip["params"][name]["vary"] for name in rest):    # the linked branch holds none
            return f"component {me[:20]}: a linked component's own shape parameter is held (a fit lets it vary)"
        parent[me] = mid
        for name in exprs:
            master[(me, name)] = (mid, name)
    # support: a linked component FOLLOWS its root ancestor (its id, its verdict); an unlinked one follows nothing
    def root_of(cid):
        seen = set()
        while cid in parent and cid not in seen:
            seen.add(cid)
            cid = parent[cid]
        return cid
    for ip in peaks:
        me, sup = f"{ip['id']}", ip["support"]
        if me in parent:
            root = by_id[root_of(me)]
            if "follows" not in sup or not _same(sup["follows"], root["id"]) or sup["supported"] != root["support"]["supported"]:
                return f"component {me[:20]}: its support does not follow its root component as a fit writes it"
        elif "follows" in sup:
            return f"component {me[:20]}: an unlinked component's support follows another"
    # every parameter as lmfit holds it (Codex round 15): a bound is finite (the fit writes an infinite one as null),
    # min < max (lmfit swaps reversed bounds and refuses equal ones), the value inside them (lmfit clips it); a linked
    # parameter has none (above)
    for ip in peaks:
        for name, rec in ip["params"].items():
            if name == "area" or rec["expr"] is not None:
                continue
            lo, hi, v = rec["min"], rec["max"], rec["value"]
            if any(b is not None and not math.isfinite(b) for b in (lo, hi)) or (lo is not None and hi is not None and not lo < hi) \
                    or (lo is not None and v < lo) or (hi is not None and v > hi):
                return f"component {str(ip['id'])[:20]}: its {name} is not inside bounds a fit can write"
    if O["fit_method"] not in _FIT_METHODS or O["seed_source"] not in ("caller", "request"):
        return "the recorded method or seed source is not one a fit writes"
    # the bounds _make_peak_params gives a shape parameter whatever the request says (the others are the request's):
    # a free parameter carries them exactly, a held one the same widened to its held value (_set), a linked one none
    for ip in peaks:
        me = f"{ip['id']}"
        for name, rec in ip["params"].items():
            fixed = _FIXED_BOUNDS.get((ip["shape"], name, me in parent)) or _FIXED_BOUNDS.get((ip["shape"], name, None))
            if fixed is None or rec["expr"] is not None:
                continue
            lo, hi = fixed
            if not rec["vary"]:
                lo, hi = min(lo, rec["value"]), max(hi, rec["value"])
            if rec["min"] != lo or rec["max"] != hi:
                return f"component {me[:20]}: its {name} bounds are not the ones a fit gives a {ip['shape']} component"
    import sys
    limit = sys.getrecursionlimit() // 4
    for start in master:
        cur, seen = start, {start}
        while cur in master:
            cur = master[cur]
            if cur in seen:
                return "the links form a cycle"
            seen.add(cur)
            if len(seen) > limit:
                return "a chain of links is deeper than a comparison follows"
    # the scattered starts: every component, in order; an alternative's components carry exactly their own parameters
    st = O["starts"]
    if isinstance(st, dict) and st.get("ran"):
        same_ids = lambda cs: len(cs) == len(peaks) and all(type(c["id"]) is type(ip["id"]) and c["id"] == ip["id"]
                                                            for c, ip in zip(cs, peaks))     # the id itself, copied
        if not same_ids(st["fit"]["components"]):
            return "the scattered starts do not list the fit's components in order"
        own = {f"{ip['id']}": set(ip["params"]) - {"area"} for ip in peaks}
        for alt in st["alternatives"]:
            if not same_ids(alt["components"]):
                return "a scattered-start alternative does not list the fit's components in order"
            for c in alt["components"]:
                if set(c["params"]) != own[f"{c['id']}"]:
                    return f"a scattered-start alternative's component {str(c['id'])[:20]} does not carry its own parameters"
    # every scale a comparison measures against: finite
    with np.errstate(over="ignore", invalid="ignore"):
        x = np.asarray(O["energy"], float)
        counts, bg = np.asarray(O["counts"], float), np.asarray(O["background_y"], float)
        both = np.isfinite(counts) & np.isfinite(bg)
        net = counts[both] - bg[both]                       # a fit's background-subtracted signal is finite
        if not np.isfinite(np.ptp(x) * len(x)) or not np.isfinite(net).all():
            return "its energy span or signal overflows a comparison's arithmetic"
        for ip in peaks:
            for name, rec in ip["params"].items():
                if name != "area" and rec["min"] is not None and rec["max"] is not None \
                        and not np.isfinite(np.float64(rec["max"]) - np.float64(rec["min"])):
                    return f"component {str(ip['id'])[:20]}: a bound span ({name}) overflows a comparison's arithmetic"
    return None


def numerics_difference(sw):
    """The numerics fields in which the software record ``sw`` differs from this server's (a field it does not
    declare differs), as text; [] when the same numerics made it."""
    return [f"{k} {sw.get(k, '(not recorded)')} (here {SOFTWARE.get(k)})"
            for k in NUMERICS_IDENTITY_KEYS if sw.get(k) != SOFTWARE.get(k)]


SOFTWARE = _software_identity()

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Lineshape functions (all FWHM‑parameterised, amplitude = peak maximum)
# ─────────────────────────────────────────────────────────────────────────────

_LN2 = np.log(2.0)
_SQRT_PI_4LN2 = np.sqrt(np.pi / (4.0 * _LN2))  # ≈ 1.06447


def _gaussian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    """Gaussian; amplitude is the peak maximum value."""
    return amplitude * np.exp(-4.0 * _LN2 * ((x - center) / fwhm) ** 2)


def _lorentzian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    """Lorentzian; amplitude is the peak maximum value."""
    hwhm = fwhm / 2.0
    return amplitude * hwhm ** 2 / ((x - center) ** 2 + hwhm ** 2)


def _pseudo_voigt_gl(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    gl_ratio: float,
) -> np.ndarray:
    """
    Pseudo‑Voigt as a linear combination of Gaussian and Lorentzian.

    gl_ratio : Lorentzian fraction  (0 = pure Gaussian, 1 = pure Lorentzian)
    """
    eta = float(np.clip(gl_ratio, 0.0, 1.0))
    return (1.0 - eta) * _gaussian(x, amplitude, center, fwhm) + eta * _lorentzian(
        x, amplitude, center, fwhm
    )


def _asymmetric_gl(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    asymmetry: float,
    gl_ratio: float,
) -> np.ndarray:
    """
    Asymmetric GL pseudo‑Voigt with independent asymmetry parameter.

    fwhm      : base FWHM (used on the low‑BE side, i.e. x ≤ center)
    asymmetry : broadening factor for the high‑BE side;
                fwhm_right = fwhm × (1 + asymmetry).  0 = symmetric.
    gl_ratio  : common Lorentzian fraction for both sides.

    Both halves meet at x = center with value = amplitude.
    """
    asym = float(np.clip(asymmetry, 0.0, 1.0))
    fwhm_r = fwhm * (1.0 + asym)
    result = np.empty_like(x, dtype=float)
    left = x <= center
    result[left] = _pseudo_voigt_gl(x[left], amplitude, center, fwhm, gl_ratio)
    result[~left] = _pseudo_voigt_gl(x[~left], amplitude, center, fwhm_r, gl_ratio)
    return result


def _doniach_sunjic(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    alpha: float,
    gamma_asym: float = 0.0,
) -> np.ndarray:
    """
    Doniach‑Sunjic lineshape for metallic core‑level spectra.

      DS(x) = A · N · cos(πα/2 + (1‑α)·arctan((c‑x)/γ))
                    ─────────────────────────────────────────
                         ((c‑x)² + γ²)^((1‑α)/2)
              × exp(−gamma_asym · max(0, x−c))

    where γ = fwhm/2,  N = γ^(1‑α)/cos(πα/2)  so that DS(c) = A.
    dx = c − x so the power-law tail extends toward HIGHER BE (inelastic losses).
    gamma_asym > 0 adds an exponential envelope that limits how far the
    high-BE tail extends (0 = pure DS power-law tail, no limit).

    alpha     : asymmetry index  (0 = symmetric Lorentzian, typical 0–0.3)
    gamma_asym: exponential tail-decay rate (eV⁻¹).  0 = standard DS.
    """
    alpha      = float(np.clip(alpha, 0.0, 0.995))
    gamma_asym = max(float(gamma_asym), 0.0)
    gamma      = max(fwhm / 2.0, 1e-12)
    cos0 = np.cos(np.pi * alpha / 2.0)
    if abs(cos0) < 1e-12:
        cos0 = 1e-12
    norm = gamma ** (1.0 - alpha) / cos0
    # dx = center − x  →  positive on LOW-BE side, negative on HIGH-BE side.
    # The arctan and power-law terms produce a tail toward HIGH-BE (dx < 0).
    dx = center - x
    phase = np.pi * alpha / 2.0 + (1.0 - alpha) * np.arctan(dx / gamma)
    denom = (dx ** 2 + gamma ** 2) ** ((1.0 - alpha) / 2.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = amplitude * norm * np.cos(phase) / denom
    # Exponential envelope to gently limit the HIGH-BE tail extent.
    # dx = center - x: negative on the HIGH-BE side (x > center).
    # We want: decay = 1 at center, tapering toward zero far into the tail.
    # Use |dx| on the high-BE side only: exp(-gamma_asym * max(x - center, 0))
    if gamma_asym > 0.0:
        tail_decay = np.exp(-gamma_asym * np.maximum(x - center, 0.0))
        result = result * tail_decay
    result = np.where(np.isfinite(result), result, 0.0)
    return result


def _ds_g_dscore_gauss(
    x: np.ndarray,
    amplitude: float,
    center: float,
    alpha: float,    # CasaXPS: dimensionless asymmetry index, 0 ≤ α < 0.5
    beta: float,     # CasaXPS: Lorentzian half-width (eV)
    m_gauss: float,  # CasaXPS: Gaussian FWHM (eV) for convolution
) -> np.ndarray:
    """
    DS+G lineshape (formerly mislabeled "LA(α,β,m) [CasaXPS]") —
    Doniach-Šunjić asymmetric core convolved analytically with a Gaussian
    instrument-broadening kernel. NOT to be confused with the true CasaXPS
    LA shape (see _la_casaxps_true), which uses a piecewise-asymmetric
    Lorentzian with point-domain Gaussian convolution.

    The DS core with asymmetry index α and Lorentzian half-width β is convolved
    with a Gaussian of FWHM m for instrument broadening.

    Tail direction: eps = x − center > 0 → HIGHER binding energy (physically
    correct: low-energy electron-hole pair excitations produce intensity on the
    high-BE side only).

    Parameters
    ----------
    alpha   : dimensionless asymmetry index, 0 ≤ α < 0.5
              (0 = symmetric Lorentzian, ~0.1–0.3 for metallic systems)
    beta    : Lorentzian half-width at half-maximum (eV); controls core width
    m_gauss : Gaussian FWHM (eV) for instrument/phonon broadening (0 = none)

    Fixes (v2)
    ----------
    1. Convolution uses a padded grid (±10·m on each side) with cosine taper
       to eliminate cliff artifacts at array boundaries.
    2. Explicit FFT convolution with a properly normalised Gaussian kernel,
       so DS tail direction is preserved regardless of m value.
    """
    alpha   = float(np.clip(alpha, 0.0, 0.495))
    beta    = max(float(beta),    1e-6)
    m_gauss = max(float(m_gauss), 0.0)

    # ── DS core evaluator (independent of m_gauss) ───────────────────────────
    #
    # eps = x − center: positive on HIGH-BE side (where tail belongs)
    # DS formula:  cos(πα/2 − (1−α)·arctan2(ε, β)) / (ε² + β²)^((1−α)/2)
    #
    # Sign convention proof:
    #   At ε >> β (high BE):  arctan2(ε, β) → +π/2
    #     phase → πα/2 − (1−α)·π/2 → −π(1−2α)/2  (negative for α < 0.5)
    #     cos(phase) > 0, and denominator grows as |ε|^(1−α)
    #     → slow power-law decay toward HIGH BE  ✓
    #   At ε << −β (low BE): arctan2(ε, β) → −π/2
    #     phase → πα/2 + (1−α)·π/2 → π/2  (for small α)
    #     cos(phase) → 0, faster falloff
    #     → steeper decay toward LOW BE  ✓

    def _ds_core(xgrid):
        """Evaluate DS kernel on arbitrary grid. Independent of m_gauss."""
        eps = xgrid - center
        r2 = eps ** 2 + beta ** 2
        r2 = np.maximum(r2, 1e-30)
        rPow = r2 ** ((1.0 - alpha) / 2.0)
        phase = np.pi * alpha / 2.0 - (1.0 - alpha) * np.arctan2(eps, beta)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            core = np.cos(phase) / rPow
        core = np.where(np.isfinite(core), core, 0.0)
        return core

    # ── No Gaussian broadening — just return normalised DS core ──────────────
    if m_gauss < 0.001:
        ds_core = _ds_core(x)
        peak_val = float(np.interp(center, x if x[-1] > x[0] else x[::-1],
                                   ds_core if x[-1] > x[0] else ds_core[::-1]))
        if peak_val <= 0.0:
            peak_val = np.max(np.abs(ds_core))
        if peak_val <= 0.0:
            return np.zeros_like(x)
        return amplitude * ds_core / peak_val

    # ── Build padded grid for convolution ─────────────────────────────────────
    # Pad by ±10·m_gauss (≈ ±4.25σ) to avoid truncation artifacts.
    # The DS power-law tail decays as |ε|^(α−1), which is slow for small α,
    # so generous padding is essential.
    step = float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 0.05
    step = max(step, 1e-6)

    pad_ev = max(10.0 * m_gauss, 20.0 * beta)  # eV of padding on each side
    n_pad = int(np.ceil(pad_ev / step))
    n_pad = max(n_pad, 1)

    # Determine sort direction of input x
    ascending = (x[-1] > x[0]) if len(x) > 1 else True

    # Create padded energy grid extending beyond the data range
    if ascending:
        x_pad_lo = x[0] - n_pad * step
        x_pad_hi = x[-1] + n_pad * step
    else:
        x_pad_lo = x[-1] - n_pad * step
        x_pad_hi = x[0] + n_pad * step

    n_total = len(x) + 2 * n_pad
    x_padded = np.linspace(x_pad_lo, x_pad_hi, n_total)  # always ascending

    # Evaluate DS core on padded grid
    ds_padded = _ds_core(x_padded)

    # ── Cosine taper on pad regions ───────────────────────────────────────────
    # Smoothly ramp to zero at the array edges to kill any residual signal
    # that would cause Gibbs-like ringing in FFT convolution.
    taper = np.ones(n_total)
    if n_pad > 1:
        # Left taper: 0→1 over n_pad points (half cosine)
        taper[:n_pad] = 0.5 * (1.0 - np.cos(np.linspace(0, np.pi, n_pad)))
        # Right taper: 1→0 over n_pad points
        taper[-n_pad:] = 0.5 * (1.0 + np.cos(np.linspace(0, np.pi, n_pad)))
    ds_padded *= taper

    # ── FFT convolution with Gaussian kernel ──────────────────────────────────
    # σ_eV = m_gauss / (2√(2·ln2))  (convert FWHM to sigma)
    sigma_ev = m_gauss / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    # Kernel grid centred at zero, same length as padded array (for FFT)
    n_k = len(x_padded)
    k_half = (n_k - 1) / 2.0
    k_grid = (np.arange(n_k) - k_half) * step  # eV relative to centre
    gauss_kernel = np.exp(-0.5 * (k_grid / sigma_ev) ** 2)
    gauss_kernel /= gauss_kernel.sum()  # normalise to unit area

    # FFT convolution (circular, but padding makes edge effects negligible)
    ft_ds = np.fft.rfft(ds_padded)
    ft_gk = np.fft.rfft(np.fft.ifftshift(gauss_kernel))
    ds_conv = np.fft.irfft(ft_ds * ft_gk, n=n_total)

    # ── Interpolate back to original x grid ───────────────────────────────────
    # x_padded is always ascending; np.interp handles arbitrary query points.
    result = np.interp(x, x_padded, ds_conv)

    # ── Normalise so value at x = center equals amplitude ─────────────────────
    if center < x_padded[0] or center > x_padded[-1]:
        # NEW GUARDED BRANCH (2026-09-25, unit fix-dsg-page-evaluator): the
        # centre lies OUTSIDE the padded grid, so "the value at the centre"
        # is np.interp's clamped end value — the tail of a curve whose peak
        # is not on the grid, of order 1e-20 once the tapers have acted, and
        # its SIGN decided which of two unrelated curves came back (the
        # max-normalised tail, or that tail divided by ~1e-20; Codex round 2
        # of the unit). Normalise by the curve's maximum instead. A centre
        # inside the padded grid takes the branch below, unchanged.
        peak_val = float(np.max(np.abs(result)))
        if peak_val <= 0.0:
            return np.zeros_like(x)
    else:
        # Interpolate at exact center rather than nearest grid point to avoid
        # normalization error when center falls between data points.
        peak_val = float(np.interp(center, x_padded, ds_conv))
        if peak_val <= 0.0:
            peak_val = np.max(np.abs(result))
        if peak_val <= 0.0:
            return np.zeros_like(x)

    result = amplitude * result / peak_val

    # Final safety: suppress any NaN/Inf
    return np.where(np.isfinite(result), result, 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Background functions
# ─────────────────────────────────────────────────────────────────────────────

def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
    """Return a copy of *y* with the first/last *n_avg* points replaced by their mean.

    No production caller since 2026-10-01: endpoint averaging sets the edge
    LEVELS only (_edge_levels). Kept for the tests and scripts that reproduce
    the old reading (background-math findings F1)."""
    n = len(y)
    if n_avg <= 1 or n < 4:
        return y.copy()
    cap = min(n_avg, n // 4)
    if cap < 1:
        return y.copy()
    out = y.copy()
    out[:cap] = np.mean(y[:cap])
    out[-cap:] = np.mean(y[-cap:])
    return out


# ── Backgrounds: one reading of endpoint averaging, one relative stop, a certificate ──
#
# Endpoint averaging sets the two EDGE LEVELS only (owner, 2026-10-01; findings
# F1): b_low / b_high are the means of the first / last k = min(n_avg, n // 4)
# points (k = 1 below 4 points); every integral and every B <= I constraint
# reads the RAW data. Every iterative background stops when one more step
# changes it by at most BG_REL_TOL of the window's intensity span (findings F5:
# relative, not in intensity units) and returns the point that step was taken
# FROM — the point whose residual against its statement was just measured.
# background_certificate() checks each result against its defining statement;
# compute_background() raises BackgroundNotConverged on a failure (findings
# F10, F11, F12), and nothing downstream uses such a background.

BG_REL_TOL = 1e-12
"""Stop and certificate tolerance of every iterative background, as a fraction
of the window's intensity span (max - min of the raw data). Measured on the 121
committed spectra: every Shirley iteration reaches it within 19 steps (cap
200); the residual floor the iteration reaches is <= 1.3e-16 of the span."""


class BackgroundNotConverged(ValueError):
    """A background that does not satisfy its defining statement: the iteration
    cycled or ran out of steps, the Shirley relation is undefined (no net
    signal), or Tougaard's anchor leaves its amplitude undetermined or has no
    solution. The message is meant for the user."""


def _edge_levels(ys: np.ndarray, n_avg: int) -> tuple[float, float]:
    """(level at index 0, level at index -1): the means of the first / last
    k = min(n_avg, n // 4) points, k >= 1 (1 below four points)."""
    n = len(ys)
    k = max(1, min(int(n_avg), n // 4)) if n >= 4 else 1
    return float(np.mean(ys[:k])), float(np.mean(ys[-k:]))


def _ascending(x, y):
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    if xa[0] > xa[-1]:
        return xa[::-1].copy(), ya[::-1].copy(), True
    return xa.copy(), ya.copy(), False


def _cum_from_high(xs: np.ndarray, s: np.ndarray) -> np.ndarray:
    """Trapezoid integral of s from each point to the high-x end (ascending xs)."""
    n = len(s)
    cum_right = np.zeros(n)
    for i in range(n - 2, -1, -1):
        cum_right[i] = cum_right[i + 1] + 0.5 * (s[i] + s[i + 1]) * (xs[i + 1] - xs[i])
    return cum_right


def _shirley_map(xs, ys, B, b_low, b_high):
    """T(B) on an ascending grid: b_high + (b_low - b_high) * (integral of
    max(I - B, 0) from E to E_max) / (the whole integral) — the Shirley
    relation's right-hand side. None where it is undefined (unequal edge
    levels and no positive net signal); the flat level when the levels are
    equal (a zero step)."""
    if b_low == b_high:
        return np.full(len(ys), b_low)
    cum_right = _cum_from_high(xs, np.maximum(ys - B, 0.0))
    total = cum_right[0]
    if not total > 0.0:
        return None
    return b_high + (b_low - b_high) * cum_right / total


def shirley_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = BG_REL_TOL,
    n_avg: int = 1,
) -> np.ndarray:
    """Shirley background: the solution of the Shirley integral relation.

    DEFINING STATEMENT. On the window [E_min, E_max] the background B satisfies

        B(E) = b_low + (b_high - b_low) * INT_{E_min}^{E} s dE' / INT_{E_min}^{E_max} s dE',
        s = max(I - B, 0),

    with I the MEASURED data and b_low, b_high the intensity levels at the low-
    and high-BE edges — the means of the first / last k = min(``n_avg``, n // 4)
    points (k >= 1): endpoint averaging sets the levels only, so one noisy end
    sample does not set a whole edge level (audit F3, 2026-07-17), and the
    integral reads the raw data (owner, 2026-10-01; until then this function
    replaced the end bands of the DATA by their means and integrated that
    modified spectrum — findings F1). The background rises above the low-BE level
    in proportion to the net (no-loss) intensity already accumulated at LOWER
    binding energy, reaching the high-BE level at the far edge. Discretised by
    the trapezoid rule on the data's grid (either BE order).

    SOLVED by fixed-point iteration from the straight line between the levels
    until one more step changes it by at most ``tol`` (BG_REL_TOL) of the
    window's intensity span — relative, not in intensity units (findings F5) —
    at most ``n_iter`` steps; the point returned is the one that step was taken
    FROM. compute_background() certifies it against the relation
    (background_certificate) and raises BackgroundNotConverged when it fails:
    the iteration can alternate between two curves forever on some small
    positive spectra (14 % of the span on E = 0..3, I = [2, 3, 10, 13], where an
    exact solution [2, z, z + 5.5, 13], z = (17 - sqrt(37)) / 4, exists —
    findings F12), and when the data lie at or below the edge line there is no
    net signal and the relation is undefined (findings F10). The relation can
    have MORE THAN ONE solution (findings F9); a certified result is the one
    reached from the line. Every committed spectrum is certified within 19 steps.

    ASSUMPTIONS, and when they fail:
      * each no-loss electron at lower BE adds the same, energy-independent step
        to the background at every higher BE in the window (a constant loss
        probability, all losses inside the window). Fails for structured losses
        (plasmons, shake-up) and for windows wide enough that the loss function
        varies across them — a loss cross-section (tougaard_background) models that.
      * both edges lie where the net signal is zero, so B meets the edge levels.
        Fails when the window cuts through a peak tail: the edge level then
        includes signal and the step is mis-sized.
      * only positive net intensity scatters (s = max(I - B, 0)); B itself is NOT
        required to stay below the data — it rises above it (mostly at noise
        dips) on 116 of the 121 committed spectra, by up to 6 % of the span. For
        B <= I see smart_background.

    NOISE (findings F2): on noisy data the Shirley estimate of net area carries
    its own bias at large background steps — +2.3 % (+- 0.2) in a Poisson Monte
    Carlo at a step of 4000 counts under a 20 000-count line, not resolved at a
    step of 400.

    Corroboration (not the defence): D. A. Shirley, Phys. Rev. B 5, 4709 (1972);
    the iterative form: A. Proctor and P. M. A. Sherwood, Anal. Chem. 54, 13 (1982).
    """
    if len(x) < 2:
        return np.zeros_like(y)
    xs, ys, flipped = _ascending(x, y)
    b_low, b_high = _edge_levels(ys, n_avg)        # the levels only; the integral reads the raw data
    stop = tol * float(np.max(ys) - np.min(ys))
    B = np.linspace(b_low, b_high, len(ys))        # linear initial guess
    for _ in range(n_iter):
        Bn = _shirley_map(xs, ys, B, b_low, b_high)
        if Bn is None:                             # undefined: no net signal (certificate: not converged)
            break
        if np.max(np.abs(Bn - B)) <= stop:         # B's residual against the relation is within the stop
            break
        B = Bn
    return B[::-1] if flipped else B


def smart_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = BG_REL_TOL,
    n_avg: int = 1,
) -> np.ndarray:
    """Constrained Shirley background: the solution of B = min(T(B), I).

    DEFINING STATEMENT. At every point of the window either the Shirley relation
    holds and the background is at or below the data, or the constraint B = I is
    active where the relation would put it above:

        B = min(T(B), I),   T(B) = the right-hand side of shirley_background's relation.

    Justification of B <= I: the net (no-loss) intensity is a non-negative count rate.

    WHY A CLAMP OF THE SHIRLEY SOLUTION SOLVES IT (not a truncation of a
    different problem): shirley_background integrates s = max(I - B, 0), and
    s(min(B, I)) = s(B) — clamping changes the background only where the net
    signal is already zero. So T(min(B, I)) = T(B) = B: the clamp of a solution
    of the Shirley relation is a solution of the constrained problem (a
    correspondence between solutions; neither problem need have only one).
    It holds because the integrand and the clamp read the SAME data at every
    endpoint averaging: averaging sets only the two edge levels (owner,
    2026-10-01 — until then the integrand read end-averaged data and the clamp
    the raw data, and at n_avg > 1 the result solved neither reading, findings
    F1). The clamp is exact in floating point (I - min(B, I) is 0 where it
    clamps), so a certified Shirley solution gives a certified constrained one.
    When the Shirley iteration does not converge (findings F10, F12) neither
    does this: compute_background() raises BackgroundNotConverged.

    ASSUMPTIONS: those of shirley_background, plus B <= I POINTWISE ON THE
    MEASURED COUNTS. Net intensity is non-negative in EXPECTATION; measured counts
    scatter below the background, so the constraint binds on noise dips and
    pulls B down.

    NOISE, PLAINLY (findings F2): the smart methods constrain against noisy
    counts, which raises net area by about 1 % on noisy data — in a Poisson Monte
    Carlo against a background that satisfies the relation exactly, +0.90 %
    (+- 0.02) at one step size, +1.28 % (+- 0.04) at a ten times larger one and
    +0.83 % (+- 0.01) there with endpoint averaging 10. Plain Shirley carries its
    own bias at large steps (+2.3 % there; not resolved at the small step).
    """
    if len(x) < 2:
        return np.zeros_like(y)
    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
    return np.minimum(shir, np.asarray(y, dtype=float))


def linear_background(x: np.ndarray, y: np.ndarray, n_avg: int = 1) -> np.ndarray:
    """Linear background: the affine function of energy through the two edge LEVELS,

        B(E) = J_first + (J_last - J_first) (E - E_first) / (E_last - E_first),

    J_first / J_last the means of the window's first / last k points (k = min(n_avg,
    n // 4), k >= 1 — the levels every method reads; owner 2026-10-03: it used the raw
    end points, so one noisy end sample tilted the whole line). ASSUMPTIONS: the
    background varies linearly across the window and no loss intensity builds up under
    the peaks (no inelastic step) — reasonable for a narrow window around small peaks,
    not for a core level whose loss tail raises the high-BE side; both edges lie on
    background. Evaluated exactly (tests/test_background_defining_statements.py).
    When the two end energies are equal the line is the flat I_first if the two
    end intensities are equal too; otherwise NO line passes through both end
    points and BackgroundNotConverged is raised (Codex impl round 4: the flat
    I_first used to be returned and fitted against).
    """
    if len(x) == 0:
        return np.zeros(0)        # an empty window: an empty curve, as the page (round 8)
    lo, hi = _exact_edge_levels(y, n_avg)
    return _line_through(x, x[0], lo, x[-1], hi, _span(y))


def _exact_edge_levels(y, n_avg=1):
    """The two edge LEVELS of the window as exact rationals: the means of its first and
    last k points (_avg_k) — what endpoint averaging sets for every method (owner
    2026-10-03: linear reads it too)."""
    from fractions import Fraction
    ys = np.asarray(y, dtype=float).tolist()
    k = _avg_k(len(ys), n_avg)
    if not all(math.isfinite(v) for v in ys[:k] + ys[-k:]):
        return float("nan"), float("nan")            # refused by _line_through as not finite
    return sum(map(Fraction, ys[:k])) / k, sum(map(Fraction, ys[-k:])) / k


def _span(y):
    """The window's intensity span EXACTLY (a Fraction: max - min of two doubles can
    overflow in float), for the explicit curves' precision check."""
    from fractions import Fraction
    y = np.asarray(y, dtype=float)
    return Fraction(float(np.max(y))) - Fraction(float(np.min(y))) if len(y) else Fraction(0)


def _precision_words(label):
    return (f"{label} background not converged: its exact values cannot be represented within "
            "the certificate's precision at this span (the data exceed what double precision "
            "resolves).")


def _explicit_background(bg, label):
    """An EXPLICIT background (linear, manual) has nothing to converge, but it must
    exist (Codex impl round 5): every value a finite number — the arithmetic can
    overflow on finite inputs (a slope over a 1e-309 eV window, intensities near
    1e308). Raises BackgroundNotConverged otherwise. The page's twin is the
    finiteness check in computeBackgroundCore, with the same words."""
    bg = np.asarray(bg, dtype=float)
    if not np.all(np.isfinite(bg)):
        raise BackgroundNotConverged(
            f"{label} background not converged: it is not a finite number at every point "
            "(the arithmetic overflowed or an input is not finite).")
    return bg


def _line_through(x, x0, y0, x1, y1, span=None):
    """The affine function of energy through (x0, y0) and (x1, y1), evaluated on x
    EXACTLY — (y0 (x1 - v) + y1 (v - x0)) / (x1 - x0) in Fraction arithmetic, rounded
    once to the nearest double (half to even), as the manual curve (Codex impl round
    11: y0 + slope (v - x0) cancelled to a finite, wrong 0 beside a 1e20 end point; the
    page's twin is _bgExactLine). Raises BackgroundNotConverged when x0 == x1 and y0 !=
    y1 (no such line) or when a value is not finite (an extrapolation past the largest
    double). The rounding of each exact value to a double is itself an error: it must
    meet the certificate's predicate, BG_REL_TOL x `span` (the span of the data the
    curve is judged against), exactly, or the background is refused (Codex impl round
    16: a line at 1e12 counts over a span of 1 rounds by 4e-5)."""
    from fractions import Fraction
    x0, x1 = float(x0), float(x1)
    xv = np.asarray(x, dtype=float)
    # the levels: exact means (Fractions, linear_background / run_fit) or doubles
    if not (math.isfinite(x0) and math.isfinite(x1)) or not all(
            isinstance(v, Fraction) or math.isfinite(float(v)) for v in (y0, y1)):
        return _explicit_background(np.full(len(xv), np.nan), "Linear")   # raises: not finite
    Y0 = y0 if isinstance(y0, Fraction) else Fraction(float(y0))
    Y1 = y1 if isinstance(y1, Fraction) else Fraction(float(y1))
    tol = None if span is None else Fraction(BG_REL_TOL) * Fraction(span)
    if x1 == x0:
        if Y1 != Y0:
            raise BackgroundNotConverged(
                "Linear background not converged: its two end points are at the same energy "
                "with different intensities, so no line passes through both.")
        flat = float(Y0)
        if tol is not None and abs(Fraction(flat) - Y0) > tol:
            raise BackgroundNotConverged(_precision_words("Linear"))
        return _explicit_background(np.where(np.isfinite(xv), flat, np.nan), "Linear")
    X0, X1 = Fraction(x0), Fraction(x1)
    D = X1 - X0
    out = np.empty(len(xv))
    for i, v in enumerate(xv.tolist()):
        if not math.isfinite(v):
            out[i] = float("nan")
            continue
        X = Fraction(v)
        q = (Y0 * (X1 - X) + Y1 * (X - X0)) / D
        try:
            out[i] = float(q)
        except OverflowError:
            out[i] = float("inf")
            continue
        if tol is not None and abs(Fraction(out[i]) - q) > tol:
            raise BackgroundNotConverged(_precision_words("Linear"))
    return _explicit_background(out, "Linear")


def _check_anchors(anchors):
    """Every anchor a pair of finite real numbers (not a string, bool or None) — an
    anchor that is not one has no place on the curve; the page's twin refuses the
    same, in the same words (Codex impl rounds 5-6)."""
    def _num(v):
        return isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, (bool, np.bool_)) \
            and math.isfinite(float(v))
    if not all(isinstance(p, (list, tuple)) and len(p) >= 2 and _num(p[0]) and _num(p[1]) for p in anchors):
        raise BackgroundNotConverged(
            "Manual background not converged: an anchor is not a pair of finite numbers.")


def manual_anchor_background(x, anchors, span=None):
    """The user's anchors as a curve: the piecewise-affine function through them,
    constant beyond the outermost (as np.interp), EVALUATED EXACTLY and rounded once
    to the nearest double (Codex impl rounds 9-10: np.interp's floating-point formula
    overflowed on far anchors, and on finite ones cancelled to a finite, wrong 0 —
    anchors at -1e20 eV against data at 280 eV). Every anchor and energy is an exact
    rational, so (fp0 (xp1 - x) + fp1 (x - xp0)) / (xp1 - xp0) is computed in
    Fraction arithmetic and float() rounds it correctly (half to even): no tolerance,
    no overflow (a convex combination of finite values), and the page computes the
    same value bit for bit (its BigInt twin in manualAnchorBackground). Nothing to
    converge, but the curve must exist: two anchors at one energy with different
    intensities have no curve through both, and every anchor must be a pair of finite
    numbers; either raises BackgroundNotConverged. Fewer than two anchors is the
    caller's case (the line through the window's ends)."""
    import bisect
    from fractions import Fraction as F
    _check_anchors(anchors)
    a = sorted(anchors, key=lambda p: p[0])
    ax = [float(p[0]) for p in a]
    ay = [float(p[1]) for p in a]
    for k in range(1, len(a)):
        if ax[k] == ax[k - 1] and ay[k] != ay[k - 1]:
            raise BackgroundNotConverged(
                "Manual background not converged: two anchors are at the same energy with "
                "different intensities, so no curve passes through both.")
    xv = np.asarray(x, dtype=float)
    out = np.empty(len(xv))
    tol = None if span is None else F(BG_REL_TOL) * F(span)
    for i, v in enumerate(xv.tolist()):
        if not math.isfinite(v):
            out[i] = float("nan")
        elif v <= ax[0]:
            out[i] = ay[0]
        elif v >= ax[-1]:
            out[i] = ay[-1]
        else:
            j = bisect.bisect_right(ax, v) - 1          # ax[j] <= v < ax[j + 1]
            if ax[j] == v:
                out[i] = ay[j]
            else:
                X, X0, X1 = F(v), F(ax[j]), F(ax[j + 1])
                q = (F(ay[j]) * (X1 - X) + F(ay[j + 1]) * (X - X0)) / (X1 - X0)
                out[i] = float(q)
                if tol is not None and abs(F(out[i]) - q) > tol:
                    raise BackgroundNotConverged(_precision_words("Manual"))
    return _explicit_background(out, "Manual")


def smart_experimental_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = BG_REL_TOL,
    n_avg: int = 1,
) -> np.ndarray:
    """Constrained Shirley background, the constraint inside the iteration: B = min(T(B), I).

    DEFINING STATEMENT: the constrained problem of smart_background — the
    Shirley relation wherever B < I, the constraint B = I where the relation
    would exceed the data — solved by the projected fixed-point iteration
    B <- min(T(B), I) from the straight line between the edge levels (the means
    of the averaged ends; the integral and the clamp read the raw data), with
    smart_background's stop; compute_background() certifies the result and
    raises BackgroundNotConverged when the iteration cycles or cannot start
    (findings F10, F12). The same problem as smart_background, read the same way
    since 2026-10-01 (findings F3: whether the two ever differ is measured in
    docs/findings/background-math/). Assumptions and the noise bias of the
    constraint — about +1 % of net area on noisy data: see smart_background.
    """
    if len(x) < 2:
        return np.zeros_like(y)
    xs, ys, flipped = _ascending(x, y)
    b_low, b_high = _edge_levels(ys, n_avg)
    stop = tol * float(np.max(ys) - np.min(ys))
    B = np.linspace(b_low, b_high, len(ys))        # linear initial guess
    for _ in range(n_iter):
        Tn = _shirley_map(xs, ys, B, b_low, b_high)
        if Tn is None:
            break
        Bn = np.minimum(Tn, ys)                    # the projection: lock to the data where T exceeds it
        if np.max(np.abs(Bn - B)) <= stop:
            break
        B = Bn
    B = np.minimum(B, ys)                          # the line, if the first step already stopped
    return B[::-1] if flipped else B


def shirley_linear_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = BG_REL_TOL,
    n_avg: int = 1,
) -> np.ndarray:
    """A REVERSED-STEP background — kept only so saved files that use it restore.

    DEFINING STATEMENT (what it solves; Codex round 1 corrected an earlier
    "none"): B = min(L + d (1 - F(B)), I), L the line between the averaged edge
    levels AFFINE IN THE POINT INDEX (np.linspace; affine in energy only on a
    uniform grid), d = |b_low - b_high|, F(B) the cumulative fraction of
    max(I - B, 0) counted from the low-BE edge; the levels are the means of the
    averaged ends, the integral reads the raw data; smart_background's relative
    stop. compute_background() certifies the result and raises
    BackgroundNotConverged where it fails: equal edge levels (d below an absolute
    1e-12) return L itself, UNCLAMPED — not the equation's min(L, I) wherever the
    data dip below the line; the net integral not positive; the iteration
    cycling between two curves (E = 0..4, I = [20, 44, 34, 41, 47]: 12.5 % of the
    span, the same at 2000 iterations; findings F12). The
    unclamped curve meets the high-BE level, but
    its step is LARGEST AT THE LOW-BE EDGE and shrinks as net signal accumulates
    toward higher BE — the reverse of inelastic scattering, whose background
    grows with the signal at lower BE — and it sits d above the low-BE level
    there (a median 5 %, up to 41 %, of the span on the committed spectra); the
    clamp to the data is active on a median 43 % (up to 72 %) of the points. No
    physical assumption yields that curve. Off the page's menu permanently
    (de-listed 2026-09-03; owner, 2026-10-01 — findings F4); kept so saved files
    that use it restore.
    """
    if len(x) < 2:
        return np.zeros_like(y)
    xs, ys, flipped = _ascending(x, y)
    n = len(ys)
    IL, IH = _edge_levels(ys, n_avg)   # low-BE, high-BE levels

    # Linear baseline
    linear = np.linspace(IL, IH, n)

    # Flatten
    flat = ys - linear

    step_h = abs(IL - IH)
    if step_h < 1e-12:
        return linear[::-1] if flipped else linear

    stop = tol * float(np.max(ys) - np.min(ys))
    B = np.zeros(n)
    for _ in range(n_iter):
        cum_right = _cum_from_high(xs, np.maximum(flat - B, 0.0))
        total = cum_right[0]
        if not total > 0.0:
            break
        Bn = step_h * cum_right / total
        if np.max(np.abs(Bn - B)) <= stop:
            break
        B = Bn

    result = np.minimum(linear + B, ys)
    return result[::-1] if flipped else result


def _tougaard_loss(x, y, n_avg=1):
    """The parts of tougaard_background's statement on the DESCENDING working
    grid: (loss sum at every point, high-BE anchor level, C0, flipped)."""
    n = len(x)

    # Universal cross-section constants, Tougaard (1988): B = 2866 eV²,
    # C = 1643 eV². A long-standing transcription slip shipped C = 1643²
    # (~2.7e6 eV²), which pushed the kernel maximum from ~23 eV to ~949 eV
    # of energy loss and flattened the background to ~zero over any real
    # XPS window. Fixed 2026-07-04 together with the JS twin.
    B_coef, C_coef = 2866.0, 1643.0

    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)

    # The one-sided loss sum below (j >= i) is physical only when BE
    # DESCENDS along the array: the loss contributions at x[i] must come
    # from lower-BE (higher-KE) emitters, which sit at higher indices only
    # on a descending grid. Normalize to descending internally and flip
    # the result back — the mirror of shirley_background's ascending
    # normalization — so both BE orderings give identical output.
    flipped = bool(xa[0] < xa[-1])
    if flipped:
        xa, ya = xa[::-1].copy(), ya[::-1].copy()

    # The edge levels (endpoint averaging sets these only; the integral reads
    # the raw data): on the descending working array index -1 is the low-BE
    # edge — C0, the out-of-window (pre-loss) baseline the kernel integral runs
    # above — and index 0 the high-BE edge, the anchor.
    a_high, c0 = _edge_levels(ya, n_avg)
    net = ya - c0

    # bg[i] = SUM_{j>=i} K(|x[j]-x[i]|) * net[j] * w[j],  K(T) = B*T / (C + T^2)^2,
    # w[j] = the local quadrature weight (energy spacing) at point j — the
    # stated sum, evaluated as stated on EVERY grid (background math,
    # 2026-10-01). A convolution against index separations used to stand in for
    # it on grids uniform to 1e-6 of the step: an approximation whose error the
    # anchor amplifies near cancellation (16 % of the span on a constructed case,
    # and an exact zero where the stated sum has none — the page, which always
    # summed exactly, then disagreed with the server). The sum is numpy's
    # pairwise np.sum, which the page's twin reproduces (_npPairwiseSum).
    w = np.abs(np.gradient(xa))
    bg = np.zeros(n)
    for i in range(n):
        # an intermediate that overflows (u·u at energies near 1e80) turns real
        # terms into silent zeros: the sum is then NaN, and the background is
        # refused as not finite (Codex impl round 12); ordinary sums are untouched
        with np.errstate(over="ignore", invalid="ignore"):
            T = np.abs(xa[i:] - xa[i])
            u = C_coef + T * T
            uu = u * u
            bt = B_coef * T
            terms = (bt / uu) * net[i:] * w[i:]
        if np.all(np.isfinite(uu)) and np.all(np.isfinite(bt)) and np.all(np.isfinite(terms)):
            bg[i] = float(np.sum(terms))
        else:
            bg[i] = float("nan")

    return bg, a_high, c0, flipped


def tougaard_background(
    x: np.ndarray,
    y: np.ndarray,
    n_avg: int = 1,
) -> np.ndarray:
    """Tougaard background: the solution of the loss-integral relation.

    DEFINING STATEMENT. With I the MEASURED data, C0 the low-BE edge level and
    J_high the high-BE edge level (the means of the last / first k =
    min(``n_avg``, n // 4) points on the descending grid: endpoint averaging
    sets the levels only, as for every background — owner, 2026-10-01; until
    then the end bands of the DATA were replaced by their means and that
    modified spectrum integrated, findings F1), the background at binding
    energy E is the constant plus the electrons emitted at LOWER BE (higher
    kinetic energy) E' that lost T = E - E':

        B(E) = C0 + lam * INT_{E_min}^{E} K(E - E') (I(E') - C0) dE',
        K(T) = T / (C + T^2)^2,   C = 1643 eV^2,

    with lam fixed by B(E_high) = J_high (no primary signal at the high-BE
    edge). Explicit in I — one pass, no iteration. When the discrete loss sum
    at the high-BE edge is zero (the sampled quadrature: a two-point window has
    no term with T > 0, although the continuum integral of the interpolated data
    would not vanish; or net intensities whose terms cancel) the anchor does not
    fix lam. If J_high = C0 the solutions form a family, one per lam, and the
    flat C0 returned is its lam = 0 member (every member is flat only when the
    whole loss vector vanishes, as on a two-point window — then the flat C0 IS
    the answer); if J_high != C0 no solution exists and the anchor is missed
    (findings F11). Both are reported: compute_background() raises
    BackgroundNotConverged for the undetermined and the unsolvable case. The sum
    is evaluated AS STATED on every grid (since 2026-10-01: a convolution used to
    stand in for it on grids uniform to 1e-6 of the step, an approximation the
    anchor amplifies near cancellation — 16 % of the span on a constructed case).
    Near cancellation the statement itself is ill-conditioned: the anchor divides
    by a small high-edge sum, so a tiny change of the data moves the background a
    long way; that is the statement's property, reported, not an error.
    Measured on
    the committed spectra, against an independent evaluation: equal to the
    discrete sum to <= 1e-13 of the span, the anchor met exactly, within
    1.4e-5 of the span (2.7e-3 % of net area) of the integral on a 10x finer grid.

    ASSUMPTIONS, and when they fail:
      * the emitters are homogeneously distributed in depth and lose energy by
        the universal cross-section K (fitted to noble / transition metals).
        Fails for layered or particulate samples and for materials with sharp
        plasmon losses (free-electron-like metals, many polymers).
      * everything emitted BELOW the window contributes a constant, C0. Fails
        when a strong line just below the window feeds a sloping loss tail in.
      * the window samples enough of the loss region for K's shape to be what the
        data test: K peaks at T = sqrt(C/3) = 23.4 eV. On the committed B 1s, C 1s
        and Cl 2p windows (10–20 eV) no loss beyond the maximum is sampled; on
        the U 4f windows (31–35 eV) up to 30 % of the high-BE edge's integral
        comes from beyond it, and replacing K by its small-loss linear form moves
        the background by up to 3.9 % of the span (0.02–0.7 % on the narrower
        windows) — the shape does matter there (findings F6).
      * the high-BE edge carries no primary signal (the anchor).

    Corroboration (not the defence): S. Tougaard, Surf. Interface Anal. 11, 453
    (1988); the coefficient values B = 2866 eV^2, C = 1643 eV^2 are the universal
    cross-section's as attributed there (not re-verified against the paper text
    in the 2026-09-30 review). B cancels in the anchor; C alone sets the shape.

    Uses the two-parameter universal loss function
    K(T) = B·T / (C + T²)² with B = 2866 eV², C = 1643 eV²
    (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
    cross-section fitted to noble/transition-metal optical data; the
    kernel maximum sits at T = sqrt(C/3) ~= 23.4 eV energy loss).

    FORMULATION (2026-07-17 background audit, finding F1).  The idealized
    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
    window BEGINS in a loss-free region, so that J at the low-BE edge is
    the zero-loss level.  Real windows never satisfy this: at (say) Fe 2p
    there is a large inelastic baseline produced by every lower-BE
    (higher-KE) transition OUTSIDE the window, which a window-limited
    integral structurally cannot reproduce.  Because K(0) = 0, the bare
    integral is identically zero at the low-BE edge REGARDLESS OF THE DATA
    — the background visibly dove to ~0 there, and a flat featureless
    window produced a full-amplitude phantom "signal".

    So the low-BE edge level is taken as a constant offset C0 (the
    out-of-window baseline the kernel cannot see), the kernel runs over the
    net (J - C0), and the amplitude is then anchored so the background
    meets the measured intensity at the HIGH-BE edge — the standard
    practical Tougaard criterion (B is effectively fitted, which is why the
    nominal B_coef cancels; C alone sets the kernel shape).  Equivalent to
    fitting B together with an offset rather than B alone.

    ``n_avg``: C0 and the high-BE anchor are the means of the end bands, so
    neither rests on a single noisy sample; the loss sum reads the raw data.
    n_avg = 1 = raw endpoints = previous behaviour.

    The background at each binding energy accumulates loss contributions
    from electrons emitted at LOWER BE (higher kinetic energy), so the
    one-sided sum requires a descending-BE grid; input in either BE order
    is normalized internally.  Mirrors the frontend JS twin
    ``tougaardBackground``.
    """
    n = len(x)
    if n < 2:
        return np.zeros_like(y, dtype=float)
    # Computed on the intensities scaled by an exact power of two to max|I| in [0.5, 1)
    # and scaled back (Codex impl round 14): the relation is homogeneous in the
    # intensity, so on ordinary data every intermediate is the same bits times 2^-e and
    # the result is bit for bit unchanged — and the certificate's rounding bound,
    # computed in the same frame, never underflows on tiny data or overflows on huge.
    e = _pow2_exp(y)
    bg, a_high, c0, flipped = _tougaard_loss(x, np.ldexp(np.asarray(y, dtype=float), -e), n_avg)
    # Amplitude anchor: scale the loss integral so the background equals the
    # measured intensity at the HIGH-BE edge (index 0 on the descending
    # working array), then sit it on the C0 pedestal. Guard semantics: if NO
    # net loss signal accumulates at the high-BE edge (bg[0] == 0 — e.g. a
    # flat or empty window), the honest background is the flat pre-loss level
    # C0 itself, NOT zeros: a featureless window contains no loss signal to
    # model, and returning zeros would report the entire baseline as net
    # signal (the pre-F1 behaviour). Negative counts (physically invalid
    # input) pass through signed; no clamping policy is imposed here.
    if bg[0] == 0.0:
        out = np.full(n, c0)
    else:
        out = c0 + bg * ((a_high - c0) / bg[0])
    back = np.ldexp(out, e)
    # scaling back is exact only if it round-trips: a value that lost bits — into the
    # subnormal range or all the way to zero (Codex impl round 15) — is refused (NaN)
    out = np.where(np.ldexp(back, -e) == out, back, np.nan)
    return out[::-1] if flipped else out


def _pow2_exp(y) -> int:
    """e with max|I| in [2^(e-1), 2^e) (numpy's frexp); 0 for an all-zero or empty window."""
    M = float(np.max(np.abs(np.asarray(y, dtype=float)))) if len(y) else 0.0
    return int(np.frexp(M)[1]) if (M > 0.0 and math.isfinite(M)) else 0


_BG_LABELS = {
    "shirley": "Shirley",
    "smart": "Smart (constrained Shirley)",
    "smart_exp": "Smart (experimental)",
    "shirley_linear": "Shirley + linear",
    "tougaard": "Tougaard",
}


def background_certificate(x, y, bg, method, n_avg=1) -> dict[str, Any]:
    """Check a background against its DEFINING STATEMENT (not against how it
    was computed). Returns {"converged": bool, "residual": float | None,
    "reason": str | None}; the residual is a fraction of the window's intensity
    span and the test is ``residual <= BG_REL_TOL`` — the same number every
    iteration stops on.

      shirley         B = T(B)                       (_shirley_map)
      smart, smart_exp  B = min(T(B), I)
      shirley_linear  B = min(L + d (1 - F(B)), I)   (its docstring)
      tougaard        the loss-sum anchor determines the amplitude: a zero
                      high-edge sum with equal edge levels leaves it
                      undetermined (unless the whole loss vector is zero:
                      then the flat C0 is the one answer), with unequal levels
                      there is no solution (findings F11)
      linear, manual, none  explicit — nothing to converge

    T and the edge levels read endpoint averaging as the backgrounds do (the
    levels only; the integral and the clamp read the raw data)."""
    m = (method or "").lower()
    label = _BG_LABELS.get(m, m)
    bg = np.asarray(bg, dtype=float)
    if not np.all(np.isfinite(bg)):
        return {"converged": False, "residual": None, "reason": "the computed background is not finite"}
    if m not in _BG_LABELS:
        return {"converged": True, "residual": None, "reason": None}
    if len(x) < 2:
        return {"converged": False, "residual": None,
                "reason": "the background window holds fewer than two data points"}
    # the integral relations are defined along the energy axis (Codex impl round 6):
    # the data must be finite numbers and the window's energies in order (ascending
    # or descending, repeats allowed); an unsorted window integrates the array order
    # and its own iteration and certificate agree on a curve no statement gives
    xv, yv = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if not (np.all(np.isfinite(xv)) and np.all(np.isfinite(yv))):
        return {"converged": False, "residual": None, "reason": "the data in the window are not all finite numbers"}
    dx = np.diff(xv)
    if not (np.all(dx >= 0) or np.all(dx <= 0)):
        return {"converged": False, "residual": None, "reason": (
            "the energies in the window are not in order (neither ascending nor descending), and the "
            "%s relation is an integral along the energy axis" % label)}
    if m == "tougaard":
        # judged in the frame tougaard_background computes in (power-of-two-normalised)
        e = _pow2_exp(yv)
        yn = np.ldexp(yv, -e)
        loss, a_high, c0, _ = _tougaard_loss(x, yn, n_avg)
        if loss[0] != 0.0:
            # the curve is closed-form (no iteration), so its only error is rounding:
            # certified only if a rigorous bound on that rounding meets the predicate
            # (Codex impl round 13: a high-edge sum that nearly cancels amplified it
            # 280 000-fold past it, on four ordinary points)
            tb, tl = _tougaard_rounding_bound(x, yn, n_avg), BG_REL_TOL * float(np.max(yn) - np.min(yn))
            if math.isfinite(tb) and math.isfinite(tl) and tb <= tl:   # finite-only (owner 2026-10-06)
                return {"converged": True, "residual": None, "reason": None}
            return {"converged": False, "residual": None, "reason": _TOUGAARD_CANCELS}
        if not np.any(loss):
            return _tougaard_zero_loss_verdict(x, yv, bg, n_avg)
        if a_high == c0:
            return {"converged": False, "residual": None, "reason": (
                "the loss sum at the high-BE edge cancels to zero, so the edge does not fix the "
                "background's amplitude and different amplitudes give different backgrounds")}
        return {"converged": False, "residual": None, "reason": _TOUGAARD_NO_AMPLITUDE}
    # The Shirley family: the residual of the RETURNED curve against its relation, in
    # EXACT rational arithmetic — exact edge means, exact trapezoids, exact map — so the
    # verdict is the statement's, not the arithmetic's (Codex impl round 13: on 1e12 ± 8
    # counts the float check rounded a residual of 6.6e-7 to 0 against a predicate of
    # 8e-12). Measured on the committed targets: the same verdict on all 1 212 cases,
    # the exact residual at most 0.993 of the predicate
    # (scripts/bg_math_exact_certificate_margin.py). The page's twin is _bgCertificate.
    return _exact_shirley_certificate(x, y, bg, m, n_avg, label)


def _fmt3(v: float) -> str:
    """Three significant digits, ROUNDED HALF UP ON THE EXACT BINARY VALUE, trailing
    zeros stripped, exponent form below 1e-4 and from 1e3 ('1.23e-05', '1.23e+03').
    One definition the page computes exactly too (JavaScript's toExponential rounds
    the exact value half up; its twin is the page's _fmt3) — Python's '%.3g' rounds
    ties to even and differed from the page on exact ties such as 12.25 (Codex impl
    round 7)."""
    from decimal import Decimal, ROUND_HALF_UP
    if v == 0:
        return "0"
    if not math.isfinite(v):
        return "nan" if math.isnan(v) else ("inf" if v > 0 else "-inf")
    d = Decimal(v)                                   # exact
    e = d.adjusted()
    q = d.quantize(Decimal(1).scaleb(e - 2), rounding=ROUND_HALF_UP)
    if q.adjusted() != e:                            # 999.6 -> 1.00e+03
        e = q.adjusted()
        q = d.quantize(Decimal(1).scaleb(e - 2), rounding=ROUND_HALF_UP)

    def strip(t):
        return t.rstrip("0").rstrip(".") if "." in t else t
    if e < -4 or e >= 3:
        m = strip(f"{q.scaleb(-e):.2f}")
        return f"{m}e{'-' if e < 0 else '+'}{abs(e):02d}"
    return strip(f"{q:.{max(0, 2 - e)}f}")


# F13 (owner 2026-10-03): a window without a peak has no Shirley-family background —
# the refusal says what to use instead
_NO_PEAK = " — for a window with no peak, use the Linear background"


def _exact_shirley_certificate(x, y, bg, m, n_avg, label):
    from fractions import Fraction as F
    xs, ys, flipped = _ascending(x, y)
    Ba = bg[::-1] if flipped else bg
    X = [F(v) for v in xs.tolist()]
    Y = [F(v) for v in ys.tolist()]
    B = [F(v) for v in np.asarray(Ba, dtype=float).tolist()]
    n = len(Y)
    k = max(1, min(int(n_avg), n // 4)) if n >= 4 else 1
    b_low, b_high = sum(Y[:k]) / k, sum(Y[-k:]) / k
    cum = [F(0)] * n
    for i in range(n - 2, -1, -1):
        cum[i] = cum[i + 1] + (max(Y[i] - B[i], 0) + max(Y[i + 1] - B[i + 1], 0)) * (X[i + 1] - X[i]) / 2
    if m == "shirley_linear":
        d = abs(b_low - b_high)
        L = [b_low + (b_high - b_low) * i / (n - 1) for i in range(n)]
        if d != 0 and not cum[0] > 0:
            target = None
        elif d == 0:
            target = [min(L[i], Y[i]) for i in range(n)]
        else:
            target = [min(L[i] + d * cum[i] / cum[0], Y[i]) for i in range(n)]
    elif b_low == b_high:
        target = [b_low] * n if m == "shirley" else [min(b_low, Y[i]) for i in range(n)]
    elif not cum[0] > 0:
        target = None
    else:
        T = [b_high + (b_low - b_high) * c / cum[0] for c in cum]
        target = T if m == "shirley" else [min(T[i], Y[i]) for i in range(n)]
    if target is None:
        return {"converged": False, "residual": None, "reason": (
            "the data lie at or below the line between the two edge levels, so there is no net "
            "signal and the %s relation is undefined%s" % (label, _NO_PEAK))}
    diff = max(abs(B[i] - target[i]) for i in range(n))
    span = max(Y) - min(Y)
    residual = float(diff / span) if span > 0 else (0.0 if diff == 0 else float("inf"))
    if diff <= F(BG_REL_TOL) * span:
        return {"converged": True, "residual": residual, "reason": None}
    pct = _fmt3(float(100 * diff / span)) if span > 0 else "inf"
    return {"converged": False, "residual": residual, "reason": (
        "the result misses the %s relation by %s %% of the intensity span (its iteration alternates "
        "or ran out of steps, or the data exceed what double precision resolves at this span)%s"
        % (label, pct, _NO_PEAK))}


_TOUGAARD_CANCELS = ("the loss sum at the high-BE edge nearly cancels, so its rounding moves the "
                     "background by more than the certificate's precision")
_TOUGAARD_NO_AMPLITUDE = "the loss sum at the high-BE edge is zero, so no amplitude can meet the high-BE edge level"


def _tougaard_zero_loss_verdict(x, y, bg, n_avg):
    """Every computed loss sum is zero: the relation's flat member C0 is the answer only if
    the EXACT loss vector is zero and the EXACT edge means agree (Codex impl round 14: float
    means of 1 and 1 + 2^-53 compared equal and an unsolvable anchor was certified). The
    exact loss is zero when every term has an exactly zero factor — K(T) = 0 only at T = 0,
    a zero weight, or a zero net against the exact low-edge mean; a float zero that is not
    proven so is refused as cancelling. Certified only if the returned flat curve is the
    exact mean within the predicate."""
    from fractions import Fraction as F
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if xa[0] < xa[-1]:
        xa, ya = xa[::-1], ya[::-1]
    n = len(xa)
    k = max(1, min(int(n_avg), n // 4)) if n >= 4 else 1
    Y = [F(v) for v in ya.tolist()]
    a_high, c0 = sum(Y[:k]) / k, sum(Y[-k:]) / k
    w = np.abs(np.gradient(xa))
    for i in range(n):
        for j in range(i, n):
            if not (xa[j] == xa[i] or w[j] == 0.0 or Y[j] == c0):
                return {"converged": False, "residual": None, "reason": _TOUGAARD_CANCELS}
    if a_high != c0:
        return {"converged": False, "residual": None, "reason": _TOUGAARD_NO_AMPLITUDE}
    span = max(Y) - min(Y)
    if max(abs(F(float(v)) - c0) for v in np.asarray(bg, dtype=float).tolist()) <= F(BG_REL_TOL) * span:
        return {"converged": True, "residual": None, "reason": None}
    return {"converged": False, "residual": None, "reason": _TOUGAARD_CANCELS}


def _tougaard_rounding_bound(x, y, n_avg=1) -> float:
    """A RIGOROUS bound on how far rounding can move the computed Tougaard background from
    the exact value of its relation, at the worst point (Codex impl rounds 13-15); inf
    when the high-edge sum's own uncertainty reaches its magnitude (its sign, and the
    anchoring, are then undetermined). Called on the power-of-two-normalised intensities
    tougaard_background computes with (max|I| in [0.5, 1)). With u = eps/2, eta = 2^-1074
    (the absolute error of a subnormal rounding), g(m) = m u / (1 - m u) and, per row i,
    the computed loss sum L_i of m_i terms, S_i = sum |term|, W_i = sum K w:
      each term carries <= 16 roundings, any summation tree <= m_i - 1:
        dL_i = g(m_i + 15) S_i + 2 (m_i + 15) eta + dc W_i (1 + g(m_i)),
      the last for the edge mean C0 (off by <= dc) inside every net;
      dc = da = g(k + 1) max|I| (each edge mean of k points);
      the exact ratio s_i = L_i / L_0 then lies within
        rho_i = (dL_i + r_i dL_0) / (|L_0| - dL_0)  of the computed one (r_i = |L_i / L_0|),
      requiring dL_0 < |L_0|; the exact D = J_high - C0 within dD = da + dc + u |D|; so
        E_i = dc + dD (r_i + rho_i) + |D| rho_i + 4 u (|C0| + |B_i| + |D| r_i) + eta,
    and the maximum is enlarged by (1 + 64 u) for the bound's own roundings. No
    first-order truncation: a computed D or L_0 of zero cannot hide the exact one. The
    page's twin (_tougaardRoundingBound) uses the same operations, so the verdicts
    agree bit for bit."""
    u = np.finfo(float).eps / 2
    eta = 2.0 ** -1074

    def g(m):
        return m * u / (1 - m * u)
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if xa[0] < xa[-1]:
        xa, ya = xa[::-1].copy(), ya[::-1].copy()
    n = len(xa)
    k = max(1, min(int(n_avg), n // 4)) if n >= 4 else 1
    a_high, c0 = _edge_levels(ya, n_avg)
    net = ya - c0
    w = np.abs(np.gradient(xa))
    L, S, W = np.zeros(n), np.zeros(n), np.zeros(n)
    for i in range(n):
        T = np.abs(xa[i:] - xa[i])
        uu = (1643.0 + T * T) * (1643.0 + T * T)
        kw = (2866.0 * T) / uu * w[i:]
        t = kw * net[i:]
        L[i], S[i], W[i] = float(np.sum(t)), float(np.sum(np.abs(t))), float(np.sum(kw))
    M = float(np.max(np.abs(ya)))
    dc = da = g(k + 1) * M
    D = abs(a_high - c0)
    m = n - np.arange(n)
    dL = g(m + 15) * S + 2 * (m + 15) * eta + dc * W * (1 + g(m))
    aL0 = abs(L[0])
    if not dL[0] < aL0:
        return float("inf")
    r = np.abs(L) / aL0
    rho = (dL + r * dL[0]) / (aL0 - dL[0])
    dD = da + dc + u * D
    bg = c0 + L * ((a_high - c0) / L[0])
    E = dc + dD * (r + rho) + D * rho + 4 * u * (abs(c0) + np.abs(bg) + D * r) + eta
    return float(np.max(E)) * (1 + 64 * u)


def _region_in_order(x, method):
    """An integral background is computed on its window and held flat beyond it at
    the nearer edge's value — by array POSITION, which is by energy only when the
    whole fitted region is in order (Codex impl round 7: a sorted window inside an
    unsorted region gave the high-BE side the low-edge level). Raises
    BackgroundNotConverged otherwise; the page's twin is in computeBackgroundCore."""
    xv = np.asarray(x, dtype=float)
    dx = np.diff(xv)
    if len(xv) > 1 and not (np.all(dx >= 0) or np.all(dx <= 0)):
        label = _BG_LABELS.get(method, method)
        raise BackgroundNotConverged(
            f"{label} background not converged: the energies in the fitted region are not in order "
            f"(neither ascending nor descending), and the {label} background is held flat beyond its "
            "window along the energy axis.")


def compute_background(x, y, method, n_avg=1, report=None) -> np.ndarray:
    """The integral background of ``method`` on the window (x, y), CERTIFIED:
    raises BackgroundNotConverged (a ValueError carrying a plain message) when
    the result does not satisfy its defining statement. Every caller that fits
    against, subtracts or reports a background goes through here. ``report``, if
    a dict, receives the certificate (``background_certificate``'s result) — so a
    caller can RECORD the verdict without certifying twice (fit recording,
    2026-10-10)."""
    m = (method or "").lower()
    fn = {"shirley": shirley_background, "smart": smart_background,
          "smart_exp": smart_experimental_background,
          "shirley_linear": shirley_linear_background,
          "tougaard": tougaard_background}.get(m)
    if fn is None:
        raise ValueError(f"Unknown background method '{method}'")
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    bg = fn(x, y, n_avg=n_avg)
    cert = background_certificate(x, y, bg, m, n_avg)
    if report is not None:
        report.update(cert)
    if not cert["converged"]:
        raise BackgroundNotConverged(f"{_BG_LABELS[m]} background not converged: {cert['reason']}.")
    return bg


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
        α extends it.

    2.  Gaussian convolution with a continuous-m kernel: σ_pts = m/3,
        kernel half-width max(1, ceil(3.5·σ_pts)) (±3.5σ; see the inline
        comment for why 3.5, not 3), truncation-renormalized, convolved
        with mode='same' on the uniform x grid. m < 1e-3 means no
        convolution. NOTE this deliberately deviates from the original
        integer 2m+1 design (still implemented by the frontend's
        laTrueCasaXPS_array — a tracked ~0.15%-at-m=50 parity gap, todo
        in tests/js/lineshape_parity.test.js): m flows through
        continuously so lmfit's finite-difference Jacobian in m is
        non-singular.

    With α=β=1 and m=0, this reduces exactly to amplitude × L(x) (a pure
    Lorentzian of peak height = amplitude, FWHM = `fwhm`).

    Parameters
    ----------
    fwhm  : Lorentzian FWHM in eV (must be > 0)
    alpha : high-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    beta  : low-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    m     : Gaussian convolution kernel width in DATA POINTS (not eV);
            0–499, used CONTINUOUSLY (no rounding — see kernel note above).
    """
    fwhm = max(float(fwhm), 1e-9)
    alpha = max(float(alpha), 1e-3)
    beta = max(float(beta), 1e-3)
    # Continuous-σ kernel: m flows through to the kernel weights as a real
    # number, so the Jacobian column for m is well-defined under lmfit's
    # finite-difference perturbation. Previously m was rounded with
    # int(round(m)), making the function locally constant in m and
    # producing a singular Hessian whenever m varied — that poisoned
    # covariance estimation for every other free param too.
    # Defensive guard preserves the prior [0, 499] cap in case a saved
    # spec or caller bypasses the lmfit bound.
    m_cont = max(0.0, min(499.0, float(m)))

    eps = x - center
    # Base unit-amplitude Lorentzian
    L = 1.0 / (1.0 + 4.0 * (eps / fwhm) ** 2)
    # Piecewise exponentiation. BE-axis: high-BE side is eps ≥ 0.
    high = eps >= 0
    base = np.where(high, np.power(L, alpha), np.power(L, beta))

    # Below ε, treat as un-convolved Lorentzian so an optimizer that lands
    # exactly at m=0 returns the bare base curve rather than degenerating.
    if m_cont < 1e-3:
        return amplitude * base

    sigma_pts = m_cont / 3.0
    # Kernel half-width: ±3.5σ captures > 99.95% of the Gaussian. Use 3.5
    # rather than 3 specifically so the kernel-length quantization step
    # `ceil(3.5σ)` doesn't coincide with integer m — that would put a
    # discrete jump in the output exactly at integer m and re-break
    # backwards compat with previously-saved (integer-m) fits. With 3.5
    # the next jump from m=N is at m = 6(N+1)/7 ≠ integer.
    half = max(1, int(np.ceil(3.5 * sigma_pts)))
    k = np.arange(-half, half + 1, dtype=float)
    kern = np.exp(-(k ** 2) / (2.0 * sigma_pts ** 2))
    kern = kern / kern.sum()

    convolved = np.convolve(base, kern, mode='same')
    # np.convolve mode='same' returns max(len(base), len(kern)) — not
    # len(base). When the input grid is shorter than the kernel, trim
    # back to len(base) so the function's len(output) == len(x) contract
    # holds. lmfit's composite-fit residual path will broadcast the
    # per-peak arrays against the data grid, so a kernel-length return
    # surfaces as a cryptic shape mismatch downstream.
    if len(convolved) > len(base):
        excess = len(convolved) - len(base)
        start = excess // 2
        convolved = convolved[start:start + len(base)]

    peak_idx = int(np.argmin(np.abs(eps)))
    peak_val = convolved[peak_idx]
    if peak_val <= 0:
        peak_val = float(np.max(convolved))
    if peak_val <= 0:
        return np.zeros_like(x)
    return amplitude * convolved / peak_val


# ─────────────────────────────────────────────────────────────────────────────
# lmfit Model factory
# ─────────────────────────────────────────────────────────────────────────────

_SHAPE_FUNCS = {
    "gaussian": _gaussian,
    "lorentzian": _lorentzian,
    "pseudo_voigt_gl": _pseudo_voigt_gl,
    "asymmetric_gl": _asymmetric_gl,
    "doniach_sunjic": _doniach_sunjic,
    "ds_g": _ds_g_dscore_gauss,
    "la_casaxps": _la_casaxps_true,
}

AVAILABLE_SHAPES = list(_SHAPE_FUNCS.keys())


def _id_failure(pid) -> str | None:
    """Why ``pid`` cannot be a component id, or None. Every parameter is named f"p{id}_<name>": that must be an
    identifier, and one Python reads as written — Python normalises identifiers (NFKC) when it parses an expression,
    so an id like "\u212a" (KELVIN SIGN) would name the parameters of "K" inside an expression while the links and
    the records spell it otherwise (seal 1d Codex round 14)."""
    import unicodedata
    if isinstance(pid, (list, dict)) or not f"p{pid}_x".isidentifier():
        return f"the peak id '{pid}' cannot name a parameter (p<id>_<name> must be an identifier)"
    if unicodedata.normalize("NFKC", f"p{pid}_x") != f"p{pid}_x":
        return f"the peak id '{pid}' is not written in normalised form (NFKC); write it as Python reads it"
    return None


def _link_masters(peak_specs: list[dict]) -> dict:
    """{str(id): str(master id) or None} — each peak's master found as _make_peak_params finds it: the FIRST spec
    whose id EQUALS its constrain_to (so 1.0 and true name the peak with id 1). One reading for every walk over
    the links — the graph check, the support verdict, the required-component refit and the verifier (seal 1d Codex round 12: they
    compared string spellings, "1.0" != "1", so a peak linked by an equal reference was linked but not followed)."""
    out = {}
    for s in peak_specs:
        mid = s.get("constrain_to")
        m = None if mid is None else next((t for t in peak_specs if t.get("id") == mid), None)
        out[str(s.get("id"))] = None if m is None else str(m.get("id"))
    return out


def _validate_constraint_graph(peak_specs: list[dict]) -> None:
    """Reject self-referential or circular spin-orbit constraints (audit F11).

    A peak whose ``constrain_to`` names its own id — or a cycle such as
    A→B→A — produces a self-referencing lmfit expression that recurses to
    "maximum recursion depth exceeded". Catch it here with a clean ValueError
    (→ 400) before any lmfit parameter/expression is built. Two peaks sharing an
    id, a ``constrain_to`` that names no peak in the request (matched as
    ``_make_peak_params`` matches it) and a link across lineshapes are refused
    here too (Q10 0c').
    """
    # every id once, as the parameter prefix spells it (f"p{id}_": 1 and "1" collide), and every
    # constraint naming a peak that is there — refused HERE, before a job starts and on every route
    # (Q10 0c' Codex round 1: /api/fit/start admitted a missing master, /api/analyze answered 500
    # for a shared id)
    # — and every id once as a VALUE too (1, 1.0 and true are equal: a link names peaks by equality, so it could not
    # tell them apart; /api/fit refused them already, run_fit now too — seal 1d Codex round 13)
    seen_ids: list = []
    for s in peak_specs:
        why = _id_failure(s.get("id"))
        if why:
            raise ValueError(why[:1].upper() + why[1:])
        if any(str(s.get("id")) == str(t) or s.get("id") == t for t in seen_ids):
            raise ValueError(f"Two peaks share the id '{s.get('id')}'; each peak must have its own id")
        seen_ids.append(s.get("id"))
    # each master found as _make_peak_params finds it (_link_masters: the first peak whose id EQUALS constrain_to),
    # on ids keyed by their spelling (unique, above) — a dict keyed by the ids themselves merged 1, 1.0 and true and
    # kept the LAST (seal 1d Codex round 12)
    parent: dict = {}
    masters = _link_masters(peak_specs)
    by_id = {str(s.get("id")): s for s in peak_specs}
    for s in peak_specs:
        sid = str(s.get("id"))
        master = s.get("constrain_to")
        if master is None:
            continue
        if masters[sid] is None:
            raise ValueError(f"Peak '{s.get('name') or s.get('id')}' is linked to a peak that is not in the model ('{master}')")
        if masters[sid] == sid:
            raise ValueError(f"Peak '{s.get('id')}' cannot constrain to itself")
        master = parent[sid] = masters[sid]
        # a linked peak has its parent's lineshape (Q10 0c', owner 2026-10-11): an expression on a
        # parameter the child's shape does not read was fitted but never drawn (a Voigt child of a
        # GL parent: fitted at the parent's mix, drawn at 0.5). Voigt and GL are one backend shape,
        # so the page sends each peak's `frontend_shape` too.
        m = by_id.get(master)
        if m is not None:
            fs, fm = s.get("frontend_shape"), m.get("frontend_shape")
            # the backend shapes always, and the page's shapes too when both are named (Codex round 3:
            # two peaks of different backend shapes both labelled "GL" passed)
            differ = s.get("shape") != m.get("shape") or (fs is not None and fm is not None and fs != fm)
            if differ:
                # name the shapes that differ: the page's when both are named and differ, else the
                # backend's ("(GL, GL)" named nothing, Codex 0c' round 4 run B)
                pair = (fs, fm) if (fs is not None and fm is not None and fs != fm) else (s.get("shape"), m.get("shape"))
                raise ValueError(
                    f"Peak '{s.get('name') or sid}' is linked to '{m.get('name') or master}' but has a different "
                    f"lineshape ({pair[0]}, {pair[1]}); a linked peak takes its parent's lineshape")

    # Walk each constrained peak's master chain; a repeat is a cycle.
    for start in parent:
        chain = [start]
        cur = parent[start]
        while cur is not None:
            chain.append(cur)
            if cur == start or cur in chain[:-1]:
                pretty = " → ".join(str(x) for x in chain)
                raise ValueError(f"Circular peak constraint detected: {pretty}")
            cur = parent.get(cur)


def _make_peak_params(
    model: Model,
    spec: dict[str, Any],
    prefix: str,
    all_specs: list[dict],
) -> Parameters:
    """
    Build lmfit Parameters for one peak from a spec dict.

    Spec keys
    ---------
    shape          : str   – one of AVAILABLE_SHAPES
    center         : float – initial centre (eV)
    center_min     : float – lower bound   (optional)
    center_max     : float – upper bound   (optional)
    amplitude      : float – peak maximum counts
    amplitude_min  : float – lower bound   (default 0)
    fwhm           : float – full width at half max (eV)
    fwhm_min       : float – lower bound   (default 0.1)
    fwhm_max       : float – upper bound   (default 15.0)
    gl_ratio       : float – Lorentzian fraction for *_gl shapes  [0–1]
    asymmetry      : float – high-BE broadening factor for asymmetric_gl [0–1]
    alpha          : float – DS asymmetry index
    constrain_to   : str   – id of master peak (spin‑orbit slave)
    splitting      : float – centre offset from master (eV)
    area_ratio     : float – amplitude = master_amplitude × area_ratio
    fix_fwhm       : bool  – if True, lock FWHM to master value
    """
    shape = spec["shape"]
    p = model.make_params()

    center = spec.get("center", 285.0)
    amp = spec.get("amplitude", 1000.0)
    fwhm = spec.get("fwhm", 1.5)
    asymmetry = spec.get("asymmetry", 0.0)

    def _set(name, value, min_=None, max_=None, expr=None, vary=True):
        full = prefix + name
        if full not in p:
            return
        if not vary and expr is None:
            # A HELD parameter is held at the value requested. The bounds are
            # the optimiser's search limits; lmfit clips a value outside them
            # even when it does not vary, which silently changed a locked
            # DS+G m of 0 (the page's delta-kernel branch, drawn without
            # convolution) into 0.05 (a convolved fit) — A03 Codex round 2's
            # locked-at-bounds round trips. Widen the limit to the value.
            if min_ is not None and value < min_:
                min_ = value
            if max_ is not None and value > max_:
                max_ = value
        p[full].set(value=value)
        if expr is not None:
            p[full].expr = expr
            p[full].vary = False
        else:
            if min_ is not None:
                p[full].min = min_
            if max_ is not None:
                p[full].max = max_
            p[full].vary = vary

    # Constrain to a master peak (spin‑orbit doublet)?
    master_id = spec.get("constrain_to")
    if master_id is not None:
        # Find the master spec to get its prefix
        master_spec = next((s for s in all_specs if s["id"] == master_id), None)
        if master_spec is None:
            raise ValueError(f"Master peak '{master_id}' not found for spin‑orbit constraint")
        m_prefix = f"p{master_spec['id']}_"
        # + 0.0 folds −0.0 to 0.0: the number is written INTO the expression's text, and a JSON
        # writer spells −0 as 0 — one reading of the field (seal 1a′ Codex round 1)
        splitting = float(spec.get("splitting", 0.0)) + 0.0
        area_ratio = float(spec.get("area_ratio", 1.0)) + 0.0

        _set("center", center, expr=f"{m_prefix}center + {splitting}")
        _set("amplitude", amp, expr=f"{m_prefix}amplitude * {area_ratio}")
        _set("fwhm", fwhm, expr=f"{m_prefix}fwhm" if spec.get("fix_fwhm", True) else None,
             min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0))
        if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
            _set("gl_ratio", spec.get("gl_ratio", 0.3),
                 expr=f"{m_prefix}gl_ratio" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=1.0)
        if shape == "asymmetric_gl":
            _set("asymmetry", asymmetry,
                 expr=f"{m_prefix}asymmetry" if spec.get("fix_fwhm", True) else None,
                 min_=spec.get("asymmetry_min", 0.0),
                 max_=spec.get("asymmetry_max", 1.0))
        if shape == "doniach_sunjic":
            _set("alpha", spec.get("alpha", 0.1),
                 expr=f"{m_prefix}alpha" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=0.5)
            _set("gamma_asym", spec.get("gamma_asym", 0.0),
                 expr=f"{m_prefix}gamma_asym" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=1.0)
        if shape == "ds_g":
            fix = spec.get("fix_fwhm", True)
            _set("alpha",   spec.get("alpha",   0.10), expr=f"{m_prefix}alpha"   if fix else None, min_=0.0,  max_=0.49)
            _set("beta",    spec.get("beta",    0.3),  expr=f"{m_prefix}beta"    if fix else None, min_=0.05, max_=2.0)
            _set("m_gauss", spec.get("m_gauss", 0.4),  expr=f"{m_prefix}m_gauss" if fix else None, min_=0.0,  max_=4.0)
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
        return p

    # Free (master or unconstrained) peak
    # Non-DS+G peaks (satellites, etc.) get a default ±2 eV constraint to prevent
    # the optimizer from drifting to physically unreasonable positions.
    c_min = spec.get("center_min")
    c_max = spec.get("center_max")
    if shape != "ds_g" and c_min is None:
        c_min = center - 2.0
    if shape != "ds_g" and c_max is None:
        c_max = center + 2.0
    _set("center", center, min_=c_min, max_=c_max, vary=not spec.get("fix_center", False))
    _set("amplitude", amp,
         min_=spec.get("amplitude_min", 0.0), max_=spec.get("amplitude_max"),
         vary=not spec.get("fix_amplitude", False))
    _set("fwhm", fwhm,
         min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0),
         vary=not spec.get("fix_fwhm", False))

    if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
        _set("gl_ratio", spec.get("gl_ratio", 0.3), min_=0.0, max_=1.0,
             vary=not spec.get("fix_gl_ratio", False))
    if shape == "asymmetric_gl":
        _set("asymmetry", asymmetry,
             min_=spec.get("asymmetry_min", 0.0),
             max_=spec.get("asymmetry_max", 1.0),
             vary=not spec.get("fix_asymmetry", False))
    if shape == "doniach_sunjic":
        _set("alpha", spec.get("alpha", 0.1), min_=0.0, max_=0.5,
             vary=not spec.get("fix_alpha", False))
        _set("gamma_asym", spec.get("gamma_asym", 0.0), min_=0.0, max_=5.0,
             vary=not spec.get("fix_gamma_asym", False))
    if shape == "ds_g":
        _set("alpha",   spec.get("alpha",   0.10), min_=0.0,  max_=0.49,
             vary=not spec.get("fix_alpha", False))
        _set("beta",    spec.get("beta",    0.3),  min_=0.05, max_=2.0,
             vary=not spec.get("fix_beta", False))
        _set("m_gauss", spec.get("m_gauss", 0.4),  min_=0.05, max_=4.0,
             vary=not spec.get("fix_m_gauss", False))
    if shape == "la_casaxps":
        _set("alpha", spec.get("alpha", 1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_alpha", False))
        _set("beta",  spec.get("beta",  1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_beta", False))
        _set("m",     spec.get("m",    50.0), min_=0.0, max_=499.0,
             vary=not spec.get("fix_m", True))

    return p


# ── Cancellation (unit 2, 2026-09-27: long fits via start-then-poll) ────────
# A fit started through /api/fit/start runs in a background thread; the page
# can abandon it (a re-run, a tab switch, an edited model, a closed tab). The
# job passes ``run_fit(..., cancel=callable)``; inside that thread every
# model.fit below receives an ``iter_cb`` that returns True — lmfit's abort —
# once ``cancel()`` is true (checked at most every 0.25 s). Thread-local, so a
# concurrent fit in another thread of the same worker is untouched; and
# WITHOUT a cancel callable no ``iter_cb`` argument is passed at all, so every
# synchronous call is made exactly as before. Never part of fit_kws: the
# request seed cannot see it.
_CANCEL = threading.local()


class FitCancelled(RuntimeError):
    """The job was cancelled while run_fit ran."""


def _cancel_kw() -> dict:
    fn = getattr(_CANCEL, "fn", None)
    if fn is None:
        return {}
    state = {"t": 0.0, "hit": False}

    def iter_cb(params, it, resid, *args, **kws):
        if state["hit"]:
            return True
        now = time.monotonic()
        if now - state["t"] >= 0.25:
            state["t"] = now
            if fn():
                state["hit"] = True
                _CANCEL.hit = True
                return True
        return None

    return {"iter_cb": iter_cb}


def _finite_search_box(params: Parameters, x: np.ndarray,
                       y_sub: np.ndarray) -> dict[str, dict[str, float]]:
    """Give every freely varying parameter a finite box, in place.

    lmfit's ``differential_evolution`` samples its population from the
    parameter bounds and refuses to run when any varying parameter has an
    open one. The page sends ``amplitude_min: 0`` and no ``amplitude_max``,
    and a free DS+G centre has no default window, so without this every
    ordinary request for that method failed (HTTP 422). Only open sides of
    freely varying parameters are closed; fixed and expression-constrained
    parameters, and bounds the request did set, are left alone.

    The box is a SEARCH limit, not a constraint the request made: an
    amplitude reaches max(10 x the largest |background-subtracted
    intensity|, 2 x |start|, 1) (both signs when the request leaves the
    floor open too; the page never does), a centre the fitted energy range.
    A component centred outside a narrowed ROI can need far more than the
    visible intensity, and a box can shape an answer that lies nowhere near
    its sides, so ``_search_then_refine`` refines every boxed search under
    the request's own bounds.

    Returns ``{name: {side: width}}`` for the sides it generated (``width``
    is the extent it gave that side).
    """
    xf = np.asarray(x, float)
    yf = np.asarray(y_sub, float)
    xf, yf = xf[np.isfinite(xf)], yf[np.isfinite(yf)]
    if xf.size == 0 or yf.size == 0:
        raise ValueError("differential_evolution needs finite energy and intensity values")
    x_lo, x_hi = float(xf.min()), float(xf.max())
    span = (x_hi - x_lo) or 1.0
    y_top = float(np.max(np.abs(yf)))
    generated: dict[str, dict[str, float]] = {}
    for name, par in params.items():
        if not par.vary or par.expr is not None:
            continue
        open_min, open_max = not np.isfinite(par.min), not np.isfinite(par.max)
        if not (open_min or open_max):
            continue
        if name.endswith("_amplitude"):
            width = max(10.0 * y_top, 2.0 * abs(par.value), 1.0)
            lo, hi = -width, width
        elif name.endswith("_center"):
            width = span
            lo, hi = min(x_lo, par.value), max(x_hi, par.value)
        else:
            raise ValueError(
                f"differential_evolution needs finite bounds for '{name}'")
        new_min = lo if open_min else par.min
        new_max = hi if open_max else par.max
        # A bound the request did set can sit at or beyond the generated
        # side (centre_min = 300 on a 280-290 eV ROI): keep a real interval.
        if open_max and new_max <= new_min:
            new_max = new_min + width
        if open_min and new_min >= new_max:
            new_min = new_max - width
        par.set(min=new_min, max=new_max)
        generated[name] = {side: width for side, is_open in (("min", open_min), ("max", open_max)) if is_open}
    return generated


def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
    """One differential-evolution candidate: search inside a generated box,
    then refine FROM that solution with ``least_squares`` under the request's
    own (open) bounds.

    Whenever a side was generated the refinement is unconditional (a request
    that bounds everything itself is returned as found). A box can shape the answer without the
    solution lying anywhere near a side (centre and width compensate for a
    capped amplitude), and an unrefined boundary candidate can lose the
    perturb loop's comparison to a worse interior one, so every candidate is
    freed from the box before it is compared or returned. The refined fit
    replaces the search result whenever it converged; if it did not (or
    raised) the search result is returned marked
    ``box_unverified`` (with the sides we generated, so they are not
    reported as bounds) and ``run_fit`` does not call it a success.
    """
    # ``params`` may come from an earlier candidate and still carry that
    # candidate's generated sides: always start from the request's bounds.
    boxed = params.copy()
    for name, (lo, hi) in requested.items():
        boxed[name].set(min=lo, max=hi)
    generated = _finite_search_box(boxed, x, y_sub)
    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws, **_cancel_kw())
    found.box_unverified, found.search_box = bool(generated), generated
    if not generated:
        return found
    free = found.params.copy()
    for name in generated:
        free[name].set(min=requested[name][0], max=requested[name][1])
    # Only what a local solver understands: DE options (seed, popsize, ...)
    # passed through fit_kws would make least_squares raise.
    refine_kws = {"method": "least_squares", "nan_policy": kws.get("nan_policy", "omit")}
    try:
        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws, **_cancel_kw())
    except Exception:
        log.debug("refinement outside the search box raised", exc_info=True)
        return found
    # A converged refinement IS the result: it is a least_squares fit of the
    # requested model under the requested bounds, which is what the default
    # method returns and the acceptance rule accepts. It is deliberately NOT
    # compared with the boxed search's chi-square. least_squares descends
    # from its start, so it cannot end materially above it (four review
    # rounds found no reachable case), but it does end a hair above an EXACT
    # start that sits on a requested bound (the bound transform is degenerate
    # there; the centre moves ~1e-7 eV), by an amount that depends on peak
    # width, position and counts. Every tolerance tried for that comparison
    # produced reachable false failures and no reachable protection.
    if refined.success:
        refined.box_unverified, refined.search_box = False, {}
        return refined
    return found


def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws):
    """A differential-evolution candidate that is never worse than the
    default method from the same start.

    Differential evolution ignores the starting values. On a needle-narrow
    peak in a wide box it can converge, "successfully", with the component
    outside the fitted range (chi-square 1e7 where ``least_squares`` from the
    request's start reaches 1e-4), and the refinement has nothing to descend
    to from there. So a ``least_squares`` fit from the candidate's own start,
    under the request's bounds, competes with the search: a verified result
    beats an unverified one, then the lower chi-square wins.
    """
    searched = _search_then_refine(model, params, requested, y_sub, x, weights, kws)
    start = params.copy()
    for name, (lo, hi) in requested.items():
        start[name].set(min=lo, max=hi)
    try:
        local = model.fit(y_sub, start, x=x, weights=weights,
                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"), **_cancel_kw())
    except Exception:
        log.debug("local candidate from the start raised", exc_info=True)
        return searched
    if not local.success:
        return searched
    local.box_unverified, local.search_box = False, {}
    if searched.box_unverified or not searched.success or local.chisqr < searched.chisqr:
        return local
    return searched


# The methods run_fit accepts, and the two of them that draw random numbers.
# Validated HERE, not only in the /api/fit route: /api/analyze forwards
# options.fit_method straight to run_fit, and lmfit also understands e.g.
# "ampgo", "dual_annealing" and "BasinHopping", which would run with
# numpy's global generator, unseeded.
# ── basinhopping: verified by refinement (unit F2, 2026-09-26) ─────────────
# lmfit 1.3 sets MinimizerResult.success = True before minimising and its
# basinhopping never reads scipy's result, so a basinhopping fit always
# "converged" (sweep H2). scipy's own flag is no better a verdict: on 23 of 24
# sampled committed targets it reports the lowest local minimisation as failed
# (BFGS "Desired error not necessarily achieved due to precision loss") while
# the point equals Trust-Region's minimum (median relative chi2r difference
# 1e-9). Owner decision 2026-09-26: the DE pattern, in full. Basinhopping
# searches; an UNCONDITIONAL least_squares refinement from its point under the
# request's bounds decides — a refinement that converged IS the candidate (no
# chi-square comparison with the search, no tolerance: the DE unit's lesson);
# then that candidate competes with a least_squares fit from the same start
# (verified beats unverified, then the lower chi-square), so basinhopping is
# never worse than the default method from the same start.
def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
    nan_policy = kws.get("nan_policy", "omit")
    start = params.copy()
    for name, (lo, hi) in requested.items():
        start[name].set(min=lo, max=hi)
    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws, **_cancel_kw())
    candidate = None
    try:   # from wherever the search stopped, even an evaluation-budget abort (as DE)
        refined = model.fit(y_sub, found.params.copy(), x=x, weights=weights,
                            method="least_squares", nan_policy=nan_policy, **_cancel_kw())
        if refined.success:
            candidate = refined
    except Exception:
        log.debug("basin-hopping refinement raised", exc_info=True)
    if candidate is None:
        # the search's point could not be verified: it is not a converged fit
        found.success = False
        found.message = ("basin-hopping: the local refinement from the point it found did not converge, "
                         "so the result is not a verified fit")
        candidate = found
    try:
        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy,
                          **_cancel_kw())
    except Exception:
        log.debug("local candidate from the start raised", exc_info=True)
        return candidate
    if local.success and (not candidate.success or local.chisqr < candidate.chisqr):
        return local
    return candidate


# ── The minimum certificate (unit A2, 2026-09-29; owner-accepted in A1) ─────
# A local fit's success flag says only that its optimiser stopped by its own
# rule; the scope check (docs/findings/fit-termination-scope/) found the fit
# returned to the student short of its minimum on 8 of 202 committed targets
# with Trust-Region and 32 of 196 with Levenberg-Marquardt, and perturbed
# restarts and scattered starts "succeeding" > 10 % short by the hundred. The
# verdict is instead: restart Trust-Region from the end point, and again from
# each point that restart improves, until a restart improves chi-square by less
# than Trust-Region's OWN stopping tolerance (scipy's ftol default, read from
# its signature: relative, so scale-free, and no new constant). Out of restarts,
# a non-finite or raising restart = not converged. A restart cut off by its
# evaluation cap (lmfit's ``aborted``) is no verdict: if it lowered chi-square
# the next restart continues from there, otherwise the fit is not converged.
# The point returned is the one the final restart CERTIFIED — the fit itself
# when it was already at its minimum, so a Levenberg-Marquardt fit that reached
# it is returned exactly as MINPACK returned it; a fit the certificate MOVES
# carries Trust-Region's arithmetic (and its rounding jitter, owner decision
# 2026-09-21: regeneration within meaningful precision, not bit-identity).
# Trust-Region restarts, not the student's method: a Levenberg-Marquardt
# restart from a stall point reproduces the stall (the warm restart A1
# removed). Find Peaks has the same rule (autofit.engine._certify_minimum),
# which keeps the restart's point instead — immaterial there.
#
# SCOPE (owner decision 2026-09-29, variant V3 of the A2 measurement,
# docs/findings/runfit-certificate/): the RETURNED fit — after the fit and its
# perturbed restarts have run exactly as before, judged by the flag and
# perturbed from the point the optimiser returned — each scattered start, and
# the required-component refit. Certifying every perturbed restart (V1) or the
# fit before the restarts (V2) changed the points they start from and with it
# the basin they reach: identical presses then differed by 16–37 pp (V1
# Trust-Region) and > 20 pp (V2 Levenberg-Marquardt); V3's Levenberg-Marquardt
# presses agree to 0.074 pp (main: 0.23 pp) at a median +0.04 s.
CERTIFY_FTOL = float(inspect.signature(_scipy_least_squares).parameters["ftol"].default)
CERTIFY_MAX_RESTARTS = 50        # a count: A1 measured 1-21 restarts on 208 real fits
_CERTIFIED_METHODS = ("leastsq", "least_squares", "nelder")   # the local methods; DE / basinhopping end in their own refinement


def _certify_fit(model, result, y_sub, x, weights, nan_policy, max_nfev=None):
    """(point, certified, restarts, why) — see the block comment above. A
    caller's ``max_nfev`` limits each restart too (a restart it cuts off is
    no verdict), so the certificate never exceeds a limit the request set."""
    cap = {} if max_nfev is None else {"max_nfev": max_nfev}
    def chi_of(r):
        return float(r.chisqr) if r.chisqr is not None else float("nan")
    current, chi = result, chi_of(result)
    if not np.isfinite(chi):
        return current, False, 0, "the fit's chi-square is not finite"
    for k in range(1, CERTIFY_MAX_RESTARTS + 1):
        try:
            r = model.fit(y_sub, current.params.copy(), x=x, weights=weights,
                          method="least_squares", nan_policy=nan_policy, **cap, **_cancel_kw())
        except Exception as exc:
            log.debug("certificate restart raised", exc_info=True)
            return current, False, k, f"a restart from the end point failed ({type(exc).__name__})"
        new = chi_of(r)
        if not np.isfinite(new):
            return current, False, k, "a restart from the end point gave a non-finite chi-square"
        if getattr(r, "aborted", False):
            if new < chi:
                current, chi = r, new
                continue
            return current, False, k, "a restart from the end point was cut off by its evaluation limit"
        improvement = (chi - new) / chi if chi > 0 else 0.0
        if improvement < CERTIFY_FTOL:
            return current, True, k, ""
        current, chi = r, new
    return current, False, CERTIFY_MAX_RESTARTS, (
        f"restarting from where it stopped still lowered chi-square after {CERTIFY_MAX_RESTARTS} restarts")


def _certified(model, result, y_sub, x, weights, kws):
    """``result`` judged by the certificate: the certified point, with
    ``success`` = the verdict and ``certificate`` = what it took."""
    flagged, flag_message = bool(result.success), result.message
    point, ok, restarts, why = _certify_fit(model, result, y_sub, x, weights, kws.get("nan_policy", "omit"),
                                            kws.get("max_nfev"))
    point.success = bool(ok)
    point.certificate = {"certified": bool(ok), "restarts": int(restarts), "moved": point is not result,
                         "optimiser_flag": flagged}
    # how far the continued fit carried each centre from where the optimiser stopped (by parameter name;
    # run_fit maps them to components for the page's displacement notice)
    point.certificate_centre_moves = {
        name: float(point.params[name].value - result.params[name].value)
        for name in point.params if name.endswith("_center") and name in result.params}
    if not ok:
        point.message = "The fit did not reach a minimum: " + why + "."
    elif point is not result or not flagged:
        point.message = ("Reached a minimum (checked by restarting from the end point); the optimiser itself "
                         "had stopped with: " + str(flag_message))
    return point


_FIT_METHODS = ("leastsq", "least_squares", "nelder", "differential_evolution", "basinhopping")
_STOCHASTIC_METHODS = ("differential_evolution", "basinhopping")

def _canonical(value):
    """Spelling-independent form: keys sorted, every number a float (a browser
    writes 1.0 as ``1``; -0.0 folds to 0.0), arrays as lists."""
    if isinstance(value, dict):
        return {str(k): _canonical(value[k]) for k in sorted(value, key=str)}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [_canonical(v) for v in value]
    if isinstance(value, (bool, np.bool_)) or value is None or isinstance(value, str):
        return bool(value) if isinstance(value, np.bool_) else value
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value) + 0.0
    return repr(value)


ENDPOINT_AVG_MAX = 50   # the page field's own max (#bg-endpoint-avg max="50")


def check_endpoint_avg(raw) -> int:
    """Endpoint averaging as every reader takes it, or a refusal (owner 2026-10-11): a whole
    number from 1 to ENDPOINT_AVG_MAX — a JSON integer, or an integral finite float such as
    3.0. Anything else is REFUSED (ValueError, HTTP 400), never clamped: the routes used to
    read max(1, int(x)), so 0 or -5 fitted at 1 and 1e21 at the window's quarter while the
    page's helpers read 1e21 as 1 (logged 2026-10-10, fit recording round 3)."""
    import math
    import numbers
    ok = not isinstance(raw, (bool, np.bool_)) and (
        isinstance(raw, numbers.Integral)
        or (isinstance(raw, numbers.Real) and math.isfinite(raw) and float(raw).is_integer()))
    if not ok or not 1 <= int(raw) <= ENDPOINT_AVG_MAX:
        raise ValueError(f"endpoint_avg must be a whole number from 1 to {ENDPOINT_AVG_MAX}, got {raw!r}")
    return int(raw)


def _avg_k(n: int, n_avg) -> int:
    """The number of points each edge level averages: k = min(n_avg, n // 4), k >= 1
    (1 below four points) — _edge_levels' rule."""
    return max(1, min(int(n_avg), n // 4)) if n >= 4 else 1


def _background_effect(method, n_roi, i0, i1, endpoint_avg, manual_bg) -> dict:
    """What the background is computed FROM, by its effect (the seed's background
    term since v2): the method, the window (where the method reads one), the
    averaging as it acts (k, not the field), and a manual background's anchors in
    energy order. Two requests with equal effects compute the same background."""
    m = (method or "").lower()
    if m in ("none", "flat", ""):
        return {"method": "none"}
    if m == "manual":
        anchors = manual_bg or []
        if len(anchors) >= 2:
            return {"method": "manual", "anchors": sorted([float(a[0]), float(a[1])] for a in anchors)}
        return {"method": "manual-line", "k": _avg_k(n_roi, endpoint_avg)}   # the line through the ROI's ends
    return {"method": m, "window": [int(i0), int(i1)], "k": _avg_k(int(i1) - int(i0), endpoint_avg)}


def _request_seed(x, counts, background_effect, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
    """The seed: the first 32 bits of ``_request_digest`` (unchanged by seal 1a′, which only names the
    digest)."""
    return int.from_bytes(bytes.fromhex(_request_digest(x, counts, background_effect, shapes, prefixes, params,
                                                        fit_kws=fit_kws, n_perturb=n_perturb))[:4], "little")


def _request_digest(x, counts, background_effect, shapes, prefixes, params, *, fit_kws, n_perturb) -> str:
    """SHA-256 (hex) of the fit's INPUTS, by effect — the seed's derivation before it is cut to 32 bits.
    Reported with every fit as ``request_digest`` whatever the seed's source (seal 1a′ Codex round 8): it
    binds a recorded response to every number the fit started from, so the verification needs no
    enumeration of starts the fit routes would refuse.

    The seed for every random draw of one fit: a pure function of the fit's
    INPUTS — energies and counts (little-endian float64), what the background is
    computed from (`_background_effect`: method, window, averaging as it acts,
    anchors), the lineshape of each component in fitting order, each lmfit
    parameter's effective role, the method, solver options and ``n_perturb``.

    v2 (background math, owner 2026-10-03): the background enters by its INPUTS,
    not as the computed curve, so a numerical change in a derived quantity (a
    stop tolerance, an exact evaluation) no longer redraws the restarts — v1
    hashed the curve, and a 1e-7-of-span change in it moved 8-JT C 1s fits between
    basins by up to 28 pp.

    A parameter's role is what it can do to the fit: a constrained one is its
    expression (its own start value and bounds are overridden), a fixed one
    is its value (its bounds cannot act), a free one is its value and bounds.
    Settings are hashed by their EFFECT, never as sent, so nothing the fit
    ignores can change the draws: a peak's name or colour, the
    ``fix_gl_ratio`` the page still sends for a Gaussian, stale shape
    parameters kept after a shape switch, an ``endpoint_avg`` beyond what the
    window's quarter lets act (k) or one a background does not read (none,
    manual anchors), anchor order, and the peaks' internal IDs —
    parameter names and constraint references are rewritten by component
    POSITION (``prefixes`` lists each component's lmfit prefix in fitting
    order), because the page never reuses an ID and the same model rebuilt
    after deleting a peak would otherwise fit differently. (Measured in review: each such
    no-op edit moved an area fraction by 15-45 percentage points while the
    request was hashed as sent.) It is a seed, not an identity: 32 bits
    collide, never use it as a cache key. Changing this derivation changes
    what saved projects regenerate: bump the version tag and say so.
    """
    kws = dict(fit_kws or {})
    solver = {k: v for k, v in dict(kws.pop("fit_kws", None) or {}).items() if k != "seed"}
    # longest prefix first so "p1_" cannot match inside "p11_"
    alias = sorted(((pre, f"c{k}_") for k, pre in enumerate(prefixes)), key=lambda a: -len(a[0]))

    def by_position(text):
        for pre, pos in alias:
            text = re.sub(r"(?<![A-Za-z0-9_])" + re.escape(pre), pos, text)
        return text

    roles = []
    for name, par in params.items():
        name = by_position(name)
        if par.expr is not None:
            roles.append([name, "expr", by_position(par.expr)])
        elif not par.vary:
            roles.append([name, "fixed", par.value])
        else:
            roles.append([name, "free", par.value, par.min, par.max])
    rest = _canonical({"shapes": list(shapes), "params": roles, "fit_kws": kws, "solver": solver,
                       "n_perturb": n_perturb, "background": background_effect})
    h = hashlib.sha256(SEED_TAG.encode() + b"\0")
    for arr in (x, counts):
        a = np.ascontiguousarray(arr, dtype="<f8") + 0.0       # -0.0 -> 0.0 (the CSV path keeps "-0.00")
        h.update(str(a.size).encode() + b"\0" + a.tobytes())
    h.update(json.dumps(rest, sort_keys=True, separators=(",", ":"), allow_nan=True).encode())
    return h.hexdigest()                                        # the seed is its first 32 bits (scipy's limit)


# ── Scattered starts: is the fit the only solution the data allow? ────────────
# Measured on the lab's 202 committed fit targets (docs/findings/
# 2026-09-fit-determinacy.md): the default method's result is more than 5 pp of
# area fraction from the best known solution on 7.8 % of not-yet-fitted starts;
# a second METHOD from the same start shares the minimum too often to help;
# three more fits of the SAME method from scattered starts expose it (3.2 %),
# at ~0.6 s. The fit the student asked for is never replaced (owner decision:
# the lowest chi-square can be a chemically absurd relocation of a component);
# solutions with a lower reduced chi-square are returned beside it, with how
# far each component moved from the student's start.
MAX_N_STARTS = 10
_STARTS_METHODS = ("leastsq", "least_squares", "nelder")     # the global methods already search
_SAME_FRACTION_PP = 1.0      # "same solution": every area fraction within 1 pp ...
_SAME_CENTRE_EV = 0.1        # ... and every centre within 0.1 eV (presentation grain, not science)
_LOWER_CHI_REL = 1e-3        # an alternative's reduced chi-square is lower by more than 0.1 %


def _scattered_start(params: Parameters, rng) -> Parameters:
    """One scattered start, anchored to the REQUEST's start (``params`` as
    built from the request, never a fitted solution, which jitters): free
    amplitudes x/÷ 3 (sign kept), free widths x/÷ 1.5, free centres ± 0.5 eV —
    each clamped into the request's bounds, a thousandth of the interval off
    a finite wall (lmfit's bound transform has zero gradient ON a wall) —
    and every other freely varying parameter with finite bounds redrawn
    inside the middle 90 % of its range. Fixed and constrained parameters,
    and the integer CasaXPS ``m``, are left alone."""
    out = params.copy()
    for name, par in out.items():
        if not par.vary or par.expr is not None:
            continue
        lo, hi = par.min, par.max
        both = np.isfinite(lo) and np.isfinite(hi)
        edge = 1e-3 * (hi - lo) if both else 0.0

        def clamp(v):
            if np.isfinite(lo):
                v = max(v, lo + edge)
            if np.isfinite(hi):
                v = min(v, hi - edge)
            return v

        if name.endswith("_amplitude"):
            sign = -1.0 if par.value < 0 else 1.0
            value = clamp(sign * max(abs(par.value), 1.0) * float(np.exp(rng.uniform(-np.log(3), np.log(3)))))
        elif name.endswith("_fwhm"):
            value = clamp(par.value * float(np.exp(rng.uniform(-np.log(1.5), np.log(1.5)))))
        elif name.endswith("_center"):
            value = clamp(par.value + float(rng.uniform(-0.5, 0.5)))
        elif name.endswith("_m"):
            continue
        elif both:
            value = float(rng.uniform(lo + 0.05 * (hi - lo), hi - 0.05 * (hi - lo)))
        else:
            continue
        par.set(value=float(value))
    return out


def _component_of(model, spec):
    """The component model of ``spec`` and the parameter names that are ITS OWN: its model's
    ``param_names``, never a prefix match — ids "1" and "1_x" give prefixes "p1_" and "p1_x_",
    and "p1_x_center" starts with both (seal 1a′ Codex round 1)."""
    prefix = f"p{spec['id']}_"
    comp = next(c for c in model.components if c.prefix == prefix)
    return comp, prefix, list(comp.param_names)


def _solution_components(model, result, peak_specs, x) -> list[dict[str, Any]]:
    """Per component, in the request's order: area, area %, and every fitted
    parameter value (what the page needs to show and to apply a solution)."""
    comps = []
    for spec in peak_specs:
        comp, prefix, names = _component_of(model, spec)
        area = float(abs(trapezoid(comp.eval(result.params, x=x), x)))
        values = {n[len(prefix):]: float(par.value) for n, par in result.params.items() if n in names}
        comps.append({"id": spec["id"], "area": area, "params": values})
    total = sum(c["area"] for c in comps)
    for c, spec in zip(comps, peak_specs):
        c["area_percent"] = 100.0 * c["area"] / total if total > 0 else 0.0
        c["center_shift_from_start"] = c["params"]["center"] - float(spec["center"])
    return comps


def _same_solution(a, b) -> bool:
    """Same decomposition: every area fraction within 1 pp and every centre
    within 0.1 eV, COMPONENT BY COMPONENT (by the request's ids). No
    permutations: "C-O" and "C=O" trading places is a different chemical
    reading even when both are GL lines, and the page shows fractions by
    name. Two truly interchangeable components that swapped labels are
    therefore counted as a different solution of equal chi-square — which is
    what they are: the data do not say which label goes where."""
    return (max(abs(p["area_percent"] - q["area_percent"]) for p, q in zip(a, b)) <= _SAME_FRACTION_PP
            and max(abs(p["params"]["center"] - q["params"]["center"]) for p, q in zip(a, b)) <= _SAME_CENTRE_EV)


def _largest_shift(comps) -> dict[str, Any]:
    c = max(comps, key=lambda c: abs(c["center_shift_from_start"]))
    return {"id": c["id"], "ev": c["center_shift_from_start"]}


def _scattered_starts(n_starts, fit_once, model, start_params, result, peak_specs, x, rng) -> dict[str, Any]:
    """Run the starts and sort what they found relative to THE FIT (``result``),
    which this function never changes."""
    fit_comps = _solution_components(model, result, peak_specs, x)
    fit_chi = float(result.redchi)
    clusters: list[dict[str, Any]] = []
    n_converged = n_same = 0
    for _ in range(n_starts):
        try:
            trial = fit_once(_scattered_start(start_params, rng))
        except Exception:
            log.debug("scattered start raised", exc_info=True)
            continue
        if not trial.success or trial.redchi is None or not np.isfinite(trial.redchi):
            continue
        n_converged += 1
        comps = _solution_components(model, trial, peak_specs, x)
        if _same_solution(comps, fit_comps):
            n_same += 1
            continue
        home = next((c for c in clusters if _same_solution(comps, c["components"])), None)
        if home is None:
            clusters.append({"chi2r": float(trial.redchi), "n_starts": 1, "components": comps})
        else:
            home["n_starts"] += 1
            if trial.redchi < home["chi2r"]:
                home.update(chi2r=float(trial.redchi), components=comps)
    lower = sorted((c for c in clusters if c["chi2r"] < fit_chi * (1.0 - _LOWER_CHI_REL)), key=lambda c: c["chi2r"])
    other = [c for c in clusters if c not in lower]
    for alt in lower:
        alt["largest_centre_shift_from_start"] = _largest_shift(alt["components"])
        alt["largest_fraction_difference_pp"] = max(
            abs(p["area_percent"] - q["area_percent"]) for p, q in zip(alt["components"], fit_comps))
    return {
        "ran": True, "n_run": n_starts, "n_converged": n_converged, "n_same_as_fit": n_same,
        # solutions that are NOT better: counted, never listed (they are what a bad start looks like)
        "n_in_alternatives": sum(c["n_starts"] for c in lower),
        "n_not_better_elsewhere": sum(c["n_starts"] for c in other),
        "not_better_chi2r": sorted(c["chi2r"] for c in other),
        "fit": {"chi2r": fit_chi, "largest_centre_shift_from_start": _largest_shift(fit_comps),
                "components": [{k: c[k] for k in ("id", "area_percent", "center_shift_from_start")} for c in fit_comps]},
        "alternatives": lower,
    }


# ── "Not supported by the data": the one statement that needs no intensity floor
# (six were tried for the Auto-Fit anchor and each rejected real components or
# accepted residue). With the OTHER components held at their fitted values,
# taking this component out of the model must make the fit to the data
# significantly worse:
#     chi2_with    = sum w (y - fitted)^2          w = the fit's own weights
#     chi2_without = sum w (y - fitted + component)^2
#     F = ((chi2_without - chi2_with) / p) / (chi2_with / dof)
# A component driven to its amplitude floor, pinned on a bound or fitted to
# numerical residue has chi2_without <= chi2_with (removing it costs nothing).
# Owner decision 2026-09-18: such a component is an explicit OUTCOME — the fit
# did not determine it — and its centre, width and sigma are not reported.
# Known limits, same as the Auto-Fit anchor: a gross single-channel artefact
# inflates chi2_with and can mark a real component unsupported; redundancy
# under overlap is NOT detected (a refit without the component is the test for
# that; step (c) does it for the Auto-Fit anchor). Threshold F >= 10 (~ p 1e-9
# at these sizes); on the 202 committed targets resolved components have
# F >= 1.1e3 and 3 of 752 components are unsupported (F 0.95-3.9).
SUPPORT_MIN_F = 10.0


def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
    w2 = np.asarray(weights, float) ** 2
    r = np.asarray(y_sub, float) - np.asarray(fitted_sub, float)
    ok = np.isfinite(r) & np.isfinite(comp_y) & np.isfinite(w2)
    chi_with = float(np.sum(w2[ok] * r[ok] ** 2))
    chi_without = float(np.sum(w2[ok] * (r[ok] + np.asarray(comp_y, float)[ok]) ** 2))
    delta = chi_without - chi_with
    p = max(1, int(n_free_comp))
    dof = max(1, int(ok.sum()) - int(n_free_total))
    if delta <= 0:
        f = 0.0
    elif chi_with == 0:
        f = float("inf")
    else:
        f = (delta / p) / (chi_with / dof)
    return {"f": None if not np.isfinite(f) else f, "delta_chi2": delta,
            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}


# ── "Is this component REQUIRED?" — the refit test ───────────────────────────
# `support` (above) holds the OTHER components at their fitted values, so it
# cannot see redundancy under overlap: a component the others could absorb if
# they were refitted still passes. The test for that is the refit itself:
# remove the component, refit the rest from their fitted values under the
# request's own bounds, and compare the fit to the data with and without it:
#     F = ((chi2_without_refit - chi2_with) / p) / (chi2_with / dof)
# p = the component's free parameters, dof = n - nvarys of the full model.
# One extra fit, so it is done only when asked for (Auto-Fit asks for its
# charge-reference anchor: an anchor that is not required must not set the
# energy reference of a whole spectrum). Same threshold as `support`.
def _component_required(fit_reduced, params_full, removed_names, y_sub, weights,
                        chi2_with, n_free_comp, n_free_total) -> dict[str, Any]:
    """``fit_reduced(params)`` is the run's own fitter for the reduced model
    (the same candidate machinery and seeding the fit used, so differential
    evolution's box/refinement and the request seed apply to the refit too).
    ``removed_names`` are the parameter names OWNED by the removed component and everything linked
    to it, transitively (``_component_of``: exact membership, never a prefix — seal 1a′). The reduced start is built in dependency order: plain
    parameters first, expressions after, so a child ordered before its parent
    in the request still resolves."""
    removed_names = set(removed_names)
    kept = [(name, par) for name, par in params_full.items() if name not in removed_names]
    # ALL retained parameters exist before any expression is assigned, so a
    # chain of links in any request order resolves (lmfit evaluates an
    # expression when it is set).
    start = Parameters()
    for name, par in kept:
        start.add(name, value=par.value, min=par.min, max=par.max, vary=par.vary)
    for name, par in kept:
        if par.expr:
            start[name].set(expr=par.expr)
    refit = fit_reduced(start)
    chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
    if not refit.success or getattr(refit, "box_unverified", False):
        # F2 (2026-09-26): a refit that did not converge establishes nothing
        # (nor does a differential-evolution candidate whose search box no
        # refinement verified — the main fit's acceptance rule rejects it too;
        # Codex round 1)
        # either way — its chi-square is wherever the optimiser stopped (a
        # redundant anchor read "required", F 992, from a refit stopped early;
        # F 1.17 once it completed). No verdict; the caller decides.
        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
                "refit_converged": False, "reason": "refit_not_converged",
                "message": str(getattr(refit, "message", "") or "")[:200]}
    delta = chi2_without - chi2_with
    p = max(1, int(n_free_comp))
    dof = max(1, len(y_sub) - int(n_free_total))
    # No tolerance of any kind (Codex rounds 2-3: a floor on the chi-square
    # change relative to the data's power, and then an "exactness" cutoff on
    # the reduced fit, each masked a resolved anchor at high dynamic range —
    # the same lesson as the DE unit). Known limit, accepted: on NOISE-FREE
    # data whose full fit is numerically exact (chi2_with ~ 1e-28) F is not
    # meaningful and a truly redundant component (two identical half-amplitude
    # components) reports "required"; real data never fit to machine precision.
    if not np.isfinite(chi2_without):
        f, required = None, True                     # the rest could not even be fitted without it
    elif delta <= 0:
        f, required = 0.0, False
    elif chi2_with == 0:
        f, required = None, True
    else:
        f = (delta / p) / (chi2_with / dof)
        required = f >= SUPPORT_MIN_F
    return {"required": bool(required), "f": f, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
            "refit_converged": bool(refit.success)}


# ─────────────────────────────────────────────────────────────────────────────
# Main fitting API
# ─────────────────────────────────────────────────────────────────────────────

def _determined(n_free, n_data) -> bool:
    """Determinacy (unit F2): fewer free parameters than finite data points — run_fit's refusal and
    the verification's check, one rule."""
    return n_free < n_data


def _normalise_fit_kws(fit_kws):
    """``(fit_kws, caller_seed, method)``: the method case-folded and checked, a caller's seed taken
    out of the solver options and checked. Shared by ``run_fit`` and the verification (seal 1a′)."""
    fit_kws = dict(fit_kws or {})
    method = str(fit_kws.get("method", "leastsq")).lower()
    if method not in _FIT_METHODS:
        raise ValueError(f"Unknown fit method '{fit_kws.get('method')}'. Choices: {list(_FIT_METHODS)}")
    fit_kws["method"] = method
    # A caller's seed is consumed HERE: it replaces the request-derived one
    # and is never forwarded as a solver option (least_squares, leastsq and
    # nelder reject a 'seed' keyword).
    solver_kws = dict(fit_kws.pop("fit_kws", None) or {})
    caller_seed = solver_kws.pop("seed", None)
    if solver_kws:
        fit_kws["fit_kws"] = solver_kws
    if caller_seed is not None and (
            isinstance(caller_seed, (bool, np.bool_)) or not isinstance(caller_seed, (int, np.integer))
            or not 0 <= int(caller_seed) < 2 ** 32):
        raise ValueError("fit_kws.fit_kws.seed must be an integer in [0, 2**32)")
    return fit_kws, caller_seed, method


def _assemble_background(energy, counts, background_method, bg_start_idx, bg_end_idx, endpoint_avg, manual_bg):
    """run_fit's WHOLE background over the fitted region (seal 1a′, V6.5: one function, called by
    ``run_fit`` and by the verification): the window normalisation, every method, the flat hold
    beyond the window, and the background BY ITS EFFECT. Returns ``(bg, bg_cert, bg_effect,
    bg_method)``; raises ``BackgroundNotConverged`` / ``ValueError`` exactly as the fit did."""
    # The fit runs on the ENTIRE incoming ROI; bg_start_idx / bg_end_idx
    # narrow only the anchor window used to construct the background
    # curve. Reusing the slice for both was the bug where putting bg
    # anchors inside the ROI silently chopped the fit window — and the
    # reported χ², residuals, and σ — down to that same sub-slice.
    i0 = bg_start_idx if bg_start_idx is not None else 0
    i1 = bg_end_idx if bg_end_idx is not None else len(energy)
    i0 = max(0, i0)
    i1 = min(len(energy), i1)
    # Normalize the user-supplied anchor pair: reversed order is a valid
    # choice — the frontend sends bg-start = higher BE and bg-end = lower
    # BE, so the index order depends on whether the data array is
    # BE-ascending or BE-descending. Treat the pair as an unordered
    # anchor window regardless of direction.
    if i0 > i1:
        i0, i1 = i1, i0
    # Bail to the full ROI only if the normalized window is genuinely
    # unusable (< 2 points): the integral / interp / linear-fit
    # functions below all need at least two distinct anchor points.
    if i1 - i0 < 2:
        i0, i1 = 0, len(energy)

    x = energy
    y = counts
    x_bg = energy[i0:i1]
    y_bg = counts[i0:i1]

    # ── Background ────────────────────────────────────────────────────────────
    # Integral backgrounds (Shirley, Tougaard, Smart variants) are
    # physically defined only between the user's two anchor points: the
    # integral represents inelastic-loss cumulation through the peaks
    # *between* those anchors. Computing them over the full ROI would
    # let peaks outside the anchor window contribute to the loss
    # integral, which violates the model's premise. We therefore
    # compute them on [i0:i1] and flat-hold the endpoint value across
    # the rest of the ROI — Shirley/Tougaard asymptote to the anchor
    # values by construction, so constant extension is the least-bad
    # continuation. Linear backgrounds are extrapolated across the
    # full ROI (the line is well-defined outside the anchor window).
    bg_method = background_method.lower()
    bg_inner: np.ndarray | None = None
    bg_cert: dict[str, Any] = {}          # the integral methods' certificate (compute_background)

    if bg_method == "manual":
        # no anchors sent (an omitted / null manual_bg) is the page's "fewer than two
        # anchors": the line through the ROI's ends — never a silent zero (Codex impl round 6)
        manual_bg = manual_bg if manual_bg is not None else []
        # manual_bg is a list of [be, intensity] anchor points from the
        # frontend. The anchors are BE-anchored (independent of i0/i1),
        # so interpolate them across the full ROI grid.
        if len(manual_bg) >= 1:
            _check_anchors(manual_bg)                     # every anchor, even a lone one
        if len(manual_bg) >= 2:
            bg = manual_anchor_background(x, manual_bg, _span(y))   # raises BackgroundNotConverged
        else:
            bg = linear_background(x, y, n_avg=endpoint_avg)
    elif bg_method in _BG_LABELS:
        # certified: a background that does not satisfy its statement raises
        # BackgroundNotConverged and no fit is made against it
        _region_in_order(x, bg_method)                  # the flat hold below is by energy
        bg_inner = compute_background(x_bg, y_bg, bg_method, n_avg=endpoint_avg, report=bg_cert)
    elif bg_method == "linear":
        # Extrapolate the line through (E[i0], y[i0]) ↔ (E[i1-1], y[i1-1])
        # across the full ROI. The line is well-defined everywhere, so
        # constant extension would discard real information.
        # (raises BackgroundNotConverged when the window's ends share an energy but
        # not an intensity: no line passes through both)
        # through the window's two edge LEVELS (the means of its first / last k points,
        # owner 2026-10-03), extrapolated across the ROI
        lo, hi = _exact_edge_levels(y_bg, endpoint_avg)
        bg = _line_through(x, x[i0], lo, x[i1 - 1], hi, _span(y_bg))
    elif bg_method in ("none", "flat", ""):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{background_method}'")

    if bg_inner is not None:
        # Embed the anchor-window integral background into a full-ROI
        # array; flat-hold the endpoint value outside [i0, i1]. In the
        # common case where the user keeps bg anchors at the ROI edges
        # this is a no-op (i0=0, i1=len(y)).
        bg = np.zeros_like(y)
        if len(bg_inner) > 0:
            bg[i0:i1] = bg_inner
            if i0 > 0:
                bg[:i0] = bg_inner[0]
            if i1 < len(y):
                bg[i1:] = bg_inner[-1]

    # the background BY ITS EFFECT — one reading, for the seed and for the recorded verdict;
    # taken once the background exists (its anchors have been checked: a malformed one refuses
    # the fit above, never here)
    bg_effect = _background_effect(background_method, len(y), i0, i1, endpoint_avg, manual_bg)
    return bg, bg_cert, bg_effect, bg_method


def _build_model(peak_specs):
    """``(ordered, composite_model, all_params)``: the lmfit model of a request, masters first —
    the fit's own construction, shared with the verification (seal 1a′)."""
    # Sort so unconstrained (master) peaks come before constrained ones
    ordered = sorted(
        peak_specs,
        key=lambda s: 0 if s.get("constrain_to") is None else 1,
    )

    composite_model: Model | None = None
    all_params = Parameters()

    for spec in ordered:
        shape = spec.get("shape", "pseudo_voigt_gl")
        if shape not in _SHAPE_FUNCS:
            raise ValueError(f"Unknown peak shape '{shape}'. Choices: {AVAILABLE_SHAPES}")
        func = _SHAPE_FUNCS[shape]
        prefix = f"p{spec['id']}_"
        m = Model(func, prefix=prefix)
        p = _make_peak_params(m, spec, prefix, ordered)
        all_params.update(p)
        composite_model = m if composite_model is None else composite_model + m

    if composite_model is None:
        raise RuntimeError("No peaks were built")
    return ordered, composite_model, all_params


def _run_fit_impl(
    energy: np.ndarray,
    counts: np.ndarray,
    peak_specs: list[dict[str, Any]],
    background_method: str = "shirley",
    bg_start_idx: int | None = None,
    bg_end_idx: int | None = None,
    charge_shift_ev: float = 0.0,
    fit_kws: dict | None = None,
    n_perturb: int = 0,
    manual_bg: list | None = None,
    endpoint_avg: int = 1,
    n_starts: int = 0,
    require_component=None,
) -> dict[str, Any]:
    """
    Run XPS peak fitting and return a serialisable result dict.

    Parameters
    ----------
    energy            : 1‑D array of binding energies (eV)
    counts            : 1‑D array of intensities (counts / CPS)
    peak_specs        : list of peak specification dicts (see _make_peak_params)
    background_method : 'shirley' | 'linear' | 'none'
    bg_start_idx      : slice start for background region (None → 0)
    bg_end_idx        : slice end for background region   (None → len)
    charge_shift_ev   : shift to apply to energy axis before fitting
    fit_kws           : extra kwargs forwarded to lmfit minimize

    Returns
    -------
    dict with keys: energy, fitted_y, background_y, residuals,
                    individual_peaks, statistics, charge_shift_applied, success
    """
    # One computation dtype: the weights are a function of the counts AND of
    # the precision they are held in (float32 counts give weights that differ
    # at 1e-8 and a different fit), and the seed hashes float64.
    energy = np.asarray(energy, dtype=float)
    counts = np.asarray(counts, dtype=float)
    if len(energy) != len(counts):
        raise ValueError("energy and counts must have the same length")
    if not peak_specs:
        raise ValueError("At least one peak specification is required")
    # Reject self/cyclic spin-orbit constraints before building lmfit exprs (F11)
    _validate_constraint_graph(peak_specs)

    # Apply charge correction
    energy = energy + charge_shift_ev

    fit_kws, caller_seed, method = _normalise_fit_kws(fit_kws)
    endpoint_avg = check_endpoint_avg(endpoint_avg)

    x = energy
    y = counts
    bg, bg_cert, bg_effect, bg_method = _assemble_background(
        x, y, background_method, bg_start_idx, bg_end_idx, endpoint_avg, manual_bg)
    y_sub = y - bg

    # Poisson weights: σ = √(raw counts), weight = 1/σ
    # Use raw counts (before background subtraction) for uncertainty estimate,
    # since the noise comes from the total photon counting statistics.
    # Floor at 1.0 to avoid division by zero for zero-count channels.
    sigma = np.sqrt(np.maximum(y, 1.0))
    weights = 1.0 / sigma

    # ── Build composite lmfit model ───────────────────────────────────────────
    ordered, composite_model, all_params = _build_model(peak_specs)
    if require_component is not None:
        ids = [str(spec["id"]) for spec in peak_specs]
        if str(require_component) not in ids:
            raise ValueError(f"require_component '{require_component}' is not one of the peaks")
        if len(ids) < 2:
            raise ValueError("require_component needs at least two components")

    # Every random draw below (the perturbed restarts; the populations of the
    # two stochastic methods, which lmfit otherwise takes from numpy's GLOBAL
    # generator) comes from this one seed, so an identical request gives
    # identical DRAWS. (Not an identical Trust-Region result: see CLAUDE.md,
    # "Reproducibility".)
    request_digest = _request_digest(
        x, y, bg_effect,
        [spec.get("shape", "pseudo_voigt_gl") for spec in ordered],
        [f"p{spec['id']}_" for spec in ordered], all_params,
        fit_kws=fit_kws, n_perturb=n_perturb)
    if caller_seed is not None:
        random_seed = int(caller_seed)
    else:
        random_seed = int.from_bytes(bytes.fromhex(request_digest)[:4], "little")   # = _request_seed
    # spawn(3) yields the same first two children as spawn(2): adding the
    # scattered-starts stream leaves every existing draw (and its pins) alone.
    perturb_rng, solver_rng, starts_rng = (np.random.default_rng(child)
                                           for child in np.random.SeedSequence(random_seed).spawn(3))
    if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
        raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")

    # ── Determinacy (unit F2, 2026-09-26) ─────────────────────────────────────
    # "Nothing is a fit unless it converged and is determined." With at least
    # as many free parameters as data points the model can pass through every
    # point: lmfit reports redchi = chi2 / max(1, nfree) as if it were a fit,
    # and the support / required F tests clamp their dof to 1, so such a model
    # read as a near-perfect, fully supported fit (sweep M2: 6 points, 2 GL
    # components, chi2r 2.8e-6, both "supported"). A count, not a threshold:
    # zero or negative degrees of freedom is refused outright.
    n_free_request = sum(1 for par in all_params.values() if par.vary and not par.expr)
    n_data_request = int(np.count_nonzero(np.isfinite(y_sub)))
    if not _determined(n_free_request, n_data_request):
        raise ValueError(
            f"The model is not determined by these data: {n_free_request} free parameters for "
            f"{n_data_request} data points leaves no degrees of freedom. Widen the fitted range, "
            f"remove components or lock parameters.")

    # ── Fit ───────────────────────────────────────────────────────────────────
    kws = {"method": "leastsq", "nan_policy": "omit"}
    if fit_kws:
        kws.update(fit_kws)

    # Differential evolution needs a finite box and the page leaves amplitudes
    # open above: each candidate is searched in a generated box and then
    # refined under the request's own bounds (_search_then_refine). Every
    # other method fits the request's parameters exactly as before.
    def seeded(call_kws):
        """``call_kws`` with a fresh solver seed for the stochastic methods
        (one per minimisation, else every perturbed restart of differential
        evolution would replay the same population); unchanged otherwise."""
        if call_kws.get("method") not in _STOCHASTIC_METHODS:
            return call_kws
        solver_kws = dict(call_kws.get("fit_kws") or {})
        solver_kws["seed"] = int(solver_rng.integers(0, 2 ** 32 - 1))
        return {**call_kws, "fit_kws": solver_kws}

    # One fitter for any (sub)model of this request: the DE candidate machinery
    # when the method is differential evolution, else a plain seeded fit. The
    # scattered starts and the required-component refit go through it too.
    requested_bounds = {name: (par.min, par.max) for name, par in all_params.items()}

    def fit_model(model, params, certify=True):
        if kws.get("method") == "differential_evolution":
            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
            return _global_or_local_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
        if kws.get("method") == "basinhopping":
            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
            return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
        fitted = model.fit(y_sub, params, x=x, weights=weights, **seeded(kws), **_cancel_kw())
        if certify and kws.get("method") in _CERTIFIED_METHODS:
            # each scattered start and the required-component refit are judged
            # by the certificate, never by the optimiser's flag (unit A2); the
            # fit and its perturbed restarts pass certify=False and the WINNER
            # is certified after the search (V3)
            fitted = _certified(model, fitted, y_sub, x, weights, kws)
        return fitted

    def fit_once(params):
        return fit_model(composite_model, params)

    # ── Diagnostic logging: BEFORE optimisation ──────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT START ═══  method=%s  n_data=%d", kws.get('method'), len(y_sub))
        for pname, par in sorted(all_params.items()):
            log.debug("  BEFORE  %-30s value=%12.6f  vary=%-5s  expr=%s  min=%s  max=%s",
                      pname, par.value, str(par.vary), par.expr,
                      f"{par.min:.4f}" if np.isfinite(par.min) else '-inf',
                      f"{par.max:.4f}" if np.isfinite(par.max) else 'inf')

    try:
        # the fit and its perturbed restarts run exactly as before the certificate (judged by the
        # optimiser's flag, perturbed from the point it returned): certifying them first moves the
        # point the restarts start from and changes which basin they reach (A2 measurement, V2)
        result = fit_model(composite_model, all_params, certify=False)
    except Exception as exc:
        raise RuntimeError(f"lmfit fitting failed: {exc}") from exc

    # ── Diagnostic logging: AFTER optimisation ───────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT DONE ═══  success=%s  nfev=%s  message=%s",
                  result.success, result.nfev, result.message)
        for pname, par in sorted(result.params.items()):
            init = all_params[pname].value if pname in all_params else None
            delta = f"  Δ={par.value - init:+.6f}" if init is not None and abs(par.value - init) > 1e-10 else ""
            log.debug("  AFTER   %-30s value=%12.6f  stderr=%s%s",
                      pname, par.value,
                      f"{par.stderr:.6f}" if par.stderr is not None else 'None', delta)

    # ── Perturb and refit to escape local minima ─────────────────────────
    # Not for basinhopping (unit F2, 2026-09-26, owner): it is already a global
    # search, so perturbed restarts add nothing — the reason the scattered-
    # starts check excludes it — and with the page's n_perturb 3 they
    # quadrupled its time past the server's 300 s timeout on 14 of 16 sampled
    # multi-component targets (median 386 s, max 1066 s; without them median
    # 96 s, max 256 s, and chi2r identical to 1e-8 on all 16).
    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
        best_result = result
        best_redchi = result.redchi if result.redchi is not None else float('inf')
        rng = perturb_rng

        for attempt in range(n_perturb):
            perturbed_params = result.params.copy()
            for pname, par in perturbed_params.items():
                if par.vary and par.value != 0:
                    # Perturb by ±15% random
                    scale = 1.0 + rng.uniform(-0.15, 0.15)
                    new_val = par.value * scale
                    # Respect bounds
                    if np.isfinite(par.min):
                        new_val = max(new_val, par.min)
                    if np.isfinite(par.max):
                        new_val = min(new_val, par.max)
                    perturbed_params[pname].set(value=new_val)
                elif par.vary and par.value == 0:
                    # For zero-valued params, add small absolute perturbation
                    perturbed_params[pname].set(value=rng.uniform(0.001, 0.05))

            try:
                trial = fit_model(composite_model, perturbed_params, certify=False)
                trial_redchi = trial.redchi if trial.redchi is not None else float('inf')
                log.debug("  PERTURB %d/%d  redchi=%.4f  (best=%.4f)",
                          attempt + 1, n_perturb, trial_redchi, best_redchi)
                # A candidate whose search box was never cleared by its
                # refinement (differential evolution only) does not displace
                # one that was; for every other method both flags are False.
                trial_rank = (getattr(trial, "box_unverified", False), trial_redchi)
                best_rank = (getattr(best_result, "box_unverified", False), best_redchi)
                if trial.success and trial_rank < best_rank:
                    best_result = trial
                    best_redchi = trial_redchi
                    log.debug("  *** New best found! redchi improved to %.4f", best_redchi)
            except Exception:
                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
                continue

        if best_result is not result:
            log.debug("═══ PERTURB IMPROVED FIT ═══  redchi: %.4f → %.4f",
                      result.redchi, best_redchi)
            result = best_result

    # ── The certificate on the fit that is returned (unit A2) ────────────────
    # Only the winner: the search above is unchanged, so the certificate can
    # only carry the returned fit further down from where it stopped.
    if kws.get("method") in _CERTIFIED_METHODS:
        result = _certified(composite_model, result, y_sub, x, weights, kws)

    # ── Scattered starts (never changes `result`) ────────────────────────────
    starts = None
    if n_starts:
        n_unlinked = sum(1 for spec in peak_specs if spec.get("constrain_to") is None)
        if kws.get("method") not in _STARTS_METHODS:
            starts = {"ran": False, "reason": "method"}          # a global method already searches
        elif n_unlinked < 2:
            starts = {"ran": False, "reason": "single_component"}
        elif not result.success:
            starts = {"ran": False, "reason": "fit_not_converged"}
        else:
            try:
                starts = _scattered_starts(int(n_starts), fit_once, composite_model, all_params, result,
                                           peak_specs, x, starts_rng)
            except Exception as exc:                              # the check must never cost the student the fit
                log.exception("scattered starts failed")
                starts = {"ran": False, "reason": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}

    # ── "Is this component required?" (never changes `result`) ─────────────
    required = None
    if require_component is not None:
        rprefix = f"p{require_component}_"
        if not result.success:
            required = {"ran": False, "reason": "fit_not_converged"}
        else:
            try:
                # remove the component and everything linked to it, transitively
                master_of = _link_masters(peak_specs)
                removed = {str(require_component)}
                grew = True
                while grew:
                    grew = False
                    for pid, master in master_of.items():
                        if master is not None and master in removed and pid not in removed:
                            removed.add(pid); grew = True
                removed_prefixes = [f"p{pid}_" for pid in removed]
                without = None
                for m in composite_model.components:
                    if m.prefix in removed_prefixes:
                        continue
                    without = m if without is None else without + m
                if without is None:
                    required = {"ran": False, "reason": "nothing_left"}
                else:
                    own = {spec_id: _component_of(composite_model, spec)[2]
                           for spec_id, spec in ((str(sp["id"]), sp) for sp in peak_specs)}
                    n_free_comp = sum(1 for n in own[str(require_component)]
                                      if result.params[n].vary and result.params[n].expr is None)
                    removed_names = {n for pid in removed for n in own[pid]}
                    required = {"ran": True, **_component_required(
                        lambda params: fit_model(without, params), result.params, removed_names, y_sub, weights,
                        float(result.chisqr), n_free_comp, result.nvarys)}
            except Exception as exc:                              # the check must never cost the student the fit
                log.exception("required-component refit failed")
                required = {"ran": False, "reason": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}

    # Sides WE closed on the returned result (non-empty only for a
    # differential-evolution result whose refinement did not take over).
    search_box = getattr(result, "search_box", {})

    fitted_sub = result.best_fit
    fitted_y = fitted_sub + bg

    # ── Per‑peak results ──────────────────────────────────────────────────────
    individual_peaks = []
    for spec in peak_specs:
        pid = spec["id"]
        comp, prefix, own = _component_of(composite_model, spec)
        peak_y = comp.eval(result.params, x=x)

        # Area by numerical integration. abs(): real XPS grids are
        # BE-descending, which makes the raw trapezoid integral negative —
        # the area is a magnitude by convention (matches autofit/engine.py).
        area = float(abs(trapezoid(peak_y, x)))

        # Parameter extraction with stderr
        param_info: dict[str, Any] = {}
        for pname in result.params:
            if pname in own:                       # exact membership (_component_of), in the fit's own order
                short = pname[len(prefix):]
                par = result.params[pname]
                param_info[short] = {
                    "value": float(par.value),
                    "stderr": float(par.stderr) if par.stderr is not None else None,
                    "vary": par.vary,
                    "expr": par.expr,
                    "min": float(par.min) if np.isfinite(par.min) and "min" not in search_box.get(pname, {}) else None,
                    "max": float(par.max) if np.isfinite(par.max) and "max" not in search_box.get(pname, {}) else None,
                }

        param_info["area"] = {"value": area, "stderr": None}

        # Approximate area stderr via amplitude + fwhm propagation
        amp_par = result.params.get(prefix + "amplitude")
        fwhm_par = result.params.get(prefix + "fwhm")
        if (amp_par and fwhm_par and amp_par.stderr and fwhm_par.stderr
                and amp_par.value and fwhm_par.value):
            rel_err = np.sqrt(
                (amp_par.stderr / amp_par.value) ** 2
                + (fwhm_par.stderr / fwhm_par.value) ** 2
            )
            param_info["area"]["stderr"] = abs(area) * rel_err

        n_free_comp = sum(1 for n in own if result.params[n].vary and result.params[n].expr is None)
        support = _component_support(y_sub, fitted_sub, peak_y, weights, n_free_comp, result.nvarys)
        # A linked component follows its parent: it is supported exactly when the
        # parent is (its own removal test would double-count the parent's role).
        individual_peaks.append({
            "id": pid,
            # the lineshape, explicitly: a curve cannot always tell it apart (a very broad
            # Gaussian and Lorentzian agree to 1e-13 on a grid); additive, no numerical effect
            "shape": spec.get("shape", "pseudo_voigt_gl"),
            "y": peak_y.tolist(),
            "params": param_info,
            "support": support,
        })

    # A linked component follows its ROOT ancestor (a grandchild follows the
    # root), whatever the request order; a cycle or a missing master leaves
    # its own verdict. The master is found as _make_peak_params finds it — the
    # first spec whose id EQUALS constrain_to — so `constrain_to: 1.0` (or true)
    # for a peak with id 1 follows it as it is linked to it (seal 1d Codex round
    # 12: the string spellings were compared here, "1.0" != "1", so such a
    # component kept its own verdict while its parameters followed the master's).
    by_id = {str(ip["id"]): ip for ip in individual_peaks}
    master_of = _link_masters(peak_specs)

    def root_of(pid: str) -> str:
        seen = set()
        while master_of.get(pid) is not None and master_of[pid] in by_id and pid not in seen:
            seen.add(pid)
            pid = master_of[pid]
        return pid

    for ip in individual_peaks:
        root = root_of(str(ip["id"]))
        if root != str(ip["id"]):
            ip["support"]["follows"] = by_id[root]["id"]
            ip["support"]["supported"] = by_id[root]["support"]["supported"]

    # ── Statistics ────────────────────────────────────────────────────────────
    # formed from the arrays returned (seal 1a′, V6.6), so the verification recomputes them exactly
    n_varys = sum(1 for par in result.params.values() if par.vary and par.expr is None)
    statistics = _fit_statistics(y_sub, fitted_sub, weights, n_varys)
    residuals = (y_sub - fitted_sub).tolist()

    success, message = result.success, result.message
    if getattr(result, "box_unverified", False):
        # Searched inside limits the request never set, and the refinement
        # that would show they did not matter did not converge to an equal
        # or better solution. The acceptance rule shows this as a failed fit.
        success = False
        message = ("differential_evolution searched inside generated limits for "
                   + ", ".join(sorted(search_box))
                   + " and a local refinement without them did not converge to an equal or better"
                     " solution. Set bounds for those parameters or use another method.")

    return {
        "success": success,
        "message": message,
        "energy": x.tolist(),
        "counts": y.tolist(),
        "fitted_y": fitted_y.tolist(),
        # the model sum (seal 1a′): fitted_y is fitted_sub + background_y in that association, and
        # fitted_y − background_y does not recover it exactly
        "fitted_sub": fitted_sub.tolist(),
        "background_y": bg.tolist(),
        "residuals": residuals,
        "individual_peaks": individual_peaks,
        "statistics": statistics,
        "charge_shift_applied": charge_shift_ev,
        "random_seed": random_seed,
        # the SHA-256 of every input the fit started from, by effect (seal 1a′): binds this response to its request
        "request_digest": request_digest,
        # RECORDING (owner 2026-10-10; additive — nothing here changes a fitted number or decides
        # whether a fit is current): the method, where the seed came from, the background's
        # verdict against its defining statement, and the software that computed the fit
        "fit_method": method,
        "seed_source": "caller" if caller_seed is not None else "request",
        "background_verdict": _background_verdict(bg_method, bg_cert, bg_effect),
        "software": SOFTWARE,
        "starts": starts,
        "required": required,
        # the returned fit's certificate (unit A2): None for differential
        # evolution / basinhopping, whose verdict is their own refinement
        "certificate": _certificate_report(result, peak_specs),
    }


def _fit_statistics(y_sub, fitted_sub, weights, n_varys):
    """The reported statistics, formed from the returned arrays (seal 1a′, V6.6 — one association):
    lmfit's denominators and floor, but over ``fitted_sub`` (lmfit's ``best_fit``, a fresh
    evaluation at the returned parameters) rather than the residual of the minimiser's last
    evaluation, so ``/api/verify-fit`` recomputes every one exactly from the response.

    chi2_raw = Σ(((y_sub − fitted_sub)·w)²) (NumPy's pairwise sum, as lmfit's ``(residual**2).sum()``);
    reduced = chi2_raw / max(1, n − n_varys); chi_square = max(chi2_raw, 1e-250·n); aic / bic by
    lmfit's formulas from that chi_square; rmse = √(Σ r² / n), r = y_sub − fitted_sub; the R-factor
    Σ|r| / Σ|y_sub| (null when Σ|y_sub| = 0). Every internal decision (restart ranking, the
    certificate, the scattered starts, the required refit) keeps lmfit's own value."""
    n = len(y_sub)
    r = y_sub - fitted_sub
    chi2_raw = ((r * weights) ** 2).sum()
    red = chi2_raw / max(1, n - n_varys)
    chi2 = max(chi2_raw, 1.e-250 * n)
    n2ll = n * np.log(chi2 / n)
    denom = np.sum(np.abs(y_sub))
    return {
        "chi_square": float(chi2),
        "reduced_chi_square": float(red),
        "r_factor": float(np.sum(np.abs(r)) / denom) if denom > 0 else None,
        "n_data": n,
        "n_free_params": n_varys,
        "aic": float(n2ll + 2 * n_varys),
        "bic": float(n2ll + np.log(n) * n_varys),
        "rmse": float(np.sqrt(np.sum(r * r) / n)),
    }


def _background_verdict(method, cert, effect):
    """The background's verdict against its defining statement, as recorded with the fit (owner
    2026-10-10). The integral methods carry their certificate (``background_certificate``:
    converged, residual, reason); the explicit ones (linear, manual, none) have nothing to
    converge — they exist or the fit was refused before this point (BackgroundNotConverged)."""
    # what the background was computed FROM, as it acts (`_background_effect`: the window where the
    # method reads one, the averaging k as it acts, a manual background's anchors) — the same
    # reading the seed hashes, so a setting the method ignores is not recorded as if it acted
    out = {"method": method, "effect": effect}
    if cert:
        res = cert.get("residual")
        out.update({"check": "defining_statement", "converged": bool(cert.get("converged")),
                    "residual": None if res is None else float(res), "reason": cert.get("reason") or ""})
    else:
        out.update({"check": "explicit", "converged": True, "residual": None, "reason": ""})
    return out


def _certificate_report(result, peak_specs):
    """The returned fit's certificate with, per component, how far the
    continued fit moved its centre from where the optimiser stopped (eV,
    signed) and the largest such move — what the page's displacement notice
    shows. None for the global methods."""
    cert = getattr(result, "certificate", None)
    if cert is None:
        return None
    moves = getattr(result, "certificate_centre_moves", {})
    per = [{"id": spec["id"], "ev": moves[f"p{spec['id']}_center"]}
           for spec in peak_specs if f"p{spec['id']}_center" in moves]
    largest = max(per, key=lambda m: abs(m["ev"]), default=None)
    return {**cert, "centre_moves": per, "largest_centre_move": largest}


def compute_background_only(
    energy: np.ndarray,
    counts: np.ndarray,
    method: str = "shirley",
    start_idx: int | None = None,
    end_idx: int | None = None,
    endpoint_avg: int = 1,
) -> dict[str, Any]:
    """Return just the background array without fitting peaks."""
    endpoint_avg = check_endpoint_avg(endpoint_avg)
    i0 = start_idx if start_idx is not None else 0
    i1 = end_idx if end_idx is not None else len(energy)
    x, y = energy[i0:i1], counts[i0:i1]

    if method in _BG_LABELS:
        bg = compute_background(x, y, method, n_avg=endpoint_avg)   # raises BackgroundNotConverged
    elif method in ("linear", "manual"):
        # manual has no anchors on this route: its fewer-than-two-anchors case, the line
        # through the window's edge levels (as run_fit and the page) — never a silent zero
        bg = linear_background(x, y, n_avg=endpoint_avg)
    elif method in ("none", "flat", ""):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{method}'")

    return {
        "energy": x.tolist(),
        "background": bg.tolist(),
        "net_counts": (y - bg).tolist(),
    }


def run_fit(*args, cancel=None, **kwargs):
    """Fit peaks — see ``_run_fit_impl`` for every argument and the result.

    ``cancel`` (optional, unit 2): a callable polled during the fit; once it
    returns true every remaining minimisation aborts and ``FitCancelled`` is
    raised instead of a result. Without it this is exactly the synchronous fit
    it always was (no ``iter_cb`` reaches any minimiser)."""
    if cancel is None:
        return _run_fit_impl(*args, **kwargs)
    _CANCEL.fn, _CANCEL.hit = cancel, False
    try:
        result = _run_fit_impl(*args, **kwargs)
    except Exception as exc:
        # An aborted minimisation can surface as the solver's own error (an
        # AttributeError from Levenberg-Marquardt, a RuntimeError from
        # Nelder-Mead or DE): once cancellation was observed it is a
        # cancellation, never a failed fit (unit 2, Codex round 1).
        if getattr(_CANCEL, "hit", False):
            raise FitCancelled("the fit was cancelled") from exc
        raise
    finally:
        hit = getattr(_CANCEL, "hit", False)
        _CANCEL.fn, _CANCEL.hit = None, False
    if hit:
        raise FitCancelled("the fit was cancelled")
    return result


run_fit.__wrapped__ = _run_fit_impl



# ─────────────────────────────────────────────────────────────────────────────
# Verification of a recorded fit (seal 1a′; sealed fit record v6, option (b))
# ─────────────────────────────────────────────────────────────────────────────
# The keys of a fit response, exactly: a recorded O with more or fewer is not a response.
RESPONSE_KEYS = frozenset({
    "success", "message", "energy", "counts", "fitted_y", "fitted_sub", "background_y", "residuals",
    "individual_peaks", "statistics", "charge_shift_applied", "random_seed", "request_digest", "fit_method", "seed_source",
    "background_verdict", "software", "starts", "required", "certificate"})
_PEAK_KEYS = frozenset({"id", "shape", "y", "params", "support"})
_PARAM_KEYS = frozenset({"value", "stderr", "vary", "expr", "min", "max"})
# Lineshapes whose evaluation is NOT bit-stable on this server (V6.5, owner Q7: such a fit is
# UNCONFIRMED — never compared within a tolerance — until its evaluator is made deterministic, a
# unit of its own). LA(α,β,m): np.convolve's inner product is an alignment-dependent BLAS dot
# (CLAUDE.md "Reproducibility"); measured in seal 1a′ (docs/findings/seal-1a: two evaluations of one
# model's LA components differ in one process) and 1b.
NOT_BIT_STABLE_SHAPES = frozenset({"la_casaxps"})


class _Mismatch(Exception):
    def __init__(self, check, reason):
        super().__init__(reason)
        self.check, self.reason = check, reason


class _Unverifiable(Exception):
    def __init__(self, check, reason):
        super().__init__(reason)
        self.check, self.reason = check, reason


def _exact_float(v):
    """``v`` as the float it equals EXACTLY, else None (an integer beyond 2**53 that no float
    represents, or one that overflows a float — never a 500; Codex round 3)."""
    try:
        f = float(v)
    except (OverflowError, TypeError, ValueError):
        return None
    return f if f == v else None


def _is_number(v) -> bool:
    """A JSON number as a JSON reader holds it — never a bool, never a numeric string."""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _same(a, b) -> bool:
    """JSON-typed equality: numbers by value (a JavaScript writer spells 3.0 as 3), but a flag is a
    flag, a text a text, null null — Python's ``==`` would take ``False`` for ``0`` and ``1`` for
    ``True`` (seal 1a′ Codex round 1)."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if _is_number(a) or _is_number(b):
        return _is_number(a) and _is_number(b) and a == b
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, str) or isinstance(b, str):
        return isinstance(a, str) and isinstance(b, str) and a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    return False


def _as_json(value):
    """``value`` as a JSON reader of the response holds it (tuples → lists, numpy → Python)."""
    return json.loads(json.dumps(value, default=lambda o: o.item() if hasattr(o, "item") else o.tolist()))


def _non_finite(value, path="O"):
    """The path of the first non-finite number in ``value``, or None."""
    if isinstance(value, float):                 # a JSON integer is finite whatever its size (Codex round 2)
        return None if math.isfinite(value) else path
    if isinstance(value, list):
        for k, v in enumerate(value):
            hit = _non_finite(v, f"{path}[{k}]")
            if hit:
                return hit
    if isinstance(value, dict):
        for k, v in value.items():
            hit = _non_finite(v, f"{path}.{k}")
            if hit:
                return hit
    return None


# The recorded-only objects' form (option (b): their TRUTH is not recomputed, but their form is
# what the producer emits — Codex round 2). A spec is a type name, ("null", spec), ("list", spec),
# ("map", spec) or a dict of exact keys (a key spelt "?k" is optional).
_ID_T = "id"                 # what the fit routes accept as an id and the producer echoes: any JSON scalar
_MOVE_T = {"id": _ID_T, "ev": "num"}
_NOT_RUN_T = {"ran": "false", "reason": "str", "?error": "str"}
_STARTS_T = {"ran": "true", "n_run": "int", "n_converged": "int", "n_same_as_fit": "int",
             "n_in_alternatives": "int", "n_not_better_elsewhere": "int", "not_better_chi2r": ("list", "num"),
             "fit": {"chi2r": "num", "largest_centre_shift_from_start": _MOVE_T,
                     "components": ("list", {"id": _ID_T, "area_percent": "num", "center_shift_from_start": "num"})},
             "alternatives": ("list", {"chi2r": "num", "n_starts": "int",
                                       "components": ("list", {"id": _ID_T, "area": "num", "params": ("map", "num"),
                                                               "area_percent": "num", "center_shift_from_start": "num"}),
                                       "largest_centre_shift_from_start": _MOVE_T,
                                       "largest_fraction_difference_pp": "num"})}
_REQUIRED_T = {"ran": "true", "required": ("null", "bool"), "f": ("null", "num"), "chi2_with": "num",
               "chi2_without_refit": "num", "refit_converged": "bool", "?reason": "str", "?message": "str"}
_CERTIFICATE_T = {"certified": "bool", "restarts": "int", "moved": "bool", "optimiser_flag": "bool",
                  "centre_moves": ("list", _MOVE_T), "largest_centre_move": ("null", _MOVE_T)}
_SUPPORT_T = {"f": ("null", "num"), "delta_chi2": "num", "supported": "bool", "?follows": _ID_T}
# the background verdict (_background_verdict) and the effect it records (_background_effect)
_BG_EFFECT_T = {"method": "str", "?window": ("list", "int"), "?k": "int", "?anchors": ("list", ("list", "num"))}


def _bg_effect_form_failure(e):
    """The effect's exact form as _background_effect writes it (Codex rule round 4): per method, its fields and
    nothing else — a two-integer window and k for a windowed method, k for the manual line, two-number anchors for
    a manual background, nothing for none."""
    if not _typed(e, _BG_EFFECT_T):
        return "the recorded background effect is not of a response's form"
    m, keys = e["method"], set(e) - {"method"}
    want = {"none": set(), "manual": {"anchors"}, "manual-line": {"k"}}.get(m, {"window", "k"})
    if keys != want or ("window" in e and len(e["window"]) != 2) or \
            ("anchors" in e and (len(e["anchors"]) < 2 or any(len(a) != 2 for a in e["anchors"]))):   # manual: >= 2 anchors
        return "the recorded background effect is not of a response's form"
    return None
_BG_VERDICT_T = {"method": ("null", "str"), "effect": _BG_EFFECT_T, "check": "str", "converged": "bool",
                 "residual": ("null", "num"), "reason": "str"}
_STATISTICS_T = {"chi_square": "num", "reduced_chi_square": "num", "r_factor": ("null", "num"), "n_data": "int",
                 "n_free_params": "int", "aic": "num", "bic": "num", "rmse": "num"}


def _typed(v, spec) -> bool:
    if isinstance(spec, str):
        return {"bool": lambda: isinstance(v, bool), "true": lambda: v is True, "false": lambda: v is False,
                "int": lambda: isinstance(v, int) and not isinstance(v, bool), "num": lambda: _is_number(v),
                "str": lambda: isinstance(v, str),
                "id": lambda: v is None or isinstance(v, (str, bool, int, float))}[spec]()
    if isinstance(spec, tuple):
        kind, inner = spec
        if kind == "null":
            return v is None or _typed(v, inner)
        if kind == "list":
            return isinstance(v, list) and all(_typed(e, inner) for e in v)
        if kind == "map":
            return isinstance(v, dict) and all(isinstance(k, str) and _typed(e, inner) for k, e in v.items())
    if isinstance(spec, dict):
        if not isinstance(v, dict):
            return False
        required = {k for k in spec if not k.startswith("?")}
        allowed = required | {k[1:] for k in spec if k.startswith("?")}
        if not required <= set(v) <= allowed:
            return False
        return all(_typed(v[k], spec[k] if k in spec else spec["?" + k]) for k in v)
    return False


def _non_finite_request(peak_specs, manual_bg) -> bool:
    """A request number with no exact reading: a NaN anywhere, or ±Infinity anywhere but a bound
    (a key ending "_min" / "_max", where Infinity is an open side, as lmfit reads it). An infinite
    START, splitting or anchor is never a fit the routes return (Codex round 6: a pairing of
    such a request with a finite response read consistent once O's values replaced the start)."""
    def bad(v, bound):
        if isinstance(v, float):
            return math.isnan(v) or (math.isinf(v) and not bound)
        if isinstance(v, (list, tuple)):
            return any(bad(e, False) for e in v)
        if isinstance(v, dict):
            return any(bad(e, str(k).endswith(("_min", "_max"))) for k, e in v.items())
        return False
    return bad(list(peak_specs), False) or bad(manual_bg, False)


def verify_fit(O, *, energy, counts, peak_specs, background_method="shirley", bg_start_idx=None,
               bg_end_idx=None, charge_shift_ev=0.0, fit_kws=None, n_perturb=0, manual_bg=None,
               endpoint_avg=1, n_starts=0, require_component=None) -> dict[str, Any]:
    """Is the recorded response ``O`` what THIS server's code computes from the request? (seal 1a′,
    V6.5 step 2; the keyword arguments are ``run_fit``'s, as ``/api/verify-fit`` normalises them.)

    Recomputes — never fits — and compares EXACTLY, no tolerance anywhere: the structure and JSON
    types of every field, the parameters' roles as the fitter holds them, every held value, every
    parameter value against the one evaluated, every expression from O's free values, the method,
    the shift, the seed, the whole background and its verdict, each component's curve and area,
    the model sum, ``fitted_y`` and the residuals in their associations, the statistics
    (``_fit_statistics``) and each component's support.

    ``{"state": "consistent" | "mismatch" | "unconfirmed", "check", "reason", "software"}``.
    The record is ALWAYS recomputed (owner 2026-10-15): another git commit, checkout state or environment
    is information only, and a recomputation that matches is ``consistent`` whatever produced it.
    ``mismatch`` = the record is not of a response's form (``schema``, the software record included), or
    the recomputation differs under the SAME numerics (``NUMERICS_IDENTITY_KEYS``): the record does not
    hold. ``unconfirmed`` = it cannot be judged exactly here: the recomputation differs and the record was
    made under OTHER numerics (check ``numerics``, naming the fields and the failed check), O holds a non-finite number, or one of the two EVALUATION identities (a recorded curve / the
    model sum is this server's evaluation of the parameters) failed on a request with a lineshape that is
    not evaluated bit-identically (``NOT_BIT_STABLE_SHAPES``, owner Q7); every relation of the recorded
    arrays stays exact. CONSISTENT is consistency under
    this verifier's code, not acceptance: ``success``, ``message``, the σ, ``certificate``,
    ``starts`` and ``required`` are the producer's statements, shown AS RECORDED (option (b),
    owner 2026-10-11) — a re-run is what tests them."""
    def answer(state, check=None, reason=""):
        return {"state": state, "check": check, "reason": reason, "software": SOFTWARE}

    other = []          # the numerics fields that differ from this server's (none known yet: a malformed record is a mismatch)
    try:
        if not isinstance(O, dict):
            raise _Mismatch("schema", "the recorded result is not an object")
        why = response_form_failure(O, len(energy) if energy is not None else 0)
        if why:
            raise _Mismatch("schema", why)
        # which numerics made the record: decides only how a recomputation that DIFFERS reads
        other = numerics_difference(O["software"])
        bad = _non_finite(O)
        if bad:
            return answer("unconfirmed", "non_finite",
                          f"the record holds a non-finite number ({bad}); it cannot be verified exactly")
        _verify(O, energy=energy, counts=counts, peak_specs=peak_specs, background_method=background_method,
                bg_start_idx=bg_start_idx, bg_end_idx=bg_end_idx, charge_shift_ev=charge_shift_ev, fit_kws=fit_kws,
                n_perturb=n_perturb, manual_bg=manual_bg, endpoint_avg=endpoint_avg, n_starts=n_starts,
                require_component=require_component)
    except _Unverifiable as exc:
        return answer("unconfirmed", exc.check, exc.reason)
    except _Mismatch as exc:
        # a record not of a response's FORM was refused above, whatever made it; past that, a recomputation that
        # differs under other numerics is a check that cannot be made here
        if other and exc.check != "schema":
            return answer("unconfirmed", "numerics",
                          f"made under other numerics ({'; '.join(other)}) and the recomputation differs "
                          f"({exc.check}: {exc.reason})")
        return answer("mismatch", exc.check, exc.reason)
    except Exception as exc:                 # never a 500 and never current: a record this verifier could not judge
        log.exception("verification raised")
        return answer("unconfirmed", "error", f"the verification could not judge this record ({type(exc).__name__})")
    return answer("consistent")


def _verify(O, *, energy, counts, peak_specs, background_method, bg_start_idx, bg_end_idx, charge_shift_ev,
            fit_kws, n_perturb, manual_bg, endpoint_avg, n_starts, require_component):
    # ── structure and JSON types (no field is read through a coercion) ──
    if set(O) != RESPONSE_KEYS:
        extra, missing = sorted(set(O) - RESPONSE_KEYS), sorted(RESPONSE_KEYS - set(O))
        raise _Mismatch("schema", f"the recorded result's fields differ from a response's (extra {extra}, missing {missing})")
    if not isinstance(O["success"], bool) or not isinstance(O["message"], str):
        raise _Mismatch("schema", "success / message are not a flag and a text")
    for k, spec in (("starts", ("null", _STARTS_T)), ("required", ("null", _REQUIRED_T)),
                    ("certificate", ("null", _CERTIFICATE_T))):
        if not (_typed(O[k], spec) or (O[k] is not None and _typed(O[k], _NOT_RUN_T) and k != "certificate")):
            raise _Mismatch("schema", f"{k} is not of a response's form")
    if not _typed(O["statistics"], _STATISTICS_T):
        raise _Mismatch("schema", "the recorded statistics are not of a response's form")
    if not _is_number(O["charge_shift_applied"]) or not isinstance(O["random_seed"], int) \
            or isinstance(O["random_seed"], bool) or not isinstance(O["fit_method"], str) \
            or not isinstance(O["request_digest"], str) \
            or not isinstance(O["seed_source"], str) or not isinstance(O["background_verdict"], dict):
        raise _Mismatch("schema", "a recorded field is not of its type")

    # a NaN in the request (a bound, a start, an anchor — accepted by a JSON parser that reads the NaN token;
    # a browser writes null) has no exact reading: differential evolution searches a NaN bound as open, a
    # range check never holds (Codex round 5); nor has an infinite start (round 6; `1e400` parses as one).
    # Unjudgeable, never current — not a mismatch; judged BEFORE the parameters are built (Codex round 7b:
    # an infinite centre collapsed its default window and was refused as a mismatch first).
    if _non_finite_request(peak_specs, manual_bg):
        raise _Unverifiable("non_finite", "the request holds a number with no exact reading (NaN, or an infinite "
                                          "start); its fit cannot be verified exactly")
    # ── the request, read as run_fit reads it (a request run_fit refuses has no response) ──
    try:
        energy = np.asarray(energy, dtype=float)
        counts = np.asarray(counts, dtype=float)
        if energy.ndim != 1 or len(energy) != len(counts) or not peak_specs:
            raise ValueError("energy and counts must be one-dimensional, of the same length, with a peak")
        _validate_constraint_graph(peak_specs)
        energy = energy + charge_shift_ev
        fit_kws, caller_seed, method = _normalise_fit_kws(fit_kws)
        endpoint_avg = check_endpoint_avg(endpoint_avg)
        if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
            raise ValueError("n_starts out of range")
        ordered, composite_model, start_params = _build_model(peak_specs)
        if require_component is not None and (str(require_component) not in [str(s["id"]) for s in peak_specs]
                                              or len(peak_specs) < 2):
            raise ValueError("require_component is not one of two or more peaks")
        # the parameters AS THE FITTER HOLDS THEM: Model.fit deep-copies its start, and the copy
        # orders reversed bounds and clips a value into them (lmfit Parameter._init_bounds; Codex
        # round 1); the seed is derived from the start itself, as run_fit derives it
        params = copy.deepcopy(start_params)
    except Exception as exc:
        raise _Mismatch("request", f"the request is not one a fit accepts: {exc}")
    # the fit's first step evaluates the START model (Model.fit, before any optimisation): a start that cannot be
    # evaluated (a Lorentzian fwhm of 1e160 overflows) is refused by the fit routes, so it has no response
    # (Codex round 7c). Evaluated on the fitter's copy, nothing fitted.
    try:
        with np.errstate(all="ignore"):
            composite_model.eval(copy.deepcopy(params), x=energy)
    except Exception as exc:
        raise _Mismatch("request", f"the request's starting model cannot be evaluated ({type(exc).__name__}): "
                                   f"no fit has this response")
    x, y, n = energy, counts, len(energy)
    unstable = sorted({s.get("shape", "pseudo_voigt_gl") for s in peak_specs} & NOT_BIT_STABLE_SHAPES)

    def arr(value, name):
        """O's array as recorded — JSON numbers, n of them — never converted: a recorded number is
        compared EXACTLY with a computed float (Python compares int and float exactly), so two
        different JSON integers can never round into one (Codex round 2)."""
        if not isinstance(value, list) or len(value) != n or not all(_is_number(v) for v in value):
            raise _Mismatch("schema", f"{name} is not {n} numbers")
        return value

    def equal(recorded, computed):
        return all(r == c for r, c in zip(recorded, np.asarray(computed, dtype=float).tolist()))

    if not equal(arr(O["energy"], "energy"), x) or not equal(arr(O["counts"], "counts"), y):
        raise _Mismatch("data", "the recorded energies or counts are not the request's")
    if O["fit_method"] != method:
        raise _Mismatch("method", f"recorded method {O['fit_method']!r}, requested {method!r}")
    if O["charge_shift_applied"] != charge_shift_ev:
        raise _Mismatch("shift", "the recorded charge shift is not the request's")

    # ── the background: run_fit's one assembly, on the request's data ──
    try:
        bg, bg_cert, bg_effect, bg_method = _assemble_background(
            x, y, background_method, bg_start_idx, bg_end_idx, endpoint_avg, manual_bg)
    except Exception as exc:
        raise _Mismatch("background", f"the request's background cannot be computed ({exc})")
    if not equal(arr(O["background_y"], "background_y"), bg):
        raise _Mismatch("background", "the recorded background is not the request's")
    if not _same(O["background_verdict"], _as_json(_background_verdict(bg_method, bg_cert, bg_effect))):
        raise _Mismatch("background", "the recorded background verdict is not the request's")
    y_sub = y - bg
    weights = 1.0 / np.sqrt(np.maximum(y, 1.0))

    # ── the request digest and the seed — from the request's STARTING parameters ──
    digest = _request_digest(x, y, bg_effect, [s.get("shape", "pseudo_voigt_gl") for s in ordered],
                             [f"p{s['id']}_" for s in ordered], start_params, fit_kws=fit_kws, n_perturb=n_perturb)
    if O["request_digest"] != digest:
        raise _Mismatch("request_digest", "the recorded response was not fitted from this request's inputs")
    if caller_seed is not None:
        if O["random_seed"] != int(caller_seed) or O["seed_source"] != "caller":
            raise _Mismatch("seed", "the recorded seed is not the caller's")
    elif O["random_seed"] != int.from_bytes(bytes.fromhex(digest)[:4], "little") or O["seed_source"] != "request":
        raise _Mismatch("seed", "the recorded seed is not the one the request derives")

    # ── each component, in request order: its OWN parameters (exact membership) ──
    peaks = O["individual_peaks"]
    if not isinstance(peaks, list) or len(peaks) != len(peak_specs):
        raise _Mismatch("schema", "one recorded component per requested peak")
    owned = []
    for spec, ip in zip(peak_specs, peaks):
        comp, prefix, own = _component_of(composite_model, spec)
        owned.append((comp, prefix, own))
        if not isinstance(ip, dict) or set(ip) != _PEAK_KEYS or not isinstance(ip["params"], dict) \
                or not _typed(ip["support"], _SUPPORT_T):
            raise _Mismatch("schema", "a recorded component's fields differ from a response's")
        if not _same(ip["id"], _as_json(spec["id"])) or ip["shape"] != spec.get("shape", "pseudo_voigt_gl"):
            raise _Mismatch("schema", f"component {spec['id']!r}: the recorded id or lineshape is not the request's")
        rp = ip["params"]
        if set(rp) != {nm[len(prefix):] for nm in own} | {"area"}:
            raise _Mismatch("schema", f"component {spec['id']!r}: the recorded parameters are not the model's")
        for name in own:
            rec = rp[name[len(prefix):]]
            if not isinstance(rec, dict) or set(rec) != _PARAM_KEYS or not _is_number(rec["value"]) \
                    or not (rec["stderr"] is None or _is_number(rec["stderr"])) or not isinstance(rec["vary"], bool) \
                    or not (rec["expr"] is None or isinstance(rec["expr"], str)) \
                    or not all(rec[b] is None or _is_number(rec[b]) for b in ("min", "max")):
                raise _Mismatch("schema", f"{name}: the recorded parameter is not of a response's form")
        area = rp["area"]
        if not isinstance(area, dict) or set(area) != {"value", "stderr"} or not _is_number(area["value"]) \
                or not (area["stderr"] is None or _is_number(area["stderr"])):
            raise _Mismatch("schema", f"component {spec['id']!r}: the recorded area is not of a response's form")

    # every parameter's value as the fitter EVALUATES it — the float (a request's integer amplitude of
    # 10000000000000001 is evaluated, and recorded, as 1e16; Codex round 3: one reading)
    try:
        effective = {name: float(par.value) for name, par in params.items()}
    except OverflowError:
        raise _Mismatch("request", "a parameter of the request overflows a float: no fit has this response")
    for (comp, prefix, own), spec, ip in zip(owned, peak_specs, peaks):
        for name in own:
            par, rec = params[name], ip["params"][name[len(prefix):]]
            lo = float(par.min) if np.isfinite(par.min) else None
            hi = float(par.max) if np.isfinite(par.max) else None
            if rec["vary"] is not bool(par.vary) or rec["expr"] != par.expr or not _same(rec["min"], lo) \
                    or not _same(rec["max"], hi):
                raise _Mismatch("roles", f"{name}: the recorded role (vary / expression / bounds) is not the request's")
            if par.expr is None and not par.vary and rec["value"] != effective[name]:
                raise _Mismatch("held", f"{name}: the recorded held value is not the request's")
            # the bounds as the producer records and the fit reads them: floats (an integer bound of
            # 10000000000000001 is 1e16 to both — Codex round 4: one reading)
            if par.expr is None and par.vary and not float(par.min) <= rec["value"] <= float(par.max):
                raise _Mismatch("roles", f"{name}: the recorded value lies outside the request's bounds")

    n_varys = sum(1 for par in params.values() if par.vary and par.expr is None)
    if not _determined(n_varys, int(np.count_nonzero(np.isfinite(y_sub)))):
        raise _Mismatch("determinacy", "the request is not determined by its data: no fit has this response")

    # set the free values, evaluate every expression; then EVERY recorded value (free, held, expression)
    # must be the value the evaluation holds (each parameter is recorded exactly once, by its owner)
    for (comp, prefix, own), ip in zip(owned, peaks):
        for name in own:
            if params[name].expr is None and params[name].vary:
                v = _exact_float(ip["params"][name[len(prefix):]]["value"])
                if v is None:
                    raise _Mismatch("roles", f"{name}: the recorded value is not a number a fit can hold")
                params[name].value = v
            elif params[name].expr is None:
                params[name].value = effective[name]           # a held value, as the fitter evaluates it
    params.update_constraints()
    for (comp, prefix, own), ip in zip(owned, peaks):
        for name in own:
            if ip["params"][name[len(prefix):]]["value"] != float(params[name].value):   # recorded as float(par.value)
                check = "expressions" if params[name].expr is not None else "roles"
                raise _Mismatch(check, f"{name}: the recorded value is not the value evaluated")

    # ── the arrays' relations, EXACTLY, from the RECORDED arrays — no evaluator involved ──
    rec_sub = arr(O["fitted_sub"], "fitted_sub")
    rec_ys = [arr(ip["y"], f"component {spec['id']!r} curve") for spec, ip in zip(peak_specs, peaks)]
    arr(O["fitted_y"], "fitted_y")
    arr(O["residuals"], "residuals")
    _verify_relations(O, peaks, peak_specs, owned, params, x, bg, y_sub, weights, n_varys, rec_sub, rec_ys, equal)

    # ── the evaluations: each recorded curve and the model sum ARE the parameters' ──
    # A lineshape not evaluated bit-identically here (NOT_BIT_STABLE_SHAPES, owner Q7) makes ONLY these
    # identities unjudgeable — unconfirmed, never a tolerance; every relation above stays exact
    def unverifiable(what, shapes):
        return _Unverifiable("components" if what != "fitted_sub" else "fitted_sub",
                             f"{what}: the recorded curve is not this server's evaluation of its parameters, and "
                             f"the lineshape ({', '.join(shapes)}) is not evaluated bit-identically here, so it "
                             f"cannot be verified exactly")
    # every stable evaluation is judged before an unstable one can answer "unconfirmed" (Codex round 3)
    def evaluate(model, what):
        # the producer evaluated its own parameters without error, so parameters this server cannot
        # evaluate (an overflow, Codex round 4) are not the producer's
        try:
            with np.errstate(all="ignore"):
                return model.eval(params, x=x)
        except Exception as exc:
            raise _Mismatch("components" if what != "the model sum" else "fitted_sub",
                            f"{what}: the recorded parameters cannot be evaluated ({type(exc).__name__})")

    deferred = None
    for (comp, prefix, own), spec, rec_y in zip(owned, peak_specs, rec_ys):
        if not equal(rec_y, evaluate(comp, f"component {spec['id']!r}")):
            shape = spec.get("shape", "pseudo_voigt_gl")
            if shape not in NOT_BIT_STABLE_SHAPES:
                raise _Mismatch("components", f"component {spec['id']!r}: the recorded curve is not its parameters'")
            deferred = deferred or unverifiable(f"component {spec['id']!r}", [shape])
    if deferred is not None:
        raise deferred
    if not equal(rec_sub, evaluate(composite_model, "the model sum")):
        if unstable:
            raise unverifiable("the model sum", unstable)
        raise _Mismatch("fitted_sub", "the recorded model sum is not its components'")


def _verify_relations(O, peaks, peak_specs, owned, params, x, bg, y_sub, weights, n_varys, rec_sub, rec_ys, equal):
    """Every relation of the recorded arrays, in run_fit's own associations, computed FROM the
    recorded curves (exact; independent of any lineshape evaluator): areas, fitted_y, residuals,
    the statistics and each component's support."""
    # each recorded number exactly a float (an integer beyond 2**53 is not): Python's float / int
    # comparison is exact, numpy's would convert first
    if any(_exact_float(v) is None for curve in [rec_sub, *rec_ys] for v in curve):
        raise _Mismatch("schema", "a recorded curve holds a number no float represents")
    fitted_sub = np.asarray(rec_sub, dtype=float)
    comp_ys = [np.asarray(r, dtype=float) for r in rec_ys]
    for spec, ip, cy in zip(peak_specs, peaks, comp_ys):
        if ip["params"]["area"]["value"] != float(abs(trapezoid(cy, x))):
            raise _Mismatch("components", f"component {spec['id']!r}: the recorded area is not its curve's")
    if not equal(O["fitted_y"], fitted_sub + bg):
        raise _Mismatch("fitted_y", "the recorded fitted curve is not the model sum plus the background")
    if not equal(O["residuals"], y_sub - fitted_sub):
        raise _Mismatch("residuals", "the recorded residuals are not the data less the background and the model")
    if not _same(O["statistics"], _as_json(_fit_statistics(y_sub, fitted_sub, weights, n_varys))):
        raise _Mismatch("statistics", "the recorded statistics are not the ones its arrays give")

    # support, as run_fit forms it (a linked component follows its root)
    supports = []
    for (comp, prefix, own), cy in zip(owned, comp_ys):
        n_free_comp = sum(1 for nm in own if params[nm].vary and params[nm].expr is None)
        supports.append(_component_support(y_sub, fitted_sub, cy, weights, n_free_comp, n_varys))
    by_id = {str(s["id"]): sup for s, sup in zip(peak_specs, supports)}
    master_of = _link_masters(peak_specs)
    ids = {str(s["id"]): s["id"] for s in peak_specs}
    for s, sup in zip(peak_specs, supports):
        pid, seen = str(s["id"]), set()
        while master_of.get(pid) is not None and master_of[pid] in by_id and pid not in seen:
            seen.add(pid)
            pid = master_of[pid]
        if pid != str(s["id"]):
            sup["follows"] = ids[pid]
            sup["supported"] = by_id[pid]["supported"]
    for spec, ip, sup in zip(peak_specs, peaks, supports):
        if not _same(ip["support"], _as_json(sup)):
            raise _Mismatch("support", f"component {spec['id']!r}: the recorded support is not the one its fit gives")
