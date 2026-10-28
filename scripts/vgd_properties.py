"""Read the property sets of a Thermo Avantage .VGD file exactly (MS-OLEPS), for measurement only.

olefile's ``getproperties`` misreads these streams: its LPWSTR branch (olefile.py:2286-2293 in the
installed 0.47) returns strings that run past their own end (property 6 comes back as
'Nexsa_G2\\x00\\x00\\x03\\x00…'). This reader follows the property-set format: each property a 4-byte
type header and its value padded to 4 bytes; a vector's fixed-size elements packed and the sequence padded
(MS-OLEPS). The committed files hold no vectors; the vector branch is pinned by tests only.

Each set carries its own DICTIONARY (property 0: id -> name), which ``property_names`` decodes; the names
used by this unit (``ACQUISITION``) are the files' own (docs/findings/noise-estimator/counting-time.md).
The app never reads these properties (vgd_parser.py reads only VGData, VGDataAxes and VGSpaceAxes).

    venv/bin/python scripts/vgd_properties.py FILE.VGD     # dump every property of every set
"""
import datetime
import struct
import sys

import olefile

_VT = {0: "EMPTY", 1: "NULL", 2: "I2", 3: "I4", 4: "R4", 5: "R8", 7: "DATE", 8: "BSTR", 10: "ERROR",
       11: "BOOL", 12: "VARIANT", 16: "I1", 17: "UI1", 18: "UI2", 19: "UI4", 20: "I8", 21: "UI8",
       22: "INT", 23: "UINT", 30: "LPSTR", 31: "LPWSTR", 64: "FILETIME", 65: "BLOB", 72: "CLSID"}

# the ids this unit reads, with the name each file's own dictionary gives them (checked in every file)
ACQUISITION = {
    105: "SourceEnergy", 303: "AcquisitionStart", 304: "AcquisitionEnd", 305: "DwellTime", 306: "Scans",
    311: "DetectorMode", 313: "SignatureCorrected", 328: "Current Scan", 331: "DetectorSignatureCorrectionPath",
    404: "PassEnergy", 406: "ChamberWorkFunction", 413: "NumberOfTXFNCoeffs", 415: "Acq_TXFN_Correction",
    416: "Acq_TXFN_CCorrectionType", 417: "NumberOfPSFCoeffs", 850: "DataStorageMethod",
    981: "Calibration Energy Scale", 982: "Calibration Detector Efficiency",
}
_SIZE = {2: 2, 18: 2, 3: 4, 22: 4, 10: 4, 19: 4, 23: 4, 16: 1, 17: 1, 4: 4, 5: 8, 7: 8, 11: 2, 20: 8, 21: 8, 64: 8,
         72: 16}


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
        if base in _SIZE:                                     # fixed-size elements: packed, the sequence padded
            size = _SIZE[base]
            for i in range(n):
                v, _ = _value(b[o + i * size:o + (i + 1) * size] + b"\0" * 16, 0, base)
                out.append(v)
            return ("VECTOR", out), o + _pad4(n * size)
        for _ in range(n):                                    # variants and strings: each its own padded value
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
    if base == 16:
        return ("I1", struct.unpack_from("<b", b, o)[0]), o + 4
    if base == 17:
        return ("UI1", b[o]), o + 4
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


def property_names(raw):
    """{id: name} from the property set's dictionary (property 0) — MS-OLEPS DictionaryEntry: id, character
    count, UTF-16LE name (code page 1200 in every committed file), padded to 4 bytes. {} when there is none."""
    names = {}
    for s in range(struct.unpack_from("<I", raw, 24)[0]):
        off = struct.unpack_from("<I", raw, 28 + 20 * s + 16)[0]
        nprop = struct.unpack_from("<I", raw, off + 4)[0]
        ids = dict(struct.unpack_from("<II", raw, off + 8 + 8 * i) for i in range(nprop))
        if 0 not in ids:
            continue
        o = off + ids[0]
        for _ in range(struct.unpack_from("<I", raw, o)[0]):
            pid, cnt = struct.unpack_from("<II", raw, o + 4)
            names[pid] = raw[o + 12:o + 12 + 2 * cnt].decode("utf-16-le").rstrip("\0")
            o = o + 8 + _pad4(2 * cnt)
    return names


def main_property_names(path):
    """The dictionary of the file's main property set."""
    with olefile.OleFileIO(path) as ole:
        for e in ole.listdir():
            if e[-1].startswith("\x05"):
                raw = ole.openstream("/".join(e)).read()
                if len(property_set(raw)) > 10:
                    return property_names(raw)
    return {}


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
    names = main_property_names(sys.argv[1])
    for name, props in all_property_sets(sys.argv[1]).items():
        print("==", repr(name))
        for k in sorted(props):
            print(f"  {k:>10} {names.get(k, ''):40.40} {props[k]!r:.300}")
