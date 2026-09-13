# T017 — Branch a task from its single unmerged dependency

Kind: feature · Epic: E05 · Status: planned

Source: the accepted autopilot design, `docs/spikes/T007-design-taskrail-s-autopilot-from-existin.md`
(evidence E1, *Session state*, *Recommendation*), and
`docs/research/autopilot-reference-behaviour.md` (*Eligibility and order*, *Session state*).

## Behaviour

Today a task's state and its dependencies are read only from the current checkout's backlog.
After a lane runs `taskrail done T001` and commits on T001's branch, the main checkout still
reports T001 as `pending`, `next` offers it again, and `done` has released the claim (E1,
reproduced on this branch's base, see *Evidence*). Its dependents stay `blocked` on the
mainline, and inside T001's worktree they branch from the mainline even though T001 is not there.

After this change:

- **Done on its branch.** A task is *done on its branch* when its row is `✅` at the tip of its
  task branch — the local branch or `<remote>/<branch>`, the branch name rendered from the kind's
  template as today — and `✅` on neither the local mainline nor `<remote>/<mainline>` of its
  backlog (`<remote>` resolved as in T022). The backlog files at those tips are read with one
  `git cat-file --batch`, as `ids.py` already does, and only for tasks whose branch exists.
- **New state `done-branch`.** A task that is `⬜` in the current checkout but done on its branch
  is reported as `done-branch` by `list`, `show` and `next`. `next` never offers it,
  `list --state done-branch` selects it, and `claim` refuses it with exit 5, naming the branch.
- **Dependencies.** A dependency that is done on its branch does not block, whether its row in
  the current checkout is `⬜` (the main checkout) or `✅` (a worktree stacked on it). Any other
  dependency blocks or not exactly as today.
  - **Exactly one** such dependency: the task is eligible, and its base is that dependency's
    branch.
  - **Two or more:** the task is `blocked`, `blocked_by` lists them, `next` does not offer it,
    `claim` refuses it, and its base has no `onto`.
- **The base** (`show`, `list --json`, `next --json`) gains two keys: `commit`, the commit `onto`
  names, and `dependency`, the ID the task is stacked on or `null`. For a stacked task, `onto` is
  the further-ahead of the dependency's local branch and `<remote>/<branch>` (the same rule as for
  mainlines, so the two copies can be `diverged`), and `reason` says the dependency is done on
  that branch but not merged into the mainline. The text form of `show` prints it as today.
- **`new --workspace --depends-on …`** creates the branch from that same base, and refuses with
  exit 5 — creating nothing and freeing the reserved ID — when two or more dependencies are done
  only on their branches.
- **`claim`** records the base in the claim: `base: {onto, commit, dependency}`, where `commit`
  is the fork point, `git merge-base HEAD <onto>`, so a later `git rebase --onto <mainline>
  <base.commit>` works after the dependency is squash-merged. It is `null` outside git or without
  a base. The remote copy of a claim carries it too: it holds only branch names and a commit.
- **`review`** on a stacked branch whose dependency is still unmerged reports that dependency's
  branch as `rebase.onto` and its ID as `rebase.dependency`; `needed` compares HEAD with it. The
  pull request `target` stays the mainline. Once the dependency is merged, `review` behaves as
  today with `rebase.dependency: null`.
- The core skill's workspace step stops asking which base to use for a dependency finished on an
  unmerged branch: `base.onto` already is that branch, and a null `onto` with a reason means stop.

## Acceptance criteria

Scenario for 1–5 and 9–10, as in E1: T001; T002 depends on T001; T003 independent; T004
depends on T001 and T003. T001 is claimed in its worktree, marked done there and committed.

1. On the main checkout, `show T001 --json` reports `state` `done-branch`, `next` does not list
   T001, `list --state done-branch --json` returns exactly T001, and `claim T001` exits 5 naming
   `T001-base-task`.
2. On the main checkout, T002 is `pending` with `blocked_by` `[]`, `next` lists it, and its
   `base` has `onto` `T001-base-task`, `dependency` `T001` and `commit` equal to that branch's
   tip.
3. With T003 also done on its own branch, T004 is `blocked` with `blocked_by` `["T001", "T003"]`,
   is not in `next`, its `base.onto` is `null` with a reason naming both, and `claim T004` exits 5.
4. Inside T001's worktree (T001 `✅` there, not on the mainline), `show T002` reports the same
   stacked base as criterion 2.
5. After T001's row is `✅` on the local mainline, or only on `<remote>/<mainline>`, T001 is no
   longer `done-branch`, and T002's base is the mainline base with `dependency` `null`.
6. With only `<remote>/T001-base-task` present, T002's `base.onto` is `origin/T001-base-task`;
   with both copies present and the remote one ahead, it is the remote one; with the two
   diverged, `base.diverged` is `true` and `onto` is `null`.
7. `new --workspace --depends-on T001` creates the new branch at T001's branch tip;
   `new --workspace --depends-on T001,T003`, with both done only on their branches, exits 5, leaves
   no branch or worktree, and the next `reserve-id` returns the same ID.
8. `claim T002` in a worktree branched from T001's branch writes `base` with `onto`
   `T001-base-task`, `dependency` `T001` and `commit` equal to the fork point, and keeps that
   commit after T001's branch gains a new commit; a claim on a task based on the mainline records
   the mainline base; a claim file written without `base` still loads.
