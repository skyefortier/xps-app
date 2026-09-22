"""Bridge for tests/js/local_lm_descent.test.js: run the SERVER fit (fitting.run_fit,
Poisson weights, Trust-Region) from the same scaled starting model the local
engine received, so the JS test can pin local-vs-server parity (unit W1).
stdin: {be, inten, peaks (frontend peak objects), ui}; argv[1]: repo root.
"""
import json
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import fitting  # noqa: E402
from autofit.reference import peak_to_backend_spec  # noqa: E402

d = json.load(sys.stdin)
x = np.asarray(d["be"], float)
y = np.asarray(d["inten"], float)
ui = d["ui"]
specs = [peak_to_backend_spec(p, d["peaks"]) for p in d["peaks"]]
if d.get("bg_idx"):
    # the caller selected the window on the page's DISPLAY grid (_bgWindowIndices), before upload rounding
    i0, i1 = int(d["bg_idx"][0]), int(d["bg_idx"][1])
else:
    lo, hi = sorted([float(ui["bgStart"]), float(ui["bgEnd"])])
    idx = [i for i, b in enumerate(x) if lo <= b <= hi]
    i0, i1 = idx[0], idx[-1] + 1
res = fitting.run_fit(x, y, specs, background_method=ui["bgType"], bg_start_idx=i0, bg_end_idx=i1,
                      endpoint_avg=int(ui.get("endpointAvg") or 1), fit_kws={"method": "least_squares"},
                      n_perturb=int(d.get("n_perturb") or 0))   # the page sends 3; the W1 test sends none
print(json.dumps({"success": bool(res["success"]), "chi2r": res["statistics"]["reduced_chi_square"],
                  "peaks": [{k: v["value"] for k, v in ip["params"].items()} for ip in res["individual_peaks"]]}))
