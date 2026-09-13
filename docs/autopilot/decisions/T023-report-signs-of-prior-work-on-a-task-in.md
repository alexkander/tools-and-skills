# T023 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T023-report-signs-of-prior-work-on-a-task-in.md` (commit `929e01b`), its ten criteria, and the prototype run against this repository's history.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Approve the plan? | approve · with changes | **approve** | Informational only, testable, measured against real history, and it keeps out of `task_dict` while other lanes edit it. |
| 2 | Subjects that only mention the ID elsewhere | exclude · report as `mention` | **exclude** | The prototype showed backlog commits opening a task would flag it as already worked on. |
| 3 | Report an existing task branch | include · rely on step 3 | **include** | The most direct signal, for one `for-each-ref`. |
| 4 | Opt-out for the history search | none now · flag · config key | **none now** | Measured in milliseconds here; add a switch only when a consumer needs one. |
| 5 | Skill step 2 also asks to check the description's premises | include · mechanical only | **include** | One clause, and it restores a check a consumer's pipelines already make. |

## Conflict handling agreed for all lanes

T021 and T022 both edit the config template in `install.py` (`[columns]` and `[review]`), T022 and T023 both edit adjacent steps of the core skill, and every lane adds a `## Unreleased` changelog line and a decisions index row. Each lane touches only its own section. When a later rebase conflicts there: keep both sides in sources, changelog and indexes, then regenerate `.claude/skills/` with `taskrail upgrade` instead of merging installed copies by hand.
