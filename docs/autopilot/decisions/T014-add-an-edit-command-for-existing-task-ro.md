# T014 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T014-add-an-edit-command-for-existing-task-ro.md` (commit
`300ccb3`), its fifteen acceptance criteria, refusals and branch-record handling.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Moving a task to another epic | leave out, no follow-up · `--epic` now · follow-up | **leave out, no follow-up now** | A move rewrites two tables, possibly two files, and conflicts easily; no one has asked for it yet. |
| 2 | Closed and `done-branch` tasks | exit 5, `--force` overrides · allow all · allow text fields only | **as recommended** | A closed row is history other branches rely on; `--force` covers a deliberate correction. |
| 3 | Claim | not required, exit 4 on someone else's claim, `--force` overrides · require the caller's claim | **as recommended** | Matches `discard`; fixing a dependency on a pending task should not need a claim. |
| 4 | `--kind` | editable and validated · excluded | **editable** | A wrong kind is the same kind of mistake as a wrong dependency, and validation catches disallowed kinds. |
| 5 | `--allow-invalid` | run on an invalid backlog, write only an error-free result · plain refusal | **as recommended** | Lets `edit` repair a cycle a merge left behind without writing another invalid state. |
| 6 | Title change that alters the template branch name | record the old name when that local branch exists, mirrored like `claim`, `--local-only` skips · warn only | **as recommended** | A task already being worked must not lose its branch because its title changed. |
| 7 | Dependencies | `--depends-on` replaces the list, `""` clears · add and remove flags | **replace** | Same shape as `new --depends-on`; `show` gives the current list to build from. |
| 8 | Hand edits in the core skill | point to `taskrail edit` only · keep hand edits with `validate` as fallback | **point to `edit`** | The CLI owns the table format; conflict resolution keeps its own rule in step 8. |

Plan approved.
