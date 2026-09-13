# T036 — Mirror branch records to a remote ref

Kind: feature · Epic: E02 · Status: plan

Source: the T019 decision record (`docs/autopilot/decisions/T019-let-the-executor-name-or-rename-a-task-b.md`,
decision 7) and `tools/taskrail/DESIGN.md` §6.2 (remote claims) and §6.4 (task branches) as of T019.

## Problem

T019 records a task's chosen branch in `<git common dir>/taskrail/branches/<ID>.json`. Every
worktree of a clone sees it; another clone does not, so it resolves a renamed task to its
template name. Reproduced on this branch's base with two clones of one bare remote and
`claim_remote = "origin"`: clone A claims T001, renames it to `feature/base`, marks it done and
pushes the branch; A reports T001 `done-branch` on `feature/base` and its dependent T002 pending on
`origin/feature/base`, while a fresh clone B reports T001 `pending` on `T001-base-task`
(`branch_source: template`) and T002 `blocked` by T001 on `origin/main` (see *Evidence*).

## Behaviour

- **Opt-in setting.** `[git].branch_record_remote = ""` (default: off). When it names a remote,
  branch records are mirrored there. It is independent of `claim_remote`: records outlive claims,
  so enabling it leaves one small ref per recorded task on the remote, a cost a repository that
  mirrors claims should choose separately. Both usually name the same remote.
- **Remote ref.** Each record is pushed as `refs/taskrail/branches/<ID>`: a parentless commit whose
  tree holds only `branch.json` with the local record's `id`, `branch` and `recorded`, committed as
  `taskrail <taskrail@localhost>` with the message `taskrail branch <ID>` — the same plumbing as a
  remote claim, generalized in `gitutil`. A record never held an owner, host or path, so nothing
  is removed from it before pushing.
- **Local copy of the remote.** Remote records are fetched into
  `refs/taskrail/remotes/<remote>/branches/<ID>` with one
  `git fetch --prune --no-tags <remote> +refs/taskrail/branches/*:refs/taskrail/remotes/<remote>/branches/*`.
  Those refs sit outside `refs/heads` and `refs/remotes`, so branch listings, `done-branch`
  detection and prior work never see them.
- **When records are pushed.** Whenever a command writes a record and the setting is on:
  `taskrail branch <ID> <NAME>` (also when `NAME` is already the task's branch, which makes it the
  way to retry a failed push), `claim` when it freezes the template name, and
  `new --workspace --branch`. `--local-only` on `claim` and `branch` skips the record's fetch and
  push, as it already skips the claim's remote copy. The push carries
  `--force-with-lease=refs/taskrail/branches/<ID>:<expected>`, `<expected>` being the local copy's
  commit, or empty when this clone knows of none; on success the local copy is moved to the pushed
  commit.
- **When records are read.** The resolver keeps reading only the local record files, so `show`,
  `list` and `next` stay offline by default and cost nothing more. Remote records reach those files
  by a fetch, which happens:
  - on demand with a new `--fetch` flag on `show`, `list` and `next` (a no-op when the setting is
    off), and the core skill's step 3 reads `show <ID> --json --fetch` after its `git fetch`, so an
    executor branches from the right base;
  - automatically at the start of `claim`, `branch` and `new --workspace` (before any branch is
    resolved), and in `review` next to its existing fetch, unless `--no-fetch`; `review` resolves
    `head` after that fetch.
- **Local and remote disagree.** After a fetch, each remote record is compared with the local file
  for its ID: a remote record with no local file, or whose `recorded` is later, replaces the file,
  keeping its own timestamp; an equal or earlier one leaves the local file, which is then a change
  not yet pushed (made with `--local-only` or offline) and goes out with that task's next record
  write. A fetch never deletes a local record, and never renames or deletes a local git branch.
