"""Read the property sets of a Thermo Avantage .VGD file exactly (MS-OLEPS), for measurement only.

olefile's ``getproperties`` misreads these streams: several values are vectors of variants and its
string reader runs past them (it returns 'Nexsa_G2\\x00\\x00\\x03\\x00…' for property 6). This reader
follows the property-set format — each property a 4-byte type header and its value padded to 4 bytes;
VT_VECTOR of VT_VARIANT elements each with its own header.

The app never reads these properties (vgd_parser.py reads only VGData, VGDataAxes and VGSpaceAxes).
``ACQUISITION`` names the ids this unit uses; every name is an identification by evidence, not a
documented meaning — Thermo does not publish the ids (docs/findings/noise-estimator/counting-time.md).

    venv/bin/python scripts/vgd_properties.py FILE.VGD     # dump every property of every set
"""
import datetime
import struct
import sys

import olefile

_VT = {0: "EMPTY", 1: "NULL", 2: "I2", 3: "I4", 4: "R4", 5: "R8", 7: "DATE", 8: "BSTR", 10: "ERROR",
       11: "BOOL", 12: "VARIANT", 16: "I1", 17: "UI1", 18: "UI2", 19: "UI4", 20: "I8", 21: "UI8",
       22: "INT", 23: "UINT", 30: "LPSTR", 31: "LPWSTR", 64: "FILETIME", 65: "BLOB", 72: "CLSID"}

# id -> (name, evidence) — identifications, see counting-time.md for the evidence of each
ACQUISITION = {
    105: "photon energy (eV)",
    305: "dwell time per step (s)",
    306: "number of scans",
    328: "number of scans (second copy)",
    404: "pass energy (eV)",
    406: "unidentified (4.2; a work function would be one reading)",
    303: "acquisition start",
    304: "acquisition end",
    331: "detector signature file (path on the instrument PC)",
    981: "energy calibration (text)",
}


def _pad4(n):
    return (n + 3) & ~3


def _value(b, o, vt=None):
    """(type name, value), next offset. Reads the 4-byte type header when ``vt`` is None."""
    if vt is None:
        vt = struct.unpack_from("<H", b, o)[0]
        o += 4
    base = vt & 0x0FFF
    if vt & 0x1000:
        n = struct.unpack_from("<I", b, o)[0]
        o += 4
        out = []
        for _ in range(n):
            v, o = _value(b, o, None if base == 12 else base)
            out.append(v)
        return ("VECTOR", out), o
    if base in (0, 1):
        return (_VT[base], None), o
    if base == 2:
        return ("I2", struct.unpack_from("<h", b, o)[0]), o + 4
    if base == 18:
        return ("UI2", struct.unpack_from("<H", b, o)[0]), o + 4
    if base in (3, 22):
        return ("I4", struct.unpack_from("<i", b, o)[0]), o + 4
    if base in (10, 19, 23):
        return (_VT[base], struct.unpack_from("<I", b, o)[0]), o + 4
    if base in (16, 17):
        return (_VT[base], b[o]), o + 4
    if base == 4:
        return ("R4", struct.unpack_from("<f", b, o)[0]), o + 4
    if base == 5:
        return ("R8", struct.unpack_from("<d", b, o)[0]), o + 8
    if base == 7:
        d = struct.unpack_from("<d", b, o)[0]
        return ("DATE", datetime.datetime(1899, 12, 30) + datetime.timedelta(days=d)), o + 8
    if base == 11:
        return ("BOOL", struct.unpack_from("<h", b, o)[0] != 0), o + 4
    if base in (20, 21):
        return (_VT[base], struct.unpack_from("<q" if base == 20 else "<Q", b, o)[0]), o + 8
    if base == 64:
        ticks = struct.unpack_from("<Q", b, o)[0]           # 100 ns since 1601-01-01 (UTC)
        return ("FILETIME", (datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=ticks // 10), ticks)), o + 8
    if base == 30:
        n = struct.unpack_from("<I", b, o)[0]
        return ("LPSTR", b[o + 4:o + 4 + n].split(b"\0")[0].decode("latin-1")), o + 4 + _pad4(n)
    if base == 31:
        n = struct.unpack_from("<I", b, o)[0]
        return ("LPWSTR", b[o + 4:o + 4 + 2 * n].decode("utf-16-le").split("\0")[0]), o + 4 + _pad4(2 * n)
    if base == 8:                                            # these files hold UTF-16 text in BSTRs
        n = struct.unpack_from("<I", b, o)[0]
        raw = b[o + 4:o + 4 + n]
        try:
            text = raw.decode("utf-16-le").split("\0")[0]
        except UnicodeDecodeError:
            text = raw
        return ("BSTR", text), o + 4 + _pad4(n)
    if base == 65:
        n = struct.unpack_from("<I", b, o)[0]
        return ("BLOB", b[o + 4:o + 4 + n]), o + 4 + _pad4(n)
    if base == 72:
        return ("CLSID", b[o:o + 16].hex()), o + 16
    raise ValueError(f"unhandled property type {vt:#x} at offset {o}")


def property_set(raw):
    """{id: (type, value)} over every section of one property-set stream (0 = dictionary, 1 = code page)."""
    out = {}
    for s in range(struct.unpack_from("<I", raw, 24)[0]):
        off = struct.unpack_from("<I", raw, 28 + 20 * s + 16)[0]
        nprop = struct.unpack_from("<I", raw, off + 4)[0]
        for i in range(nprop):
            pid, poff = struct.unpack_from("<II", raw, off + 8 + 8 * i)
            if pid == 0:
                out[pid] = ("DICTIONARY", None)
            elif pid == 1:
                out[pid] = ("CODEPAGE", struct.unpack_from("<h", raw, off + poff + 4)[0])
            else:
                out[pid] = _value(raw, off + poff)[0]
    return out


def all_property_sets(path):
    """{stream name without its leading \\x05: property set} for every property-set stream of the file."""
    with olefile.OleFileIO(path) as ole:
        return {"/".join(e)[1:]: property_set(ole.openstream("/".join(e)).read())
                for e in ole.listdir() if e[-1].startswith("\x05")}


def main_properties(path):
    """The file's main property set — the one stream with more than a handful of properties."""
    sets = [p for p in all_property_sets(path).values() if len(p) > 10]
    if len(sets) != 1:
        raise ValueError(f"{path}: expected one main property set, found {len(sets)}")
    return sets[0]


if __name__ == "__main__":
    for name, props in all_property_sets(sys.argv[1]).items():
        print("==", repr(name))
        for k in sorted(props):
            print(f"  {k:>10} {ACQUISITION.get(k, ''):40.40} {props[k]!r:.300}")
