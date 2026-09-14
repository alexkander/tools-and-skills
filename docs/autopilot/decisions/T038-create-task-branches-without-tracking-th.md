# T038 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

The orchestrator opened this task with `taskrail new --workspace` after noticing that every lane's
branch, and that workspace's own branch, tracked `origin/main`; it committed the row and unset the
upstream before starting the lane.

## scope gate

Reviewed: the scope in `docs/chores/T038-create-task-branches-without-tracking-th.md` (commit
`a52a4cc`), and the evidence: under `push.default=upstream` a plain `git push` from a task branch
created from `origin/main` landed the task's commit on `main`; `--no-track` leaves no upstream even
with `branch.autoSetupMerge=always`; `new --workspace` sets `branch.<task>.merge refs/heads/main`.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Apply `--no-track` to every base | unconditionally, CLI and skill · only for remote-tracking bases | **unconditionally** | A stacked base is a dependency's pull request branch, and `autoSetupMerge=always` tracks local start points too. |
| 2 | `review --publish` keeps `--set-upstream` | keep · drop | **keep** | The upstream then is the task's own remote branch, which is what a plain push or pull should reach. |
| 3 | Two clauses in DESIGN.md | add · leave | **add** | The design states the rule the CLI and skill follow. |
| 4 | Existing branches that track the mainline | no migration, mention the fix in the CHANGELOG · follow-up check | **no migration; the CHANGELOG bullet names `git branch --unset-upstream`** | Few branches are affected and the fix is one command; a detector is not worth its code. |

Change set approved.
