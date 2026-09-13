# T034 — Clear done-branch for a task reopened on its mainline

Kind: bug · Epic: E05 · Status: diagnosed

## Symptom

A task that was finished on its branch, squash-merged, and later reopened on the mainline with
`taskrail reopen` reads as `done-branch` for as long as its old task branch — the local branch,
its `<remote>/<branch>` copy, or either one under a recorded name — still exists with the row `✅`.
While it does:

- `taskrail show` and `taskrail list` report `done-branch` although the task is pending again;
- `taskrail next` never offers it;
- `taskrail claim` refuses it with exit 5, **even from a fresh worktree branched from the
  mainline that already contains the reopen** — so the task cannot be redone without deleting
  the stale branch (and its remote copy) first;
- a dependent is stacked on the stale branch instead of being blocked by the reopened task.

Expected: the reopen supersedes the stale `✅`, so the task is `pending` (or `claimed`/`blocked`).
A second `done` on a branch that contains the reopen must make it `done-branch` again.

## Reproduction

A throwaway repository under a temporary directory with a bare `origin`, running the CLI from this
branch (`uv run --project tools/taskrail taskrail --root <repo> …`); the script was deleted
afterwards together with the directory.

```bash
git init -b main; # .taskrail/config.toml: one backlog "main", mainline "main", [review] remote = "origin"
# TODO.md: E01 with T001 (feature, "Base task") and T002, both ⬜
git add -A; git commit -m backlog
git init --bare -b main ../origin.git; git remote add origin ../origin.git; git push -u origin main
# 1. finish T001 on its branch and push it
git worktree add ../lane -b T001-base-task origin/main
taskrail --root ../lane claim T001 --owner lane; taskrail --root ../lane done T001 --owner lane
git -C ../lane commit -am "chore(T001): mark done"; git -C ../lane push origin T001-base-task
# 2. squash-merge into main and push
git merge --squash T001-base-task; git commit -m "feat: base task (T001) (#1)"; git push origin main
# 3. reopen on main, commit with the suggested message (Reopens: T001 trailer), push
taskrail reopen T001 --reason "Not finished after all" --json   # commit_message → git commit -F
git push origin main
# 4. observe
taskrail show T001 --json; taskrail next --json; taskrail list; taskrail claim T001
# 5. variant: remove the worktree and the local branch; only origin/T001-base-task and the record remain
git worktree remove --force ../lane; git branch -D T001-base-task
taskrail show T001 --json; taskrail claim T001
```

## Evidence

Output of the script above (state printed as `status state branch branch_source`):

```text
--- 1. finish T001 on its branch, push it
T001 done
show T001 state: done-branch
--- 2. squash-merge into main and push
Squash commit -- not updating HEAD
show T001 state: done
--- 3. reopen T001 on main, commit with the trailer, push
Reopen T001: Base task

Not finished after all

Reopens: T001

grep: 8a1b77f Reopen T001: Base task
refs: T001-base-task main origin/T001-base-task origin/main
--- 4. observe
$ taskrail show T001 --json (state)
pending done-branch T001-base-task recorded
$ taskrail next --json (ids)
['T002']
$ taskrail list
T001   ⬜ done-branch feature   2pt  E01   Base task
T002   ⬜ pending     feature   1pt  E01   Other
$ taskrail claim T001
taskrail: T001 is done on branch T001-base-task, origin/T001-base-task, not yet merged into main
exit=5
--- 5. variant: local branch and worktree removed, only origin/T001-base-task and the record remain
record: {"id":"T001","branch":"T001-base-task","recorded":"2026-09-13T22:34:07+00:00"}
refs: main origin/T001-base-task origin/main
pending done-branch
taskrail: T001 is done on branch origin/T001-base-task, not yet merged into main
exit=5
```

A second probe on the same setup checked the git query proposed below, and tried to redo the
task on a fresh worktree from `origin/main` under the same branch name:

```text
$ git log -1 --format=%h -E --grep=<P> main origin/main --not T001-base-task
19c48b1
$ git log -1 --format=%h -E --grep=<P> main origin/main --not origin/T001-base-task
19c48b1
--- second done: delete the stale local branch, redo T001 from origin/main on the same (recorded) name
taskrail: T001 is done on branch origin/T001-base-task, not yet merged into main
taskrail: T001 is not claimed; claim it before marking it done, or pass --force
$ git log -1 ... --not T001-base-task   (new tip contains the reopen: expect empty)
(end)
$ git log -1 ... --not origin/T001-base-task   (stale remote copy: expect the reopen commit)
19c48b1
current CLI: done-branch
taskrail: T001 is done on branch origin/T001-base-task, not yet merged into main
exit=5
```

with `<P>` = `^Reopens:[[:space:]]*T001[[:space:]]*$`. The fresh worktree's `claim` is refused
because of the stale remote copy alone, so the bug also blocks redoing the task.

