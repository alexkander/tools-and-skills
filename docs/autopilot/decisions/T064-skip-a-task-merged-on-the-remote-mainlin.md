# T064 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## escalated to the human

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Who decides changes to `DESIGN.md` and `CLAUDE.md` proposed by autopilot lanes | the human per text · the orchestrator · remove them from `governing` | **the orchestrator decides them and the human reviews them in the pull request; both files were removed from `governing` (T060)** | The human's instruction during run 20260914-1, made permanent by T060. |
| 2 | Launch the follow-ups T064 and T065 | — | **run 20260915-1 with T064 and T065** | The human's instruction ("lanza T063, T064 y T065"; T063 was already finished and in review). |

Answered by the human (repository owner), in the orchestrator session.

## diagnose gate

Reviewed: the diagnosis in `docs/bugs/T064-skip-a-task-merged-on-the-remote-mainlin.md` (commit
`7a90c44`) with its scripted reproduction (after a merge into `origin/main` that was not pulled,
`status` reads the task `done-merged` or `discarded` while `autopilot next --run` dispatches it again;
the same for a task closed from another clone), and on `origin/main` (`33f3531`) `next_lanes`, which
takes candidates from `query.eligible` and never consults `done_on_mainline`, and `_on_mainline`,
which has no reopen rule across the two mainline refs. The root cause is located. No code changed, so
no checks were re-run.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Diagnosis and fix 1–4, reported in `skipped` | skip with a reason · drop silently | **as recommended (skip with a reason)** | Plain `next` still offers the task, so the reason tells the orchestrator its local mainline is behind. |
| 2 | Reopen rule in `_on_mainline` | include · accept the gap · follow-up | **as recommended (include)** | Without it the new skip would hide a task reopened locally and not yet pushed, which `next` offers correctly today. |
| 3 | Plain `next`, `show` and `claim` | record only · follow-up bug | **as recommended (record only)** | They read the checkout by design (§7), and a workspace started from `base.onto` refuses the claim. |
| 4 | DESIGN.md (a)–(c) and the CHANGELOG bullet | approve as written · change | **approve as written** | Decided under the human's delegation of DESIGN.md decisions. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T064 owns the candidate loop and cache warm-up in `dispatch.py` `next_lanes`, `_on_mainline` in `status.py`, and two tests in `tests/test_autopilot_next.py`. T065 owns `WITH_BRANCH`, `_handoff` and `_closed_time` in `status.py`, `MOVED_ON`, `cmd_lane`'s `handed-off` check, `cmd_review`, and T062's two assertions in `tests/test_autopilot_next.py`. T063 (in review) edits only skill text and the lane brief.** | Built from the plans reached so far; a conflict between the two test edits in one file keeps both. |
| 2 | CHANGELOG, TODO.md, index READMEs, same-line DESIGN rows | resolve at hand-off · serialize | **resolve at hand-off, keeping every phrase** | Known conflict classes 1–2. |
