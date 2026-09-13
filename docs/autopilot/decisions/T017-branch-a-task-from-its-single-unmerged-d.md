# T017 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T017-branch-a-task-from-its-single-unmerged-d.md` (commit
`d41471f`), its twelve criteria, and the lane's reproduction of T007's evidence E1 plus a second
symptom: inside a finished dependency's worktree, a dependent task already looks pending and would
branch from a mainline that lacks the dependency's work.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| Q1 | "Merged" means ✅ on the local or remote mainline | mainline · current checkout | **mainline** | The same answer in every checkout; it removes the wrong base inside a lane's worktree. |
| Q2 | `done-branch` with a live claim | `done-branch` wins · `claimed` wins | **`done-branch`** | The work is finished; the orchestrator must not dispatch it again. |
| Q3 | Two or more unmerged dependencies | `blocked` with `blocked_by` · new state | **`blocked`** | The reference behaviour makes such a task ineligible; reusing `blocked` means existing refusals apply and no consumer learns a new state. |
| Q4 | `base.commit` | fork point · tip of `onto` at claim time | **fork point** (`merge-base`) | Stays correct for `rebase --onto` even if `onto` moves before the claim. |
| Q5 | Stacked branch in `review` | rebase onto the dependency, PR targets the mainline · PR against the dependency · refuse publishing | **rebase onto the dependency; PR targets the mainline** | Branches are handed off dependencies first; after the dependency merges, follow-through rebases the dependent onto the mainline (T031). |
| Q6 | Claims read by older CLIs | accept, tolerant loader from now on · separate file | **accept; the loader ignores unknown keys** | No released consumer relies on the old format beyond 0.1.0's own claims, which stay local; tolerance prevents the same problem next time. |
| 7 | Scope | keep 5 points · split | **keep** | Coherent change; points order work, they do not budget it. |

Plan approved. The lane must remove its scratch repositories under `/tmp` when it no longer needs them.
