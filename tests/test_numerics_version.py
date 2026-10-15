"""NUMERICS_VERSION is bumped by a change to the fitting math, and only by one (owner 2026-10-15).

It matters because a seal recorded under OTHER numerics whose recomputation differs reads "unconfirmed"
(the numerics changed), where under the same numerics it reads "mismatch" (fitting.verify_fit); a git
commit alone never makes a seal unconfirmed. scripts/numerics_digest.py defines "the fitting math" and
tests/fixtures/numerics_manifest.json is the history of (version, digest) pairs.
"""
import ast
import os
import sys

import fitting

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import numerics_digest as nd  # noqa: E402


def test_the_version_names_todays_fitting_math():
    h = nd.history()
    digest = nd.math_digest()
    assert h[-1]["numerics"] == fitting.NUMERICS_VERSION, (
        "NUMERICS_VERSION changed without a manifest entry: bump it ONLY for a change to the fitting math, then run "
        "`python scripts/numerics_digest.py --append`")
    assert h[-1]["math_sha256"] == digest, (
        "the fitting math changed without a NUMERICS_VERSION bump: bump it in fitting.py, then run "
        "`python scripts/numerics_digest.py --append` (or, if no fitted number can move, the change belongs in the "
        "verifier / recording code that scripts/numerics_digest.py excludes)")


def test_every_bump_in_the_history_came_with_a_math_change():
    h = nd.history()
    assert len({e["numerics"] for e in h}) == len(h), "a version appears twice"
    for a, b in zip(h, h[1:]):
        assert a["math_sha256"] != b["math_sha256"], (a, b)


def _digest_of(src_fitting):
    tree = nd._strip_docstrings(ast.parse(src_fitting))
    parts = [ast.dump(n) for n in tree.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))
             and not (nd._names(n) & nd.EXCLUDED)]
    return "\n".join(parts)


def test_the_digest_reads_code_not_comments_and_not_the_verifier():
    src = open(os.path.join(nd.ROOT, "fitting.py")).read()
    base = _digest_of(src)
    # a comment, a docstring and the verifier: not fitting math
    assert _digest_of(src.replace("def _gaussian(", "# a comment\ndef _gaussian(", 1)) == base
    assert _digest_of(src.replace('"""Is the recorded response', '"""IS the recorded response', 1)) == base
    assert _digest_of(src.replace('"the recorded result is not an object"', '"not an object"', 1)) == base
    assert _digest_of(src.replace("NUMERICS_VERSION = ", "NUMERICS_VERSION = 'x' or ", 1)) == base
    # a lineshape's arithmetic, the background, the statistics: fitting math
    for old, new in (("_LN2 = np.log(2.0)", "_LN2 = np.log(2.00001)"),
                     ("def _fit_statistics(y_sub, fitted_sub, weights, n_varys):",
                      "def _fit_statistics(y_sub, fitted_sub, weights, n_varys):\n    n_varys = n_varys")):
        assert old in src, old
        assert _digest_of(src.replace(old, new, 1)) != base, old
