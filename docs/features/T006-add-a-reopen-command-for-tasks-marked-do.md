# T006 — Add a reopen command for tasks marked done by mistake

Kind: feature · Epic: E02 · Status: plan

## Behaviour

`taskrail reopen <ID> --reason "<why>"` moves a task that is `✅` done (or `❌` discarded) back to
`⬜` pending. Today the only way back is typing the status emoji by hand, which the core skill
forbids, and which leaves no record of why a closed task came back.

The reason is required and is written into the task's own row: the `Description` cell gets
`Reopened YYYY-MM-DD: <reason>.` appended, separated from the existing text by a space. The
trace therefore travels with the row, lands in the same one-line diff as the status change,
and is visible to anyone reading the backlog or `taskrail show`. No new file, column or
configuration is introduced.

The command follows the existing write rules: one row changes, the edit is validated in memory
before anything is written, and `--json` returns the result. It needs no claim, since a closed
task has none, and it does not claim the task for the caller.

Tasks that depend on the reopened one and are already done or claimed may now rest on an
unfinished dependency. The command does not refuse for that; it lists them, in the text output
and as `dependents` in the JSON, so the caller can decide whether they need reopening too.

## Acceptance criteria

1. `reopen <ID> --reason R` on a done task sets its status cell to `⬜` and appends
   `Reopened <today>: R.` to its Description; the file diff is exactly that one row.
2. The same works on a discarded task.
3. On a pending task it exits 5 (refused) and writes nothing.
4. An unknown ID exits 3; a missing or blank `--reason` is a usage error (exit 2).
5. A reason containing `|` is escaped, and one containing a line break is refused, with
   nothing written.
6. A backlog whose task table has no Description column is refused with exit 2 and nothing
   written, since the reason would have nowhere to go.
7. An invalid backlog is refused with exit 1, as for every other write command.
8. The output lists done or claimed tasks that depend on the reopened one; `--json` returns
   `{"id", "status": "pending", "reason", "dependents": [...]}`.
9. After reopening, `taskrail show` reports the task as `pending` (or `blocked`) and it can be
   claimed again.

## Affected areas

- `tools/taskrail/src/taskrail/writer.py` — a function that rewrites the status and the
  Description cells of one row.
- `tools/taskrail/src/taskrail/cli.py` — the `reopen` subcommand and its handler.
- `tools/taskrail/tests/test_write.py` — tests for the criteria above.
- `tools/taskrail/DESIGN.md` (§7 command table and write rules) and `README.md` (Use block).
- `tools/taskrail/src/taskrail/skills/taskrail/SKILL.md` — mention `reopen`, and amend the
  close-step rule "a status cell that is `✅` on either side stays `✅`" so a rebase does not
  silently undo a reopen: when the other side's row carries a `Reopened` trace, keep that side.
  The installed copies under `.claude/skills/` are refreshed with `taskrail upgrade`.

## Out of scope

- A separate reopen log, history file or new column.
- Reopening dependents automatically.
- Handling reopen in the git merge driver; that belongs to T004, which should honour the same
  rule the skill states here.
- Reverting any code or artifact the mistaken closure produced.

## Open questions and risks

- **Where the trace goes.** Appending to Description is proposed because it needs no new
  structure. It lengthens the row, and repeated reopens accumulate text; the alternative is a
  per-backlog log file, which adds a concept the tool does not have yet.
- **Discarded tasks.** The task names only done tasks; including discarded ones costs nothing
  extra and covers the same mistake.
- **Rebase conflicts.** A reopen on one branch against an unchanged `✅` on another is a clean
  merge, but the skill's "`✅` wins" rule would override it whenever the row conflicts for
  another reason. The skill change above addresses that; until T004 lands it relies on the
  agent following it.
