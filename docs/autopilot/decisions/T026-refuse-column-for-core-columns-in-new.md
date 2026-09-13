# T026 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## diagnose gate

Reviewed: `docs/bugs/T026-refuse-column-for-core-columns-in-new.md` (commit `cc59c29`) with its
reproduction across all seven core columns, lower-case spellings, no aliases, a partial alias
and full aliases, and the root cause in `cmd_new`'s `--column` loop.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Confirm the diagnosis and proposed fix | confirm · rethink | **confirm** | Reproduced for every core column with real output; the root cause explains each outcome (overwritten flag, dropped `ID`/`✓`, misleading lower-case error, and a `--workspace` branch created for a different kind than the row records); suspects were ruled out with evidence. |
| 2 | Exit code for the refusal | 2 (usage) · 5 (refused) | **2** | Consistent with the existing refusal for aliased columns; 5 means a task is not pending or is blocked. |
| 3 | Presentation of the behaviour change | `fix`, not breaking, stated in the changelog · breaking `!` | **`fix`, not breaking, stated in the changelog bullet** | The overriding behaviour was never documented, it contradicted the flags, and the package is 0.x. |
| 4 | Update DESIGN.md §3.2 in the fix commit | yes · follow-up | **yes** | One sentence already documents the refusal; widening it keeps the design accurate in the same pull request. |
