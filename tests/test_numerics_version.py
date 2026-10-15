"""NUMERICS_VERSION is bumped by a change to the fitting math, and only by one (owner 2026-10-15).

It matters because a seal recorded under OTHER numerics whose recomputation differs reads "unconfirmed",
where under the same numerics it reads "mismatch" (fitting.verify_fit); a git commit alone never makes a
seal unconfirmed. scripts/numerics_digest.py defines "the fitting math"; tests/fixtures/numerics_manifest.json
is the history of (version, digest) entries.
"""
import json
import os
import subprocess
import sys

import pytest

import fitting

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import numerics_digest as nd  # noqa: E402

FIT = open(os.path.join(nd.ROOT, "fitting.py")).read()
APP = open(os.path.join(nd.ROOT, "app.py")).read()
BASE = nd.math_digest(FIT, APP)


def test_the_version_names_todays_fitting_math():
    h = nd.history()
    assert h[-1]["numerics"] == fitting.NUMERICS_VERSION, (
        "NUMERICS_VERSION changed without a manifest entry: bump it ONLY for a change to the fitting math, then run "
        "`python scripts/numerics_digest.py --append`")
    assert h[-1]["math_sha256"] == BASE, (
        "the fitting math changed without a NUMERICS_VERSION bump: bump it in fitting.py and run "
        "`python scripts/numerics_digest.py --append`; for a refactor that moves no number, record it with "
        "`--equivalent \"<reason and evidence>\"`")


def test_the_history_moves_the_version_only_with_the_math():
    h = nd.history()
    for a, b in zip(h, h[1:]):
        assert a["math_sha256"] != b["math_sha256"], ("an entry without a math change", a, b)
        if b["numerics"] == a["numerics"]:
            assert isinstance(b.get("equivalence"), str) and b["equivalence"].strip(), ("same version, new code: needs a reason", b)
        else:
            assert "equivalence" not in b, ("a bump is not an equivalence", b)
    assert "equivalence" not in h[0]
    versions = [e["numerics"] for e in h]
    assert all(versions.index(v) == i or versions[i - 1] == v for i, v in enumerate(versions)), "a version returns after another"


def test_the_history_is_append_only_against_main():
    try:
        out = subprocess.run(["git", "show", "main:tests/fixtures/numerics_manifest.json"], cwd=nd.ROOT,
                             capture_output=True, text=True, timeout=20)
    except Exception:
        pytest.skip("git unavailable")
    if out.returncode != 0:
        pytest.skip("main has no numerics manifest yet")
    old = json.loads(out.stdout)["history"]
    assert nd.history()[:len(old)] == old, "an entry already on main was changed or removed"


@pytest.mark.parametrize("old,new,where", [
    ("def _gaussian(", "# a comment\ndef _gaussian(", "fitting"),
    ('    """The reported statistics, formed from the returned arrays',
     '    """THE reported statistics, formed from the returned arrays', "fitting"),               # an INCLUDED docstring
    ('log.debug("refinement outside the search box raised", exc_info=True)',
     'log.debug("the refinement raised", exc_info=True)', "fitting"),                            # a log message
    ('raise ValueError(f"Circular peak constraint detected: {pretty}")',
     'raise ValueError(f"A circular constraint: {pretty}")', "fitting"),                         # an error's wording
    ("weights = 1.0 / np.sqrt(np.maximum(y, 1.0))", "weights = 1.0 / np.sqrt(np.maximum(y, 2.0))", "fitting"),   # the verifier
    ('"""Convert a JSON value to a bounded integer index."""', '"""A bounded index."""', "app"),
])
def test_text_comments_and_the_verifier_are_not_fitting_math(old, new, where):
    src = FIT if where == "fitting" else APP
    assert src.count(old) == 1, old
    f, a = (src.replace(old, new), APP) if where == "fitting" else (FIT, src.replace(old, new))
    assert nd.math_digest(f, a) == BASE, old


@pytest.mark.parametrize("old,new,where", [
    ("_LN2 = np.log(2.0)", "_LN2 = np.log(2.00001)", "fitting"),                                 # a lineshape constant
    ("    chi2_raw = ((r * weights) ** 2).sum()", "    chi2_raw = ((r * weights) ** 2).sum() * 1.0000001", "fitting"),  # the statistics
    ("            v = max(0, hi + v)  # support negative indexing like Python", "            v = max(0, hi + v + 1)", "app"),  # _parse_int
])
def test_arithmetic_is_fitting_math(old, new, where):
    src = FIT if where == "fitting" else APP
    assert src.count(old) == 1, old
    f, a = (src.replace(old, new), APP) if where == "fitting" else (FIT, src.replace(old, new))
    assert nd.math_digest(f, a) != BASE, old
