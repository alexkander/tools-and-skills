# T031 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T031-detect-squash-merges-by-content-and-foll.md` (commit
`568db44`), its fifteen acceptance criteria and Q1–Q10, against DESIGN.md §6.1, §12.1, §12.4 and
§12.8, and the lane's probe: an unstarted branch passes both the ancestor and the merge-tree checks,
one streamed `git log -p | git patch-id` finds a squash the tree check misses, and
`--ancestry-path` with `--first-parent` names a merge commit. The orchestrator's own follow-through
so far has verified merges by content the same way (an empty diff between the squash and the
branch, or a no-op `merge-tree`), always on branches whose row is `✅`.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| Q1 | Branch an ID resolves to | live claim's branch, else `branches.task_branch` · `task_branch` only · `--branch` | **as recommended** | Follows a lane's actual branch while it runs and the recorded name after `done`. |
| Q2 | Local branch or remote copy | local when it exists, else remote, both SHAs reported · remote first · either | **as recommended** | Unpushed local commits must read as not merged, so cleanup never deletes work. |
| Q3 | `✅` at the head before any check | yes · no guard · `base.commit` guard | **yes** | Without it an unstarted branch reports merged, as the probe shows. |
| Q4 | What "marks done-merged" stores | `merged` evidence in the lane, state still derived · nothing · lane state | **as recommended** | Keeps §12.4's rule that `done-merged` is derived; the evidence survives a later hand edit of the row. |
| Q5 | With and without a run | `--run` optional, every run holding the task updated, standalone needs no enablement · require `--run` · `--run` adds the task | **as recommended** | Merge detection is useful outside the autopilot; exit 3 for an unknown run or one not holding the task. |
| Q6 | Stacked dependents | by `Depends On`, fork point from the claim, else merge-base with the dependency head, else the run's stored head; command run in the dependent's worktree · live claims only · name the branch | **as recommended** | Finished dependents waiting for hand-off are exactly the ones to rebase; computed before anything is removed, as §6.1 requires. |
| Q7 | Cleanup refusals | exit 5 for unproven merge, modified or untracked files, current directory or `--root` inside, checked out in the main worktree, locked; exit 4 for another owner's claim · `--force` | **as recommended, no `--force`** | Cleanup deletes; every doubt refuses. |
| Q8 | Branch record on cleanup | keep · remove | **keep** | §6.4 says a record outlives its branch; T034 already handles a stale branch after a reopen. |
| Q9 | patch-id cost | first-parent `M..mainline`, only after ancestor and tree miss, streamed newest first, stop at first match · cap | **as recommended** | A cap would miss old merges silently. |
| Q10 | Exit codes | 0 when the check ran, merged or not; 1, 2, 3, 4, 5 as listed · 5 when not merged | **as recommended** | "Not merged yet" is an answer, not a failure; `merged` in the JSON carries it. |

Plan approved. The lane must use throwaway repositories with local bare remotes only, never run
`--cleanup` against this repository, and remove its scratch directories when done.

## implement gate

Reviewed: commits `22104ab` (tests alone, before any code) and `b116932` (`autopilot/merged.py`,
the registration in `commands.py`, `recorded_merges` inside `status.done_on_mainline`, DESIGN.md,
README, CHANGELOG). Re-ran `uv run --directory tools/taskrail pytest -q` in the lane's worktree: 498
passed. The lane resumed after an API limit with an unrun test file, committed it, and showed all 29
tests failing before writing code. Six deliberate breakages — no `✅` guard, untracked files not
refusing cleanup, the claim's fork point ignored, the branch delete without its checked commit, no
recorded merges in `status`, and a patch-id check that never matches — each failed the tests that
cover them.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Approve, with `checks` as an object, `--owner`, `runs` listing only runs written, and the older-git `--ancestry-path` form | approve · list and no `--owner` | **approve** | `--owner` is what lets cleanup release the caller's own leftover claim and refuse another owner's; the rest is output shape and portability. |
| 2 | Run a lint check | no, none configured · add ruff in a chore | **no** | The repository configures no lint; adding one is its own decision, outside this task. |
| 3 | Update a rebased stacked dependent's claim `base` | follow-up only if the trial shows it matters · open now | **not now** | `touched` may over-report for that lane until its claim is released; T033's trial will show whether it misleads the orchestrator. |
