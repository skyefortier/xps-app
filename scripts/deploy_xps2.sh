#!/usr/bin/env bash
# Deploy the commit production (the i9) runs to the xps2 droplet, then prove it (DEPLOY.md, step 5).
#
#   scripts/deploy_xps2.sh <commit>          deploy, restart xps-app, check
#   scripts/deploy_xps2.sh --check <commit>  checks only: change nothing, report whether xps2 runs it
#
# Run on the i9, from the production checkout, AFTER the i9 itself is deployed and checked.
# REFUSED (exit 1) = nothing on the droplet was changed. Refuses unless:
#   - <commit> is the i9 checkout's HEAD, on branch main, with no modified tracked files;
#   - <commit> is on origin/main (the droplet fetches from GitHub);
#   - constraints.txt at <commit> equals the libraries installed in the i9's venv (production's);
#   - the droplet's checkout has no modified tracked files.
# Then, on the droplet: record the current commit and `pip freeze`, fast-forward to exactly <commit>,
# pip install -r requirements.txt -c constraints.txt (each pinned version verified), `import app`,
# restart xps-app (only), and the checks:
#   1. /api/health on the droplet and through https://xps2.fortierlab.org
#   2. a fit through the public URL records git_commit = <commit>, git_dirty = false
#   3. nothing accepts a TCP connection on <droplet>:5000 from outside (the app is on 127.0.0.1)
# FAILED (exit 2) after the droplet was changed prints the exact rollback (the previous commit AND
# the previous libraries); it does not roll back by itself.
set -euo pipefail

