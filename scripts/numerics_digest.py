"""The digest of the FITTING MATH that NUMERICS_VERSION names (owner 2026-10-15).

NUMERICS_VERSION is bumped by a change to the fitting math and only by one, because a seal made
under other numerics reads "unconfirmed" when its recomputation differs, where under the same
numerics it would read "mismatch" (fitting.verify_fit). This digest is what "the fitting math" means:

- fitting.py, every top-level statement EXCEPT the verifier (RESPONSE_KEYS … _verify_relations), the
  software recording (fit_record, _git_state, _env_sha256, _software_identity, SOFTWARE, RECORD_KEYS,
  NUMERICS_IDENTITY_KEYS), NUMERICS_VERSION itself and the logger;
- app.py's ``_normalise_fit_request`` (how a request's fields are read before run_fit);
- as their abstract syntax (``ast.dump``) with every docstring removed, so comments, docstrings and
  formatting never count, and any change to code does.

tests/fixtures/numerics_manifest.json is the HISTORY [{numerics, math_sha256}, ...] (oldest first, from
2026-10-15); tests/test_numerics_version.py requires its last entry to be today's version and digest and
every entry's digest to differ from the one before — a math change without a bump, or a bump without a
math change, fails.

Usage: python scripts/numerics_digest.py            # prints today's version and digest
       python scripts/numerics_digest.py --append   # after a DELIBERATE bump: appends today's entry
"""
import ast
import hashlib
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MANIFEST = os.path.join(ROOT, "tests", "fixtures", "numerics_manifest.json")

# not fitting math: the verifier, the software recording, the version itself
EXCLUDED = {
    "NUMERICS_VERSION", "NUMERICS_IDENTITY_KEYS", "RECORD_KEYS", "fit_record", "_git_state", "_env_sha256",
    "_software_identity", "SOFTWARE", "log",
    "RESPONSE_KEYS", "_PEAK_KEYS", "_PARAM_KEYS", "NOT_BIT_STABLE_SHAPES", "_Mismatch", "_Unverifiable",
    "_exact_float", "_is_number", "_same", "_as_json", "_non_finite", "_ID_T", "_MOVE_T", "_NOT_RUN_T",
    "_STARTS_T", "_REQUIRED_T", "_CERTIFICATE_T", "_SUPPORT_T", "_STATISTICS_T", "_typed",
    "_non_finite_request", "verify_fit", "_verify", "_verify_relations",
}


def _names(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {node.name}
    if isinstance(node, ast.Assign):
        return {t.id for t in node.targets if isinstance(t, ast.Name)}
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return {node.target.id}
    return set()


def _strip_docstrings(tree):
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and \
                isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            node.body = body[1:] or [ast.Pass()]
    return tree


def math_digest():
    parts = []
    tree = _strip_docstrings(ast.parse(open(os.path.join(ROOT, "fitting.py")).read()))
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant):
            continue                                            # a bare string (the module docstring)
        if _names(node) & EXCLUDED:
            continue
        parts.append(ast.dump(node, include_attributes=False))
    app = _strip_docstrings(ast.parse(open(os.path.join(ROOT, "app.py")).read()))
    norm = [n for n in app.body if isinstance(n, ast.FunctionDef) and n.name == "_normalise_fit_request"]
    assert len(norm) == 1, "app.py: _normalise_fit_request not found"
    parts.append(ast.dump(norm[0], include_attributes=False))
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def numerics_version():
    tree = ast.parse(open(os.path.join(ROOT, "fitting.py")).read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "NUMERICS_VERSION" for t in node.targets):
            return node.value.value
    raise AssertionError("NUMERICS_VERSION not found")


def history():
    with open(MANIFEST) as fh:
        return json.load(fh)["history"]


if __name__ == "__main__":
    cur = {"numerics": numerics_version(), "math_sha256": math_digest()}
    if "--append" in sys.argv:
        h = history() if os.path.exists(MANIFEST) else []
        if h and h[-1]["numerics"] == cur["numerics"]:
            sys.exit("NUMERICS_VERSION was not bumped: bump it in fitting.py first")
        if h and h[-1]["math_sha256"] == cur["math_sha256"]:
            sys.exit("the fitting math has not changed: NUMERICS_VERSION must not be bumped")
        with open(MANIFEST, "w") as fh:
            json.dump({"history": h + [cur]}, fh, indent=2)
            fh.write("\n")
    print(json.dumps(cur))
