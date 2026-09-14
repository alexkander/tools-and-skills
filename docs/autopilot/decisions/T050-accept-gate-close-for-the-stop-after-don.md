# T050 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T050-accept-gate-close-for-the-stop-after-don.md` (commit
`43df757`), its six acceptance criteria, the lane's reproduction of F10 (`--gate close` exits 2
with `` `close` is not a stage of kind feature (plan, implement, verify) ``), and
`_gate_problem` in `tools/taskrail/src/taskrail/autopilot/commands.py` on `origin/main`
(`b184707`). No code changed yet, so no checks were re-run.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | DESIGN.md §12.1 and §12.6 text (governing) | approve as written · leave DESIGN.md unchanged | **taken to the human; implement without editing DESIGN.md until answered** | DESIGN.md is a governing path; its changes reach the human. The code does not depend on the text, so the lane is not held. |
| 2 | Accept `close` when the task's kind is not defined | yes, check `close` before the kind lookup · keep exit 2 | **as recommended** | `close` does not depend on the kind's stages. |
| 3 | Require `done-branch` for `--gate close` | no · exit 5 unless `done-branch` | **as recommended (no)** | The gate review of the close already checks that `done` is committed; a state check would add a git read to `lane`. |
| 4 | Reserve `close` as a stage name | no · `validate` rejects it | **as recommended (no)** | Rejecting it would break any custom kind using the name, for no gain. |
| 5 | `<kind>:close` in `escalate_gates` | keep "moved-on tasks are not flagged" and document it · flag it | **as recommended (keep)** | §12.6 already says tasks past `done-branch` are not flagged; flagging would change `escalation.py` and `status.py`, which T049 owns in this run. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T050 owns `autopilot/commands.py` (`_gate_problem`, `--gate` help), its `--gate` tests in `tests/test_autopilot_notify.py`, and the *Close and hand off* section of the `taskrail-autopilot` skill source. T049 owns `autopilot/escalation.py` `flags()`, `_escalation_text()` in `autopilot/commands.py`, its governing tests, condition 1 of the skill's *Escalate* section and the *Close* section of `references/gate-review.md`. T053 owns the hand-off queue in `autopilot/status.py`. Each lane leaves the others' functions and sections alone; edits in different functions of one file are merged at hand-off.** | Built from the plans reached so far; extended as other lanes reach their first gate. |
| 2 | Installed skill copies, `installed.json`, CHANGELOG, TODO.md, index READMEs | resolve at hand-off by the known classes · serialize | **resolve at hand-off** | Known conflict classes 1–3. |
