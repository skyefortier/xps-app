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
POST /api/charge-correct    Compute charge shift from a reference peak
GET  /api/peak-shapes       List available lineshape names
GET  /api/elements          List built‑in spin‑orbit element presets
GET  /api/session/<id>      Retrieve raw session data
DELETE /api/session/<id>    Delete session files
"""

from __future__ import annotations

import logging
import os
import uuid
from functools import wraps
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

import fitting
import parser as xps_parser
import vgd_parser

# ─────────────────────────────────────────────────────────────────────────────
# Application factory
# ─────────────────────────────────────────────────────────────────────────────

def create_app(upload_folder: str = "uploads") -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")

    app.config["UPLOAD_FOLDER"] = upload_folder
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

def _session_path(session_id: str, upload_folder: str) -> Path:
    return Path(upload_folder) / f"{session_id}.npz"


def _load_session(session_id: str, upload_folder: str) -> tuple[np.ndarray, np.ndarray]:
    """Load energy and counts arrays from a session file."""
    path = _session_path(session_id, upload_folder)
    if not path.exists():
        raise KeyError(session_id)
    archive = np.load(path)
    return archive["energy"], archive["counts"]


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
            return render_template("index.html")
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
        }
        return jsonify({k: descriptions[k] for k in fitting.AVAILABLE_SHAPES})

    @app.get("/api/elements")
    def elements():
        return jsonify(SPIN_ORBIT_PRESETS)

    @app.get("/api/charge-references")
    def charge_references():
        return jsonify(fitting.CHARGE_REFERENCES)

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

        # Save raw upload temporarily
        tmp_path = Path(app.config["UPLOAD_FOLDER"]) / filename
        f.save(str(tmp_path))

        try:
            energy, counts = xps_parser.parse_file(tmp_path)
        except Exception as exc:
            tmp_path.unlink(missing_ok=True)
            return _err(f"Failed to parse file: {exc}")
        finally:
            tmp_path.unlink(missing_ok=True)

        session_id = str(uuid.uuid4())
        try:
            _save_session(session_id, app.config["UPLOAD_FOLDER"],
                          energy, counts, filename)
        except Exception as exc:
            return _err(f"Failed to store session: {exc}", 500)

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
            return _err(str(exc))
        except Exception as exc:
            return _err(f"VGD parse error: {exc}", 500)
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

        try:
            result = fitting.compute_background_only(
                energy, counts, method=method,
                start_idx=start_idx, end_idx=end_idx,
            )
        except Exception as exc:
            return _err(str(exc))

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
          ],

          "charge_correction": {                  // optional
            "method":      "c1s",                 // "c1s" | "au4f" | "manual"
            "measured_be": 285.0,                 // observed reference peak BE
            "reference_be": 284.8                 // for "manual" only
          }
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

        # Peak specs
        peak_specs = body.get("peaks", [])
        if not peak_specs:
            return _err("'peaks' list is empty – provide at least one peak")

        # Validate peak ids are unique
        ids = [p.get("id") for p in peak_specs]
        if len(ids) != len(set(ids)):
            return _err("Duplicate peak ids found – each peak must have a unique 'id'")

        # Charge correction
        shift_ev = 0.0
        cc = body.get("charge_correction")
        if cc:
            method_cc = cc.get("method", "").lower()
            if method_cc == "manual":
                ref = float(cc.get("reference_be", 0.0))
                meas = float(cc.get("measured_be", 0.0))
                shift_ev = ref - meas
            else:
                try:
                    shift_ev = fitting.charge_shift(method_cc, float(cc["measured_be"]))
                except (KeyError, ValueError) as exc:
                    return _err(str(exc))

        _ALLOWED_METHODS = {
            "leastsq", "least_squares", "nelder",
            "differential_evolution", "basinhopping",
        }
        fit_method = body.get("fit_method", "leastsq")
        if fit_method not in _ALLOWED_METHODS:
            return _err(f"Unknown fit_method '{fit_method}'")

        n_perturb = int(body.get("n_perturb", 5))
        try:
            result = fitting.run_fit(
                energy=energy,
                counts=counts,
                peak_specs=peak_specs,
                background_method=bg_method,
                bg_start_idx=bg_start,
                bg_end_idx=bg_end,
                charge_shift_ev=shift_ev,
                fit_kws={"method": fit_method},
                n_perturb=n_perturb,
            )
        except ValueError as exc:
            return _err(str(exc))
        except RuntimeError as exc:
            return _err(str(exc), 422)
        except Exception as exc:
            app.logger.exception("Unexpected fitting error")
            return _err(f"Internal fitting error: {exc}", 500)

        return jsonify(result)

    # ── Charge correction (standalone) ────────────────────────────────────────

    @app.post("/api/charge-correct")
    @_require_json
    def charge_correct():
        """
        Compute and return the charge shift without running a full fit.

        Request body
        ------------
        {
          "method":      "c1s" | "au4f" | "manual",
          "measured_be": 285.2,
          "reference_be": 284.8   // required for "manual"
        }

        Returns
        -------
        {"charge_shift": <float>, "corrected_reference": <float>}
        """
        body = request.get_json()
        method = body.get("method", "c1s").lower()
        measured = body.get("measured_be")
        if measured is None:
            return _err("'measured_be' is required")

        if method == "manual":
            reference = body.get("reference_be")
            if reference is None:
                return _err("'reference_be' is required for manual correction")
            shift = float(reference) - float(measured)
        else:
            try:
                shift = fitting.charge_shift(method, float(measured))
            except ValueError as exc:
                return _err(str(exc))

        return jsonify({
            "charge_shift": shift,
            "corrected_reference": fitting.CHARGE_REFERENCES.get(method),
        })

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
    # Debug mode is on by default; set FLASK_DEBUG=0 to disable.
    debug = os.environ.get("FLASK_DEBUG", "1") != "0"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
