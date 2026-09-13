# T022 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T022-use-each-mainline-s-own-remote-in-review.md` (commit `92e1e04`) and its eight acceptance criteria.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Approve the plan? | approve · with changes | **approve** | Criteria cover base, fetch, push, link and two backlogs on different remotes, with local bare remotes only; `config.py` stays untouched while T018 and T021 edit it. |
| 2 | Where to push the task branch | resolved remote · `[review].remote` | **resolved remote** | The consumer that motivated the task asked for push and link on the mainline's own remote; a same-repository compare link needs the branch there. |
| 3 | Tracking config wins over an explicit `[review].remote` | accept · per-backlog override now | **accept**, and state the behaviour change in the changelog line | It is the order the task itself specifies; git's tracking config is the more specific fact about a mainline. An override can follow if a repository needs it. |
| 4 | Core skill step 3: `git fetch <base.remote>` | yes · `--all` · unchanged | **yes** | A bare fetch only updates the current branch's upstream. |
| 5 | Follow-ups for `branch.<mainline>.merge` and fork push remotes | open now · note only | **note only** | No consumer needs them today. |

## Conflict handling agreed for all lanes

T021 and T022 both edit the config template in `install.py` (`[columns]` and `[review]`), T022 and T023 both edit adjacent steps of the core skill, and every lane adds a `## Unreleased` changelog line and a decisions index row. Each lane touches only its own section. When a later rebase conflicts there: keep both sides in sources, changelog and indexes, then regenerate `.claude/skills/` with `taskrail upgrade` instead of merging installed copies by hand.
