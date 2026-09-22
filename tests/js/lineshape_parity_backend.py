#!/usr/bin/env python3
"""Backend-shape evaluator bridge for tests/js/lineshape_parity.test.js.

Reads a JSON spec from stdin:
    {"shape": "<key in fitting._SHAPE_FUNCS>", "params": {...}, "x": [...]}
or a JSON list of such specs.
Writes a JSON array of y-values (or a list of arrays) to stdout.

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


def _eval(spec: dict) -> list[float]:
    x = np.array(spec["x"], dtype=float)
    fn = _SHAPE_FUNCS[spec["shape"]]
    return [float(v) for v in fn(x, **spec["params"])]


def main() -> None:
    spec = json.load(sys.stdin)
    # A list of specs (the A03 parameter sweep) is answered with a list of
    # curves in one interpreter start; a single spec as before.
    if isinstance(spec, list):
        json.dump([_eval(s) for s in spec], sys.stdout)
    else:
        json.dump(_eval(spec), sys.stdout)


if __name__ == "__main__":
    main()
