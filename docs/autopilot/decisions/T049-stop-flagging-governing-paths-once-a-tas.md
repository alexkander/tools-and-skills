# T049 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T049-stop-flagging-governing-paths-once-a-tas.md` (commit
`eda4c82`), its seven acceptance criteria, and `flags()` in
`tools/taskrail/src/taskrail/autopilot/escalation.py` and `_escalation_text()` in
`autopilot/commands.py` on `origin/main` (`b184707`): `governing` is computed without looking at
the state, while `escalate_gate` needs `gate` or `escalated`, so the premise (finding F9) holds. No
code changed yet, so no checks were re-run.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | DESIGN.md §12.4 (`autopilot status` row) and §12.6 (*Governing paths*) text (governing) | approve as written · other wording · no change | **taken to the human; implement without editing DESIGN.md until answered** | DESIGN.md is a governing path; its changes reach the human. The code does not depend on the text, so the lane is not held. |
| 2 | What `status` reports at `done-branch` and `handed-off` | A: keep `governing_touched`, drop `governing` from `escalation` · B: empty both · C: drop only at `handed-off` | **as recommended (A)** | Keeps the evidence for the close review while ending the repeated flag F9 describes; C leaves F9 in the queue. |
| 3 | Change skill condition 1 and the gate review's *Close* section, then `taskrail upgrade` | yes · no | **as recommended (yes)** | Option A moves the post-gate governing edit to the close review, so the skill must say so. |
| 4 | Open a follow-up for recording a human's approval of a governing edit before `done-branch` | open · do not open · widen T049 | **as recommended (open)** | The task row narrows T049 to `done-branch`; the approval half needs its own design. It is verifiable by pytest. Create it with `taskrail new` in this worktree and commit it on this branch. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T049 owns `autopilot/escalation.py` `flags()`, `_escalation_text()` in `autopilot/commands.py`, its governing tests, condition 1 of the skill's *Escalate* section and the *Close* section of `references/gate-review.md`. T050 owns `_gate_problem` and the `--gate` help in `autopilot/commands.py`, its `--gate` tests and the skill's *Close and hand off* section. T053 owns the hand-off queue in `autopilot/status.py`. Each lane leaves the others' functions and sections alone; edits in different functions of one file are merged at hand-off.** | Built from the plans reached so far; extended as other lanes reach their first gate. |
| 2 | Installed skill copies, `installed.json`, CHANGELOG, TODO.md, index READMEs | resolve at hand-off by the known classes · serialize | **resolve at hand-off** | Known conflict classes 1–3. |
