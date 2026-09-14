# T055 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## escalated to the human

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Who decides changes to the governing documents (`DESIGN.md`, `CLAUDE.md`) proposed by this run's lanes | the human per text · the orchestrator for this run · remove them from `governing` | **the orchestrator decides every `DESIGN.md` and `CLAUDE.md` change in this run; the human reviews them in the pull request. Also open a separate task removing both files from `[autopilot].governing` (T060)** | The human delegated the decisions to keep the lanes moving, and chose to make the change permanent. |

Answered by the human (repository owner), in the orchestrator session.

## scope gate

Reviewed: the scope in `docs/chores/T055-fix-the-autopilot-skill-text-found-wrong.md` (commit
`946ce5f`) with the exact skill, lane-brief, DESIGN and CHANGELOG text, and the premises the lane
checked on `origin/main` (`1631ab8`): `OCCUPYING` excludes `done-branch` (F5), `ids.reserve` locks in
the common directory (F6), `dispatch_live` expires after the claim grace (F7), and `claims.create`
accepts a repeat claim by the same owner and branch (F2). This run's orchestrator already refills on
`done-branch` and was told the IDs premise at T049's implement gate. Nothing else is edited yet.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | DESIGN.md §12.3 first paragraph and lane-contract bullet, §12.7 resource sentence, §12.8 hand-off bullet | approve all · only §12.3 | **as recommended (approve all)** | §12.7 and §12.8 would otherwise contradict the new skill text. Decided by the orchestrator under the human's delegation; the edits avoid T056's §12.3 sentence and the §12.1 rows other lanes change. |
| 2 | Resource values after an early refill | skill rule · CLI keeps values until hand-off · refill at hand-off | **as recommended (skill rule)** | Fixes F5 without changing §12.7's release rule; a CLI change is not needed while no repository here configures resources. |
| 3 | Which installed copies the tests read | copies `init` installs · also this repository's copy | **as recommended (`init` copies)** | Keeps the tool's tests independent of this checkout, as T056 did. |
| 4 | When a `running` lane is restarted | once `silent` · as soon as the handle fails | **as recommended (once `silent`)** | Two sub-sessions must never write in one worktree. |
| 5 | Hand-off message body | always · only without a link | **as recommended (always)** | The finding was exactly a hand-off without title and body. |
| 6 | CHANGELOG entry | add · none | **as recommended (add)** | Consumers get changed skill text. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T055 owns `taskrail-autopilot` SKILL.md *Dispatch* steps 6–7 and the IDs paragraph, *Close and hand off* steps 1 and 4, *After a merge* step 2, the new *Resume a run* section, `references/lane-brief.md`, its five tests in `tests/test_autopilot_skill.py`, and the DESIGN §12.3 first paragraph and lane bullet, §12.7 resource sentence and §12.8 hand-off bullet. T049 owns *Escalate* condition 1 and gate-review *Close*; T048 the paragraph at the end of *Escalate*; T050 (merged) the `--gate close` sentence; T051 the *Supervise* `overlaps` bullet; T056 the OpenCode note and its §12.3 sentence; T052 (later) the Claude Code note.** | Built from the gates reached so far. |
| 2 | Installed skill copies, `installed.json`, CHANGELOG, TODO.md, index READMEs, adjacent new tests in `test_autopilot_skill.py` | resolve at hand-off · serialize | **resolve at hand-off, keeping every entry** | Known conflict classes 1–3; new test functions added at the same place are kept side by side, as at T049's rebase. |
