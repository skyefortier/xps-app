"""
Thermo Scientific Avantage VGD file parser.

VGD files are OLE Compound Documents (Microsoft CFBF) with the following
streams used for XPS spectral data:

  VGData      – float64 array, intensity counts per point.
                For overlay files this is n_scans × n_pts values concatenated.

  VGDataAxes  – binary block; bytes 12–15 (uint32 LE) = n_intervals
                (number of energy steps; n_pts = n_intervals + 1).

  VGSpaceAxes – binary block containing the energy-axis parameters.
                Both single-scan and multi-scan (overlay) files contain a
                consecutive float64 pair: (start_ke, step_ke).
                  start_ke ∈ (100, 2000) eV  – kinetic energy of first point
                  step_ke  ∈ (0.01, 10)  eV  – KE step per point (positive)
                BE is computed as:
                  BE[i] = photon_energy − (start_ke + i·step_ke) − work_function

Default assumptions (standard Thermo lab configuration):
  photon_energy = 1486.6 eV  (Al Kα monochromated)
  work_function = 4.5 eV     (typical spectrometer WF)

The returned arrays are sorted in *increasing* BE order.
"""

import struct
import numpy as np


# ── Public defaults ────────────────────────────────────────────────────────────
DEFAULT_PHOTON_ENERGY: float = 1486.6   # Al Kα (eV)
DEFAULT_WORK_FUNCTION: float = 4.5      # spectrometer work function (eV)


# ── Main entry point ───────────────────────────────────────────────────────────

def parse_vgd(
    filepath: str,
    photon_energy: float = DEFAULT_PHOTON_ENERGY,
    work_function: float = DEFAULT_WORK_FUNCTION,
) -> tuple[list[float], list[float]]:
    """Parse a Thermo Avantage VGD file.

    Parameters
    ----------
    filepath      : path to the .vgd file
    photon_energy : X-ray source energy in eV (default Al Kα 1486.6 eV)
    work_function : spectrometer work function in eV (default 4.5 eV)

    Returns
    -------
    (be, intensity) : two Python lists of floats, sorted by increasing BE.
    For overlay (multi-scan) files the intensity is the per-point average
    across all constituent scans.

    Raises
    ------
    ValueError if the file is not a valid VGD/OLE file or the required
    streams cannot be decoded.
    """
    try:
        import olefile
    except ImportError:
        raise ImportError("olefile is required: pip install olefile")

    if not olefile.isOleFile(filepath):
        raise ValueError(
            "Not a valid Thermo VGD file (OLE compound document magic bytes not found)"
        )

    with olefile.OleFileIO(filepath) as ole:
        # ── 1. Intensity counts ────────────────────────────────────────────────
        raw_data = ole.openstream("VGData").read()
        n_total = len(raw_data) // 8
        if n_total < 5:
            raise ValueError("VGData stream is too short to contain spectral data")

        # ── 2. Number of energy points ─────────────────────────────────────────
        ax_raw = ole.openstream("VGDataAxes").read()
        if len(ax_raw) < 16:
            raise ValueError("VGDataAxes stream too short")
        n_intervals = struct.unpack("<I", ax_raw[12:16])[0]
        n_pts = n_intervals + 1

        # ── 3. Energy-axis parameters from VGSpaceAxes ─────────────────────────
        sp_raw = ole.openstream("VGSpaceAxes").read()
        start_ke, step_ke = _find_ke_axis(sp_raw)

    # ── 4. Build intensity array (average overlapping scans if present) ────────
    if n_pts < 1:
        raise ValueError(f"Degenerate axis: n_pts = {n_pts}")

    if n_total >= n_pts and n_total % n_pts == 0:
        n_scans = n_total // n_pts
        all_counts = np.frombuffer(raw_data[: n_pts * n_scans * 8], dtype="<f8")
        counts = all_counts.reshape(n_scans, n_pts).mean(axis=0)
    else:
        # Mismatch — use however many complete points we have
        n_use = min(n_pts, n_total)
        counts = np.frombuffer(raw_data[: n_use * 8], dtype="<f8")
        n_pts = n_use

    # ── 5. KE → BE conversion ─────────────────────────────────────────────────
    ke = start_ke + np.arange(n_pts) * step_ke
    be = photon_energy - ke - work_function

    # ── 6. Sort to increasing BE (KE increases ⟹ BE decreases, so reverse) ───
    if len(be) > 1 and be[0] > be[-1]:
        be = be[::-1]
        counts = counts[::-1]

    return be.tolist(), counts.tolist()


# ── Internal helpers ───────────────────────────────────────────────────────────

def _find_ke_axis(sp: bytes) -> tuple[float, float]:
    """Locate (start_ke, step_ke) float64 pair in the VGSpaceAxes stream.

    Works for both single-scan (51-byte) and overlay/multi-axis (≥136-byte)
    variants by scanning for the first consecutive float64 pair where:
      start_ke ∈ (100, 2000) eV   and   step_ke ∈ (0.01, 10) eV
    These constraints are tight enough to avoid false positives.
    """
    for off in range(0, len(sp) - 15):
        try:
            v1 = struct.unpack("<d", sp[off : off + 8])[0]
            v2 = struct.unpack("<d", sp[off + 8 : off + 16])[0]
        except struct.error:
            continue
        if 100.0 < v1 < 2000.0 and 0.01 < v2 < 10.0:
            return v1, v2

    raise ValueError(
        "Could not locate KE axis parameters in VGSpaceAxes stream. "
        "The file may use an unsupported VGD variant."
    )