- **Failures never undo local work.** A fetch that fails (unreachable remote, no permission)
  prints a warning on stderr and the command continues with local records. A push that fails —
  offline, a server refusing refs outside `refs/heads` and `refs/tags`, or a lease rejected because
  another clone pushed that record meanwhile — keeps the local branch, record and claim, prints a
  warning naming the ref and the retry (`taskrail branch <ID> <NAME>`), and leaves the exit code as
  it would have been. `branch`, `claim` and `new --json` report `record_remote`: `null` when nothing
  was mirrored, else `name`, `ref`, `commit` (pushed commit or `null`), `pushed` and `error`.
- **Deletion.** Nothing deletes a remote record automatically, like a local one; `done`,
  `release`, `discard` and `reopen` leave it. A repository cleans up with
  `git push <remote> --delete refs/taskrail/branches/<ID>`, and the next fetch prunes the local copy.

## Acceptance criteria

1. With `branch_record_remote` unset, `branch`, `claim`, `new --workspace --branch`, `review` and
   `show/list/next --fetch` create no `refs/taskrail/branches/*` on the remote and no
   `refs/taskrail/remotes/*` locally, and report `record_remote: null`; a non-string value is a
   configuration error (exit 2).
2. With it set, `taskrail branch <ID> <NAME>` pushes `refs/taskrail/branches/<ID>`: a commit with no
   parent, author and committer `taskrail <taskrail@localhost>`, message `taskrail branch <ID>`, and
   a tree holding only `branch.json` whose keys are exactly `id`, `branch` and `recorded`, equal to
   the local record; `record_remote.pushed` is true and the local copy ref names that commit.
3. `claim` on the template branch with no record pushes the frozen record; `claim` on an
   already-recorded or on another branch pushes nothing; `new --workspace --branch NAME` pushes the
   new task's record.
4. `--local-only` on `claim` and `branch` neither fetches nor pushes records (`record_remote: null`).
5. Running `taskrail branch <ID> <NAME>` again pushes the new record with a lease on the previous
   commit; when the remote ref was changed by another clone since this clone's copy, the push is
   rejected, the local branch and record stay, `record_remote.pushed` is false with the error, a
   warning is printed and the exit code is 0.
6. In a second clone, `show <ID> --fetch` reports the renamed branch with `branch_source: recorded`,
   `state: done-branch` for a task done on that branch, and a dependent's `base.onto` on
   `<remote>/<renamed>`; `list --fetch` and `next --fetch` agree. Plain `show` does not fetch and
   still reports the template.
7. In a second clone, `claim`, `branch`, `new --workspace` and `review` (without `--no-fetch`) fetch
   records before resolving a branch: `review` on the renamed branch succeeds without an earlier
   `--fetch`; `review --no-fetch` does not fetch records.
8. A fetched remote record replaces a local file only when the local file is missing or its
   `recorded` is earlier; the local record is kept otherwise; a remote ref deleted by hand
   disappears from `refs/taskrail/remotes/` on the next fetch while the local record file remains.
9. With the remote unreachable, `show --fetch`, `branch` and `new --workspace --branch` print a
   warning, use local records and exit as they would online.
10. No pushed record contains an owner, host, worktree path or any key other than the three above
    (covered by 2), and prior work does not report record commits.
11. `DESIGN.md` §4, §6.2, §6.4 and §7, the README, the core skill's step 3 and `CHANGELOG.md`
    describe the setting, the ref, the flags and the rules above.

## Affected areas

- `tools/taskrail/src/taskrail/config.py` — the `branch_record_remote` key.
- `tools/taskrail/src/taskrail/branches.py` — push, fetch and the adoption rule; `write` also
  accepts a record to adopt.
- `tools/taskrail/src/taskrail/gitutil.py` — `write_claim_commit` generalized to any single-file
  plumbing commit; `claims.py` calls the general form.
- `tools/taskrail/src/taskrail/cli.py` — `branch`, `claim` (`_freeze_branch`), `new`, `review`,
  and `--fetch` on `show`, `list`, `next`.
- `tools/taskrail/src/taskrail/skills/taskrail/SKILL.md` step 3, then `taskrail upgrade` for the
  installed copies.
- `tools/taskrail/DESIGN.md`, `tools/taskrail/README.md`, `tools/taskrail/CHANGELOG.md`.
- A new `tools/taskrail/tests/test_branch_records_remote.py` with two clones of a local bare
  remote.

