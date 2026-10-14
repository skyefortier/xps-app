"""Record Auto-Fit's ANCHOR request bodies (session_id removed) from the page served at a given checkout.

Usage: python scripts/seal_1c_record_autofit_anchor.py CHECKOUT OUT.json   (the committed baseline: CHECKOUT = 34ce8ba)
"""
import json, sys, subprocess, socket, time, urllib.request
from playwright.sync_api import sync_playwright
root, out = sys.argv[1], sys.argv[2]
s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
proc = subprocess.Popen(["/Users/skyefortier/xps-app/venv/bin/gunicorn", "app:app", "-w", "1", "-b", f"127.0.0.1:{port}", "--timeout", "120"],
                        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
base = f"http://127.0.0.1:{port}"
for _ in range(50):
    try: urllib.request.urlopen(base + "/api/health", timeout=1); break
    except Exception: time.sleep(0.2)
res = {}
try:
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        for name, anchors in (("autofit_anchor_plain", False), ("autofit_anchor_with_anchors", True)):
            pg = b.new_page()
            pg.goto(base + "/", wait_until="load")
            pg.set_input_files("#load-session-input", root + "/docs/autofit/test_data/8-JT Graphite.proj.zip")
            pg.wait_for_function("() => tabManager.tabs.some(t => t.name === 'C1s Scan')", timeout=60000)
            pg.evaluate("() => tabManager.activateTab(tabManager.tabs.find(t => t.name === 'C1s Scan').id)")
            pg.evaluate("""(anchors) => { window._showAutoFitConfirmModal = () => Promise.resolve(true);
                if (anchors) { _setManualAnchors([{ x: 283.0, y: 1500 }, { x: 292.0, y: 1200 }]); updatePlot(); } }""", anchors)
            with pg.expect_request("**/api/fit/start", timeout=60000) as info:
                pg.evaluate("() => { window.__af = runAutoFitC1sGraphite(); }")
            body = info.value.post_data_json; body.pop("session_id", None)
            res[name] = body
            pg.evaluate("async () => { try { await window.__af; } catch (e) {} }")
            pg.close()
        b.close()
finally:
    proc.terminate()
json.dump(res, open(out, "w"), indent=1, sort_keys=True)
print({k: (len(v["peaks"]), v["background"]) for k, v in res.items()})
