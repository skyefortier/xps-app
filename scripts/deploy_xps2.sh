#!/usr/bin/env bash
# Deploy the commit production (the i9) runs to the xps2 droplet, then prove it (DEPLOY.md, step 5).
#
#   scripts/deploy_xps2.sh <commit>          deploy, restart xps-app, check
#   scripts/deploy_xps2.sh --check <commit>  checks only: change nothing, report whether xps2 runs it
#
# Run on the i9, from the production checkout, AFTER the i9 itself is deployed and checked.
# Refuses (exit 1, nothing changed on the droplet) unless:
#   - <commit> is the i9 checkout's HEAD, on branch main, with no modified tracked files;
#   - <commit> is on origin/main (the droplet fetches from GitHub);
#   - the droplet's checkout has no modified tracked files and fast-forwards to exactly <commit>.
# Then: pip install -r requirements.txt -c constraints.txt (production's library versions, verified
# package by package), `import app`, restart xps-app (only), and the checks:
#   1. /api/health on the droplet and through https://xps2.fortierlab.org
#   2. a fit through the public URL records git_commit = <commit>, git_dirty = false
#   3. port 5000 refuses connections from outside (the app listens on 127.0.0.1 only)
# A failure after the restart says so and prints the rollback; it does not roll back by itself.
set -euo pipefail

