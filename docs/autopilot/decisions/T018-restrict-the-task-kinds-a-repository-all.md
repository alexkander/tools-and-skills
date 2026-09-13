# T018 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T018-restrict-the-task-kinds-a-repository-all.md` (commit
`4168610`), its eight acceptance criteria, and the lane's evidence (152 tests passing, `validate`
clean).

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Approve the plan? | approve · approve with changes | **approve** | Criteria are testable and cover absence of the table, core, local and overridden kinds, stale names, config errors and both `new` paths; the scope keeps shared files in small hunks while T021 edits `config.py`. |
| 2 | Allowlist or denylist? | `allowed` · `disabled` · both | **`allowed`** | Both consumer projects state a closed set ("exactly three kinds"); an allowlist also keeps a core kind added in a later release excluded instead of appearing silently. |
| 3 | Closed tasks of a disallowed kind: error or warning? | error for every status · warning when closed | **error for every status** | Consistent with `task-kind-unknown`, which ignores status. A repository that restricts kinds reclassifies old rows or allows the kind; silently tolerating them would weaken the rule it asked for. |
| 4 | Key name | `allowed` · `enabled` | **`allowed`** | Matches the task title and reads as the rule it encodes. |
| 5 | Skip installing skills of disallowed kinds | out of scope with a follow-up · include in T018 | **out of scope, open a follow-up at the `docs` stage** | Installation is a separate concern with its own manifest rules; bundling it would widen a 2-point task. A repository allowing only three kinds should not see `taskrail-feature` offered to its agent, so the follow-up is worth recording. |
