"""scripts/scan_batch_fit_signature.py — finds saved files whose "fit" came
from the local optimiser that never descended (unit A0, 2026-09-15).

Signature of a local-optimiser result in a saved tab / spectrum:
  * the stored statistics are UNWEIGHTED: chiReduced ~= rmse^2 * n/dof
    (a backend fit stores a Poisson-weighted chi-square, so
    chiReduced / rmse^2 ~= 1/<counts>, orders of magnitude smaller);
  * corroborated by chiReduced far above any plausible weighted value, and
    by another tab in the same project carrying the identical centre/width
    set (a Batch Fit clone that was never fitted).
"""
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "scan_batch_fit_signature.py"
sys.path.insert(0, str(ROOT / "scripts"))


def _tab(name, peaks, chi_reduced, rmse, n=200, k=3):
    return {"id": name, "name": name, "rawBE": [0.0] * n, "rawIntensity": [100.0] * n, "peaks": peaks,
            "fitResult": {"chi": chi_reduced * (n - k), "chiReduced": chi_reduced, "rmse": rmse}, "ui": {}}


def _peaks(centers, fwhm=1.2, amp=1000.0):
    return [{"id": i + 1, "name": f"p{i}", "shape": "GL", "center": c, "fwhm": fwhm, "amplitude": amp}
            for i, c in enumerate(centers)]


def _backend_tab(name, centers):
    # weighted chi-square ~2 on counts ~1e4: rmse ~ sqrt(2*1e4) ~ 141 -> ratio ~ 1e-4
    return _tab(name, _peaks(centers), chi_reduced=2.1, rmse=141.0)


def _local_tab(name, centers, n=200, k=3):
    # unweighted: chiReduced = chi/dof, rmse = sqrt(chi/n)  ->  chiReduced = rmse^2 * n/dof
    chi = 3.0e7
    return _tab(name, _peaks(centers), chi_reduced=chi / (n - k), rmse=(chi / n) ** 0.5, n=n, k=k)


def _write_proj_json(tmp_path, tabs, name="p.proj.json"):
    f = tmp_path / name
    f.write_text(json.dumps({"version": 3, "tabs": tabs}))
    return f


def test_backend_fitted_tabs_are_clean(tmp_path):
    from scan_batch_fit_signature import scan_path
    f = _write_proj_json(tmp_path, [_backend_tab("A", [284.8, 286.2]), _backend_tab("B", [284.9, 286.1])])
    hits = scan_path(f)
    assert hits == []


def test_unweighted_statistics_flag_a_local_optimiser_result(tmp_path):
    from scan_batch_fit_signature import scan_path
    f = _write_proj_json(tmp_path, [_backend_tab("A", [284.8, 286.2]), _local_tab("B", [284.9, 286.1])])
    hits = scan_path(f)
    assert [h["tab"] for h in hits] == ["B"]
    assert hits[0]["level"] == "suspected" and "unweighted" in " ".join(hits[0]["reasons"])


def test_batch_clone_is_reported_with_its_source(tmp_path):
    from scan_batch_fit_signature import scan_path
    src = _backend_tab("A", [284.8, 286.2])
    clone = _local_tab("B", [284.8, 286.2])           # identical centre/width set
    f = _write_proj_json(tmp_path, [src, clone])
    hits = scan_path(f)
    assert [h["tab"] for h in hits] == ["B"]
    assert any("identical" in r and "A" in r for r in hits[0]["reasons"])


def test_tab_without_fit_result_is_ignored(tmp_path):
    from scan_batch_fit_signature import scan_path
    t = _backend_tab("A", [284.8]); t["fitResult"] = None
    assert scan_path(_write_proj_json(tmp_path, [t])) == []


