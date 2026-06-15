"""
Stage 9 cutover tests (Codex Checkpoint-B hardening). These prove the
POST-DELETION state is safe, using the immutable fixture as the oracle that
survives constant removal (the constants no longer exist to compare against).

  - static guard: NO production-code reference to the removed constants and
    no embedded legacy dataset (comments + tests/fixtures excluded)
  - semantic parity BY ID: the post-cutover accessor (rendered page) serves
    values deep-equal to the immutable fixture, element-by-element / key-by-key
  - chem output shape: exactly {state, be, ref} (no tier leak)
  - computed allowlist diff: the value-diff vs the fixture is EMPTY (verbatim);
    any unlisted delta fails
  - load failure: when the server injects null legacy data, the page sets
    LEGACY_REFERENCE_OK=false and the accessor returns {} + flags unavailable
    (loud), instead of silently serving empty reference data
"""
import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / "templates/index.html"
FIXTURE = REPO / "tests/fixtures/xps_legacy_snapshot.json"


def _strip_js_comments(js):
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    js = re.sub(r"(^|[^:])//[^\n]*", lambda m: m.group(1), js)  # keep http:// etc.
    return js


def _render(data_folder):
    from app import create_app
    app = create_app(upload_folder="/tmp/xps_cut_up", data_folder=str(data_folder))
    app.config["TESTING"] = True
    return app.test_client().get("/").get_data(as_text=True)


# ── static guard (production code only) ──────────────────────────────────────

def test_no_production_reference_to_removed_constants():
    html = TEMPLATE.read_text()
    scripts = "\n".join(re.findall(r"<script>(.*?)</script>", html, flags=re.S))
    code = _strip_js_comments(scripts)
    # No definition or use of the removed identifiers in executable code.
    for ident in ("XPS_ELEMENTS", "CHEMICAL_STATES", "_XPS_REMOVED"):
        assert ident not in code, f"production code still references {ident}"


def test_no_embedded_legacy_dataset_fallback():
    html = TEMPLATE.read_text()
    # The element table literal (e.g. 'Li': { lines: {'1s': 55} }) must be gone.
    assert "{ lines: {'1s'" not in html and "{ lines: {\"1s\"" not in html, \
        "embedded legacy element dataset still present in template"


# ── post-cutover accessor parity / shape / value-diff (real rendered page) ───

def test_cutover_accessor_parity_and_shape():
    html = _render(REPO / "data/xps")
    rendered = Path("/tmp/xps_cutover_rendered.html")
    rendered.write_text(html)
    proc = subprocess.run(
        ["node", ".stage9/cutover_check.mjs", str(rendered), str(FIXTURE)],
        cwd=REPO, capture_output=True, text=True)
    assert proc.returncode == 0, f"cutover check failed: {proc.stdout}\n{proc.stderr}"
    result = json.loads(proc.stdout.strip().splitlines()[-1])
    assert result["pass"] and result["constantsAbsent"] and result["value_diff_count"] == 0, result


# ── fixture immutability (mechanical) ────────────────────────────────────────

def test_fixture_matches_legacy_json():
    import hashlib
    fx = json.loads(FIXTURE.read_text())
    payload = json.dumps({"XPS_ELEMENTS": fx["XPS_ELEMENTS"], "CHEMICAL_STATES": fx["CHEMICAL_STATES"]},
                         sort_keys=True, ensure_ascii=True)
    assert hashlib.sha256(payload.encode()).hexdigest() == fx["sha256"], "fixture self-checksum drift"
    ls = json.loads((REPO / "data/xps/legacy/survey-lines.json").read_text())["elements"]
    rebuilt = {e["symbol"]: {"lines": {l["orbital"]: l["be_ev"] for l in e["lines"]}} for e in ls}
    assert rebuilt == fx["XPS_ELEMENTS"], "fixture != legacy JSON (parity oracle drift)"


# ── load-failure: null injection -> loud, not silent ─────────────────────────

def test_load_failure_renders_loud_not_silent(tmp_path):
    # A data dir missing the legacy files -> _load_legacy raises -> index() injects null.
    broken = tmp_path / "xps"
    broken.mkdir()
    import shutil
    for f in ("schema.json", "sources.json", "elements-main.json",
              "elements-lanthanides.json", "elements-actinides.json", "auger-lines.json"):
        shutil.copy(REPO / "data/xps" / f, broken / f)
    # legacy/ dir intentionally absent -> payload['legacy'] is None for this dir...
    # but index() injects payload.get('legacy'); with no legacy dir that's None.
    html = _render(broken)
    assert "const LEGACY_REFERENCE = null;" in html, "expected null legacy injection on failure"
    lf = tmp_path / "lf.html"
    lf.write_text(html)
    chk = subprocess.run(["node", ".stage9/loadfail_check.mjs", str(lf)],
                         cwd=REPO, capture_output=True, text=True)
    assert chk.returncode == 0, chk.stderr
    res = json.loads(chk.stdout.strip().splitlines()[-1])
    # Loud, not silent: OK flag false, accessor returns empty, unavailable flagged.
    assert res["ok"] is False and res["empty"] and res["notified"], res
