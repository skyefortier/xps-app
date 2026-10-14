# Seal 1b, run v2: manifest

Date of the run: 2026-10-14 (recording to replay ran from about 05:26 to 06:59 local time, judging by file times).
Machine: the lab's i9 (macOS). The run did not touch production. The gunicorn it started served on 127.0.0.1:5153, with its own upload folder.

## Code and software

- Commit: `a46cd3fb3bdf82bf89d5d3f4b8e3dddaa773bfa1` (branch `seal-1b-measure`).
- Working tree at the start of the run: `run.log.head` holds `commit a46cd3f dirty=       0`, which is `git status --porcelain | wc -l` taken before the first phase.
- The software identity that every one of the 328 records carries in `O.software`. It is ONE identity. `summary.txt`, line 3, shows "software identities 1". Its full text is:

  ```json
  {"env_sha256": "cd6af4a545d3882b6f055df70ef948ee74803094889dd1ab6ba51d5b42b8a7b8",
   "git_commit": "a46cd3fb3bdf82bf89d5d3f4b8e3dddaa773bfa1", "git_dirty": false,
   "lmfit": "1.3.4", "numerics": "2026-10-13", "numpy": "2.4.4", "python": "3.12.13",
   "scipy": "1.17.1", "seed_derivation": "xps-fit-seed-v2"}
  ```
  `records_index.jsonl` carries this identity's sha256 for each record, computed from `json.dumps(software, sort_keys=True)`.
- `/api/verify-fit` compares the whole software identity before any numerical check. Every verification here therefore ran on the identity that produced the record.
- Producing `records_index.jsonl` and `summary.txt` came AFTER the run. It used two additions that are not committed yet: the `index` phase of `scripts/seal_1b_measure.py` and the rewritten `scripts/seal_1b_summarise.py`. The `index` phase only adds code. The record, record-synthetic, verify, sizes and replay phases are byte-for-byte a46cd3f's.

## Targets

These are built with today's page builder: `peakToBackendSpec` and `_bgWindowIndices`, extracted verbatim from `templates/index.html`. The builder was rerun at a46cd3f on 2026-10-14 with the two commands below. Both outputs came back byte-identical, with the same sha256 as listed under Files.

```
/Users/skyefortier/xps-app/venv/bin/python scripts/seal_1b_tabs.py tabs.json        # 121 tabs with peaks from 7 projects
node scripts/optimizer_disagreement_targets.js tabs.json > targets.json              # 202 targets (own 107, batch 95)
```

## Commands (`run.sh`, verbatim apart from the scratch path, written here as `$V`)

`$V` = `/private/tmp/claude-501/-Users-skyefortier-xps-app/892cab71-a3bf-4f7b-8318-f3125bb6ba72/scratchpad/seal1b/v2`. The commands ran from `/Users/skyefortier/xps-app/.claude/worktrees/seal-1b` with `SEAL_1B_TARGETS=$V/targets.json` and `PY=/Users/skyefortier/xps-app/venv/bin/python`.

```
echo "commit $(git rev-parse --short HEAD) dirty=$(git status --porcelain | wc -l)" > $V/run.log
$PY scripts/seal_1b_measure.py record $V/records.jsonl
$PY scripts/seal_1b_measure.py record-synthetic $V/records.jsonl
$PY scripts/seal_1b_measure.py verify $V/records.jsonl $V/verify_fresh_1.jsonl
$PY scripts/seal_1b_measure.py verify $V/records.jsonl $V/verify_fresh_2.jsonl
$PY scripts/seal_1b_measure.py verify $V/records.jsonl $V/verify_shake.jsonl --shake
/Users/skyefortier/xps-app/venv/bin/gunicorn "app:create_app(upload_folder='$V/gu-uploads')" -w 4 -b 127.0.0.1:5153 --timeout 300 &
sleep 8
$PY scripts/seal_1b_measure.py verify $V/records.jsonl $V/verify_gunicorn.jsonl --url http://127.0.0.1:5153
kill $GPID
$PY scripts/seal_1b_measure.py sizes $V/records.jsonl $V/sizes.jsonl
node scripts/seal_1b_background_twin.js $V/records.jsonl > $V/background_twin.jsonl
$PY scripts/seal_1b_measure.py replay $V/records.jsonl $V/replay.jsonl
```

