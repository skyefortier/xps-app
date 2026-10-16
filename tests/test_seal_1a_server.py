"""Seal 1a′ (sealed fit record v6, option (b); plan docs/superpowers/plans/2026-10-13-seal-1a-server.md):
the server reports the model sum `fitted_sub`, forms its statistics from the arrays it returns
(V6.6 — one association, so a verifier can recompute them exactly), reports `rmse`, and
identifies its environment (`env_sha256`, untracked files in `git_dirty`) and each rendered
page (`page_sha256`, `reference_sha256`)."""
import hashlib
import json
import os
import re
import subprocess

import numpy as np
import pytest

import fitting
from app import create_app
import test_scattered_starts as SS


SHAPES = {
    "gaussian": {},
    "lorentzian": {},
    "pseudo_voigt_gl": {"gl_ratio": 0.3},
    "asymmetric_gl": {"gl_ratio": 0.3, "asymmetry": 0.2},
    "doniach_sunjic": {"alpha": 0.1, "gamma_asym": 0.0},
    "ds_g": {"alpha": 0.1, "beta": 0.3, "m_gauss": 0.4},
    "la_casaxps": {"alpha": 1.2, "beta": 1.0, "m": 6.0},
}


def _specs(shape):
    x, y, specs = SS._well_posed()
    return x, y, [{**s, "shape": shape, **SHAPES[shape]} for s in specs]


def _recompute_statistics(r):
    """V6.6's contract, written out independently of fitting.py."""
    counts = np.asarray(r["counts"], float)
    bg = np.asarray(r["background_y"], float)
    fsub = np.asarray(r["fitted_sub"], float)
    y_sub = counts - bg
    w = 1.0 / np.sqrt(np.maximum(counts, 1.0))
    n = len(r["energy"])
    nv = sum(1 for ip in r["individual_peaks"] for k, p in ip["params"].items()
             if k != "area" and p["vary"] and p["expr"] is None)
    chi2_raw = ((y_sub - fsub) * w) ** 2
    chi2_raw = chi2_raw.sum()
    red = chi2_raw / max(1, n - nv)
    chi2 = max(chi2_raw, 1e-250 * n)
    n2ll = n * np.log(chi2 / n)
    res = y_sub - fsub
    return {"chi_square": float(chi2), "reduced_chi_square": float(red),
            "aic": float(n2ll + 2 * nv), "bic": float(n2ll + np.log(n) * nv),
            "rmse": float(np.sqrt(np.sum(res * res) / n)),
            "r_factor": float(np.sum(np.abs(res)) / np.sum(np.abs(y_sub))), "n_data": n, "n_free_params": nv}


@pytest.mark.parametrize("method", ["leastsq", "least_squares", "nelder"])
@pytest.mark.parametrize("bg", ["shirley", "linear", "none"])
def test_the_statistics_are_formed_from_the_returned_arrays(method, bg):
    x, y, specs = SS._well_posed()
    r = fitting.run_fit(x, y, specs, background_method=bg, n_perturb=0, fit_kws={"method": method})
    assert r["statistics"] == _recompute_statistics(r)


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_fitted_sub_and_the_two_associations_hold_exactly(shape):
    x, y, specs = _specs(shape)
    r = fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=0, fit_kws={"method": "leastsq"})
    fsub, bg = np.asarray(r["fitted_sub"]), np.asarray(r["background_y"])
    assert np.array_equal(np.asarray(r["fitted_y"]), fsub + bg)
    assert np.array_equal(np.asarray(r["residuals"]), (np.asarray(r["counts"]) - bg) - fsub)
    assert r["statistics"] == _recompute_statistics(r)


def test_linked_and_held_parameters_count_once():
    x, y, specs = SS._well_posed()
    specs[1] = {**specs[1], "constrain_to": 1, "splitting": 4.0, "area_ratio": 0.25}
    specs[0] = {**specs[0], "fix_gl_ratio": True}
    r = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    assert r["statistics"] == _recompute_statistics(r)


@pytest.mark.parametrize("method", ["differential_evolution", "basinhopping"])
def test_the_global_methods_report_the_same_association(method):
    x, y, specs = SS._well_posed()
    specs = specs[:1]
    r = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0,
                        fit_kws={"method": method, "max_nfev": 400})
    assert r["statistics"] == _recompute_statistics(r)


def test_internal_decisions_keep_their_own_statistic(monkeypatch):
    # the REPORTED statistics are formed from the arrays; every decision inside the fit keeps lmfit's:
    # replace the reported ones with nonsense and the required refit's chi2_with does not move
    x, y, specs = SS._well_posed()
    kw = dict(background_method="linear", n_perturb=2, n_starts=2, fit_kws={"method": "leastsq"}, require_component=2)
    a = fitting.run_fit(x, y, specs, **kw)
    monkeypatch.setattr(fitting, "_fit_statistics", lambda *a_, **k_: {"chi_square": -1.0})
    b = fitting.run_fit(x, y, specs, **kw)
    assert b["statistics"] == {"chi_square": -1.0}
    assert a["required"] == b["required"] and a["required"]["ran"] is True
    assert a["starts"] == b["starts"] and a["certificate"] == b["certificate"]
    assert [p["params"] for p in a["individual_peaks"]] == [p["params"] for p in b["individual_peaks"]]