XPS2_SSH=${XPS2_SSH:-root@137.184.183.202}
XPS2_HOST=${XPS2_SSH#*@}
XPS2_URL=${XPS2_URL:-https://xps2.fortierlab.org}
APP=/opt/xps-app
REPO=$(cd "$(dirname "$0")/.." && pwd)

die() { echo "REFUSED: $*" >&2; exit 1; }
fail() { echo "FAILED: $*" >&2; exit 2; }
ok() { echo "  ok  $*"; }

CHECK_ONLY=0
if [ "${1:-}" = "--check" ]; then CHECK_ONLY=1; shift; fi
[ $# -eq 1 ] || die "usage: $0 [--check] <commit>"

# ── the commit must be the one the i9 runs, and on origin/main ────────────────────────────────
cd "$REPO"
SHA=$(git rev-parse --verify --quiet "$1^{commit}") || die "'$1' is not a commit in $REPO"
[ "$(git symbolic-ref --quiet --short HEAD || true)" = main ] || die "the i9 checkout is not on main"
[ "$SHA" = "$(git rev-parse HEAD)" ] || die "$SHA is not the i9's HEAD ($(git rev-parse HEAD))"
[ -z "$(git status --porcelain --untracked-files=no)" ] || die "the i9 checkout has modified tracked files"
git fetch -q origin main || die "cannot fetch origin"
git merge-base --is-ancestor "$SHA" origin/main || die "$SHA is not on origin/main — push it first"
echo "commit $SHA: the i9's HEAD, on origin/main"

TMP=
on_exit() {
  [ -n "$TMP" ] && rm -rf "$TMP"
  if [ -n "${ROLLBACK:-}" ] && [ "${PASSED:-0}" = 0 ]; then echo "Rollback to $PREV: $ROLLBACK" >&2; fi
}
trap on_exit EXIT

remote() { ssh -o BatchMode=yes -o ConnectTimeout=15 "$XPS2_SSH" "$@"; }

# ── deploy ─────────────────────────────────────────────────────────────────────────────────────
if [ $CHECK_ONLY -eq 0 ]; then
  PREV=$(remote "git -C $APP rev-parse HEAD") || die "cannot reach $XPS2_SSH"
  echo "droplet was at $PREV"
  remote "SHA=$SHA APP=$APP bash -s" <<'EOF' || die "droplet refused or failed BEFORE the restart (xps-app untouched)"
set -euo pipefail
cd "$APP"
[ -z "$(git status --porcelain --untracked-files=no)" ] || { echo "droplet checkout has modified tracked files"; exit 1; }
git fetch -q origin
git merge --ff-only -q "$SHA" || { echo "not a fast-forward to $SHA"; exit 1; }
[ "$(git rev-parse HEAD)" = "$SHA" ] || { echo "HEAD is $(git rev-parse HEAD), not $SHA (deploying an older commit is a rollback: do it by hand)"; exit 1; }
[ -f constraints.txt ] || { echo "no constraints.txt in $SHA"; exit 1; }
venv/bin/pip install -q -r requirements.txt -c constraints.txt
venv/bin/python - <<'PY'
import importlib.metadata as md, sys
bad = []
for line in open("constraints.txt"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name, want = line.split("==")
    try:
        have = md.version(name)
    except md.PackageNotFoundError:
        have = None
    if have != want:
        bad.append(f"{name}: {have} != {want}")
if bad:
    sys.exit("libraries differ from production: " + "; ".join(bad))
print("  ok  libraries equal production's (constraints.txt)")
PY
venv/bin/python -c "import app" || { echo "import app failed"; exit 1; }
echo "  ok  import app"
EOF
  remote "systemctl restart xps-app" || fail "restart failed"
  echo "restarted xps-app"
  ROLLBACK="ssh $XPS2_SSH 'cd $APP && git reset -q --hard $PREV && venv/bin/pip install -q -r requirements.txt \$( [ -f constraints.txt ] && echo -c constraints.txt ) && systemctl restart xps-app'"
fi

# ── checks ─────────────────────────────────────────────────────────────────────────────────────
echo "checks:"
up=0
for _ in $(seq 1 30); do
  if remote "curl -sf -m 5 http://127.0.0.1:5000/api/health" | grep -q '"ok"'; then up=1; break; fi
  sleep 2
done
[ $up -eq 1 ] || fail "/api/health on the droplet did not answer ok within 60 s"
ok "/api/health on the droplet"
curl -sf -m 20 "$XPS2_URL/api/health" | grep -q '"ok"' || fail "$XPS2_URL/api/health not ok"
ok "$XPS2_URL/api/health"

TMP=$(mktemp -d)
python3 -c "
import math
with open('$TMP/c1s.csv', 'w') as f:
    for i in range(151):
        x = 280 + 0.1 * i
        f.write(f'{x:.4f},{200 + 5000 * math.exp(-((x - 284.8) / 0.6) ** 2) + 1500 * math.exp(-((x - 286.4) / 0.7) ** 2) + 30 * (1 + (i % 7) / 7):.4f}\n')
"
SID=$(curl -sf -m 30 -F "file=@$TMP/c1s.csv" "$XPS2_URL/api/upload" \
      | python3 -c 'import sys, json; print(json.load(sys.stdin)["session_id"])') || fail "upload through $XPS2_URL failed"
REC=$(curl -sf -m 90 "$XPS2_URL/api/fit" -H 'Content-Type: application/json' -d "{\"session_id\": \"$SID\",
      \"fit_method\": \"least_squares\", \"background\": {\"method\": \"shirley\"}, \"peaks\": [
      {\"id\": \"a\", \"shape\": \"pseudo_voigt_gl\", \"center\": 284.7, \"fwhm\": 1.0, \"amplitude\": 4000},
      {\"id\": \"b\", \"shape\": \"pseudo_voigt_gl\", \"center\": 286.5, \"fwhm\": 1.2, \"amplitude\": 1000}]}" \
      | python3 -c 'import sys, json; d = json.load(sys.stdin); s = d.get("software") or {}
print(d.get("success"), s.get("git_commit"), s.get("git_dirty"))') || fail "fit through $XPS2_URL failed"
curl -s -m 10 -X DELETE "$XPS2_URL/api/session/$SID" >/dev/null || true
[ "$REC" = "True $SHA False" ] || fail "fit record says (success, commit, dirty) = ($REC), expected (True, $SHA, False)"
ok "a fit's record: git_commit $SHA, git_dirty false"

rc=0; curl -s -m 8 -o /dev/null "http://$XPS2_HOST:5000/api/health" || rc=$?
case $rc in
  7|28) ok "port 5000 refuses connections from outside (curl exit $rc)" ;;
  0)    fail "port 5000 answers from outside — the app is reachable without Cloudflare" ;;
  *)    fail "port 5000 check inconclusive (curl exit $rc)" ;;
esac

PASSED=1
echo "PASS: xps2 runs $SHA"
