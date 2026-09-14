# T054 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## escalated to the human

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Who decides changes to the governing documents (`DESIGN.md`, `CLAUDE.md`) proposed by this run's lanes | the human per text · the orchestrator for this run · remove them from `governing` | **the orchestrator decides every `DESIGN.md` and `CLAUDE.md` change in this run; the human reviews them in the pull request. Also open a separate task removing both files from `[autopilot].governing` (T060)** | The human delegated the decisions to keep the lanes moving, and chose to make the change permanent. |

Answered by the human (repository owner), in the orchestrator session.

## diagnose gate

Reviewed: the diagnosis in `docs/bugs/T054-keep-a-closing-lane-from-reading-as-pend.md` (commit
`0ea4163`) with its scripted reproduction (after `done` without a commit and an expired dispatch,
`status` reports `pending` and `autopilot next --run` dispatches T001 again), and `task_state` in
`tools/taskrail/src/taskrail/autopilot/status.py` on `origin/main`: after `done-branch` and the
recorded states it only checks the claim and the dispatch time, so the premise (F13) holds. No code
changed, so no checks were re-run.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Diagnosis and fix 1–4 | approve · `done` keeps the claim until the commit · a closing marker in the run file | **as recommended (approve)** | Derived from git like every other state, clears itself if the lane abandons the change, and changes `done` for nobody. |
| 2 | DESIGN.md §12.4 `running` bullet, §12.1 `autopilot status` order-of-states phrase and `autopilot next` skip phrase | approve as written · no change | **approve as written** | Decided by the orchestrator under the human's delegation. T049 and T053 already changed other phrases of the §12.1 `autopilot status` row; edit only your phrase, and the later hand-off keeps every edit. |
| 3 | Leave plain `taskrail next`, `show` and `claim` unchanged | leave · follow-up | **as recommended (leave)** | Outside the autopilot the window lasts seconds and no dispatcher reads it. |
| 4 | Skip every lane-occupying state in `next`, not only `running` | every state · only `running` | **as recommended (every state)** | Same check, also covers a stopped lane whose claim was released. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T054 owns `task_state` and the new `_closing` in `autopilot/status.py`, the candidate skip in `autopilot/dispatch.py`, its regression test in `tests/test_autopilot_next.py`, §12.4's `running` bullet and its phrases of the §12.1 `autopilot status` and `autopilot next` rows. T053 (closed) owns `_handoff`/`_done_time`; T049 and T050 (closed) the escalation and `--gate` code. T048 (planning) must leave `task_state` and the dispatch skip alone. T056 owns the OpenCode note and T060 the repository config.** | Built from the gates reached so far. |
| 2 | Installed skill copies, `installed.json`, CHANGELOG, TODO.md, index READMEs | resolve at hand-off by the known classes · serialize | **resolve at hand-off** | Known conflict classes 1–3. |

## fix gate

Reviewed: commit `3bf98a7` (range `8ed9e1c..3bf98a7`): `_closing` and the `task_state` change in
`autopilot/status.py`, the lane-occupying skip in `autopilot/dispatch.py`, the three approved
DESIGN.md phrases, one CHANGELOG bullet, and two tests in `tests/test_autopilot_next.py` shown
failing on the unfixed code (`('pending', None, [])` and a re-dispatched `gate` lane). Re-ran
`uv run --directory tools/taskrail pytest -q` in the lane's worktree: 830 passed.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Approve the fix | approve · changes | **approve** | Derived from git, clears itself, covers both the F13 window and an unclaimed stopped lane; the diff stays inside the touch map. |
| 2 | Follow-up for a task discarded on its unmerged branch | open a bug · record only | **as recommended (open)**, kind bug, epic E02, with `taskrail new` in this worktree, committed on this branch | A committed `❌` on a branch reads as `pending` and can be dispatched again; a pytest can script it. |
