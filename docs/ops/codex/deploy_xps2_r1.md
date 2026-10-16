# Codex review of scripts/deploy_xps2.sh — round 1 (2026-10-16, one run per round, owner: Codex x1)

## Prompt

> Review scripts/deploy_xps2.sh in /Users/skyefortier/xps-app (branch ops-xps2-sync; read DEPLOY.md steps 4-6 and scripts/gen_constraints.py for context). It runs on the i9 (macOS, production checkout) and deploys to a DigitalOcean droplet over SSH.
> 
> Owner's requirements for the script:
> - Refuse (change nothing on the droplet) unless the commit equals the i9's commit (HEAD of the production checkout on main, clean tracked files) and is on origin/main.
> - Install libraries matching production (requirements.txt + constraints.txt), restart only the xps-app service.
> - Checks: health on the droplet and through https://xps2.fortierlab.org; a fit's record (software.git_commit / git_dirty, from fitting._software_identity) shows the deployed commit; port 5000 refuses connections from outside.
> - Fail loudly; print a rollback on failure after the restart.
> 
> Find real defects only: a path where the script reports PASS when a requirement is not met, refuses or fails wrongly, changes the droplet when it should refuse, leaves the droplet half-deployed without saying so, quoting/escaping bugs (incl. the remote heredocs and the rollback string), set -euo pipefail pitfalls, trap behaviour, and anything in gen_constraints.py that would make the two machines install different versions. You cannot reach the droplet; reason from the code. Severity per finding (BLOCKER / MAJOR / MINOR) and end with a line "VERDICT: GO" or "VERDICT: NO-GO".

## Verdict

Found six defects:

1. **MAJOR — Clean-tree checks fail open when Git fails.** [deploy_xps2.sh:39](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:39), also line 60.  
   `[ -z "$(git status …)" ]` checks stdout, discarding Git’s exit status. If Git cannot read the index and produces no stdout, the checkout is accepted as clean. `set -e` does not prevent this; I reproduced it in Bash. Locally, this permits droplet changes without establishing the required clean production checkout. Capture and check Git’s status separately.

2. **MAJOR — Pre-restart failures leave a partial deployment while claiming the app is untouched.** [deploy_xps2.sh:57](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:57).  
   The remote block advances the checkout and modifies the live virtualenv before checking package versions and importing the app. A pip or import failure exits with `REFUSED: … (xps-app untouched)` and no rollback. The service has not restarted, but its files and potentially its dependencies have changed. Report partial deployment explicitly and provide recovery instructions once mutations begin.

3. **MAJOR — A failed restart receives no rollback command.** [deploy_xps2.sh:87](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:87).  
   `ROLLBACK` is assigned only after `systemctl restart` succeeds. A restart can stop the old service and then fail to start the replacement; SSH can also fail after executing it. Both paths exit before the trap has rollback instructions. Prepare the rollback before attempting the restart.

4. **MAJOR — The external-port check can PASS with port 5000 accepting connections.** [deploy_xps2.sh:124](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:124).  
   Curl exit 28 also means an HTTP response timed out **after TCP connected**. An exposed but stalled or overloaded gunicorn therefore passes this check. Additionally, curl can use an environment-configured proxy, so the connection failure need not concern the droplet. Probe TCP connectivity directly, bypass proxies, and treat any successful connection as failure.

5. **MAJOR — Library verification establishes agreement with the file, not with production.** [deploy_xps2.sh:65](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:65).  
   Only the droplet’s installed versions are checked. Updating the i9’s virtualenv without regenerating constraints leaves tracked files clean; deployment can then install older pinned versions and report PASS despite differing from production. Compare the i9’s installed versions against the constraints before changing the droplet.

6. **MAJOR — Rollback cannot restore previous library versions when the previous commit lacks constraints.** [deploy_xps2.sh:89](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:89).  
   This applies to the documented previous deployment, `ef750f6`, which has no `constraints.txt`. The fallback installs broad requirements into the already-modified virtualenv, retaining upgraded packages that satisfy those requirements. It restores old code with potentially new dependencies. Capture the previous dependency versions before installation and use them for recovery.

The quoted remote heredocs and escaped rollback command substitution are correct. I found no dependency-closure discrepancy in `gen_constraints.py` for the current packages and documented Python 3.12 macOS/Linux environments.

Review used source inspection, dependency metadata, syntax checking, and isolated shell reproductions; no droplet access or repository changes.

VERDICT: NO-GO