## Out of scope

- Deleting or pruning remote records automatically, for example once a task is merged.
- Pushing records that existed before the setting was enabled, other than one at a time through
  `taskrail branch <ID> <NAME>`.
- Renaming or deleting a local git branch in a clone that adopts another clone's rename.
- Checking remote claims in `branch`'s owner check.
- A standalone `taskrail fetch` command, and fetching the mainline's remote in `show --fetch`.
- The remote-claim deletion bug found while reproducing (see *Open questions*).

## Open questions and risks

- **Clock skew.** "Later `recorded` wins" compares clocks of different machines; a clone whose
  clock runs behind can lose to an older record. Acceptable for a naming hint, and a re-run of
  `taskrail branch` restores it.
- **Publishing branch names.** With the setting on, a branch name is published even when
  `push_task_branch` is false and the branch itself is never pushed. Documented as a consequence of
  opting in.
- **Servers refusing custom refs** make every push warn; the same prerequisite as remote claims.
- **Bug found, outside this task.** With `claim_remote` set, `taskrail release --force` and
  `taskrail done` (which releases with `force=True`) cannot delete the remote claim:
  `claims._delete_remote` passes `--force-with-lease=<ref>` without an expected value, which git
  checks against a remote-tracking ref that does not exist for `refs/taskrail/claims/*`, so the push
  is rejected as `stale info`. `done` has then written the row but exits 2 and leaves both the local
  and the remote claim. Proposed as a follow-up bug task.
- **Parallel lane.** DESIGN.md §4 is also edited by the T029 lane; the change here is one line in
  the `[git]` block.

## Evidence

Reproduction on the base `1543057`, in `mktemp -d /tmp/t036-repro.XXXX`, with clone `a`
(`claim_remote = "origin"`), a bare `origin.git`, a lane worktree for T001 and a fresh clone `b`:

```
--- A: claim, rename, done, push branch
T001 branch renamed from T001-base-task to feature/base
taskrail: could not delete remote claim refs/taskrail/claims/T001: To /tmp/t036-repro.jqRU/origin.git
 ! [rejected]        (delete) -> refs/taskrail/claims/T001 (stale info)
error: failed to push some refs to '/tmp/t036-repro.jqRU/origin.git'
--- A: show T001 / T002
done-branch feature/base recorded
pending [] origin/feature/base
--- remote refs
2bb236243b0001add1a07df4634f148d95c93bf8 commit	refs/heads/feature/base
e390d61862d22b375375c7591574b210e94e05c0 commit	refs/heads/main
86fee055250ba6c33d1b54154d6baeb92d7b86e8 commit	refs/taskrail/claims/T001
--- B: fresh clone
pending T001-base-task template
blocked ['T001'] origin/main
```

The remote-claim bug, isolated without any rename (`claim T002`, then `release T002 --force` by
the same owner):

```
6f0c1415b443ff84902e444835d44c2e9c964d2f commit	refs/taskrail/claims/T002
--- release --force by owner, no rename
taskrail: could not delete remote claim refs/taskrail/claims/T002: To /tmp/t036-repro.jqRU/origin.git
 ! [rejected]        (delete) -> refs/taskrail/claims/T002 (stale info)
error: failed to push some refs to '/tmp/t036-repro.jqRU/origin.git'
exit 2
6f0c1415b443ff84902e444835d44c2e9c964d2f commit	refs/taskrail/claims/T002
```

The git behaviour the plan relies on, checked in the same directory: a push with
`--force-with-lease=refs/taskrail/branches/T001:` creates the ref (`[new reference]`); a fetch with
`+refs/taskrail/branches/*:refs/taskrail/remotes/origin/branches/*` copies it
(`* [new ref] refs/taskrail/branches/T001 -> refs/taskrail/remotes/origin/branches/T001`); after the
remote ref is deleted, `fetch --prune` with the same refspec removes the local copy
(`- [deleted] (none) -> refs/taskrail/remotes/origin/branches/T001`); a fetch from an unreachable
remote exits 128.
