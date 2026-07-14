"""Real-browser test for a raw-markup leak in the Find Peaks "Other
models compared" table's status tooltip (2026-07-14 bug report: "the
'Best fit' tooltip shows a literal '<b></b>' tag as text").

ROOT CAUSE: the winning candidate's status cell is built as
``'<b>' + _fpEsc(S.winner) + '</b>'`` (a small HTML fragment, meant for
``innerHTML`` display — this renders correctly as BOLD "Best fit" in the
cell itself). A prior fix (this same session, closing a DIFFERENT bug —
a raw Python ``PlausibilityFlags(...)`` repr leaking into this same
cell's tooltip) built the tooltip as
``_fpEsc(status + ' — see Technical details...')`` — i.e. it ran
``_fpEsc()`` a SECOND time over a string that, for the winning row,
ALREADY contained raw ``<b>``/``</b>`` characters. Escaping those turns
them into ``&lt;b&gt;``/``&lt;/b&gt;`` in the HTML SOURCE, which the
browser decodes back to the literal characters ``<b>``/``</b>`` when
parsing the ``title`` ATTRIBUTE VALUE — and since attribute values are
never re-parsed as markup, those literal characters show up as VISIBLE
TEXT in the tooltip instead of being interpreted as bold formatting.

This is the general case of "never escape a string that already
contains deliberately-embedded markup" — the fix separates a PLAIN-TEXT
status string (used for the tooltip, escaped exactly once) from an
HTML-rendering version (used for the cell's ``innerHTML``, with the
``<b>`` wrapper applied only at the very end).

The scenario that actually triggers the leak requires the WINNING
candidate to ALSO carry a truthy ``filter_reason``. A Codex recheck
(2026-07-14) found the first version of this test used an unrealistic
shape for that: it named the winner ``"A0_graphite_only+bfix"`` (a
``decisive_override``-style bound-fixed refit) while giving it a
``filter_reason`` — but ``autofit/engine.py``'s ``_apply_decisive_
override`` renames that refit's report to ``<original>+bfix`` and adds
it directly to ``survivors`` without ever adding it to
``filtered_out``, so ``build_analysis_record()``'s
``filtered_reason.get(name)`` lookup (keyed by exact model name) always
returns ``None`` for a real ``+bfix`` winner — that combination cannot
happen on the real backend.

The REAL trigger is ``rank_and_filter()``'s ``no_clean_survivor``
conditional tier (``autofit/engine.py``): when no candidate passes
plausibility cleanly, the same ``ModelReport`` objects that were just
appended to ``filtered_out`` (tagged with their plausibility violation)
are ALSO promoted wholesale into ``survivors`` if they're otherwise
stable — same object, same ``model.name``, no suffix. So the winner's
own name is simultaneously a key in ``filtered_reason`` (truthy
``filter_reason``) and in ``survivor_rank`` (``survived: True``,
``d.winner`` set to that same name) — the exact combination that leaks.
This file reproduces THAT shape.
"""
import glob
import os
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_chromium():
    base = os.path.expanduser("~/Library/Caches/ms-playwright")
    patterns = [
        base + "/chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
        base + "/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
        base + "/chromium-*/chrome-linux/chrome",
        base + "/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell",
    ]
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="module")
def server():
    gunicorn = os.path.join(os.path.dirname(sys.executable), "gunicorn")
    if not os.path.exists(gunicorn):
        pytest.skip("gunicorn not found next to the test interpreter")
    port = _free_port()
    proc = subprocess.Popen(
        [gunicorn, "app:app", "-w", "1", "-b", f"127.0.0.1:{port}", "--timeout", "60"],
        cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        ok = False
        for _ in range(50):
            if proc.poll() is not None:
                pytest.skip("gunicorn exited during startup")
            try:
                with urllib.request.urlopen(base + "/api/health", timeout=1) as r:
                    if r.status == 200:
                        ok = True
                        break
            except Exception:
                time.sleep(0.2)
        if not ok:
            pytest.skip("gunicorn did not become healthy")
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


@pytest.fixture(scope="module")
def browser():
    exe = _find_chromium()
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True)
        except Exception:
            if not exe:
                pytest.skip("no usable Chromium build found")
            b = p.chromium.launch(headless=True, executable_path=exe)
        yield b
        b.close()


def _new_page(browser, server):
    pg = browser.new_page(viewport={"width": 900, "height": 900})
    pg.goto(server + "/", wait_until="load")
    pg.evaluate("""() => {
        const raw = [], inten = [];
        for (let i = 0; i <= 200; i++) { raw.push(275 + i * 0.1); inten.push(1000); }
        tabManager.createTab('T', raw, inten);
    }""")
    pg.evaluate("() => openFindPeaksModal()")
    pg.wait_for_selector("#find-peaks-overlay.open", timeout=5000)
    return pg


# A synthetic payload matching the REAL backend shape that triggers the
# bug: rank_and_filter()'s "no_clean_survivor" conditional tier promotes
# a plausibility-filtered ModelReport straight into result.survivors
# without renaming it -- so its plain name (no "+bfix" suffix) is
# simultaneously a key in filtered_reason (truthy filter_reason) AND in
# survivor_rank (survived: True, and diagnostics.winner set to that same
# name) -- per autofit/engine.py's rank_and_filter and
# autofit/methods/ic_model_comparison.py's build_analysis_record.
_NO_CLEAN_SURVIVOR_WINNER_PAYLOAD = {
    "success": True, "structural_only": [],
    "peaks": [{"role": "main_graphitic", "region": "C 1s", "shape": "ds_g",
               "center": 284.6, "fwhm": 0.8, "amplitude": 5000}],
    "diagnostics": {
        "winner": "A0_graphite_only", "conditional": True,
        "conditional_reason": "no_clean_survivor",
        "winner_boundary_hits": ["s_main_graphitic_fwhm@max"],
        "winner_unphysical_widths": [],
        "winner_boundary_fixed_params": [], "filtered_dominant_alternative": None,
        "analysis_truncated": False,
    },
    "analysis": {"candidates": [
        {"name": "A0_graphite_only", "reduced_chi_sq": 1.1, "bic_star": 90.0,
         "survived": True,
         "filter_reason": ("plausibility: PlausibilityFlags(boundary_hits="
                           "['s_main_graphitic_fwhm@max'], unphysical_widths=[], "
                           "orphan_peaks=False)")},
    ]},
    "confidence": {}, "message": "placeholder",
}


