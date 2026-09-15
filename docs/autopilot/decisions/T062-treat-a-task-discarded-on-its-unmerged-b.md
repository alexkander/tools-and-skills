# T062 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## escalated to the human

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Who decides changes to `DESIGN.md` and `CLAUDE.md` proposed by autopilot lanes | the human per text · the orchestrator · remove them from `governing` | **the orchestrator decides them and the human reviews them in the pull request; both files were removed from `governing` (T060)** | The human's instruction during run 20260914-1, made permanent by T060. |
| 2 | Continue the autopilot with the follow-up tasks | — | **run 20260914-2 with T059, T061, T062 and T063, each dispatched once its row reaches `main`** | The human's instruction. |

Answered by the human (repository owner), in the orchestrator session.

## diagnose gate

Reviewed: the diagnosis in `docs/bugs/T062-treat-a-task-discarded-on-its-unmerged-b.md` (commit
`cc9fe4a`) with its scripted reproduction (a `❌` committed on T001's branch leaves `status` at
`pending`, `next` dispatching it again and `claim` succeeding, both before and after a merge that was
not pulled), and on `origin/main` (`4420c8d`) `stack._find`, which keeps a branch tip only when the
row is `✅`. The root cause is located. No code changed, so no checks were re-run.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Diagnosis and fix points 1–8 with a new `discarded-branch` state | approve · read as plain `discarded` | **as recommended (approve)** | Keeps visible that a branch still has to be merged, mirroring `done-branch`. |
| 2 | `claim` refuses `discarded-branch` with exit 5 | yes · no | **as recommended (yes)** | The claim is the lock, and the reproduction claimed the task. |
| 3 | `edit` refuses it without `--force` | yes · no | **as recommended (yes)** | Same rule as `done-branch`. |
| 4 | `❌` on either mainline ref reads `discarded` in `autopilot status` | yes · follow-up | **as recommended (yes)** | Otherwise the gap only moves to after the merge. |
| 5 | `_closing` also matches an uncommitted `❌` | yes · `✅` only | **as recommended (yes)** | T054's window, for `discard`. |
| 6 | Hand-off of a discarded branch | keep out and open a follow-up · include | **as recommended (follow-up)**: feature, E02, "Hand off a branch whose task was discarded on it", depending on T053, verified by pytest, opened at the impact stage with `taskrail new` on this branch | Queuing it needs T053's `_handoff`/`_done_time` and code near T059's. |
| 7 | DESIGN.md text a–h | approve as written · drop parts | **approve as written** | Decided under the human's delegation of DESIGN.md decisions; each replacement is one phrase, kept at hand-off beside other lanes' phrases in the same rows. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T062 owns `stack._find` and `discarded_on_branch`, `query.STATES` and `state`, the `discarded-branch` refusals in `cli.py` `cmd_claim` (after the `done_on_branch` refusal) and `cmd_edit`, `status.py` `STATES`, `task_state`, `done_on_mainline`/`discarded_on_mainline` and `_closing`, and tests in `tests/test_autopilot_next.py` and `tests/test_stacked_base.py`. T059 owns `escalation.py`, `approve.py`, `_escalation_text` and `_lane_details`/`_flag_escalations`; T061 `config.py` `read_first` and new fields in `cmd_status`/`_status_text`; unmerged T053 `_handoff`/`_done_time`, T051 `status()`, T048 `cmd_claim`'s `--run` check and `dispatch.py`, T047 `cmd_claim`'s lane line.** | Built from the plans reached so far. |
| 2 | Installed skill copies, `installed.json`, CHANGELOG, TODO.md, index READMEs, same-line DESIGN rows | resolve at hand-off · serialize | **resolve at hand-off, keeping every phrase** | Known conflict classes 1–3. |
