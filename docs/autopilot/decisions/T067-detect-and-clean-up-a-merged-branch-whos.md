# T067 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## escalated to the human

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Who decides changes to `DESIGN.md` and `CLAUDE.md` proposed by autopilot lanes | the human per text · the orchestrator · remove them from `governing` | **the orchestrator decides them and the human reviews them in the pull request; both files were removed from `governing` (T060)** | The human's instruction during run 20260914-1, made permanent by T060. |
| 2 | Launch T067 | — | **run 20260915-3 with T067** | The human's instruction ("lanza T067") after merging T066. |

Answered by the human (repository owner), in the orchestrator session.

## plan gate

Reviewed: the plan in `docs/features/T067-detect-and-clean-up-a-merged-branch-whos.md` (commit
`0091e27`), its eight acceptance criteria, and on `origin/main` (`01af8ee`) `merged.cmd_merged`, which
skips detection unless the head's row is `✅`, and `recorded_merges` feeding `done_on_mainline`
whatever status closed the task. The premise holds. No code changed, so no checks were re-run.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | DESIGN.md texts a–d | approve as written · change parts | **approve as written** | Decided under the human's delegation of DESIGN.md decisions. |
| 2 | Recorded discard merges feed `discarded_on_mainline` | yes · no | **as recommended (yes)** | Gives a proven discard merge the same protection against a hand-edited row that a done merge has. |
| 3 | Autopilot skill text | no change · name discarded branches in *After a merge* step 1 | **as recommended (no change)** | The step already runs `merged --cleanup` for any merged branch, and T065 made a discarded branch handed off like a done one. |
| 4 | Output key | `closed` · `discarded_at_head` | **as recommended (`closed`)** | Also describes a recorded merge with no branch left. |
| 5 | Which record decides | newest by `detected` · any `done` wins | **as recommended (newest)** | Unchanged for single or done-only records, and correct after a reopen. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T067 owns `_row_status`, `recorded_merges`, `cmd_merged` and `_text` in `merged.py`, `done_on_mainline` and `discarded_on_mainline` in `status.py`, its tests in `tests/test_autopilot_merged.py`, and the approved DESIGN.md text. No other lane is running.** | Single lane. |
| 2 | CHANGELOG, TODO.md, index READMEs | resolve at hand-off | **resolve at hand-off** | Known conflict classes 1–2. |
