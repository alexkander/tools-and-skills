# T037 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## diagnose gate

Reviewed: the write-up `docs/bugs/T037-delete-remote-claims-with-a-lease-on-the.md` (commit
`a3a4e2a`), the reproductions (`release --force`, `done`, `discard` and `claim --takeover` all exit
2 with `claim_remote` set, and `done`/`discard` leave the row written with both claims in place),
the git lease probes on a ref outside `refs/heads`, and the table of every remote push and delete
path. The workspace was set up by cherry-picking the row from T036's branch, as instructed.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Claim record without `remote.commit` | read the ref and compare contents · refuse with a clear message · lease on whatever `ls-remote` returns | **refuse with a clear message** naming `--local-only` and the ref to delete by hand, in both `release` and `rename_branch` | Every version of taskrail records the commit, so only a damaged record lacks it; a content-comparing lookup adds code for that case, and leasing blindly could delete another clone's claim. |
| 2 | Order and exit code in `done`/`discard` | row first, catch the failure, keep the local claim, exit 2 naming the retry · leave as is · exit 0 with a warning | **row first; exit 2 saying the row was written and naming `taskrail release <ID> --force`** | Releasing first could free a task whose row write still fails; hiding a claim other clones still see is worse than a partial success, as T019 decided for a failed claim re-push. |
| 3 | Scope | `claims.py` `_delete_remote` and `rename_branch`, `cli.py` `_change_status`, tests in `test_claims.py` · wider | **approve** | Stays clear of T036's branch records and T030's autopilot files. |

Diagnosis approved with decision 1 changed to the smaller refusal. The lane must use local bare
remotes only and remove its scratch repositories when it no longer needs them.
