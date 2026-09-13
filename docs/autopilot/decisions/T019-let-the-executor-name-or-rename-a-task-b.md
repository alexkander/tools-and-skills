# T019 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T019-let-the-executor-name-or-rename-a-task-b.md` (commit
`5a5eda8`), its eleven acceptance criteria, and the lane's reproduction: with a custom branch
name `review` refuses, `done-branch` is never detected, the dependent stays blocked on the
mainline, and editing a title by hand silently changes the template branch name.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Where the chosen name is recorded | per-task file in the git common directory · git config on the branch · backlog column · claim only | **per-task file in the common directory** | Survives `done`, `release` and branch deletion; publishes nothing; a column would change every table and appear only after merge. |
| 2 | Command surface | `taskrail branch <ID> <NAME>` plus `new --workspace --branch` · `claim` records any differing branch | **`branch` plus `new --workspace --branch`; and `claim` freezes the template name** | Renaming stays explicit. But the hand-edited title case is a real break: when no record exists and the claimed branch equals the template name, `claim` records it, so a later title edit no longer moves the branch. When the claimed branch differs from the resolved name, `claim` records nothing and warns, naming `taskrail branch`. |
| 3 | Run `git branch -m` | when the old branch exists locally, record otherwise · record only | **as recommended** | The record and the real branch must not drift; git carries upstream and worktree HEAD. |
| 4 | Branch already pushed | exit 5 without `--force`, never touch the remote · rename and warn | **exit 5 without `--force`; never touch the remote** | Renaming a pushed branch leaves a stale remote branch and possibly an open pull request; with `--force`, the result names the remote branch left behind. |
| 5 | Move the worktree | no, `show` reports where it is checked out · `--move-worktree` | **no** | Moving breaks a session whose working directory is inside it. |
| 6 | Remote claim copy | re-push with a lease · leave it | **re-push with a lease** | Other machines read the remote copy's branch; a stale one misleads them. |
| 7 | Follow-up to mirror branch records to a remote ref | open · not now | **open** | Another clone cannot resolve a renamed branch; the claims' remote ref shows the pattern. Kind `feature`, epic E02, depends on T019, opened at the implement stage. |

Plan approved with the `claim` addition in 2. The lane must remove its scratch repositories under
a temporary directory when it no longer needs them.
