"""
parser.py – File parsing for XPS spectra.

Supported formats
-----------------
  CSV   – two‑column (energy, counts); auto‑detects delimiter and header rows
  XLSX  – first sheet, first two numeric columns used
  VGD   – Thermo Scientific / Avantage binary spectrum file (best‑effort)

Entry point
-----------
  parse_file(filepath)  →  (energy: np.ndarray, counts: np.ndarray)

Both arrays are returned in their original order; callers can sort/flip as
needed.  Energy is assumed to be binding energy (eV).
"""

from __future__ import annotations

import io
import logging
import re
import struct
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {".csv", ".txt", ".xy", ".xlsx", ".xls", ".vgd"}


def parse_file(filepath: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """
    Detect format and parse an XPS data file.

    Returns
    -------
    energy : np.ndarray  – binding energy (eV), shape (N,)
    counts : np.ndarray  – intensity (counts or CPS), shape (N,)

    Raises
    ------
    ValueError  – if the format is unrecognised or the file is malformed
    """
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix in (".csv", ".txt", ".xy"):
        return parse_csv(path)
    elif suffix in (".xlsx", ".xls"):
        return parse_xlsx(path)
    elif suffix == ".vgd":
        return parse_vgd(path)
    else:
        # Try CSV as a fallback
        try:
            return parse_csv(path)
        except Exception:
            raise ValueError(
                f"Unsupported file extension '{suffix}'. "
                f"Accepted: {sorted(ALLOWED_EXTENSIONS)}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# CSV / plain text
# ─────────────────────────────────────────────────────────────────────────────

def parse_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """
    Parse a delimited text file with two numeric columns (energy, counts).

    • Supports comma, tab, semicolon, and space delimiters.
    • Skips comment lines beginning with '#' or '%'.
    • Auto‑skips any header rows that are not entirely numeric.
    • Accepts both KE and BE axes (caller must know which was exported).
    """
    raw = path.read_bytes()

    # Decode; try UTF‑8 then latin‑1
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    # Filter comment lines
    lines = [
        line for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "%"))
    ]
    if not lines:
        raise ValueError("File appears to be empty or contains only comments")

    # Detect delimiter from the first non‑empty data‑looking line
    delimiter = _detect_delimiter("\n".join(lines[:20]))

    try:
        df = pd.read_csv(
            io.StringIO("\n".join(lines)),
            sep=delimiter,
            header=None,
            comment="#",
            engine="python",
        )
    except Exception as exc:
        raise ValueError(f"CSV parse error: {exc}") from exc

    # Drop any entirely‑NaN columns (e.g. trailing delimiter)
    df.dropna(axis=1, how="all", inplace=True)

    # Extract the first two numeric columns
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if len(numeric_cols) < 2:
        # Possibly header row(s) still present – try skiprows
        for skip in range(1, min(20, len(df))):
            df2 = pd.read_csv(
                io.StringIO("\n".join(lines)),
                sep=delimiter,
                header=None,
                skiprows=skip,
                comment="#",
                engine="python",
            )
            df2.dropna(axis=1, how="all", inplace=True)
            nc = [c for c in df2.columns if pd.api.types.is_numeric_dtype(df2[c])]
            if len(nc) >= 2:
                df = df2
                numeric_cols = nc
                break
        else:
            raise ValueError(
                "Could not find two numeric columns in the file. "
                "Expected (energy, counts)."
            )

    energy = df[numeric_cols[0]].to_numpy(dtype=float)
    counts = df[numeric_cols[1]].to_numpy(dtype=float)

    mask = np.isfinite(energy) & np.isfinite(counts)
    if mask.sum() < 2:
        raise ValueError("Fewer than 2 valid (finite) data points found")

    return energy[mask], counts[mask]


def _detect_delimiter(sample: str) -> str:
    """Heuristically detect the delimiter used in a text block."""
    candidates = [",", "\t", ";", " "]
    counts = {d: sample.count(d) for d in candidates}
    return max(counts, key=counts.get)


# ─────────────────────────────────────────────────────────────────────────────
# XLSX / XLS
# ─────────────────────────────────────────────────────────────────────────────

