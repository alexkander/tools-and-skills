# T032 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T032-add-autopilot-notify-and-the-escalation.md` (commit
`8fa369b`), its twelve acceptance criteria and D1–D9, against DESIGN.md §12.1, §12.4 and §12.6,
and the lane's evidence that `status` today reports only free-text gate reasons and has no
escalation flags.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| D1 | `governing` matching | path or glob matching the file or any parent folder, over `touched` · exact paths · prefixes · gitignore · pathspecs | **as recommended** | Covers `docs/adr` and `docs/**/*.md` alike, and counts uncommitted files, which pathspecs over commits would miss. |
| D2 | Knowing which gate a lane is at | structured `lane --gate <stage>`, checked against the kind's stages · parse `--reason` · infer | **`lane --gate`** | `escalate_gates` names `kind:stage`; free text cannot be matched reliably. |
| D3 | Message on stdin | CLI summary plus optional `--message`, no passthrough · summary only · caller text only | **as recommended** | Passing taskrail's own stdin through can hang an agent's shell call. |
| D4 | Running the command | shell in the repository root, 30 s timeout killing the process group, temp files for output, exit 0 with `sent: false` on failure; caller mistakes still fail · argv split · configurable timeout · distinct exit code | **as recommended** | The command is repository configuration, like `checks`; "never blocks" means a broken notifier never stops the orchestrator. |
| D5 | Events | the three T029 already accepts, `--task` required for lane events · more events | **as recommended** | Enough for escalation and lane completion; no enablement or valid backlog needed to notify. |
| D6 | Flag conflicts outside the known classes | no computed flag, reason recorded in §12.6 · predict with `merge-tree` · list a rebase in progress | **no computed flag** | Conflicts arise in the orchestrator's own rebase, where git names them; classing by path would mark a real edit in a backlog or changelog as known. T033 can reopen the question with evidence. |
| D7 | Automatic notification | only `autopilot notify` runs it · `lane` or `status` trigger it | **only `autopilot notify`** | `status` runs on every wake-up and would repeat notifications. |
| D8 | Flag shape in `status --json` | flat per-task fields · nested · top-level list | **flat** | Matches the rest of the task row. |
| D9 | Code layout | new `autopilot/escalation.py`, small `status.py` addition · inside `status.py` | **new module** | Keeps the overlap with T030's `status.py` edits small. |

Plan approved. Notify commands in tests and verification stay local scripts writing to temporary
files; the lane removes its scratch repositories when done.
