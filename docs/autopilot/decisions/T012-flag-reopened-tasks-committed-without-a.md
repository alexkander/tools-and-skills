# T012 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T012-flag-reopened-tasks-committed-without-a.md` (commit
`6efb7b8`), its eleven acceptance criteria, and the lane's measurements: this repository's backlog
history (31 commits) reads in about 40 ms with no reopens, and a synthetic 1,000-commit history
takes about 6 s to parse, hence the required text pre-filter.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Severity | warning `reopen-untraced` · error for reopens not yet on a mainline | **warning** | Pushed history cannot be reworded; an error would block every later commit and CI run. |
| 2 | History window | last 500 backlog-changing commits from `HEAD`, `--history-limit`, `--no-history` · `<mainline>..HEAD` · unbounded | **as recommended** | Sees reopens committed on the mainline and squashes that lost the trailer, with a bounded cost. |
| 3 | Discarded tasks reopened | include · done only | **include** | `reopen` accepts discarded tasks and writes the same trailer. |
| 4 | Uncommitted reopens | not reported · informational note | **not reported** | The pre-commit hook runs before the message exists and would warn on every correct `taskrail reopen`. |
| 5 | Follow-up for the generated GitHub workflow's shallow checkout | open a chore now · record only | **open it** (kind `chore`, epic E02, committed on this branch) | The check is inert in that workflow until it fetches full history, and the fix belongs in `install.py`, outside this task. |

Plan approved.
