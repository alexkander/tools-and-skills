# T053 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## diagnose gate

Reviewed: the diagnosis in `docs/bugs/T053-order-the-autopilot-hand-off-queue-by-co.md` (commit
`c04f87d`) with its scripted reproduction (a rebase of `handoff.next` and a decision-record commit
each reorder the queue; a task done only on `<remote>/<branch>` sorts first), and `_handoff` in
`tools/taskrail/src/taskrail/autopilot/status.py` on `origin/main` (`b184707`), which sorts by
`%ct` of the local branch tip and returns 0 without a local branch. DESIGN §12.1 says "branch tip's
commit time" while §12.8 says "completion order". No code changed, so no checks were re-run.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Fix approach | author time of the done commit, local branch else remote · last commit's author time · store a completion time | **as recommended (done commit's author time)** | Survives rebases and later commits on the branch, keeps `status` read-only, and matches §12.8's "completion order". |
| 2 | DESIGN.md §12.1 `queue` phrase (governing) | approve as written · no change | **approve as written** | Decided by the orchestrator under the human's delegation below; otherwise the design keeps describing the bug. |
| 3 | Remote-only branch ordering in scope | in scope · separate bug | **as recommended (in scope)** | Same ref choice in the same helper. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T053 owns `_handoff` and a new helper in `autopilot/status.py`, its regression tests in `tests/test_autopilot.py`, and the `queue` phrase of the `autopilot status` row in DESIGN §12.1. T049 owns `escalation.py` `flags()`, `_escalation_text()` in `commands.py`, the escalation phrase of the same DESIGN row, §12.6 *Governing paths*, skill *Escalate* condition 1 and gate-review *Close*. T050 owns `_gate_problem` and `--gate` help in `commands.py`, the `autopilot lane` DESIGN row, §12.6 *Escalated gates*, and the skill's *Close and hand off*. Edits to one DESIGN table row by two lanes are combined at the later hand-off, keeping both.** | Built from the first gates of T049, T050 and T053. |
| 2 | Installed skill copies, `installed.json`, CHANGELOG, TODO.md, index READMEs | resolve at hand-off by the known classes · serialize | **resolve at hand-off** | Known conflict classes 1–3. |

## escalated to the human

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Who decides changes to the governing documents (`DESIGN.md`, `CLAUDE.md`) proposed by this run's lanes | the human per text · the orchestrator for this run · remove them from `governing` | **the orchestrator decides every `DESIGN.md` and `CLAUDE.md` change in this run; the human reviews them in the pull request. Also open a separate task removing both files from `[autopilot].governing`** | The human delegated the decisions to keep the lanes moving, and chose to make the change permanent. |

Answered by the human (repository owner), in the orchestrator session.


## fix gate

Reviewed: commit `6614fb6` (range `b2667f4..6614fb6`): `_done_time` replaces `tip_time` in
`autopilot/status.py` (author time of the newest first-parent commit off the mainline that turns
the row ✅, on the local branch else the remote one, falling back to the tip's author time); three
regression tests in `tests/test_autopilot.py`, shown failing on the unfixed code with
`(['T004', 'T003'], 'T004')`; the `queue` phrase of DESIGN §12.1 exactly as approved; one CHANGELOG
bullet. Re-ran `uv run --directory tools/taskrail pytest -q` in the lane's worktree: 831 passed.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Approve the fix | approve · make `stack._read_statuses` public | **approve, as recommended** | Covers the three scenarios of the diagnosis; renaming a private helper is a refactor outside the touch map. |
| 2 | Fallback without its own test | accept · add a test | **as recommended (accept)** | Reached only when history no longer holds the done transition, and it keeps the previous behaviour with author time. |
