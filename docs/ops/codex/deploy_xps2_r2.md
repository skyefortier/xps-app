# Codex review of scripts/deploy_xps2.sh — round 2 (2026-10-16, one run per round, owner: Codex x1)

## Prompt

> Review scripts/deploy_xps2.sh in /Users/skyefortier/xps-app (branch ops-xps2-sync; read DEPLOY.md steps 4-6 and scripts/gen_constraints.py for context). It runs on the i9 (macOS, production checkout) and deploys to a DigitalOcean droplet over SSH.
> 
> Owner's requirements for the script:
> - Refuse (change nothing on the droplet) unless the commit equals the i9's commit (HEAD of the production checkout on main, clean tracked files) and is on origin/main.
> - Install libraries matching production (requirements.txt + constraints.txt), restart only the xps-app service.
> - Checks: health on the droplet and through https://xps2.fortierlab.org; a fit's record (software.git_commit / git_dirty, from fitting._software_identity) shows the deployed commit; port 5000 refuses connections from outside.
> - Fail loudly; print a rollback on failure after the restart.
> 
> This is round 2. Round 1 (NO-GO) found: (1) clean-tree checks failed open when git fails; (2) a pre-restart failure claimed "untouched" after mutations; (3) no rollback when the restart fails; (4) curl exit 28 can mean connected-then-timed-out; (5) libraries compared to the file, not production; (6) rollback could not restore previous libraries. Verify each is fixed in the current file and look for anything new the fixes introduced (incl. passing VERIFY_PY through the ssh command string, the heredoc inside $( ), and the on_exit trap). Severity per finding (BLOCKER / MAJOR / MINOR) and end with a line "VERDICT: GO" or "VERDICT: NO-GO".

## Verdict

Several fixes work, but dependency parity, rollback completeness, and failure handling still have gaps.

1. **MAJOR — Dependency verification checks only listed pins, not completeness.** [Lines 45–60](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:45) now compare constraints against production’s interpreter, fixing round 1’s file-only comparison. However, missing pins go unnoticed. A newly added requirement can resolve differently on the droplet while both verifiers pass. Mocked verification accepted different Gunicorn versions when its pin was omitted; comment-only constraints also passed. Verify that constraints cover the full production dependency closure, as computed by `gen_constraints.py`.

2. **MAJOR — Rollback does not restore the previous package set.** [Line 101](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:101) reinstalls saved versions, but leaves packages introduced by the failed deployment installed. Those packages can introduce incompatible dependencies or change optional-import behavior. Round 1 #6 is only partially fixed. Preserve and restore the previous virtual environment, or reconstruct its exact package set and verify it before restarting.

3. **MAJOR — Port verification accepts routing failures as success.** [Lines 153–163](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:153) correctly fix the connected-then-timed-out ambiguity: a successful TCP connection immediately reports `open`. But every nonzero result passes, including `ENETUNREACH` and `EHOSTUNREACH`; I reproduced both with mocks. These indicate an inconclusive probe, not proof that port 5000 refuses connections. Handle refusal explicitly, distinguish any permitted firewall timeout, and fail on other errors.

4. **MAJOR — Cleanup failure suppresses the required rollback message.** In [the exit trap](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:30), `rm -rf "$TMP"` executes before rollback reporting under `set -e`. If cleanup fails, the trap exits immediately. A mocked cleanup failure suppressed the rollback entirely and changed exit status 2 to 1. Capture the original status, print rollback before cleanup, make cleanup best-effort, and preserve the original status.

5. **MINOR — The backup phase can still claim “nothing changed” after writes.** [Lines 94–99](/Users/skyefortier/xps-app/scripts/deploy_xps2.sh:94) create a directory and backup files before failures are classified as an untouched refusal. A failed freeze can leave partial backup files. The application is still unchanged at this point, so this is narrower than round 1’s original issue, but the message remains inaccurate.

Round 1 verification:

| Finding | Result |
|---|---|
| 1. Git failures bypass clean-tree checks | **Fixed.** Both status assignments explicitly reject command failure. |
| 2. Pre-restart failure claims untouched | **Main mutation path fixed.** Backup-phase wording remains inaccurate, as above. |
| 3. Restart failure omits rollback | **Fixed on the normal path.** Rollback is assigned before restart; its failure invokes `fail` and the exit trap. |
| 4. Curl timeout can hide an accepted connection | **Fixed specifically.** Raw TCP probing introduces the error-classification gap above. |
| 5. Libraries compared only against the file | **Partially fixed.** Production is checked, but dependency coverage is not. |
| 6. Rollback cannot restore previous libraries | **Partially fixed.** Saved versions are restored; newly installed packages remain. |

The current `VERIFY_PY` contains no single quotes, and its SSH command-string quoting preserved the exact payload in a local shell round-trip. The script passes macOS Bash 3.2 syntax checking, including the heredoc inside `$()`. Runtime testing of that heredoc was blocked by the read-only sandbox’s prohibition on temporary files.

The health and fit checks target the requested endpoints and require the exact commit with `git_dirty=False`; only `xps-app` is restarted. No deployment or remote commands were executed.

VERDICT: NO-GO
