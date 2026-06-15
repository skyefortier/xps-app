# Deploying XPS Fitting Studio

Production runs as a macOS **LaunchAgent** (`com.hal238b.xps-app`) serving
gunicorn on **`127.0.0.1:5050`**, published to https://xps.fortierlab.org via a
Cloudflare Tunnel. A separate **xps2 droplet** is deployed the same way.

> **Health-check `:5050`, never `:5000`.** macOS AirTunes intercepts `:5000`
> and returns `403 Server: AirTunes`, which looks like a failed deploy when it
> isn't.

## 0. Install dependencies FIRST (before any restart)

The reference feature depends on `jsonschema` (`app.py` → `xps_reference`
imports it). **The app fails to import without it.** Install before restarting
the LaunchAgent or deploying the droplet:

```bash
~/xps-app/venv/bin/pip install -r requirements.txt
```

## 1. Verify, then merge to main (fast-forward only)

```bash
# Pre-merge: browser-verify the change on a dev gunicorn (port 5151, --reload).
git push origin <branch>
git checkout main
git merge --ff-only <branch>
git push origin main
```

Production gunicorn serves `templates/index.html` and `data/xps/**` from disk,
so the merge ships the frontend and reference data. A `--ff-only` merge keeps
history linear and fails loudly if the branch isn't a clean fast-forward.

## 2. Restart the LaunchAgent

Required for backend (`.py`) changes; the standard sequence restarts either way.

```bash
launchctl kickstart -k gui/$(id -u)/com.hal238b.xps-app
```

## 3. Health-check

```bash
launchctl print gui/$(id -u)/com.hal238b.xps-app | grep -E 'state|last exit'   # expect state=running, last exit 0
curl http://127.0.0.1:5050/api/health                                          # {"status":"ok"}
# reference data loaded + validated:
curl -s http://127.0.0.1:5050/api/xps-reference \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("legacy:",d["legacy"] is not None,"| curated elements:",len(d["elements"]))'
```

Then spot-check https://xps.fortierlab.org in a browser: Reference Lines
overlay, NIST Lookup, a survey marker, and a fit.

## 4. xps2 droplet

Same sequence. **Install `jsonschema` (step 0) before deploying** — the import
dependency applies there too. The data files (`data/xps/**`, including
`legacy/` and `tests/fixtures/xps_legacy_snapshot.json`) ship via the merge.

## Notes

- The reference endpoint validates `data/xps/**` on load and **fails loudly**
  with a structured error (filename + JSON path) if a record is malformed —
  check `/api/xps-reference` after deploy if reference features look empty.
- The frontend degrades safely: if reference data fails to load, the
  Reference Lines / NIST Lookup / Survey controls disable with a banner while
  fitting keeps working.