def test_the_statistics_floor_and_null_cases():
    n = 5
    y_sub = np.array([1.0, 2.0, 3.0, 2.0, 1.0])
    s = fitting._fit_statistics(y_sub, y_sub.copy(), np.ones(n), 2)
    # a zero residual: reduced chi-square 0 (formed BEFORE the floor), chi-square floored at 1e-250·n
    assert s["reduced_chi_square"] == 0.0 and s["chi_square"] == 1e-250 * n and s["rmse"] == 0.0
    assert s["aic"] == n * np.log(1e-250) + 4 and s["r_factor"] == 0.0
    z = fitting._fit_statistics(np.zeros(n), np.ones(n), np.ones(n), 1)
    assert z["r_factor"] is None and z["chi_square"] == 5.0 and z["reduced_chi_square"] == 5.0 / 4


# ── provenance ─────────────────────────────────────────────────────────────────────────────────

def test_env_sha256_is_the_digest_of_the_installed_distributions():
    from importlib import metadata
    lines = sorted(f"{d.metadata['Name']}=={d.version}" for d in metadata.distributions())
    assert fitting.SOFTWARE["env_sha256"] == hashlib.sha256("\n".join(lines).encode()).hexdigest()
    manifest = json.load(open(os.path.join(os.path.dirname(__file__), "fixtures", "numerics_manifest.json")))
    assert fitting.SOFTWARE["numerics"] == fitting.NUMERICS_VERSION == manifest["history"][-1]["numerics"]


def test_git_dirty_counts_untracked_files(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "a.txt").write_text("a")
    subprocess.run(["git", "-C", str(tmp_path), "add", "a.txt"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "a"], check=True)
    assert fitting._git_state(str(tmp_path))[1] is False
    (tmp_path / "untracked.txt").write_text("b")
    assert fitting._git_state(str(tmp_path))[1] is True
    commit, dirty = fitting._git_state(str(tmp_path / "nope-not-a-repo-xyz"))
    assert commit is None and dirty is None


def test_each_rendered_page_names_its_template_source_and_reference_data(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        html = c.get("/").get_data(as_text=True)
    m = re.search(r"<meta name=\"xps-page\" content='([^']*)'>", html)
    assert m, "no xps-page meta tag"
    page = json.loads(m.group(1).replace("&#34;", '"'))
    src = open("templates/index.html", encoding="utf-8").read()
    assert page["page_sha256"] == hashlib.sha256(src.encode("utf-8")).hexdigest()
    from xps_reference import load_reference_cached
    legacy = load_reference_cached(app.config["XPS_DATA_DIR"]).get("legacy")
    canon = json.dumps(legacy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    assert page["reference_sha256"] == hashlib.sha256(canon.encode("utf-8")).hexdigest()


def test_the_page_digest_is_of_the_source_jinja_compiled_not_a_later_file(tmp_path):
    # Jinja caches a compiled template per worker: the digest must name what was compiled
    import shutil
    tdir = tmp_path / "tpl"
    tdir.mkdir()
    shutil.copy("templates/index.html", tdir / "index.html")
    app = create_app(upload_folder=str(tmp_path / "up"))
    app.template_folder = str(tdir)
    app.jinja_env.auto_reload = False
    with app.test_client() as c:
        first = c.get("/").get_data(as_text=True)
        (tdir / "index.html").write_text((tdir / "index.html").read_text() + "\n<!-- edited -->\n")
        second = c.get("/").get_data(as_text=True)
    meta = lambda h: re.search(r"<meta name=\"xps-page\" content='([^']*)'>", h).group(1)
    assert "<!-- edited -->" not in second          # still the compiled template …
    assert meta(first) == meta(second)              # … and the digest says so


def test_the_digest_belongs_to_the_compiled_template_not_its_name(tmp_path):
    # Codex round 1: a digest stored by NAME could be overwritten by another request's reload between
    # getting a template and rendering it; each compiled template carries its own source's digest
    import shutil
    tdir = tmp_path / "tpl"
    tdir.mkdir()
    shutil.copy("templates/index.html", tdir / "index.html")
    app = create_app(upload_folder=str(tmp_path / "up"))
    app.template_folder = str(tdir)
    app.jinja_env.auto_reload = True
    old = app.jinja_env.get_template("index.html")
    src = (tdir / "index.html").read_text(encoding="utf-8")
    (tdir / "index.html").write_text(src + "\n<!-- edited -->\n", encoding="utf-8")
    import os
    os.utime(tdir / "index.html", (1e10, 1e10))                 # a later mtime: the cache is out of date
    new = app.jinja_env.get_template("index.html")
    assert new is not old
    assert old.xps_source_sha256 == hashlib.sha256(src.encode("utf-8")).hexdigest()
    assert new.xps_source_sha256 == hashlib.sha256((src + "\n<!-- edited -->\n").encode("utf-8")).hexdigest()