def test_winner_tooltip_never_contains_literal_markup(browser, server):
    pg = _new_page(browser, server)
    try:
        pg.evaluate("(body) => _fpRenderResults(body)", _NO_CLEAN_SURVIVOR_WINNER_PAYLOAD)
        pg.wait_for_timeout(150)
        tooltip = pg.eval_on_selector(
            "#fp-cands tr:nth-child(2) td:nth-child(4)", "el => el.title")
        assert "<b>" not in tooltip and "</b>" not in tooltip, (
            f"tooltip leaks raw markup as literal text: {tooltip!r}")
        assert "&lt;" not in tooltip, (
            f"tooltip shows an escaped-entity artifact: {tooltip!r}")
        assert tooltip.startswith("Best fit"), tooltip
    finally:
        pg.close()


def test_winner_cell_still_renders_bold_via_innerhtml(browser, server):
    """The fix must not regress the (correct) bold rendering — only the
    TOOLTIP's construction was wrong, not the cell's own innerHTML."""
    pg = _new_page(browser, server)
    try:
        pg.evaluate("(body) => _fpRenderResults(body)", _NO_CLEAN_SURVIVOR_WINNER_PAYLOAD)
        pg.wait_for_timeout(150)
        cell_html = pg.eval_on_selector(
            "#fp-cands tr:nth-child(2) td:nth-child(4)", "el => el.innerHTML")
        cell_text = pg.eval_on_selector(
            "#fp-cands tr:nth-child(2) td:nth-child(4)", "el => el.textContent")
        assert cell_html == "<b>Best fit</b>", cell_html
        assert cell_text == "Best fit", cell_text
        is_bold = pg.eval_on_selector(
            "#fp-cands tr:nth-child(2) td:nth-child(4) b", "el => !!el")
        assert is_bold, "expected a real <b> element to exist in the cell"
    finally:
        pg.close()


def test_ordinary_winner_without_a_filter_reason_has_an_empty_tooltip(browser, server):
    """The common case (no decisive_override, winner has no
    filter_reason at all) must still show an empty tooltip -- confirms
    the fix didn't accidentally make EVERY winner row show a tooltip
    when it shouldn't."""
    payload = {
        "success": True, "structural_only": [],
        "peaks": [{"role": "main_graphitic", "region": "C 1s", "shape": "ds_g",
                   "center": 284.6, "fwhm": 0.8, "amplitude": 5000}],
        "diagnostics": {
            "winner": "A0_graphite_only", "conditional": False,
            "winner_boundary_hits": [], "winner_unphysical_widths": [],
            "winner_boundary_fixed_params": [], "filtered_dominant_alternative": None,
            "analysis_truncated": False,
        },
        "analysis": {"candidates": [
            {"name": "A0_graphite_only", "reduced_chi_sq": 1.1, "bic_star": 90.0,
             "survived": True},
        ]},
        "confidence": {}, "message": "placeholder",
    }
    pg = _new_page(browser, server)
    try:
        pg.evaluate("(body) => _fpRenderResults(body)", payload)
        pg.wait_for_timeout(150)
        tooltip = pg.eval_on_selector(
            "#fp-cands tr:nth-child(2) td:nth-child(4)", "el => el.title")
        assert tooltip == "", repr(tooltip)
    finally:
        pg.close()


def test_rejected_candidate_tooltip_is_plain_text_not_a_raw_python_repr(browser, server):
    """Regression guard for the ORIGINAL bug this code was meant to fix
    (round 3's raw-filter_reason-leak): a rejected candidate's tooltip
    must show the translated plain-English status, not the raw Python
    PlausibilityFlags(...) repr."""
    payload = {
        "success": True, "structural_only": [],
        "peaks": [{"role": "main_graphitic", "region": "C 1s", "shape": "ds_g",
                   "center": 284.6, "fwhm": 0.8, "amplitude": 5000}],
        "diagnostics": {
            "winner": "A0_graphite_only", "conditional": False,
            "winner_boundary_hits": [], "winner_unphysical_widths": [],
            "winner_boundary_fixed_params": [], "filtered_dominant_alternative": None,
            "analysis_truncated": False,
        },
        "analysis": {"candidates": [
            {"name": "A0_graphite_only", "reduced_chi_sq": 1.1, "bic_star": 90.0,
             "survived": True},
            {"name": "M2_graphite_aliphatic", "reduced_chi_sq": 1.0, "bic_star": 95.0,
             "survived": False,
             "filter_reason": ("plausibility: PlausibilityFlags(boundary_hits=[], "
                               "unphysical_widths=[], orphan_peaks=True)")},
        ]},
        "confidence": {}, "message": "placeholder",
    }
    pg = _new_page(browser, server)
    try:
        pg.evaluate("(body) => _fpRenderResults(body)", payload)
        pg.wait_for_timeout(150)
        tooltip = pg.eval_on_selector(
            "#fp-cands tr:nth-child(3) td:nth-child(4)", "el => el.title")
        assert "PlausibilityFlags" not in tooltip, tooltip
        assert "Rejected" in tooltip, tooltip
    finally:
        pg.close()
