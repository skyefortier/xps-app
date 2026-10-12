"""A link the server cannot fit as drawn is refused (Q10 0c', owner 2026-10-11): a linked peak has
its parent's lineshape. Voigt and GL are one backend shape (pseudo_voigt_gl), so the page sends
each peak's `frontend_shape`; a spec without it is judged by its backend shape. Self-links and
cycles were already refused (audit F11). The new field changes neither the seed nor the fit."""
import io

import pytest

import fitting
from app import create_app
import test_scattered_starts as SS


def _pair(child_shape="GL", parent_shape="GL", backend_child="pseudo_voigt_gl", backend_parent="pseudo_voigt_gl"):
    x, y, specs = SS._well_posed()
    parent = {**specs[0], "frontend_shape": parent_shape, "shape": backend_parent}
    child = {**specs[1], "frontend_shape": child_shape, "shape": backend_child, "constrain_to": parent["id"],
             "splitting": 2.0, "area_ratio": 0.5}
    return x, y, [parent, child]


def test_a_voigt_child_of_a_gl_parent_is_refused():
    # the round-3 gate case: one backend shape, two frontend shapes; the server fitted the child
    # at the parent's mix while the page drew it at 0.5
    x, y, specs = _pair(child_shape="Voigt", parent_shape="GL")
    with pytest.raises(ValueError, match="different lineshape .*a linked peak takes its parent's lineshape"):
        fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})


def test_different_backend_shapes_are_refused_without_frontend_shapes():
    x, y, specs = _pair(backend_child="gaussian")
    for s in specs:
        s.pop("frontend_shape")
    with pytest.raises(ValueError, match="different lineshape"):
        fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})


def test_one_lineshape_fits_as_before_and_the_new_field_changes_nothing():
    x, y, specs = _pair(child_shape="GL", parent_shape="GL")
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    bare = [{k: v for k, v in s.items() if k != "frontend_shape"} for s in specs]
    b = fitting.run_fit(x, y, bare, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    assert a["success"] and a["random_seed"] == b["random_seed"] and a["fitted_y"] == b["fitted_y"]


def test_the_route_refuses_with_a_plain_400(tmp_path):
    app = create_app(upload_folder=str(tmp_path)); app.config["TESTING"] = True
    x, y, specs = _pair(child_shape="Voigt", parent_shape="GL")
    with app.test_client() as c:
        csv = "\n".join(f"{float(a)!r},{float(b)!r}" for a, b in zip(x, y))
        sid = c.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
        for route in ("/api/fit", "/api/fit/start"):
            r = c.post(route, json={"session_id": sid, "background": {"method": "linear"}, "peaks": specs,
                                    "fit_method": "leastsq", "n_perturb": 0})
            assert r.status_code == 400 and "different lineshape" in r.get_json()["error"], (route, r.get_json())


# ── Codex 0c' round 1 ─────────────────────────────────────────────────────────

def test_a_missing_parent_and_a_shared_id_are_refused_by_the_shared_check():
    x, y, specs = _pair()
    orphan = [specs[0], {**specs[1], "constrain_to": "99"}]
    with pytest.raises(ValueError, match="linked to a peak that is not in the model"):
        fitting._validate_constraint_graph(orphan)
    # 1 and "1" are one parameter prefix (p1_)
    shared = [{**specs[0], "id": 1}, {**specs[1], "id": "1", "constrain_to": None}]
    with pytest.raises(ValueError, match="share the id"):
        fitting._validate_constraint_graph(shared)
    with pytest.raises(ValueError, match="share the id"):
        fitting.run_fit(x, y, shared, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})


def test_the_python_twin_keeps_a_link_to_a_missing_peak_so_the_server_refuses_it():
    from autofit.reference import peak_to_backend_spec
    peaks = [{"id": 3, "shape": "GL", "center": 286.0, "fwhm": 1.0, "amplitude": 100.0, "glMix": 30, "linked": 2,
              "linkOffset": 1.0, "linkRatio": 0.5}]
    spec = peak_to_backend_spec(peaks[0], peaks)
    assert spec["constrain_to"] == "2", "the twin used to drop it: the orphan was fitted free"
    x, y, _ = _pair()
    with pytest.raises(ValueError, match="not in the model"):
        fitting.run_fit(x, y, [spec], background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})


def test_every_route_refuses_at_once(tmp_path):
    app = create_app(upload_folder=str(tmp_path)); app.config["TESTING"] = True
    x, y, specs = _pair()
    orphan = [specs[0], {**specs[1], "constrain_to": "99"}]
    shared = [{**specs[0], "id": "1"}, {**specs[1], "id": "1", "constrain_to": None}]
    with app.test_client() as c:
        csv = "\n".join(f"{float(a)!r},{float(b)!r}" for a, b in zip(x, y))
        sid = c.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
        for route in ("/api/fit", "/api/fit/start"):
            r = c.post(route, json={"session_id": sid, "background": {"method": "linear"}, "peaks": orphan,
                                    "fit_method": "leastsq", "n_perturb": 0})
            assert r.status_code == 400 and "not in the model" in r.get_json()["error"], (route, r.get_json())
        # Find Peaks' "Refit my current peaks": a 400 in plain words, not "Internal analyze error" (500)
        for bad, words in ((shared, "share the id"), (orphan, "not in the model")):
            r = c.post("/api/analyze", json={"session_id": sid, "material_class": "insulator", "regions": ["C 1s"],
                                             "method": "least_squares", "peak_specs": bad,
                                             "options": {"background_method": "linear"}})
            assert r.status_code == 400 and words in r.get_json()["error"], r.get_json()
