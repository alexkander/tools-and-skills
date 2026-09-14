# T060 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in a lane beside
autopilot run 20260914-1. T060 is not a member of that run: the human added it as a priority during
the run. Each decision is recorded before it is given to the lane.

## escalated to the human

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Who decides changes to `DESIGN.md` and `CLAUDE.md` proposed by autopilot lanes | the human per text · the orchestrator for this run · remove them from `governing` | **the orchestrator decides them, the human reviews them in the pull request; make it permanent by removing both files from `[autopilot].governing` (this task), worked as a priority** | The human's instruction in the orchestrator session. |

Answered by the human (repository owner), in the orchestrator session.

## scope gate

Reviewed: the scope in `docs/chores/T060-remove-design-md-and-claude-md-from-the.md` (commit
`a62d6e8`), the T060 row commit `e16adb0`, `.taskrail/config.toml` on `origin/main`, and line 34 of
the `taskrail-autopilot` skill, which reads "the governing documents" only from the key. Nothing else
is edited yet.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Where the "read first" role is kept | `CLAUDE.md` bullet plus config comment · comment only · `CLAUDE.md` only · new taskrail key | **as recommended (`CLAUDE.md` *Backlog* bullet plus the comment on the empty key)** | Every agent reads `CLAUDE.md`; the comment explains the empty key. A new key is a follow-up. |
| 2 | How the change is checked | `.taskrail/tests/test_config.py` · root `tests/` · test under `tools/taskrail` · extend `[checks].test` · no new test | **no new test: verify with `taskrail validate` and `taskrail autopilot status --json` loading the empty key, and record their output in the artifact; edit T060's description to say so, with `taskrail edit`** | A test that no configured check runs would not be run; a test directory under `.taskrail/` adds a convention nobody else uses; the others were rejected in the scope for good reasons. The change is one configuration value and one paragraph, which the pull request shows. Also drop change 3 (a *Commands* line for that test). |
| 3 | Open a follow-up separating "read first" documents from escalating paths | open · do not open | **as recommended (open)**, feature in E02, with `taskrail new` in this worktree, committed on this branch | The general fix belongs in taskrail itself and is verifiable by pytest; the other lanes are editing that code now. |