## Root cause

`stack._find` (`tools/taskrail/src/taskrail/stack.py`) decides `done-branch` from backlog
**snapshots** only: a task is `done-branch` when its row is `✅` at a tip of its task branch and
`✅` on neither mainline ref. It never asks whether that `✅` is still current. After
`taskrail reopen` on the mainline, both mainline refs say `⬜`, so a branch tip whose `✅` predates
the reopen satisfies the test exactly like an unmerged finished branch. The history that tells the
two apart — a mainline commit carrying `Reopens: <ID>` that the tip does not contain — is written
by `reopen` and preserved by `review` through the squash, but `stack.py` does not read it.

`state()` (`query.py`), `claim` (`cli.py`), `next`/`list` and a dependent's base all consume
`stack.done_on_branch`, so the one wrong answer shows up in all of them.

## Ruled out

- **The recorded branch name (T019).** Step 5 shows the record survives, but the record only
  names which refs to read. With no record, the template renders the same name
  `T001-base-task`, so deleting the record would not change the result; and another clone has no
  records at all yet would reproduce it through `origin/T001-base-task`. The record is neither
  necessary nor sufficient for the bug.
- **`reopen` itself.** It rewrote the status cell to `⬜` on `main` and returned the message with
  the `Reopens: T001` trailer; `git log --grep='^Reopens: T001$' main` finds the commit
  (`grep: 8a1b77f …`). The current checkout's row is correct (`pending` status).
- **The merged check.** Right after the squash-merge (step 2) the task reads `done`; the mainline
  refs are read correctly, and after the reopen they are correctly `⬜`.
- **Remote-tracking refs only.** The local branch alone (step 4 lists both refs) and the remote
  copy alone (step 5) each trigger it independently.
- **Fetch state.** Everything is pushed and the refs are current; the result does not depend on
  a stale `origin/main`.

## Affected areas

- `stack.done_on_branch` and, through it, `query.state`, `query.unmerged_dependencies`,
  `query.blocked_by`, `query.base_dict`, `cmd_claim`, `next`, `list`, `show`.
- `DESIGN.md` §7, paragraph **Done on its branch**, which defines the state without the reopen
  exception. §6.1 only says `claim` refuses a `done-branch` task and stays correct; §12.4's
  one-line summary of `done-branch` belongs to another task's area and stays as it is.

## Proposed fix

In `stack._find`, after computing the tips where the row is `✅` for a task that is not merged,
drop each tip that lacks a mainline reopen of that task; the task is `done-branch` only if a tip
remains, and `refs` lists only the remaining tips.

- **Which mainline refs.** The same refs the merged check reads: the local mainline and
  `<remote>/<mainline>`, whichever exist. Local refs only, no fetch, as §7 requires.
- **The query.** Per remaining tip:
  `git log -1 --format=%H -E --grep='^Reopens:[[:space:]]*<ID>[[:space:]]*$' <mainline refs> --not <tip>`
  — a non-empty result means the mainline has a reopen of the task that the tip does not contain,
  so the tip's `✅` predates it. The ID is regex-escaped. The whitespace tolerance matches
  `review.REOPENS`, which already parses these trailers.
- **Performance.** The query runs only for tasks that would otherwise be `done-branch` (a `✅` tip
  and not merged), once per such tip — usually one or two per task — and walks only the commits
  on the mainline that the tip lacks, stopping at the first match. Tasks without a branch, or
  merged, or `⬜` at every tip cost nothing extra. The result stays cached per project.
- **Second done.** A branch created from a mainline that contains the reopen contains the
  `Reopens` commit, so the query is empty and the tip counts again: `done-branch`. A stale copy
  that lacks it (for example an old `origin/<branch>` next to a new local branch of the same name)
  is dropped individually, so `refs` names only the current tip.
- **Consistent with the rebase rule.** The core skill's backlog-conflict rule already lets a
  side's `⬜` win over `✅` when that side has a `Reopens: <ID>` commit the other lacks; this
  applies the same rule to `done-branch`.
- **Records.** Leave them as they are: records are documented to survive `reopen` (§6.4), and
  clearing them would not fix the bug (see *Ruled out*).
- **Known limit.** When a host's squash message drops the pull request description, the trailer
  never reaches the mainline and the stale `✅` still wins; the rebase rule has the same
  dependency on the trailer.
- **Tests** in `tests/test_stacked_base.py` using its `lanes` fixture: reopened on the mainline
  with the stale local and remote branch → `pending`, offered by `next`, claimable; a dependent
  is blocked instead of stacked; a second `done` on a branch containing the reopen →
  `done-branch` again, with a stale remote copy excluded from `refs`.
- **Docs.** One sentence in `DESIGN.md` §7 *Done on its branch* for the exception and its cost,
  and one bullet under `## Unreleased` in `tools/taskrail/CHANGELOG.md`.
