"""The digest of the FITTING MATH that NUMERICS_VERSION names (owner 2026-10-15).

NUMERICS_VERSION is bumped by a change to the fitting math and only by one: a seal made under other
numerics whose recomputation differs reads "unconfirmed", where under the same numerics it reads
"mismatch" (fitting.verify_fit). This digest is what "the fitting math" means:

- fitting.py, every top-level statement EXCEPT the verifier (RESPONSE_KEYS … _verify_relations,
  software_failure, numerics_difference), the software recording (fit_record, _git_state, _env_sha256,
  _software_identity, SOFTWARE, RECORD_KEYS, the identity keys), NUMERICS_VERSION itself and the logger;
- app.py's ``_normalise_fit_request`` (how a request's fields are read before run_fit) and every app.py
  function it calls, transitively (``_parse_int`` …);
- as abstract syntax (``ast.dump``) with every docstring removed, and the TEXT of messages removed: the
  string arguments of ``raise``, of logging calls (``log`` / ``logger`` / ``logging`` .debug … .critical,
  .exception, .log), of ``warnings.warn`` and of app.py's ``_err`` refusals (wording moves no number).
  Text that LANDS IN THE RECORD still counts — a background verdict's reason is part of O and the verifier
  compares it, so changing it changes what a recomputation gives. Comments and formatting never count; any
  other change to the code does, a refactor included (record a refactor that moves no number as an
  equivalence).

tests/fixtures/numerics_manifest.json is the HISTORY of entries, oldest first:
  {"numerics", "math_sha256"}                       — a version and the math it names;
  {"numerics", "math_sha256", "equivalence": why}   — the SAME version re-baselined to new code that moves
                                                      no number (a refactor), with the reason and evidence.
tests/test_numerics_version.py requires the last entry to be today's version and digest, every bump to
come with a new digest, every same-version entry to carry an equivalence reason, and (where `main` has a
manifest) `main`'s history to be a prefix of this one — so a version moves only with the math.

Usage: python scripts/numerics_digest.py                      # prints today's version and digest
       python scripts/numerics_digest.py --append             # after a DELIBERATE bump
       python scripts/numerics_digest.py --equivalent "why"   # a refactor that moves no number
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
    "NUMERICS_VERSION", "NUMERICS_IDENTITY_KEYS", "_NUMERICS_KEYS_SINCE_2026_10_15", "RECORD_KEYS", "fit_record",
    "_git_state", "_env_sha256", "_software_identity", "SOFTWARE", "log", "software_failure", "numerics_difference",
    "response_form_failure",
    "RESPONSE_KEYS", "_PEAK_KEYS", "_PARAM_KEYS", "NOT_BIT_STABLE_SHAPES", "_Mismatch", "_Unverifiable",
    "_exact_float", "_is_number", "_same", "_as_json", "_non_finite", "_ID_T", "_MOVE_T", "_NOT_RUN_T",
    "_STARTS_T", "_REQUIRED_T", "_CERTIFICATE_T", "_SUPPORT_T", "_STATISTICS_T", "_typed", "_BG_EFFECT_T", "_BG_VERDICT_T", "_bg_effect_form_failure",
    "_non_finite_request", "verify_fit", "_verify", "_verify_relations",
}
APP_ROOT = "_normalise_fit_request"
_LOG_OBJECTS = {"log", "logger", "logging"}
_LOG_METHODS = {"debug", "info", "warning", "warn", "error", "exception", "critical", "log"}


def _names(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {node.name}
    if isinstance(node, ast.Assign):
        return {t.id for t in node.targets if isinstance(t, ast.Name)}
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return {node.target.id}
    return set()


class _Normalise(ast.NodeTransformer):
    """Docstrings out; message text (raise / logging / warnings arguments) replaced by a placeholder."""

    def _strip_doc(self, node):
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and \
                isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            node.body = body[1:] or [ast.Pass()]
        return node

    def generic_visit(self, node):
        node = super().generic_visit(node)
        return self._strip_doc(node) if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else node

    @staticmethod
    def _blank_text(node):
        for sub in ast.walk(node):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                sub.value = "<text>"
            elif isinstance(sub, ast.JoinedStr):
                sub.values = [ast.Constant(value="<text>")]
        return node

    def visit_Raise(self, node):
        self.generic_visit(node)
        return self._blank_text(node)

    def visit_Call(self, node):
        self.generic_visit(node)
        f = node.func
        message = (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and
                   ((f.value.id in _LOG_OBJECTS and f.attr in _LOG_METHODS) or (f.value.id == "warnings" and f.attr == "warn"))) \
            or (isinstance(f, ast.Name) and f.id == "_err")
        if message:
            for a in node.args + [k.value for k in node.keywords]:
                self._blank_text(a)
        return node


def _parse(src):
    return _Normalise().visit(ast.parse(src))


def _app_closure(app_tree):
    defs = {n.name: n for n in app_tree.body if isinstance(n, ast.FunctionDef)}
    assert APP_ROOT in defs, f"app.py: {APP_ROOT} not found"
    seen, todo = [], [APP_ROOT]
    while todo:
        name = todo.pop(0)
        if name in seen:
            continue
        seen.append(name)
        for sub in ast.walk(defs[name]):
            if isinstance(sub, ast.Name) and sub.id in defs and sub.id not in seen:
                todo.append(sub.id)
    return [defs[n] for n in sorted(seen)]


def math_digest(fitting_src=None, app_src=None):
    fitting_src = fitting_src if fitting_src is not None else open(os.path.join(ROOT, "fitting.py")).read()
    app_src = app_src if app_src is not None else open(os.path.join(ROOT, "app.py")).read()
    parts = []
    for node in _parse(fitting_src).body:
        if isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant):
            continue
        if _names(node) & EXCLUDED:
            continue
        parts.append(ast.dump(node, include_attributes=False))
    for fn in _app_closure(_parse(app_src)):
        parts.append(ast.dump(fn, include_attributes=False))
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def numerics_version(fitting_src=None):
    fitting_src = fitting_src if fitting_src is not None else open(os.path.join(ROOT, "fitting.py")).read()
    for node in ast.parse(fitting_src).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "NUMERICS_VERSION" for t in node.targets):
            return node.value.value
    raise AssertionError("NUMERICS_VERSION not found")


def history():
    with open(MANIFEST) as fh:
        return json.load(fh)["history"]


def _write(h):
    with open(MANIFEST, "w") as fh:
        json.dump({"history": h}, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    cur = {"numerics": numerics_version(), "math_sha256": math_digest()}
    h = history() if os.path.exists(MANIFEST) else []
    if "--append" in sys.argv:
        if h and h[-1]["numerics"] == cur["numerics"]:
            sys.exit("NUMERICS_VERSION was not bumped: bump it in fitting.py first (or record --equivalent)")
        if h and h[-1]["math_sha256"] == cur["math_sha256"]:
            sys.exit("the fitting math has not changed: NUMERICS_VERSION must not be bumped")
        _write(h + [cur])
    elif "--equivalent" in sys.argv:
        why = sys.argv[sys.argv.index("--equivalent") + 1] if len(sys.argv) > sys.argv.index("--equivalent") + 1 else ""
        if not why.strip():
            sys.exit("give the reason and the evidence that no number moves")
        if not h or h[-1]["numerics"] != cur["numerics"] or h[-1]["math_sha256"] == cur["math_sha256"]:
            sys.exit("an equivalence re-baselines CHANGED code under the SAME version")
        _write(h + [{**cur, "equivalence": why}])
    print(json.dumps(cur))
