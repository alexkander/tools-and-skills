# T059 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## escalated to the human

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Who decides changes to `DESIGN.md` and `CLAUDE.md` proposed by autopilot lanes | the human per text · the orchestrator · remove them from `governing` | **the orchestrator decides them and the human reviews them in the pull request; both files were removed from `governing` (T060)** | The human's instruction during run 20260914-1, made permanent by T060. |
| 2 | Continue the autopilot with the follow-up tasks | — | **run 20260914-2 with T059, T061, T062 and T063, each dispatched once its row reaches `main`** | The human's instruction. |

Answered by the human (repository owner), in the orchestrator session.

## plan gate

Reviewed: the plan in `docs/features/T059-record-an-approved-governing-edit-so-aut.md` (commit
`a0c0f17`), its eleven acceptance criteria, and on `origin/main` (`ff8e4e6`) `escalation.flags()`,
which adds `governing` whenever `governing_touched` is not empty before `done-branch`, with no way to
record an approval. The premise holds for any repository that lists governing paths, although this
one no longer does (T060), so the lane tests on the `pilot` fixture. No code changed, so no checks
were re-run.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Command shape | `autopilot approve-governing` in a new module · `lane --approve-governing` · `autopilot approve` | **as recommended (`approve-governing`)** | Keeps `cmd_lane`, which T048 edits, untouched, and names what is approved. |
| 2 | Blob ID source | worktree file, else branch tip, else `null` · branch tip only | **as recommended (worktree first)** | Approvals happen at gates, often before a commit; a later uncommitted change must flag. |
| 3 | Refusals | exit 5 for nothing to approve, exit 2 for an unknown path · exit 0 | **as recommended (refuse)** | An approval that recorded nothing must not look like success. |
| 4 | Closed runs (T048, unmerged) | do not refuse · follow-up · stack on T048 | **do not refuse, and say so in the artifact** | Harmless while closed runs are hidden; a follow-up for one refusal is not worth its cost now. |
| 5 | DESIGN.md (a)–(e) | approve as written · other wording · no change | **approve as written** | Decided by the orchestrator under the human's delegation; each is a phrase-level addition kept at hand-off. |
| 6 | Skill *Escalate* condition 1, the new *Escalate* sentence, gate-review *Close* bullet | approve as written · no change | **approve as written** | The orchestrator must know when to record an approval. T048 adds a paragraph at the end of *Escalate*; both are kept at hand-off. |
| 7 | Approve the plan | as written · changes | **approve as written** | Criteria cover recording, re-flagging on change, partial approvals and refusals. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T059 owns the new `autopilot/approve.py`, its import lines and `add("approve-governing", …)` block after `decision` in `commands.py` `register()`, `_escalation_text()`, `flags()`'s `approved` argument, `current_blobs()` and the `governing_approved` key in `status.py` `_lane_details()`/`_flag_escalations()`, `tests/test_autopilot_governing.py`, one test at the end of `tests/test_autopilot_skill.py`, and the approved DESIGN and skill text. T061 (planning) owns the new read-first configuration key and must leave governing matching to T059. Unmerged run 20260914-1 branches keep their areas (T048 `cmd_lane`/`cmd_close`/`runs.py`, T051 `status()`, T054 `task_state`, T055 other skill sections, T052 `taskrail checks`).** | Built from the plans reached so far. |
| 2 | Installed skill copies, `installed.json`, CHANGELOG, TODO.md, index READMEs, same-line DESIGN rows | resolve at hand-off · serialize | **resolve at hand-off, keeping every phrase** | Known conflict classes 1–3; row edits apply phrase by phrase as at T054's rebase. |
