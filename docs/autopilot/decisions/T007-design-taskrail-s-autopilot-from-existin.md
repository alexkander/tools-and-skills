# T007 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane. The `decide` gate is escalated to the human: it
settles the autopilot's architecture.

## frame gate

Reviewed: the framed draft `docs/spikes/T007-design-taskrail-s-autopilot-from-existin.md` (commit
`06ee5d3`) — its question with nine points to settle, planned evidence and limits.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Scope: the nine points including the task breakdown | approve · design only | **approve** | T024 at 8 points cannot be picked up without a breakdown; T017, T019 and T020 are waiting on this decision. |
| 2 | Evidence on agent capabilities | docs and trivial runs · docs only | **docs first, plus trivial runs under constraints** | Resuming and notification are the least documented behaviours. Constraints: a handful of minimal runs, in a temporary directory outside the repository, never with flags that skip permission prompts; stop and report if a login or permission prompt appears. Runs spend the human's agent quota, so keep them minimal. |
| 3 | Where the design lives | the spike document, with a follow-up · edit `DESIGN.md` now | **the spike document, with a follow-up** | A spike decides; moving the design into `DESIGN.md` and the skills is implementation work. |
| 4 | This repository's squash merges #8–#11 as merge-detection data | yes, read-only · throwaway repositories only | **yes, read-only** | Real squash history is the case the detection must handle; reading git history changes nothing. |

State corrections for the lane: T005 was stopped before doing any work, to follow the agreed task
order (T005 runs last); its claim was released. T026 now runs in parallel and edits `cmd_new`'s
`--column` handling in `cli.py`.
