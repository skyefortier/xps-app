"""The page uploads full precision and the server reads back the same doubles
(background math, owner 2026-10-03: page and server compute on the same numbers).

`uploadToBackend` writes every value as JavaScript's `String(v)` — the shortest decimal
that reads back as the same double — and the server's CSV parser must read each one
back bit for bit, in the page's order. Until then the page sent BE toFixed(4) and
intensity toFixed(2): the server fitted, and computed its background on, other numbers
than the page drew."""
import io
import json
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from app import create_app, _load_session

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def client_and_folder(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c, str(tmp_path)


def test_the_page_writes_every_value_as_its_shortest_round_trip_text():
    html = (ROOT / "templates" / "index.html").read_text()
    body = html[html.index("async function uploadToBackend("):]
    body = body[:body.index("\n}\n")]
    assert re.search(r"be\.map\(\(e, i\) => String\(e\) \+ ',' \+ String\(inten\[i\]\)\)\.join\('\\n'\)", body), body[:600]
    assert "toFixed" not in "\n".join(l.split("//")[0] for l in body.splitlines())   # code, not the comment


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_the_server_reads_back_the_doubles_the_page_holds(client_and_folder):
    client, folder = client_and_folder
    rng = np.random.default_rng(20261003)
    n = 400
    be = np.sort(280.0 + 15.0 * rng.random(n))[::-1]                          # descending, as real files
    inten = np.concatenate([1e4 * rng.random(n - 8),                          # full-mantissa counts
                            [0.1 + 0.2, 1e-7, 123456789.12345679, 5e-324, 1e21, 2.5, 3.0, 1 / 3]])
    # the page's own formatting, by node (String(v) is JavaScript's Number::toString)
    text = subprocess.run(
        ["node", "-e", "const d = JSON.parse(require('fs').readFileSync(0, 'utf8'));"
                       "process.stdout.write(d.be.map((e, i) => String(e) + ',' + String(d.y[i])).join('\\n'));"],
        input=json.dumps({"be": be.tolist(), "y": inten.tolist()}), capture_output=True, text=True, check=True).stdout
    assert "e-7" in text and "e+21" in text and "5e-324" in text      # the exponent forms are in play
    up = client.post("/api/upload", data={"file": (io.BytesIO(text.encode()), "spectrum.csv")})
    assert up.status_code == 200, up.get_json()
    energy, counts = _load_session(up.get_json()["session_id"], folder)
    assert energy.tobytes() == be.tobytes()
    assert counts.tobytes() == inten.tobytes()
