# T062 — Treat a task discarded on its unmerged branch as closed in status and next

Kind: bug · Epic: E02 · Status: diagnosed

Source: the impact stage of [T054](T054-keep-a-closing-lane-from-reading-as-pend.md) (its
*Affected areas* and *Impact*), decided in
[T054's autopilot decisions](../autopilot/decisions/T054-keep-a-closing-lane-from-reading-as-pend.md),
fix gate question 2. It extends the lane-state work that started from the findings of
[the T033 autopilot trial](../spikes/T033-trial-the-autopilot-on-a-real-backlog-wi.md).

## Symptom

A task is discarded on its own branch — `taskrail discard <ID>` in the task's worktree, committed
there — and the branch is not merged yet. Seen from the main checkout, the task still reads as open:

- `autopilot status` reports it `pending` (once its dispatch is older than
  `[git].claim_grace_minutes`), with no `touched` files, and the hand-off queue is empty;
- `autopilot next` offers it, and `autopilot next --run R` dispatches it again to a new lane and
  counts it against the run's count;
- plain `taskrail next` offers it, `show` reports `state: pending`, and `claim` from another
  checkout succeeds.

The same holds after the branch is merged into `<remote>/<mainline>` while the local mainline is not
pulled: `autopilot status` still says `pending`, where a `✅` merged the same way reads `done-merged`.

Expected: a discard committed on the task's branch is a closed task waiting to be merged, as a `✅`
there is (`done-branch`, §7 *Done on its branch*): neither `pending` nor offered by `next` or
`autopilot next`, and not claimable.

## Reproduction

A throwaway Python script outside the repository, run with this branch's CLI
(`uv run --directory tools/taskrail python <script>`). It builds a repository under a temporary
directory — a `TODO.md` with pending tasks `T001` (bug), `T002` (chore, depends on `T001`) and `T003`
(feature), `[autopilot] enabled = true`, `max_lanes = 10`, a bare `origin` — and calls
`taskrail.cli.main` in-process:

1. `autopilot start --count 2`, then `autopilot next --run <run>` dispatches `T001` and `T003`;
2. `git worktree add <lane> -b T001-first-bug origin/main`, then
   `--root <lane> claim T001 --owner lane --run <run>`;
3. `--root <lane> discard T001 --owner lane`, then `git commit -am "chore(T001): discard"` in the
   lane; prints the `T001` row at the branch and at `main`;
4. moves `T001`'s `dispatched` time in the run file 16 minutes into the past
   (`claim_grace_minutes` is 15), as a lane that stopped at a gate a while ago would be;
5. from the main checkout: `autopilot status --run <run>`, `autopilot next` (preview),
   `taskrail next`, `show T001`, `show T002`, `claim T001 --owner someone --local-only` (released
   again), and `autopilot next --run <run>`;
6. pushes the lane branch to `origin/main` (a merge), fetches without pulling the local `main`, and
   repeats the reads of step 5.

## Evidence

```text
$ uv run --directory /…/.worktrees/T062-treat-a-task-discarded-on-its-unmerged-b/tools/taskrail python /…/T062/repro.py
--- autopilot next --run 20260915-1 (exit 0): dispatch
["T001", "T003"]
--- claim T001 --run 20260915-1 in the lane (exit 0)
claimed T001 as lane
--- discard T001 in the lane worktree (exit 0)
T001 discarded
--- git log --oneline -1 in the lane worktree; git status --short
076ef5b chore(T001): discard
(clean)
--- T001's row at refs/heads/T001-first-bug and at main
| ❌ | T001 | bug     | 1   | —          | First bug   | —           |
| ⬜ | T001 | bug     | 1   | —          | First bug   | —           |
--- T001's dispatch moved 16 minutes into the past
--- autopilot status --run 20260915-1 after the discard is committed on the branch (exit 0)
T001: state=pending claim=False touched=[]
T003: state=dispatched claim=False touched=[]
handoff={"mode": "sequential", "in_review": null, "queue": [], "next": null}
--- autopilot next (preview) after the discard is committed on the branch (exit 0)
{"dispatch": ["T001"], "skipped": [{"id": "T003", "reason": "dispatched in run 20260915-1"}]}
--- taskrail next after the discard is committed on the branch (exit 0)
["T001", "T003"]
--- show T001 after the discard is committed on the branch (exit 0)
{"status": "pending", "state": "pending", "blocked_by": [], "base.onto": "origin/main"}
--- show T002 after the discard is committed on the branch (exit 0)
{"status": "pending", "state": "blocked", "blocked_by": ["T001"], "base.onto": "origin/main"}
--- claim T001 from the main checkout (exit 0)
claimed T001 as someone
--- autopilot next --run 20260915-1 after the discard is committed on the branch (exit 0)
{"dispatch": ["T001"], "skipped": [], "remaining": 0}
--- autopilot status --run 20260915-1 after the branch is merged into origin/main (local main not pulled) (exit 0)
T001: state=pending claim=False touched=[]
T003: state=dispatched claim=False touched=[]
handoff={"mode": "sequential", "in_review": null, "queue": [], "next": null}
--- autopilot next (preview) after the branch is merged into origin/main (local main not pulled) (exit 0)
{"dispatch": ["T001"], "skipped": [{"id": "T003", "reason": "dispatched in run 20260915-1"}]}
--- taskrail next after the branch is merged into origin/main (local main not pulled) (exit 0)
["T001", "T003"]
--- show T001 after the branch is merged into origin/main (local main not pulled) (exit 0)
{"status": "pending", "state": "pending", "blocked_by": [], "base.onto": "origin/main"}
--- show T002 after the branch is merged into origin/main (local main not pulled) (exit 0)
{"status": "pending", "state": "blocked", "blocked_by": ["T001"], "base.onto": "origin/main"}
```

The branch tip holds `❌` and the lane is clean, yet every reader from the main checkout reports
`T001` as `pending`; `autopilot next --run` dispatched it again and took the run's last slot for it
(`remaining: 0`). With the dispatch still inside the grace (a first run of the same script without
step 4), `status` read `dispatched` and `next` skipped it only for that reason.

## Root cause

Every reader decides "closed" from two sources, and neither sees a committed `❌` on a task branch:

1. **The checkout's own row** (`task.status`), which is `⬜` until the branch is merged and pulled.
2. **`stack.done_on_branch`** (`tools/taskrail/src/taskrail/stack.py`), the only reader of task
   branch tips, which keeps a tip only when the row there is `✅`:

   ```python
   done = tuple(
       _short(ref)
       for ref in refs
       if statuses[ref].get(task_id) == Status.DONE.value and not _reopened_since(...)
   )
   ```

   `_find` already reads the row at every task-branch tip (`_read_statuses`, one
   `git cat-file --batch`) and has the `❌` in hand; it discards it.

Consequences, reader by reader:

- `query.state` returns `done-branch` only for `done_on_branch`, so the task falls through to
  `pending` (or `claimed`); `next`/`eligible` offer it, and `show` reports it.
- `cli.cmd_claim` refuses only `task.status` not pending or `done_on_branch`, so it claims it.
- `autopilot.status.task_state` checks `done_on_mainline` (`✅` on a mainline ref), the checkout's
  `❌`, `done_on_branch`, the recorded states, the claim, `_closing` and the dispatch — so it falls
  through to `pending`. `done_on_mainline` counts only `✅`, which is why a `❌` merged into
  `<remote>/<mainline>` but not pulled stays `pending` too, and `_closing` (T054) looks only for an
  uncommitted `✅`, so the moment between `discard` and its commit reads `pending` in the same way.
- `autopilot.dispatch.next_lanes` takes its candidates from `query.eligible` and its lane states
  from `task_state`, so the task is both a candidate and, being `pending`, not counted toward the
  run's count — it is dispatched again.

## Ruled out

- **`discard` itself.** Exit 0; the lane's tree is clean after the commit, and the branch tip holds
  `| ❌ | T001 |` while `main` holds `⬜`. Releasing the claim on discard is the documented contract
  (§6 write rules).
- **Branch resolution (`branches.task_branch`).** `show T001` resolves `T001-first-bug`, the branch
  the lane created, and `done_on_branch` reads the same candidate refs; with `done` in place of
  `discard`, the same flow reads `done-branch` (T054's regression test
  `test_a_lane_between_done_and_its_commit_is_running_and_not_dispatched_again` ends there).
- **`_reopened_since`.** No `Reopens:` commit exists in the reproduction; the tip is dropped before
  that check, by the `✅` comparison.
- **The dispatch grace (`dispatch_live`).** Inside the grace the task read `dispatched` and was
  skipped; the grace only hides the bug for 15 minutes, as T054 found for its window.
- **`autopilot next`'s skip checks.** They run over the candidates `query.eligible` already chose;
  the task should not be a candidate at all, so no skip reason is missing.
- **`blocked_by` for dependents.** `T002` is `blocked` by `T001`, which is right both before and
  after the fix: a discarded dependency is not `done`, so it keeps blocking (§7 *Dependencies and
  the base*), and `unmerged_dependencies` must not stack a dependent on a discarded branch.

## Affected areas

- `stack.py` `_find` / `done_on_branch` — the tip reader.
- `query.py` `state`, `STATES` — `list`, `show`, `next`, `list --state`.
- `cli.py` `cmd_claim` (and `cmd_edit`, which refuses `done-branch` the same way).
- `autopilot/status.py` `task_state`, `done_on_mainline`, `_closing`, `STATES`.
- `autopilot/dispatch.py` `next_lanes` — affected only through `query.eligible` and `task_state`;
  no change needed there (see *Proposed fix*).
- Not in this fix: the hand-off of a discarded branch (the queue, `autopilot lane --state
  handed-off`, the `touched` files and escalation flags of a moved-on task) — see *Proposed fix*,
  point 6.

## Proposed fix

1. **`stack.py`.** `_find` keeps, in the same scan, the tips where the row is `❌`, under the same
   rules as `✅`: the local branch or `<remote>/<branch>`, not closed (`✅` or `❌`) on either
   mainline ref, and not older than a `Reopens: <ID>` commit on a mainline ref. A task with a `✅`
   tip stays `done-branch` only. New `discarded_on_branch(project) -> dict[str, DoneOnBranch]`,
   cached next to `done_on_branch`. `done_on_branch`'s result is unchanged.
2. **`query.py`.** New state `discarded-branch`, after `done-branch` in `STATES` and in `state`:
   `next` never offers it, `show` and `list` report it, `list --state discarded-branch` filters it.
   `blocked_by`, `unmerged_dependencies` and `base_dict` are unchanged, so dependents stay blocked
   and are never stacked on it.
3. **`cli.py`.** `cmd_claim` refuses a `discarded-branch` task with exit 5, as it refuses
   `done-branch` (`<ID> is discarded on branch <refs>, not yet merged into <mainline>`), and
   `cmd_edit` refuses it without `--force`, as it refuses `done-branch` (questions 2 and 3).
4. **`autopilot/status.py`.**
   - `task_state` returns `discarded-branch` after `handed-off`/`done-branch` and before the
     recorded states; it is not in `WITH_BRANCH`, so it reports no `touched` files and raises no
     escalation flag. New `discarded-branch` in `STATES`.
   - `task_state` returns `discarded` also when the row is `❌` on the local mainline or
     `<remote>/<mainline>`: `done_on_mainline`'s scan of the mainline refs is shared, cached, with
     a sibling `discarded_on_mainline` (question 4).
   - `_closing` also matches an uncommitted `❌`, so the moment between `discard` and its commit
     reads `running`, as T054 made it for `done` (question 5).
5. **`autopilot/dispatch.py`: no change.** The task leaves `query.eligible`, so it is no longer a
   candidate. `discarded-branch` is neither in `OCCUPYING` (it uses no lane) nor in `COUNTED` (it
   frees its place in the run's count, as `discarded` does in §12.7).
6. **Hand-off queue: not queued by this fix.** `_handoff` (whose ordering T053 rewrites on its
   unmerged branch, with `_done_time` reading the `✅` commit from `done_on_branch`) keeps queuing
   only `done-branch` rows, and `autopilot lane --state handed-off` keeps refusing anything but
   `done-branch`. A `discarded-branch` row carries its `branch`, so the orchestrator sees that the
   branch still has to be merged; queuing it — with a discard-commit time in `_done_time`, a
   `handed-off` that accepts it, and `touched` plus `MOVED_ON` for its close review — is a
   follow-up task once T053 is merged (question 6).
7. **Regression tests.**
   - `tests/test_autopilot_next.py`, `pilot` fixture: dispatch, claim with `--run`, `discard` in the
     lane and commit, backdate the dispatch; assert `autopilot status` reports `discarded-branch`,
     `autopilot next --run` does not dispatch it (and counts it free), and plain `next` does not
     offer it; after pushing the branch to `origin/main` without pulling, `status` reports
     `discarded`. A second test: `discard` without a commit reads `running`.
   - A plain-CLI test next to the `done-branch` tests (`tests/test_stacked_base.py`): `show` reports
     `discarded-branch`, `next` omits it, `claim` exits 5, a dependent stays `blocked`, and a tip
     older than a `Reopens:` commit on the mainline does not count.
8. **Docs.** `DESIGN.md` §7 (state list, a *Discarded on its branch* paragraph, the `next` row),
   §12.1 `autopilot status` row, §12.4 and §12.7 (exact text at the gate), and one bullet under
   `## Unreleased` in `tools/taskrail/CHANGELOG.md`.