9. `review T002 --json` on T002's branch, after `done T002`, reports `rebase.onto`
   `T001-base-task`, `rebase.dependency` `T001` and `target` `main`; `rebase.needed` is `false`
   until T001's branch gains a commit, then `true`.
10. `done T002` succeeds on the stacked branch while T001 is still unmerged.
11. Without task branches, and outside git, every existing test passes; the only change to their
    output is the two new `base` keys.
12. `DESIGN.md` §6.1 (the claim's `base`) and §7 (`show`'s base, the `done-branch` state, `next`,
    `review`'s `rebase.dependency`), `README.md` where it describes states or the base, the core
    skill's workspace and close steps, and `CHANGELOG.md` (one bullet) describe the behaviour; the
    installed skill copies match their sources after `taskrail upgrade`.

## Affected areas

- `tools/taskrail/src/taskrail/stack.py` (new) — finds the tasks done on their branch: one
  `for-each-ref`, then the backlog files at the task-branch and mainline tips through
  `gitutil.read_blobs`, parsed for `ID` and `✓` the way `ids.py` parses IDs. Computed once per
  loaded project and reused by every task in `list` and `next`.
- `tools/taskrail/src/taskrail/query.py` — `STATES`, `state`, `blocked_by`, `eligible` and
  `base_dict` (stacked base, `commit`, `dependency`).
- `tools/taskrail/src/taskrail/cli.py` — `_open_workspace` passes `--depends-on` into its probe
  task and uses the shared base; `cmd_claim` refuses `done-branch` and records the base;
  `cmd_review` picks the dependency branch.
- `tools/taskrail/src/taskrail/claims.py` — `Claim.base`; the loader ignores keys it does not know.
- `tools/taskrail/src/taskrail/skills/taskrail/SKILL.md`, then `taskrail upgrade` for the copies
  under `.claude/skills/`.
- `tools/taskrail/DESIGN.md` §6.1 and §7 only, `tools/taskrail/README.md`,
  `tools/taskrail/CHANGELOG.md`.
- `tools/taskrail/tests/test_stacked_base.py` (new), against local bare remotes; no network.

## Out of scope

- The autopilot's other states (`running`, `failed`, `gate`, `handed-off`, `done-merged`) and
  detecting a squash merge by content (E4); here "merged" means the row is `✅` on a mainline ref.
- Rebasing a stacked branch after its dependency is squash-merged; this task only records
  `base.commit` so that `rebase --onto` is possible.
- One lookup for a task's branch (T019): the branch stays rendered from the kind's template.
- Pull requests that target the dependency's branch, and fetching in `show`, `list` or `next`.
- Dependencies of dependencies: only direct dependencies count, and a stacked branch already
  contains whatever its dependency was stacked on.

## Open questions and risks

- **Q1 — What "merged" is judged against.** Recommended: `✅` on the local or remote mainline
  ref, so the answer is the same in every checkout. Alternative: the current checkout's row, as
  today — simpler, but inside a lane's worktree it gives a stacked dependent the mainline as
  base (see *Evidence*).
- **Q2 — `done-branch` against `claimed`.** A live claim on a task already done on its branch
  should not happen, since `done` releases it. Recommended: `done-branch` wins. Alternative:
  `claimed` wins.
- **Q3 — Two or more unmerged dependencies.** Recommended: state `blocked` with them in
  `blocked_by`, so `claim` and `done` refuse through the existing path. Alternative: a separate
  state or field, which every consumer would then need to learn.
- **Q4 — `base.commit`.** Recommended: the fork point, `merge-base HEAD <onto>`, which stays
  right when `onto` moves between branching and claiming. Alternative: the tip of `onto` at
  claim time.
- **Q5 — `review` on a stacked branch.** Recommended: `rebase.onto` is the dependency's branch
  and the pull request still targets the mainline. Alternatives: target the dependency's branch,
  or refuse `--publish` while the dependency is unmerged.
- **Risk — older CLIs and the shared claim directory.** A CLI without this change fails to load
  a claim that has `base` and treats the task as unclaimed in `show`, `next` and `claims`; its
  own `claim` still fails on the existing file. Lanes running an older branch's code next to a
  newer one hit this. Recommended: accept it and make the loader ignore unknown keys from now
  on. Alternative: keep the base in a sibling file next to the claim.
- **Risk — a renamed title.** The branch is rendered from the title, so after a title edit the
  lookup misses the branch and the task looks `pending` again; T019 replaces the lookup.
- **Risk — an abandoned branch** with a `✅` row keeps its task `done-branch` and keeps stacking
  dependents until it is deleted or the task is reopened there.
- **Cost.** `list` and `next` add one `for-each-ref` and up to two `cat-file --batch` runs per
  call, regardless of the number of tasks.

## Evidence

E1 reproduced in a scratch repository with this branch's base (`dd646f5`), using the E1 setup
from the T007 spike's *How to reproduce*:

```
$ taskrail next
T001   ⬜ pending   feature   2pt  E01   Base task
T003   ⬜ pending   bug       3pt  E01   Independent
$ taskrail claims
no claims
$ taskrail show T001 --json (state, claim, prior_work.branches)
pending None ['T001-base-task']
$ taskrail show T002 --json (state, blocked_by, base.onto)
blocked ['T001'] origin/main
$ (in T001's worktree) taskrail show T002 --json (state, blocked_by, base.onto)
pending [] origin/main
```