def parse_xlsx(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """
    Parse the first sheet of an Excel workbook.

    Uses the first two columns that contain purely numeric data.
    Up to 20 header rows are tolerated.
    """
    try:
        xl = pd.ExcelFile(path, engine="openpyxl" if path.suffix.lower() == ".xlsx" else None)
    except Exception as exc:
        raise ValueError(f"Cannot open Excel file: {exc}") from exc

    sheet = xl.sheet_names[0]

    for skip in range(21):
        try:
            df = pd.read_excel(xl, sheet_name=sheet, header=None, skiprows=skip)
        except Exception:
            continue
        df.dropna(axis=1, how="all", inplace=True)
        df.dropna(axis=0, how="all", inplace=True)
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if len(numeric_cols) >= 2:
            energy = df[numeric_cols[0]].to_numpy(dtype=float)
            counts = df[numeric_cols[1]].to_numpy(dtype=float)
            mask = np.isfinite(energy) & np.isfinite(counts)
            if mask.sum() >= 2:
                return energy[mask], counts[mask]

    raise ValueError(
        "Could not find two numeric columns in the Excel file. "
        "Expected (energy, counts)."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Thermo Scientific VGD binary format
# ─────────────────────────────────────────────────────────────────────────────

# Known magic / header signatures for VGD variants
_VGD_MAGIC_BYTES = [
    b"VGD",
    b"VAMAS",
    b"Thermo",
    b"ESCALAB",
    b"K-Alpha",
    b"Avantage",
]

# Regex patterns to extract calibration from text‑style headers
_RE_START   = re.compile(r"(?:start\s*(?:ke|be|energy)|start)\s*[=:]\s*([\d.eE+\-]+)", re.I)
_RE_END     = re.compile(r"(?:end\s*(?:ke|be|energy)|end)\s*[=:]\s*([\d.eE+\-]+)", re.I)
_RE_STEP    = re.compile(r"(?:step\s*(?:size|energy)?|increment)\s*[=:]\s*([\d.eE+\-]+)", re.I)
_RE_NPTS    = re.compile(r"(?:number\s*of\s*(?:points|channels)|npoints|npts)\s*[=:]\s*(\d+)", re.I)
_RE_KE_BE   = re.compile(r"(?:energy\s*(?:reference|scale)|axis)\s*[=:]\s*(\w+)", re.I)


def parse_vgd(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """
    Parse a Thermo Scientific VGD binary spectrum file.

    Strategy (tried in order)
    -------------------------
    1. Mixed ASCII+binary: look for text header, parse calibration, read float32 payload.
    2. Structured binary: probe known byte offsets for common VGD layout variants.
    3. Brute‑force: scan the entire file for the largest contiguous block of
       plausible float32 values (all positive, < 1e9).

    Raises ValueError if no strategy succeeds.
    Notes
    -----
    The VGD format is proprietary and undocumented.  If parsing fails, export
    the spectrum as CSV from Thermo Avantage software.
    """
    data = path.read_bytes()

    if len(data) < 16:
        raise ValueError("VGD file is too small to contain spectrum data")

    # ── Strategy 1: text header ───────────────────────────────────────────────
    result = _vgd_text_header(data)
    if result is not None:
        return result

    # ── Strategy 2: known binary layouts ─────────────────────────────────────
    result = _vgd_binary_probe(data)
    if result is not None:
        return result

    # ── Strategy 3: brute‑force float32 block ────────────────────────────────
    result = _vgd_bruteforce(data)
    if result is not None:
        return result

    raise ValueError(
        "Cannot parse VGD file: unrecognised format variant.\n"
        "Tip: export as CSV from Thermo Avantage → File → Export → ASCII."
    )


def _vgd_text_header(data: bytes) -> tuple[np.ndarray, np.ndarray] | None:
    """Try to decode a text header + binary float32 payload."""
    # Look for null‑terminated text block in the first 8 KB
    header_chunk = data[: min(8192, len(data))]

    try:
        text = header_chunk.decode("ascii", errors="replace")
    except Exception:
        return None

    # Check for known signatures
    found_sig = any(sig.decode() in text for sig in _VGD_MAGIC_BYTES)
    if not found_sig and text[:4].isprintable() and len(text.strip()) < 4:
        return None

    # Extract calibration parameters
    m_start = _RE_START.search(text)
    m_end = _RE_END.search(text)
    m_step = _RE_STEP.search(text)
    m_npts = _RE_NPTS.search(text)

    if not (m_npts and (m_step or (m_start and m_end))):
        # Not enough info in header
        return None

    n_pts = int(m_npts.group(1))
    if n_pts < 2 or n_pts > 100_000:
        return None

    start_e = float(m_start.group(1)) if m_start else None
    end_e = float(m_end.group(1)) if m_end else None
    step_e = float(m_step.group(1)) if m_step else None

    if step_e is None and start_e is not None and end_e is not None:
        step_e = (end_e - start_e) / (n_pts - 1)

    if start_e is None or step_e is None:
        return None

    # Find where the binary payload starts: after the last printable text block
    # (look for a run of null bytes or a clear transition to non‑ASCII)
    bin_start = _find_binary_start(data, header_chunk)
    if bin_start is None:
        return None

    floats = _read_float32_block(data, bin_start, n_pts)
    if floats is None:
        return None

    energy = np.array([start_e + i * step_e for i in range(n_pts)])

    # Detect KE vs BE: if energy values look like KE (> 500 eV for typical lab sources)
    # convert to BE assuming Al Kα (1486.6 eV) or Mg Kα (1253.6 eV)
    # We leave this for the caller/frontend; just return as‑is.
    return energy, floats


def _vgd_binary_probe(data: bytes) -> tuple[np.ndarray, np.ndarray] | None:
    """
    Probe known byte‑offset patterns for common VGD binary layouts.

    Layout A (Avantage ≥ 4.x, 512‑byte header):
      offset 4   : uint32  version
      offset 8   : uint32  n_points
      offset 16  : float64 start_ke  (KE in eV)
      offset 24  : float64 step_ke   (step in eV)
      offset 512 : float32[n_points] intensity

    Layout B (older, 256‑byte header):
      offset 0   : uint32  n_points
      offset 8   : float64 start_ke
      offset 16  : float64 step_ke
      offset 256 : float32[n_points]
    """
    for header_size, off_npts, off_start, off_step in [
        (512, 8, 16, 24),
        (256, 0, 8, 16),
        (1024, 8, 16, 24),
        (4096, 16, 32, 40),
    ]:
        try:
            if len(data) < header_size + 8:
                continue
            n_pts = struct.unpack_from("<I", data, off_npts)[0]
            if n_pts < 2 or n_pts > 100_000:
                continue
            start_ke = struct.unpack_from("<d", data, off_start)[0]
            step_ke = struct.unpack_from("<d", data, off_step)[0]
            if not (0 < abs(start_ke) < 1e6 and 0 < abs(step_ke) < 100):
                continue

            floats = _read_float32_block(data, header_size, n_pts)
            if floats is None:
                continue

            energy = np.array([start_ke + i * step_ke for i in range(n_pts)])
            log.info("VGD parsed via binary probe (header=%d, npts=%d)", header_size, n_pts)
            return energy, floats
        except (struct.error, OverflowError):
            continue

    return None


def _vgd_bruteforce(data: bytes) -> tuple[np.ndarray, np.ndarray] | None:
    """
    Last‑resort: treat the entire file as float32 and find the longest run of
    non‑negative, finite values.  Reconstruct a synthetic energy axis.

    This recovers intensity data but loses the true energy calibration; the
    returned energy axis is a 0‑based index array that the frontend should
    replace with proper calibration if available.
    """
    try:
        n_floats = len(data) // 4
        if n_floats < 10:
            return None
        all_floats = np.frombuffer(data, dtype="<f4", count=n_floats).astype(float)
    except Exception:
        return None

    # Find longest run of plausible count values (0 ≤ v < 1e9)
    plausible = np.isfinite(all_floats) & (all_floats >= 0) & (all_floats < 1e9)

    best_start, best_len = 0, 0
    cur_start, cur_len = 0, 0
    for i, ok in enumerate(plausible):
        if ok:
            if cur_len == 0:
                cur_start = i
            cur_len += 1
        else:
            if cur_len > best_len:
                best_start, best_len = cur_start, cur_len
            cur_len = 0
    if cur_len > best_len:
        best_start, best_len = cur_start, cur_len

    if best_len < 10:
        return None

    counts = all_floats[best_start: best_start + best_len]
    energy = np.arange(best_len, dtype=float)  # placeholder index axis
    log.warning(
        "VGD brute‑force extraction: %d points, energy axis is INDEX only "
        "(calibration not recovered).  Supply energy calibration manually.",
        best_len,
    )
    return energy, counts


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _find_binary_start(data: bytes, header_chunk: bytes) -> int | None:
    """
    Find the byte offset where the binary payload starts.

    Heuristic: look for a transition from high printable‑ASCII density to
    low printable‑ASCII density, or for a cluster of null bytes.
    """
    chunk_len = len(header_chunk)
    # Look for a run of >= 8 null bytes
    null_run = data.find(b"\x00" * 8)
    if 0 < null_run < chunk_len:
        # Skip past nulls
        pos = null_run + 8
        while pos < len(data) and data[pos] == 0:
            pos += 1
        return pos if pos < len(data) else None

    # Fallback: after the printable block (first non‑printable region)
    for i in range(16, chunk_len):
        byte = data[i]
        if byte < 0x20 and byte not in (0x09, 0x0A, 0x0D):  # non‑printable, non‑whitespace
            # Round up to nearest 4‑byte boundary
            aligned = (i + 3) & ~3
            return aligned if aligned < len(data) else None

    return None


def _read_float32_block(
    data: bytes,
    offset: int,
    n: int,
    endian: str = "<",
) -> np.ndarray | None:
    """Read n little‑endian float32 values starting at offset; return None on failure."""
    byte_count = n * 4
    if offset + byte_count > len(data):
        return None
    try:
        arr = np.frombuffer(data, dtype=f"{endian}f4", count=n, offset=offset).astype(float)
    except Exception:
        return None
    if not np.all(np.isfinite(arr)):
        # Try big‑endian
        try:
            arr = np.frombuffer(data, dtype=">f4", count=n, offset=offset).astype(float)
        except Exception:
            return None
    if np.any(arr < -1e6) or np.any(arr > 1e12):
        return None
    return arr


# ─────────────────────────────────────────────────────────────────────────────
# Utility: normalise energy axis direction
# ─────────────────────────────────────────────────────────────────────────────

def ensure_ascending(energy: np.ndarray, counts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return arrays sorted by ascending energy (in‑place safe version)."""
    if energy[0] > energy[-1]:
        return energy[::-1].copy(), counts[::-1].copy()
    return energy.copy(), counts.copy()
