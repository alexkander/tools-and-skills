# T005 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T005-import-tasks-from-table-based-backlogs-w.md` (commit
`2bdcc2b`), its fifteen acceptance criteria, and the lane's evidence that `validate` today reports
only `epics-missing` for a table-based backlog and does not count its tasks. The orchestrator's
brief placed T005 in E05; the backlog has it in E02, and the lane rightly left the backlog as it is.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Command surface | dry run by default, `--write` replaces the configured file · always in place · `--output PATH` | **as recommended** | An agent iterates on the dry-run report before touching anything; `--write` refuses to overwrite a backlog that already has epics or tasks. |
| 2 | Mapping | flags · mapping file · config sections | **flags** | Iterable from the report; a status alias in config would contradict §3.3, where only ⬜✅❌ are stored. |
| 3 | `--column` direction | `CORE=HEADER` · `HEADER=CORE` | **`CORE=HEADER`** | Same direction as `[columns].aliases`. |
| 4 | Header names | rename mapped headers to the configured name · keep source headers | **rename** | The result validates under the repository's own configuration; keeping a header means configuring its alias first. |
| 5 | Epic grouping | nearest heading, default level, `--epic-level`, `--epic-name`, kept `E07` IDs · drop the extras | **all of it** | Real backlogs nest headings differently; the extras are small and tested. |
| 6 | Default status | none, a status column is required · `--default-status` | **none** | Guessing status silently marks work done or pending by accident. |
| 7 | Scope | 5 points, no follow-ups now · open follow-ups | **as recommended** | `--single-epic` and ID-less tables wait for a consumer that needs them. |

Plan approved. The lane uses invented data only and removes its scratch repositories when done.
