# Deploying XPS Fitting Studio

Production runs as a macOS **LaunchAgent** (`com.hal238b.xps-app`) serving
gunicorn on **`127.0.0.1:5050`**, published to https://xps.fortierlab.org via a
Cloudflare Tunnel. A separate **xps2 droplet** runs the same commit (step 5).

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

## 4. Libraries: `constraints.txt`

Both machines install `pip install -r requirements.txt -c constraints.txt`.
`constraints.txt` pins every package `requirements.txt` pulls in to the version
production (the i9) runs. It is generated, not edited: after changing
production's libraries, run `venv/bin/python scripts/gen_constraints.py` on the
i9 and commit the result with the change.

## 5. Deploy xps2 too — every deploy, both machines (owner, 2026-10-16)

xps2.fortierlab.org (DigitalOcean droplet `root@137.184.183.202`, app in
`/opt/xps-app`, systemd `xps-app` on `127.0.0.1:5000`, its own tunnel
`xps-droplet`) runs the same commit as production. After the i9 is deployed
and checked (steps 1–3), and **before** the deploy-log commit (the script
requires the i9's HEAD):

```bash
scripts/deploy_xps2.sh <commit>          # e.g. the merge commit just deployed
scripts/deploy_xps2.sh --check <commit>  # checks only, changes nothing
```

It refuses unless the commit is the i9's HEAD on `main` (clean) and is on
`origin/main`, and unless the droplet fast-forwards to exactly it. It then
installs the constrained libraries and verifies each, imports the app,
restarts `xps-app` (nothing else), and checks: health on the droplet and at
https://xps2.fortierlab.org; a fit's record naming the commit with
`git_dirty: false`; port 5000 refusing connections from outside. `PASS` or a
`FAILED:` line; after a failure it prints the rollback command (it does not
roll back on its own). One deploy-log entry covers both machines.

## 6. Manual failover: send xps.fortierlab.org to xps2

When the i9 is down for more than a few minutes. In-progress work is lost for
anyone mid-session (uploads and running fits live on the machine that took
them; they reload the spectrum and fit again). xps2 has 2 workers and 1 GB, so
large fits run slower.

**One-time preparation (not done yet; needs owner approval):** xps2's tunnel
must accept the main hostname. On the droplet, add to
`/root/.cloudflared/config.yml`, above the final `http_status:404` line:

```yaml
  - hostname: xps.fortierlab.org
    service: http://localhost:5000
```

then `systemctl restart cloudflared`. Harmless until DNS points there.

**Switch to xps2** — either way works:

- *From a terminal* that can SSH to the droplet:
  `ssh root@137.184.183.202 'cloudflared tunnel route dns --overwrite-dns xps-droplet xps.fortierlab.org'`
- *From the Cloudflare dashboard:* fortierlab.org → DNS → Records → the
  `xps` CNAME → Edit → change its target from
  `ee3e7f80-d0bf-4fd6-bb6f-b6712b342c58.cfargotunnel.com` to
  `f4d4196f-15dc-43b4-a5f4-28e0389145e1.cfargotunnel.com` → Save (keep it Proxied).

Check: `curl https://xps.fortierlab.org/api/health` → `{"status":"ok"}`
(a minute or two; a fit's record names the droplet's commit and `python
3.12.3`).

**Switch back** once the i9 answers on `http://127.0.0.1:5050/api/health`:

- *Terminal, on the i9:*
  `cloudflared tunnel route dns --overwrite-dns xps-fortierlab xps.fortierlab.org`
- *Dashboard:* set the `xps` CNAME target back to
  `ee3e7f80-d0bf-4fd6-bb6f-b6712b342c58.cfargotunnel.com`.

Then check `https://xps.fortierlab.org/api/health` again.

## Notes

- The reference endpoint validates `data/xps/**` on load and **fails loudly**
  with a structured error (filename + JSON path) if a record is malformed —
  check `/api/xps-reference` after deploy if reference features look empty.
- The frontend degrades safely: if reference data fails to load, the
  Reference Lines / NIST Lookup / Survey controls disable with a banner while
  fitting keeps working.