Each verify, the replay and both record phases ran in its own Python process. The client PIDs recorded in the verify files are 62043 (fresh 1), 62218 (fresh 2), 62274 (shake) and 62510 (the HTTP client of the gunicorn run).

In the gunicorn setting the verification ran in the server's workers, not in the client. `gunicorn.log` shows master 62440 and four workers: 62442, 62445, 62446 and 62447. Nothing records which worker answered which request.

`run.log` holds only the commit line, three RuntimeWarnings from lmfit and uncertainties (`invalid value encountered in sqrt`, from σ computed on a singular covariance) and `DONE`.

After the run (not part of `run.sh`), each file was produced by:

```
$PY scripts/seal_1b_measure.py index $V/records.jsonl docs/findings/seal-1b/v2/records_index.jsonl $V/targets.json
$PY scripts/seal_1b_summarise.py docs/findings/seal-1b/v2 > docs/findings/seal-1b/v2/summary.txt
```

## Files (sha256)

`targets.json` and `tabs.json` (about 2 MB each, spectra from the committed projects) are NOT committed either: the two commands above regenerate them at a46cd3f with the sha256 below, which is how they were checked.

The verbatim records are NOT committed: `records.jsonl` has 328 lines and 18,180,441 bytes, sha256 `f06931f41d98f57fe40600fd8013395bb02175b8b56d43f06a453cd1e6dc67f1`. Each line of `records_index.jsonl` carries `line_sha256`, the sha256 of that record's line without its newline, plus the sha256 of R and of O as `json.dumps` gives them. Those are the bytes that `sizes.jsonl` measures.

| file | sha256 |
|---|---|
| targets.json | `2fb09e3d1f4d2ecf73aee8fb3773e35b643178378a24ba2fe35d51c190f96cea` |
| tabs.json | `1b1ae9f9167c6810647977d602ec071279d65fc371e1f489a27aeca9480f0e38` |
| run.sh | `b1c4bc16d5b7412a3b52fcfada7f2953712d01d16aff0c334c9b8af424948ed3` |
| run.log.head | `bd61cb57878d87a91917c39238f94da626876d04da7c3135e0b976fc563907a6` |
| gunicorn.log | `3483c0afa49eb8e321645e97c742bbaa9ed73de131dd4f102fcea17fb0326c46` |
| records_index.jsonl | `32d9846b42ff257366c20f1f4d69ba8b10cb438f57879a259319cbeeafd1c9ec` |
| verify_fresh_1.jsonl | `01bb743c7dce7719aeddf407b8d03b0b3616538c5a2c6bd4928772b46a48d3d7` |
| verify_fresh_2.jsonl | `dab791c0950ee86c2773b358762be95bc3788fd71450e15f98ec99170bf60bb8` |
| verify_shake.jsonl | `71a806ac325f49eadf514c7b1d6d2521fc93c00f3bc1e02a33133135ac0ddd2c` |
| verify_gunicorn.jsonl | `2ecfbc0c466cfb67f58c111ca5d6f9bab0f94c72ca315d1b7f125fa71f20411a` |
| sizes.jsonl | `289d8d38ac44e43903b5ca7ec2cadda3ab37fed0bb36aea94601fee8e8e9b7d5` |
| background_twin.jsonl | `4ebf5b328327ced46e87d2e3d1234f1cdab71861965a49f267e4288b429afa10` |
| replay.jsonl | `e89b3b6a983ed3d3bb16ad4157c35bbf4106a56eba92dfccc4bd3333691c91cb` |
| summary.txt | `96e0728c30a3587eeb86be99fe5fd8c3be9efd2225f47c3f269a0af61e6dd4a9` |
