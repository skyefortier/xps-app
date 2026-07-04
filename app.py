"""
app.py – XPS Peak Fitting Flask application.

Gunicorn entry point:
    gunicorn "app:create_app()" -w 4 -b 0.0.0.0:5000

Development:
    python app.py          (uses FLASK_ENV / FLASK_DEBUG from environment)
    flask --app app run    (same, using Flask CLI)

Session model
-------------
Each file upload creates a UUID session.  The parsed arrays are saved as a
compressed NumPy archive at  uploads/<session_id>.npz.  Subsequent fit /
background requests reference the session by ID.  No server‑side memory state
is required, making the app compatible with multi‑worker gunicorn.

REST API
--------
POST /api/upload            Upload a data file; returns session_id + preview data
POST /api/background        Compute background for a session
POST /api/fit               Run peak fitting; returns full result
GET  /api/peak-shapes       List available lineshape names
GET  /api/elements          List built‑in spin‑orbit element presets
GET  /api/xps-reference     Validated periodic-table reference dataset (data/xps/)
GET  /api/session/<id>      Retrieve raw session data
DELETE /api/session/<id>    Delete session files
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from functools import wraps
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

import fitting
import parser as xps_parser
import vgd_parser
from xps_reference import XPSReferenceError, load_reference_cached

# Upper bound on the Monte-Carlo uncertainty resampling count accepted by
# /api/fit. Each perturbation re-runs the full composite fit, so an unbounded
# value lets a single request occupy a worker for many minutes (audit F7).
# Adjust here if more resampling is ever needed.
MAX_N_PERTURB = 100

# Session .npz files are deleted by an opportunistic sweep this many days after
# their last modification (audit F13). The sweep runs on each new session write
# — no background thread or scheduler.
SESSION_TTL_DAYS = 7

# ─────────────────────────────────────────────────────────────────────────────
# Application factory
# ─────────────────────────────────────────────────────────────────────────────

def create_app(upload_folder: str = "uploads", data_folder: str = "data/xps") -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")

    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["XPS_DATA_DIR"] = data_folder
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB hard limit

    Path(upload_folder).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # ── Routes ────────────────────────────────────────────────────────────────
    _register_routes(app)
    _register_error_handlers(app)

    return app


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _json_sanitize(obj):
    """Defensive numpy→native conversion for /api/analyze payloads (the
    methods emit natives, but a stray np scalar must not 500 the route)."""
    if isinstance(obj, dict):
        return {str(k): _json_sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_sanitize(v) for v in obj]
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def _session_path(session_id: str, upload_folder: str) -> Path:
    return Path(upload_folder) / f"{session_id}.npz"


def _load_session(session_id: str, upload_folder: str) -> tuple[np.ndarray, np.ndarray]:
    """Load energy and counts arrays from a session file."""
    path = _session_path(session_id, upload_folder)
    if not path.exists():
        raise KeyError(session_id)
    archive = np.load(path)
    return archive["energy"], archive["counts"]


def _sweep_expired_sessions(upload_folder: str) -> None:
    """Opportunistically delete session files older than SESSION_TTL_DAYS.

    Runs on each new session write (audit F13) — no scheduler/thread, which
    would risk duplicate sweeps under multi-worker gunicorn. Touches ONLY
    ``*.npz`` session files (never .vgd scratch or temp uploads), tolerates a
    concurrent worker deleting the same file first, and never raises (cleanup
    must not break a successful upload).
    """
    cutoff = time.time() - SESSION_TTL_DAYS * 86400
    try:
        candidates = list(Path(upload_folder).glob("*.npz"))
    except OSError:
        return
    for p in candidates:
        try:
            if p.stat().st_mtime < cutoff:
                p.unlink(missing_ok=True)
        except FileNotFoundError:
            pass  # another worker swept it first — fine
        except OSError:
            pass  # never let cleanup break the request


def _save_session(
    session_id: str,
    upload_folder: str,
    energy: np.ndarray,
    counts: np.ndarray,
    filename: str = "",
) -> None:
    path = _session_path(session_id, upload_folder)
    np.savez_compressed(path, energy=energy, counts=counts,
                        filename=np.array([filename]))
    # Opportunistic TTL cleanup of stale sessions (audit F13). Never raises.
    _sweep_expired_sessions(upload_folder)


def _err(message: str, status: int = 400) -> tuple:
    return jsonify({"error": message}), status


def _require_json(f):
    """Decorator: return 400 if request body is not valid JSON."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return _err("Request must be JSON (Content-Type: application/json)")
        return f(*args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# Spin‑orbit element presets
# ─────────────────────────────────────────────────────────────────────────────

#  (splitting eV, area_ratio = intensity(high‑j) / intensity(low‑j))
#  Convention: the primary peak is the high‑j component (lower BE in BE scale).
SPIN_ORBIT_PRESETS = {
    "Si 2p":  {"splitting": 0.61,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Al 2p":  {"splitting": 0.41,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "P 2p":   {"splitting": 0.84,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "S 2p":   {"splitting": 1.18,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Cl 2p":  {"splitting": 1.60,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Ti 2p":  {"splitting": 5.54,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Fe 2p":  {"splitting": 13.1,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Co 2p":  {"splitting": 15.0,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Ni 2p":  {"splitting": 17.3,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Cu 2p":  {"splitting": 19.8,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Zn 2p":  {"splitting": 23.1,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Mo 3d":  {"splitting": 3.13,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
    "Ag 3d":  {"splitting": 6.00,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
    "Cd 3d":  {"splitting": 6.74,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
    "Sn 3d":  {"splitting": 8.43,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
    "W 4f":   {"splitting": 2.18,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
    "Au 4f":  {"splitting": 3.67,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
    "Pt 4f":  {"splitting": 3.33,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
    "Pb 4f":  {"splitting": 4.86,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
}


# ─────────────────────────────────────────────────────────────────────────────
# Route registration
# ─────────────────────────────────────────────────────────────────────────────

def _register_routes(app: Flask) -> None:

    # ── Index ─────────────────────────────────────────────────────────────────

    @app.route("/")
    def index():
        # Serve index.html from the templates folder when the frontend is ready
        from flask import render_template, send_from_directory
        templates = Path(app.template_folder)
        static = Path(app.static_folder) if app.static_folder else Path("static")
        if templates.exists() and (templates / "index.html").exists():
            # Inject the validated legacy reference data synchronously so the
            # survey-marker / NIST-modal consumers (rewired to the unified
            # accessor in Stage 9) have it at parse time — no async-load race.
            # Falls back to null on validation failure; the frontend accessor
            # degrades gracefully (and, pre-cutover, the legacy constants
            # remain as a backstop).
            try:
                legacy = load_reference_cached(app.config["XPS_DATA_DIR"]).get("legacy")
            except XPSReferenceError as e:
                logging.getLogger(__name__).error(
                    "legacy reference unavailable for template injection: %s", e)
                legacy = None
            return render_template("index.html", legacy_reference=legacy)
        if static.exists() and (static / "index.html").exists():
            return send_from_directory(str(static), "index.html")
        return (
            "<h1>XPS Fitting API</h1>"
            "<p>Frontend not yet installed.  Place your <code>index.html</code> "
            "in <code>templates/</code> or <code>static/</code>.</p>"
            "<p>API ready at <code>/api/</code></p>",
            200,
        )

    # ── Metadata endpoints ────────────────────────────────────────────────────

    @app.get("/api/peak-shapes")
    def peak_shapes():
        descriptions = {
            "gaussian":        "Pure Gaussian",
            "lorentzian":      "Pure Lorentzian",
            "pseudo_voigt_gl": "Pseudo-Voigt GL mix  (η = Lorentzian fraction)",
            "asymmetric_gl":   "Asymmetric GL  (independent left/right FWHM)",
            "doniach_sunjic":  "Doniach-Sunjic  (metallic systems, asymmetric)",
            "ds_g":            "DS+G  (Doniach-Sunjic core convolved with Gaussian)",
            "la_casaxps":      "LA(alpha,beta,m) [CasaXPS]  (asymmetric Lorentzian + Gaussian conv)",
        }
        return jsonify({k: descriptions[k] for k in fitting.AVAILABLE_SHAPES})

    @app.get("/api/elements")
    def elements():
        return jsonify(SPIN_ORBIT_PRESETS)

    @app.get("/api/xps-reference")
    def xps_reference():
        """Serve the validated data/xps reference dataset (cached on mtime).

        On invalid data this fails loudly with a structured error naming the
        offending file and JSON path — a malformed transition is never
        silently dropped.
        """
        try:
            payload = load_reference_cached(app.config["XPS_DATA_DIR"])
        except XPSReferenceError as e:
            logging.getLogger(__name__).error("XPS reference dataset invalid: %s", e)
            return jsonify({"error": e.message, "file": e.filename,
                            "path": e.json_path}), 500
        return jsonify(payload)

    # ── File upload ───────────────────────────────────────────────────────────

    @app.post("/api/upload")
    def upload():
        if "file" not in request.files:
            return _err("No file field in the request")
        f = request.files["file"]
        if not f.filename:
            return _err("No filename provided")

        filename = secure_filename(f.filename)
        suffix = Path(filename).suffix.lower()
        if suffix not in xps_parser.ALLOWED_EXTENSIONS:
            return _err(
                f"File type '{suffix}' not supported. "
                f"Allowed: {sorted(xps_parser.ALLOWED_EXTENSIONS)}"
            )

        # Save raw upload temporarily. Prefix with a UUID so concurrent uploads
        # of files with the same name never collide in the shared upload dir.
        tmp_path = Path(app.config["UPLOAD_FOLDER"]) / f"{uuid.uuid4().hex}_{filename}"
        f.save(str(tmp_path))

        try:
            energy, counts = xps_parser.parse_file(tmp_path)
        except ValueError as exc:
            # Our own validation (clean, user-facing): bad format, empty file,
            # too few points, "Not a valid Thermo VGD file", etc. (audit F10).
            tmp_path.unlink(missing_ok=True)
            return _err(f"Could not parse file: {exc}")
        except Exception:
            # Unexpected library/internal failure — log the detail, return generic.
            app.logger.exception("Unexpected file-parse error")
            tmp_path.unlink(missing_ok=True)
            return _err("Internal parse error — see server log for details.", 500)
        finally:
            tmp_path.unlink(missing_ok=True)

        session_id = str(uuid.uuid4())
        try:
            _save_session(session_id, app.config["UPLOAD_FOLDER"],
                          energy, counts, filename)
        except Exception:
            app.logger.exception("Failed to store session")
            return _err("Could not store the session — see server log.", 500)

        return jsonify({
            "session_id": session_id,
            "filename": filename,
            "n_points": int(len(energy)),
            "energy_range": [float(energy.min()), float(energy.max())],
            "counts_range": [float(counts.min()), float(counts.max())],
            # Return a downsampled preview (max 2000 points) to keep payload small
            **_preview(energy, counts, max_pts=2000),
        })

    # ── VGD parse (Thermo Avantage binary format) ─────────────────────────────

    @app.post("/api/parse-vgd")
    def parse_vgd_endpoint():
        """Parse a Thermo Avantage VGD file and return (be, inten) arrays.

        Accepts a multipart/form-data POST with a single 'file' field.
        Optional form fields:
          photon_energy  – X-ray source energy in eV (default 1486.6, Al Kα)
          work_function  – spectrometer WF in eV      (default 4.5)

        Returns JSON: { be: [...], inten: [...], n_points: int, be_range: [min,max] }
        """
        if "file" not in request.files:
            return _err("No file field in the request")
        f = request.files["file"]
        if not f.filename:
            return _err("No filename provided")

        # Reject non-.vgd before spending the upload budget / writing to disk
        # (audit F12). olefile content validation remains the real gate.
        if Path(f.filename).suffix.lower() != ".vgd":
            return _err("Only .vgd files are accepted by this endpoint.")

        try:
            photon_energy = float(request.form.get("photon_energy", vgd_parser.DEFAULT_PHOTON_ENERGY))
            work_function = float(request.form.get("work_function", vgd_parser.DEFAULT_WORK_FUNCTION))
        except ValueError:
            return _err("photon_energy and work_function must be numbers")

        # Save to a temp file so olefile can open it by path
        tmp_path = Path(app.config["UPLOAD_FOLDER"]) / f"vgd_tmp_{uuid.uuid4().hex}.vgd"
        try:
            f.save(str(tmp_path))
            be, inten = vgd_parser.parse_vgd(
                str(tmp_path),
                photon_energy=photon_energy,
                work_function=work_function,
            )
        except (ValueError, ImportError) as exc:
            # Clean, user/operator-facing: "Not a valid Thermo VGD file",
            # "olefile is required: pip install olefile" (audit F10).
            return _err(str(exc))
        except Exception:
            app.logger.exception("Unexpected VGD parse error")
            return _err("Internal VGD parse error — see server log.", 500)
        finally:
            tmp_path.unlink(missing_ok=True)

        return jsonify({
            "be":       be,
            "inten":    inten,
            "n_points": len(be),
            "be_range": [min(be), max(be)] if be else [0, 0],
        })

    # ── Session management ────────────────────────────────────────────────────

    @app.get("/api/session/<session_id>")
    def get_session(session_id: str):
        _validate_session_id(session_id)
        try:
            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
        except KeyError:
            return _err(f"Session '{session_id}' not found", 404)
        return jsonify({
            "session_id": session_id,
            "n_points": int(len(energy)),
            **_preview(energy, counts, max_pts=2000),
        })

    @app.delete("/api/session/<session_id>")
    def delete_session(session_id: str):
        _validate_session_id(session_id)
        path = _session_path(session_id, app.config["UPLOAD_FOLDER"])
        path.unlink(missing_ok=True)
        return jsonify({"deleted": session_id})

    # ── Background ────────────────────────────────────────────────────────────

    @app.post("/api/background")
    @_require_json
    def background():
        """
        Request body
        ------------
        {
          "session_id": "...",
          "method":     "shirley" | "linear" | "none",
          "start_idx":  0,      // optional
          "end_idx":    -1      // optional
        }
        """
        body = request.get_json()
        session_id = body.get("session_id", "")
        _validate_session_id(session_id)

        try:
            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
        except KeyError:
            return _err(f"Session '{session_id}' not found", 404)

        method = body.get("method", "shirley")
        start_idx = _parse_int(body.get("start_idx"), 0, len(energy))
        end_idx = _parse_int(body.get("end_idx"), 0, len(energy), default=len(energy))
        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
        try:
            ep_avg = max(1, int(body.get("endpoint_avg", 1)))
        except (TypeError, ValueError):
            return _err("endpoint_avg must be an integer")

        try:
            result = fitting.compute_background_only(
                energy, counts, method=method,
                start_idx=start_idx, end_idx=end_idx,
                endpoint_avg=ep_avg,
            )
        except ValueError as exc:
            # Our own validation, e.g. "Unknown background method" (audit F10).
            return _err(str(exc))
        except Exception:
            app.logger.exception("Unexpected background error")
            return _err("Internal background error — see server log.", 500)

        return jsonify(result)

    # ── Peak fitting ──────────────────────────────────────────────────────────

    @app.post("/api/fit")
    @_require_json
    def fit():
        """
        Request body
        ------------
        {
          "session_id": "...",

          "background": {
            "method":    "shirley",   // "shirley" | "linear" | "none"
            "start_idx": 0,           // optional – slice into data array
            "end_idx":   -1           // optional
          },

          "peaks": [
            {
              "id":           "p1",               // unique string id
              "shape":        "pseudo_voigt_gl",  // peak lineshape
              "center":       284.8,
              "center_min":   283.0,              // optional bound
              "center_max":   286.0,              // optional bound
              "amplitude":    10000,
              "amplitude_min": 0,                 // optional (default 0)
              "fwhm":         1.5,
              "fwhm_min":     0.2,                // optional
              "fwhm_max":     3.0,                // optional
              "gl_ratio":     0.3,                // Lorentzian fraction [0–1]
              "fwhm_l":       1.5,                // asymmetric_gl only
              "fwhm_r":       1.5,                // asymmetric_gl only
              "alpha":        0.1,                // doniach_sunjic only
              "constrain_to": null,               // id of master peak, or null
              "splitting":    3.67,               // BE offset from master (eV)
              "area_ratio":   0.75,               // amplitude = master × ratio
              "fix_fwhm":     true                // lock FWHM to master
            }
          ]
        }
        """
        body = request.get_json()
        session_id = body.get("session_id", "")
        _validate_session_id(session_id)

        try:
            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
        except KeyError:
            return _err(f"Session '{session_id}' not found", 404)

        # Background config
        bg_cfg = body.get("background", {})
        bg_method = bg_cfg.get("method", "shirley")
        bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
        bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
        try:
            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
        except (TypeError, ValueError):
            return _err("endpoint_avg must be an integer")
        manual_bg = bg_cfg.get("manual_bg")

        # Peak specs
        peak_specs = body.get("peaks", [])
        if not peak_specs:
            return _err("'peaks' list is empty – provide at least one peak")

        # Validate peak ids are unique
        ids = [p.get("id") for p in peak_specs]
        if len(ids) != len(set(ids)):
            return _err("Duplicate peak ids found – each peak must have a unique 'id'")

        _ALLOWED_METHODS = {
            "leastsq", "least_squares", "nelder",
            "differential_evolution", "basinhopping",
        }
        fit_method = body.get("fit_method", "leastsq")
        if fit_method not in _ALLOWED_METHODS:
            return _err(f"Unknown fit_method '{fit_method}'")

        # Bounded, type-checked n_perturb (audit F7; also covers the F9
        # ValueError-on-bad-input case for this field). Reject out-of-range or
        # non-integer values with a clean 400 instead of a 500 or a worker hang.
        try:
            n_perturb = int(body.get("n_perturb", 5))
        except (TypeError, ValueError):
            return _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
        if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
            return _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")

        try:
            result = fitting.run_fit(
                energy=energy,
                counts=counts,
                peak_specs=peak_specs,
                background_method=bg_method,
                bg_start_idx=bg_start,
                bg_end_idx=bg_end,
                charge_shift_ev=0.0,
                fit_kws={"method": fit_method},
                manual_bg=manual_bg,
                n_perturb=n_perturb,
                endpoint_avg=endpoint_avg,
            )
        except ValueError as exc:
            # Our own validation: unknown shape/method, self/circular constraint,
            # "Master peak not found", bad numeric field, etc. (audit F10/F11).
            return _err(str(exc))
        except RuntimeError:
            # Solver-internal failure (e.g. lmfit non-convergence). Log the
            # detail; return a generic 422 that leaks no library internals.
            app.logger.exception("Fit failed")
            return _err("Fit failed — see server log for details.", 422)
        except Exception:
            app.logger.exception("Unexpected fitting error")
            return _err("Internal fitting error — see server log.", 500)

        return jsonify(result)

    # ── Autofit analyze (opt-in Find Peaks; STRICTLY ADDITIVE — the manual
    #    /api/fit path above is untouched) ──────────────────────────────────

    _ANALYZE_METHODS = {
        # adjustable defaults surfaced by /api/analyze/meta (spec §5A);
        # anything the client sends in `options` overrides these and is
        # validated by the METHOD's own option whitelist (ValueError → 400)
        "least_squares": {"background_method": "shirley"},
        "ic_model_comparison": {"n_refits": 4, "rng_seed": 0,
                                "enable_proposal_pass": True},
        "bayesian_exchange_mc": {"n_replicas": 8, "n_sweeps": 600,
                                 "rng_seed": 0},
        "sparse_map": {},
    }

    @app.get("/api/analyze/meta")
    def analyze_meta():
        """Registered regions, material classes, and the method menu with
        its ADJUSTABLE defaults — everything the opt-in Find Peaks UI needs
        to build its form."""
        from autofit.grammar import MaterialClass
        from autofit.methods import available_methods
        from autofit.regions import registered_regions

        menu = [dict(m) for m in available_methods()
                if m.get("id") in _ANALYZE_METHODS and m.get("implemented")]
        for m in menu:
            m["default_options"] = dict(_ANALYZE_METHODS[m["id"]])
        return jsonify({
            "regions": registered_regions(),
            "material_classes": [m.value for m in MaterialClass],
            "methods": menu,
        })

    @app.post("/api/analyze")
    @_require_json
    def analyze():
        """
        Opt-in grammar-driven peak finding (spec §5A/§8).

        Request body
        ------------
        {
          "session_id":     "...",
          "cc_shift":       0.0,          // frontend charge shift (corrected = raw − cc_shift)
          "roi":            {"be_min": ..., "be_max": ...},   // corrected frame
          "material_class": "conductor" | "insulator" | "semiconductor",
          "regions":        ["Cl 2p", ...],   // registered region names
          "phase":          {"id": "sample", "material": "graphite"},  // optional
          "method":         "ic_model_comparison" | "least_squares"
                            | "bayesian_exchange_mc" | "sparse_map",
          "options":        {...},        // per-method; validated by the method
          "peak_specs":     [...]         // least_squares only (manual baseline)
        }

        Returns the full MethodResult: candidate peaks with the per-peak
        confidence vector, the analysis namespace (ambiguity flags, ranked
        alternatives, constants provenance), diagnostics, and a review-gate
        stub — results are candidates + honesty flags, not ground truth;
        a NAMED human review is required before export (spec §8).
        """
        from autofit.grammar import (MaterialClass, Phase,
                                     PhaseAmbiguityError, UnknownRegionError,
                                     resolve)
        from autofit.methods import get_method

        body = request.get_json()
        session_id = body.get("session_id", "")
        _validate_session_id(session_id)
        try:
            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
        except KeyError:
            return _err(f"Session '{session_id}' not found", 404)

        method_id = body.get("method", "ic_model_comparison")
        if method_id not in _ANALYZE_METHODS:
            return _err(f"Unknown analyze method '{method_id}' "
                        f"(available: {sorted(_ANALYZE_METHODS)})")

        regions = body.get("regions") or []
        if (not isinstance(regions, list) or not regions
                or not all(isinstance(r, str) for r in regions)):
            return _err("'regions' must be a non-empty list of region names")

        mc_raw = body.get("material_class", "")
        try:
            mclass = MaterialClass(mc_raw)
        except ValueError:
            return _err(f"Unknown material_class '{mc_raw}'")

        try:
            cc_shift = float(body.get("cc_shift", 0.0))
        except (TypeError, ValueError):
            return _err("cc_shift must be a number")
        corrected = energy - cc_shift   # frontend getCorrectedBE convention

        roi = body.get("roi") or {}
        try:
            be_min = float(roi.get("be_min", float(corrected.min())))
            be_max = float(roi.get("be_max", float(corrected.max())))
        except (TypeError, ValueError):
            return _err("roi.be_min/be_max must be numbers")
        mask = (corrected >= be_min) & (corrected <= be_max)
        if int(mask.sum()) < 20:
            return _err("ROI selects fewer than 20 points")
        x, y = corrected[mask], counts[mask]

        options = body.get("options") or {}
        if not isinstance(options, dict):
            return _err("'options' must be an object")
        opts = {**_ANALYZE_METHODS[method_id], **options}

        peak_specs = body.get("peak_specs") or None
        if method_id == "least_squares" and not peak_specs:
            return _err("least_squares is the manual-model baseline — "
                        "provide 'peak_specs'")

        phase_kwargs = body.get("phase") or {}
        grammar = None
        if method_id != "least_squares":
            phase = Phase(id=str(phase_kwargs.get("id", "sample")),
                          material_class=mclass,
                          regions=tuple(regions),
                          material=phase_kwargs.get("material"))
            try:
                grammar = resolve(
                    [phase], regions if len(regions) > 1 else regions[0])
            except (UnknownRegionError, PhaseAmbiguityError, ValueError) as exc:
                return _err(str(exc))

        try:
            res = get_method(method_id).run(
                x, y, grammar=grammar, peak_specs=peak_specs, options=opts)
        except ValueError as exc:
            # the method's own option/spec validation
            return _err(str(exc))
        except Exception:
            app.logger.exception("analyze failed")
            return _err("Internal analyze error — see server log.", 500)

        return jsonify(_json_sanitize({
            "method": method_id,
            "success": bool(res.success),
            "peaks": res.peaks,
            "confidence": res.confidence,
            "analysis": res.analysis,
            "diagnostics": res.diagnostics,
            "message": res.message,
            "review_gate": {
                "reviewed_by": None,
                "note": "results are candidates + confidence flags, not "
                        "ground truth — a named human review is required "
                        "before export (spec §8)",
            },
        }))

    # ── Health check ──────────────────────────────────────────────────────────

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})


# ─────────────────────────────────────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────────────────────────────────────

def _register_error_handlers(app: Flask) -> None:

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "File too large (limit 50 MB)"}), 413

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception("Unhandled 500 error")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Small utilities
# ─────────────────────────────────────────────────────────────────────────────

def _validate_session_id(session_id: str) -> None:
    """Raise 400 if session_id looks unsafe (path traversal guard)."""
    try:
        uuid.UUID(session_id)
    except (ValueError, AttributeError):
        from flask import abort
        abort(400, description="Invalid session_id format (expected UUID)")


def _parse_int(value, lo: int, hi: int, default: int | None = None) -> int | None:
    """Convert a JSON value to a bounded integer index."""
    if value is None:
        return default
    try:
        v = int(value)
        if v < 0:
            v = max(0, hi + v)  # support negative indexing like Python
        return max(lo, min(hi, v))
    except (TypeError, ValueError):
        return default


def _preview(
    energy: np.ndarray,
    counts: np.ndarray,
    max_pts: int = 2000,
) -> dict:
    """Return (possibly downsampled) energy/counts lists for API responses."""
    n = len(energy)
    if n <= max_pts:
        return {"energy": energy.tolist(), "counts": counts.tolist()}
    # Uniform stride downsample (preserves endpoints)
    idx = np.round(np.linspace(0, n - 1, max_pts)).astype(int)
    return {
        "energy": energy[idx].tolist(),
        "counts": counts[idx].tolist(),
        "downsampled": True,
        "original_n_points": n,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Module‑level app instance for gunicorn / flask CLI
# ─────────────────────────────────────────────────────────────────────────────

app = create_app()

if __name__ == "__main__":
    # Development server only – gunicorn does NOT call this block.
    # Debug mode defaults OFF to avoid exposing the Werkzeug debugger
    # (which allows arbitrary code execution from the browser). Set
    # FLASK_DEBUG=1 explicitly during local development.
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