XPS2_SSH=${XPS2_SSH:-root@137.184.183.202}
XPS2_HOST=${XPS2_SSH#*@}
XPS2_URL=${XPS2_URL:-https://xps2.fortierlab.org}
APP=/opt/xps-app
REPO=$(cd "$(dirname "$0")/.." && pwd)

TMP= ROLLBACK= PASSED=0
on_exit() {
  [ -n "$TMP" ] && rm -rf "$TMP"
  if [ -n "$ROLLBACK" ] && [ "$PASSED" = 0 ]; then
    echo "The droplet was changed and is NOT verified. Rollback (previous commit and libraries):" >&2
    echo "  $ROLLBACK" >&2
  fi
}
trap on_exit EXIT

die() { echo "REFUSED: $*" >&2; exit 1; }
fail() { echo "FAILED: $*" >&2; exit 2; }
ok() { echo "  ok  $*"; }
remote() { ssh -o BatchMode=yes -o ConnectTimeout=15 "$XPS2_SSH" "$@"; }

# Compare installed versions (this interpreter's) with a constraints file; exit 1 listing differences.
VERIFY_PY='
import importlib.metadata as md, sys
bad = []
for line in open(sys.argv[1]):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name, want = line.split("==")
    try:
        have = md.version(name)
    except md.PackageNotFoundError:
        have = None
    if have != want:
        bad.append(f"{name} {have} (constraints.txt: {want})")
if bad:
    sys.exit("; ".join(bad))
'

CHECK_ONLY=0
if [ "${1:-}" = "--check" ]; then CHECK_ONLY=1; shift; fi
[ $# -eq 1 ] || die "usage: $0 [--check] <commit>"

# ── the commit must be the one the i9 runs, and on origin/main ────────────────────────────────
cd "$REPO"
SHA=$(git rev-parse --verify --quiet "$1^{commit}") || die "'$1' is not a commit in $REPO"
BRANCH=$(git symbolic-ref --quiet --short HEAD) || die "the i9 checkout is not on a branch"
[ "$BRANCH" = main ] || die "the i9 checkout is on $BRANCH, not main"
HEAD_SHA=$(git rev-parse HEAD) || die "cannot read the i9's HEAD"
[ "$SHA" = "$HEAD_SHA" ] || die "$SHA is not the i9's HEAD ($HEAD_SHA)"
DIRTY=$(git status --porcelain --untracked-files=no) || die "git status failed on the i9"
[ -z "$DIRTY" ] || die "the i9 checkout has modified tracked files"
git fetch -q origin main || die "cannot fetch origin"
git merge-base --is-ancestor "$SHA" origin/main || die "$SHA is not on origin/main — push it first"
echo "commit $SHA: the i9's HEAD, on origin/main"

if [ $CHECK_ONLY -eq 0 ]; then
  [ -f constraints.txt ] || die "no constraints.txt at $SHA"
  DIFF=$("$REPO/venv/bin/python" -c "$VERIFY_PY" constraints.txt 2>&1) \
    || die "constraints.txt does not match production's venv — run scripts/gen_constraints.py and commit: $DIFF"
  ok "constraints.txt equals production's libraries"

  # ── droplet: refusals first (nothing changed), then a recorded point of return ─────────────────
  STAMP=$(date +%Y%m%d-%H%M%S)
  SAVE=/root/backups/deploy-$STAMP
  PREV=$(remote "SAVE=$SAVE APP=$APP bash -s" <<'EOF'
set -euo pipefail
cd "$APP"
st=$(git status --porcelain --untracked-files=no) || { echo "git status failed on the droplet"; exit 1; }
[ -z "$st" ] || { echo "droplet checkout has modified tracked files"; exit 1; }
mkdir -p "$SAVE"
git rev-parse HEAD > "$SAVE/commit.txt"
venv/bin/python -m pip freeze --all > "$SAVE/pip-freeze.txt"
cat "$SAVE/commit.txt"
EOF
) || die "droplet refused (nothing changed): $PREV"
  echo "droplet was at $PREV (commit and pip freeze saved in $SAVE)"
  ROLLBACK="ssh $XPS2_SSH 'cd $APP && git reset -q --hard $PREV && venv/bin/pip install -q -r $SAVE/pip-freeze.txt && systemctl restart xps-app'"

  # ── droplet: from here on it is changed ────────────────────────────────────────────────────────
  remote "SHA=$SHA APP=$APP VERIFY_PY='$VERIFY_PY' bash -s" <<'EOF' || fail "deploying on the droplet failed BEFORE the restart: its files/libraries may be changed while xps-app still runs the old code in memory"
set -euo pipefail
cd "$APP"
git fetch -q origin
git merge --ff-only -q "$SHA" || { echo "not a fast-forward to $SHA"; exit 1; }
[ "$(git rev-parse HEAD)" = "$SHA" ] || { echo "HEAD is $(git rev-parse HEAD), not $SHA (an older commit is a rollback: do it by hand)"; exit 1; }
venv/bin/pip install -q -r requirements.txt -c constraints.txt
venv/bin/python -c "$VERIFY_PY" constraints.txt || { echo "libraries differ from constraints.txt"; exit 1; }
echo "  ok  libraries equal constraints.txt"
venv/bin/python -c "import app" || { echo "import app failed"; exit 1; }
echo "  ok  import app"
EOF
  remote "systemctl restart xps-app" || fail "systemctl restart xps-app failed"
  echo "restarted xps-app"
fi

# ── checks ─────────────────────────────────────────────────────────────────────────────────────
echo "checks:"
up=0
for _ in $(seq 1 30); do
  if remote "curl -sf -m 5 http://127.0.0.1:5000/api/health" 2>/dev/null | grep -q '"ok"'; then up=1; break; fi
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

# A raw TCP connect (no proxy, no HTTP): any accepted connection is a failure.
PORT=$(python3 -c "
import socket, errno
s = socket.socket(); s.settimeout(8)
try:
    rc = s.connect_ex(('$XPS2_HOST', 5000))
except socket.timeout:
    rc = 'timeout'
print('open' if rc == 0 else 'refused' if rc == errno.ECONNREFUSED else 'no answer (%s)' % rc)
")
[ "$PORT" != open ] || fail "$XPS2_HOST:5000 accepts connections from outside — the app is reachable without Cloudflare"
ok "$XPS2_HOST:5000 from outside: $PORT"

PASSED=1
echo "PASS: xps2 runs $SHA"
