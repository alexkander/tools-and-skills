# T036 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T036-mirror-branch-records-to-a-remote-ref.md` (commit
`9870d48`), its eleven acceptance criteria, the reproduction (a second clone resolves a renamed
task to its template branch and blocks its dependent on the mainline), the git behaviour probes,
and a separate defect found on the way: `claims._delete_remote` leases without an expected commit,
so `release --force` — and therefore `done` — fails with exit 2 whenever `claim_remote` is set.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| D1 | Setting | new `[git].branch_record_remote`, off · reuse `claim_remote` · boolean requiring `claim_remote` | **new key, off by default** | Records outlive claims and add one ref per task; a repository that enabled remote claims must not start publishing more refs after an upgrade without choosing to. |
| D2 | Ref name and content | one parentless ref per task · one shared ref | **`refs/taskrail/branches/<ID>` with `branch.json` (`id`, `branch`, `recorded`)** | Independent leases per task, the same shape as remote claims; nothing private. |
| D3 | Reading and fetching | `--fetch` on `show`/`list`/`next` plus automatic fetch in `claim`, `branch`, `new --workspace`, `review` · `show` only · none · separate command | **as recommended, and update core skill step 3** | Read-only commands stay offline by default, and the skill fetches before choosing a base, where a second clone would otherwise pick the wrong one. |
| D4 | Disagreement | later `recorded` wins, written locally · remote wins · local wins | **later `recorded` wins** | Neither side silently undoes the other; clock drift is repaired by running `branch` again. |
| D5 | Failures | warn, report `record_remote`, exit unchanged · exit 4 on a rejected lease | **warn and report** | Local state stays correct and `branch` is the retry; a rejected lease is reported in the JSON for anyone who needs to act. |
| D6 | Cleanup | none, documented · follow-up | **none, documented; no follow-up now** | Refs are tiny; pruning merged tasks belongs with merge follow-through if it is ever needed. |
| D7 | Remote-claim lease bug | follow-up task · fix inside T036 | **follow-up bug task, opened at implement with `taskrail new`** | It breaks `done` for every repository with `claim_remote` today, independent of branch records; a separate pull request can be merged first. T036 must not depend on its fix. |
| D8 | `new --local-only` | no · add | **no** | A failed push only warns there. |

Plan approved. The lane must push only to local bare remotes and remove its scratch repositories
under a temporary directory when it no longer needs them.
