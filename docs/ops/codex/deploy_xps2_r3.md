# Codex review of scripts/deploy_xps2.sh — round 3 (2026-10-16, one run per round, owner: Codex x1)

## Prompt

> Review scripts/deploy_xps2.sh in /Users/skyefortier/xps-app (branch ops-xps2-sync; read DEPLOY.md steps 4-6 and scripts/gen_constraints.py for context). It runs on the i9 (macOS, production checkout) and deploys to a DigitalOcean droplet over SSH.
> 
> Owner's requirements for the script:
> - Refuse (change nothing on the droplet) unless the commit equals the i9's commit (HEAD of the production checkout on main, clean tracked files) and is on origin/main.
> - Install libraries matching production (requirements.txt + constraints.txt), restart only the xps-app service.
> - Checks: health on the droplet and through https://xps2.fortierlab.org; a fit's record (software.git_commit / git_dirty, from fitting._software_identity) shows the deployed commit; port 5000 refuses connections from outside.
> - Fail loudly; print a rollback on failure after the restart.
> 
> This is round 3. Round 1 found 6 defects, round 2 (NO-GO) found: (1) constraints not checked for completeness; (2) rollback left packages added by the failed deploy; (3) port probe accepted ENETUNREACH/EHOSTUNREACH; (4) a cleanup failure in the trap suppressed the rollback and changed the status; (5) the backup phase said "nothing changed" after writing backups. Verify each is fixed in the current deploy_xps2.sh and gen_constraints.py (now with --check) and look for anything new the fixes introduced. Tested by me against the real droplet: the backup block (commit + 316 MB venv copy, pruning, disk check) and the port probe (droplet: refused; a blackholed address: "timeout, and port 22 unreachable too"). Severity per finding (BLOCKER / MAJOR / MINOR) and end with a line "VERDICT: GO" or "VERDICT: NO-GO".

## Verdict

All five round-2 defects are fixed for the current requirements. No BLOCKER or MAJOR findings.

One **MINOR** finding remains:

- **Some post-restart errors bypass the documented failure status.** The port-probe assignment at [deploy_xps2.sh:143](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:143) has no `|| fail` handler. An uncaught Python exception exits with status **1**, documented as “REFUSED/application unchanged,” instead of **2**. I reproduced this with a simulated DNS failure. The traceback and rollback still print, so this does not silently pass or prevent recovery. Guard the assignment with `|| fail "port probe failed"`; the temporary-directory and fixture-generation commands have the same reporting gap.

Round-2 verification:

| Previous defect | Result |
|---|---|
| Constraints completeness | **Fixed.** The dependency closure is recomputed and compared on both machines. The current environment passes with 27 packages; simulated missing, wrong-version, and extra pins fail. |
| Rollback retained added packages | **Fixed.** Rollback removes the deployed venv and restores the complete saved venv, eliminating packages introduced by the failed deploy. |
| Probe accepted unreachable errors | **Fixed.** `ENETUNREACH` and `EHOSTUNREACH` reach the failure case. A timeout passes only when port 22 accepts a connection. |
| Cleanup suppressed rollback/status | **Fixed.** Rollback prints before cleanup, with errexit disabled and the original status preserved. Verified with simulated cleanup failures. |
| Backup failure claimed nothing changed | **Fixed.** The message now specifies “application unchanged” and acknowledges a possible partial backup. |

The commit, branch, tracked-cleanliness, and `origin/main` gates run before any droplet operation. Deployment uses requirements plus constraints and restarts only `xps-app`. Both health checks and the public fit’s import-time software identity are checked.

Validation was read-only: shell syntax, the actual constraints check, and in-memory failure simulations. I did not contact the droplet or independently rerun your backup tests.

VERDICT: GO