def test_spec_json_single_spectrum_uses_statistics_block(tmp_path):
    from scan_batch_fit_signature import scan_path
    n, k, chi = 200, 3, 3.0e7
    spec = {"version": 3, "spectrumName": "S", "rawBE": [0.0] * n, "rawIntensity": [100.0] * n,
            "peaks": _peaks([284.8]), "statistics": {"chi": chi, "chiReduced": chi / (n - k), "rmse": (chi / n) ** 0.5}}
    f = tmp_path / "s.spec.json"; f.write_text(json.dumps(spec))
    hits = scan_path(f)
    assert len(hits) == 1 and hits[0]["tab"] == "S"


def test_proj_zip_is_scanned(tmp_path):
    from scan_batch_fit_signature import scan_path
    tabs = [_backend_tab("A", [284.8]), _local_tab("B", [284.8])]
    z = tmp_path / "p.proj.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("manifest.json", json.dumps({"version": 3, "spectra": [{"index": i, "filename": f"spectrum_{i}_{t['name']}.json"} for i, t in enumerate(tabs)]}))
        for i, t in enumerate(tabs):
            zf.writestr(f"spectrum_{i}_{t['name']}.json", json.dumps(t))
    hits = scan_path(z)
    assert [h["tab"] for h in hits] == ["B"]


def test_cli_reports_counts_and_exit_code(tmp_path):
    f = _write_proj_json(tmp_path, [_backend_tab("A", [284.8]), _local_tab("B", [284.8])])
    r = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 1, r.stdout + r.stderr        # hits found -> non-zero, so it is usable in scripts
    assert "B" in r.stdout and "1 suspected" in r.stdout
    clean = tmp_path / "clean"; clean.mkdir()
    _write_proj_json(clean, [_backend_tab("A", [284.8])])
    r2 = subprocess.run([sys.executable, str(SCRIPT), str(clean)], capture_output=True, text=True)
    assert r2.returncode == 0 and "0 suspected" in r2.stdout


def test_low_count_server_fit_is_only_possible_never_suspected(tmp_path):
    # backend weights are 1/sqrt(max(counts,1)): with counts ~1 the weighted ratio equals the unweighted one
    from scan_batch_fit_signature import scan_path
    t = _tab("A", _peaks([284.8]), chi_reduced=1.015, rmse=1.0)
    hits = scan_path(_write_proj_json(tmp_path, [t]))
    assert len(hits) == 1 and hits[0]["level"] == "possible"


def test_huge_chi_alone_does_not_flag_a_weighted_fit(tmp_path):
    from scan_batch_fit_signature import scan_path
    t = _tab("A", _peaks([284.8]), chi_reduced=2500.0, rmse=5000.0)   # ratio 1e-4: weighted, just a terrible fit
    assert scan_path(_write_proj_json(tmp_path, [t])) == []


def test_missing_rmse_is_reported_as_insufficient_when_corroborated(tmp_path):
    from scan_batch_fit_signature import scan_path
    src = _backend_tab("A", [284.8])
    t = _tab("B", _peaks([284.8]), chi_reduced=5.0, rmse=None); del t["fitResult"]["rmse"]
    hits = scan_path(_write_proj_json(tmp_path, [src, t]))
    assert [h["level"] for h in hits] == ["insufficient"] and hits[0]["tab"] == "B"


def test_post_fix_local_result_is_distinguished(tmp_path):
    from scan_batch_fit_signature import scan_path
    t = _local_tab("B", [284.8]); t["fitResult"]["engine"] = "local"; t["fitResult"]["objective"] = "unweighted_residual_variance"
    hits = scan_path(_write_proj_json(tmp_path, [t]))
    assert hits[0]["level"] == "post-fix"


def test_unreadable_file_gives_exit_code_2_not_clean(tmp_path):
    (tmp_path / "junk.proj.json").write_text("not json")
    r = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 2 and "UNREADABLE" in r.stdout


def test_nonexistent_path_is_unreadable_not_clean(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path / "missing.proj.zip")], capture_output=True, text=True)
    assert r.returncode == 2 and "UNREADABLE" in r.stdout


def test_no_hits_still_prints_the_triage_caveat(tmp_path):
    _write_proj_json(tmp_path, [_backend_tab("A", [284.8])])
    r = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 0 and "not proven unaffected" in r.stdout
