#!/usr/bin/env python3
"""Backend-shape evaluator bridge for tests/js/lineshape_parity.test.js.

Reads a JSON spec from stdin:
    {"shape": "<key in fitting._SHAPE_FUNCS>", "params": {...}, "x": [...]}
Writes a JSON array of y-values to stdout.

Calls fitting.py's OWN registered shape functions (_SHAPE_FUNCS) directly —
never a reimplementation — so the JS parity test is always comparing against
whatever the backend actually ships, with no fixture staleness risk.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from fitting import _SHAPE_FUNCS  # noqa: E402


def main() -> None:
    spec = json.load(sys.stdin)
    x = np.array(spec["x"], dtype=float)
    fn = _SHAPE_FUNCS[spec["shape"]]
    y = fn(x, **spec["params"])
    json.dump([float(v) for v in y], sys.stdout)


if __name__ == "__main__":
    main()
