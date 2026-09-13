# T021 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T021-map-a-repository-s-column-names-onto-tas.md` (commit `121926c`) and its ten acceptance criteria.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Alias replaces the core name, or adds a second name? | replace · accept both | **replace** | The consumer's rules fix the header; accepting both would let tables drift and need a duplicate-column rule. |
| 2 | Direction of the mapping | core → header · header → core | **core → header** (`Pts = "Size"`) | Keys form a closed, checkable set. |
| 3 | `new --column Size=3` for an aliased core column | refuse · accept | **refuse, but the message must name the flag to use** (`--pts`) | Keeps one way to fill core columns; an agent following the repository's header name must be told how. |
| 4 | Scope for 2 points | keep · split | **keep** | The criteria are coherent; points are an ordering hint, not a budget. |

## Conflict handling agreed for all lanes

T021 and T022 both edit the config template in `install.py` (`[columns]` and `[review]`), T022 and T023 both edit adjacent steps of the core skill, and every lane adds a `## Unreleased` changelog line and a decisions index row. Each lane touches only its own section. When a later rebase conflicts there: keep both sides in sources, changelog and indexes, then regenerate `.claude/skills/` with `taskrail upgrade` instead of merging installed copies by hand.
