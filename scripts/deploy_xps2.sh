#!/usr/bin/env bash
# Deploy the commit production (the i9) runs to the xps2 droplet, then prove it (DEPLOY.md, step 5).
#
#   scripts/deploy_xps2.sh <commit>          deploy, restart xps-app, check
#   scripts/deploy_xps2.sh --check <commit>  checks only: change nothing, report whether xps2 runs it
#
# Run on the i9, from the production checkout, AFTER the i9 itself is deployed and checked.
# REFUSED (exit 1) = the application on the droplet was not changed. Refuses unless:
#   - <commit> is the i9 checkout's HEAD, on branch main, with no modified tracked files;
#   - <commit> is on origin/main (the droplet fetches from GitHub);
#   - constraints.txt equals production's environment exactly (scripts/gen_constraints.py --check);
#   - the droplet's checkout has no modified tracked files and its disk keeps >= 1 GB free.
# Then, on the droplet: save the current commit and a copy of the whole venv (the two newest such
# backups are kept), fast-forward to exactly <commit>, pip install -r requirements.txt -c
# constraints.txt, require `gen_constraints.py --check` there too (same packages, same versions, none
# missing), `import app`, restart xps-app (only), and the checks:
#   1. /api/health on the droplet and through https://xps2.fortierlab.org
#   2. a fit through the public URL records git_commit = <commit>, git_dirty = false
#   3. <droplet>:5000 refuses TCP connections from outside (the app listens on 127.0.0.1); a timeout
#      counts only if the same probe reaches port 22 (then a firewall dropped it); anything else fails
# FAILED (exit 2) after the droplet was changed prints the exact rollback (previous commit and the
# saved venv); it does not roll back by itself.
set -euo pipefail

XPS2_SSH=${XPS2_SSH:-root@137.184.183.202}
XPS2_HOST=${XPS2_SSH#*@}
XPS2_URL=${XPS2_URL:-https://xps2.fortierlab.org}
APP=/opt/xps-app
REPO=$(cd "$(dirname "$0")/.." && pwd)

TMP='' ROLLBACK='' PASSED=0
on_exit() {
  local status=$?
  set +e
  if [ -n "$ROLLBACK" ] && [ "$PASSED" = 0 ]; then
    echo "The droplet was changed and is NOT verified. Rollback (previous commit and venv):" >&2
    echo "  $ROLLBACK" >&2
  fi
  [ -n "$TMP" ] && rm -rf "$TMP"
  exit $status
}
trap on_exit EXIT

die() { echo "REFUSED: $*" >&2; exit 1; }
fail() { echo "FAILED: $*" >&2; exit 2; }
ok() { echo "  ok  $*"; }
remote() { ssh -o BatchMode=yes -o ConnectTimeout=15 "$XPS2_SSH" "$@"; }

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
  [ -f constraints.txt ] && [ -f scripts/gen_constraints.py ] || die "no constraints.txt / gen_constraints.py at $SHA"
  OUT=$("$REPO/venv/bin/python" scripts/gen_constraints.py --check 2>&1) \
    || die "production's venv: $OUT — run scripts/gen_constraints.py and commit"
  ok "production's venv: $OUT"

  # ── droplet: refusals, then a point of return (backups only; the application is not touched) ──
  SAVE=/root/backups/deploy-$(date +%Y%m%d-%H%M%S)
  PREV=$(remote "SAVE=$SAVE APP=$APP bash -s" <<'EOF'
set -euo pipefail
cd "$APP"
st=$(git status --porcelain --untracked-files=no) || { echo "git status failed on the droplet"; exit 1; }
[ -z "$st" ] || { echo "droplet checkout has modified tracked files"; exit 1; }
need=$(( $(du -sk venv | cut -f1) + 1048576 ))
free=$(df -k --output=avail / | tail -1)
[ "$free" -ge "$need" ] || { echo "only $((free / 1024)) MB free; a venv backup needs $((need / 1024)) MB with 1 GB to spare"; exit 1; }
mkdir -p "$SAVE"
git rev-parse HEAD > "$SAVE/commit.txt"
cp -a venv "$SAVE/venv"
ls -1d /root/backups/deploy-* | sort | head -n -2 | xargs -r rm -rf     # keep the two newest
cat "$SAVE/commit.txt"
EOF
) || die "droplet: $PREV (application unchanged; a partial backup in $SAVE may remain)"
  echo "droplet was at $PREV (commit and venv saved in $SAVE)"
  ROLLBACK="ssh $XPS2_SSH 'cd $APP && git reset -q --hard $PREV && rm -rf venv && cp -a $SAVE/venv venv && systemctl restart xps-app'"

  # ── droplet: from here on the application is changed ───────────────────────────────────────────
  remote "SHA=$SHA APP=$APP bash -s" <<'EOF' || fail "deploying on the droplet failed BEFORE the restart: its files/libraries may be changed while xps-app still runs the old code in memory"
set -euo pipefail
cd "$APP"
git fetch -q origin
git merge --ff-only -q "$SHA" || { echo "not a fast-forward to $SHA"; exit 1; }
[ "$(git rev-parse HEAD)" = "$SHA" ] || { echo "HEAD is $(git rev-parse HEAD), not $SHA (an older commit is a rollback: do it by hand)"; exit 1; }
venv/bin/pip install -q -r requirements.txt -c constraints.txt
out=$(venv/bin/python scripts/gen_constraints.py --check 2>&1) || { echo "droplet's venv: $out"; exit 1; }
echo "  ok  droplet's venv: $out"
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

TMP=$(mktemp -d) || fail "mktemp failed"
python3 -c "
import math
with open('$TMP/c1s.csv', 'w') as f:
    for i in range(151):
        x = 280 + 0.1 * i
        f.write(f'{x:.4f},{200 + 5000 * math.exp(-((x - 284.8) / 0.6) ** 2) + 1500 * math.exp(-((x - 286.4) / 0.7) ** 2) + 30 * (1 + (i % 7) / 7):.4f}\n')
" || fail "writing the test spectrum failed"
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

# A raw TCP connect (no proxy, no HTTP). refused = closed; open = exposed; a timeout is "filtered"
# only when the same probe reaches port 22 (routing works); every other outcome is inconclusive.
PORT=$(python3 - "$XPS2_HOST" <<'EOF'
import errno, socket, sys
def probe(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(8)
    try:
        rc = s.connect_ex((sys.argv[1], port))
    except socket.timeout:
        return "timeout"
    finally:
        s.close()
    return {0: "open", errno.ECONNREFUSED: "refused", errno.ETIMEDOUT: "timeout",
            errno.EAGAIN: "timeout"}.get(rc, f"error {errno.errorcode.get(rc, rc)}")
r = probe(5000)
if r == "timeout":
    r = "filtered" if probe(22) == "open" else "timeout, and port 22 unreachable too"
print(r)
EOF
) || fail "the port probe itself failed"
case "$PORT" in
  refused|filtered) ok "$XPS2_HOST:5000 from outside: $PORT" ;;
  open) fail "$XPS2_HOST:5000 accepts connections from outside — the app is reachable without Cloudflare" ;;
  *) fail "$XPS2_HOST:5000 check inconclusive: $PORT" ;;
esac

PASSED=1
echo "PASS: xps2 runs $SHA"
