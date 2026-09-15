# T067 — Detect and clean up a merged branch whose task was discarded on it

Kind: feature · Epic: E02 · Status: planned

Source: [T065's plan](T065-hand-off-a-branch-whose-task-was-discard.md) (*Out of scope*, first
bullet), opened at T065's plan gate
([decision record](../autopilot/decisions/T065-hand-off-a-branch-whose-task-was-discard.md), question 6).
Its dependency T065 is merged (`0404505`). No prior work: `show` reported no artifact, branch or
commit for T067.

## Premise, checked on the current mainline

On `origin/main` (`01af8ee`), `tools/taskrail/src/taskrail/autopilot/`:

- `merged.cmd_merged` sets `done_at_head = _row_done(project, task, head_commit)` and, when it is
  false, skips `detect` with the reason `<ID> is not done at the head of <ref>; content detection
  needs a finished branch`. A branch whose row is `❌` at its head therefore reads `merged: false`
  whatever the mainline holds, and `--cleanup` refuses it with exit 5 (`_cleanup`, `not merged`).
- `merged.recorded_merges` returns every task with a lane `merged` record whose commit is still on a
  mainline ref, whatever status the task was closed with, and `status.done_on_mainline` unions it
  into the `✅` rows. Recording a proven merge of a discarded branch would make `task_state` return
  `done-merged` and count it toward the run's `complete`.
- Without a record, a squash merge brings the `❌` row to `<remote>/<mainline>`, which
  `status.discarded_on_mainline` reads, so `status` already shows `discarded` after the merge (T065,
  criterion 3). The gap is `autopilot merged` itself: no proof, no record, no cleanup.

The premise holds.

## Behaviour

After this change, the orchestrator's *After a merge* step 1 (`autopilot merged <ID> --cleanup
--json`) works for a branch whose task was discarded on it, as for a done one:

- **Detected.** The content checks of §12.8 run for a head whose task row is `✅` **or `❌`**. A head
  whose row is still `⬜` is refused as before (an unstarted branch is an ancestor of the mainline).
  The reason for a pending head reads `<ID> is not done or discarded at the head of <ref>; content
  detection needs a closed branch`.
- **Reported.** A new key `closed` is `"done"` or `"discarded"`: the status the checked head's row
  closes the task with, or, when no branch is left, the recorded merge's status; `null` for a
  pending head. `done_at_head` keeps its meaning. `confirmations` gains `row_discarded_on_mainline`
  beside `row_done_on_mainline`. The text form's first line ends in ` (discarded)` for a discarded
  task.
- **Recorded, without reading done-merged.** The lane's `merged` record gains
  `status: "done" | "discarded"`. `recorded_merges` returns, per task, the status of its newest valid
  record (by `detected`; a record without `status`, written before T067, is `done`).
  `done_on_mainline` takes the tasks whose newest record is `done`; `discarded_on_mainline` takes
  those whose newest record is `discarded` (question 2). So a discarded branch merged and recorded
  reads `discarded` in `autopilot status`, even after its mainline row was edited by hand, and never
  counts toward `done_merged` or `complete`.
- **Cleaned up.** `--cleanup` removes the worktree, deletes the local branch with its lease and
  releases a leftover claim for a proven discarded merge exactly as for a done one; `_cleanup` is not
  changed.

## Acceptance criteria

1. A lane that claims a task, commits work, runs `taskrail discard` and commits it, pushes its
   branch, and is squash-merged on the host: `autopilot merged <ID> --json` exits 0 with
   `merged: true`, `via` `tree`, `closed: "discarded"`, `done_at_head: false`,
   `confirmations.row_discarded_on_mainline: true` and `row_done_on_mainline: false`.
2. With the task in a run, that call writes `merged` to the run's lane with `status: "discarded"`;
   `autopilot status --run R` then reports the task `discarded` (not `done-merged`), `done_merged` 0
   and `complete` false — also after the host edits the `❌` row back to `⬜` by hand.
3. `autopilot merged <ID> --cleanup --owner <lane>` on that discarded, merged branch exits 0, removes
   the worktree, deletes the local branch, releases a claim left behind and keeps the remote branch,
   as `test_cleanup_removes_the_worktree_and_local_branch_only` asserts for a done one. With the remote
   branch deleted afterwards, a second call reports `recorded: true`, `merged: true` and
   `closed: "discarded"`.
4. A done branch keeps its behaviour: its record has `status: "done"`, `closed` is `"done"`, it reads
   `done-merged`; a record without `status` (as written before T067) still counts as done.
5. When a task has records in two runs with different statuses, the newest by `detected` decides:
   a newer `discarded` record over an older `done` one reads `discarded`, not `done-merged`.
6. A branch whose row is `⬜` at its head is still not merged (`merged: false`, `closed: null`,
   `reason` containing `not done or discarded`, no check run), and `--cleanup` still exits 5 for it.
7. The text form names a discarded merge: `<ID> merged into origin/main via tree at <sha7> (discarded)`.
8. All tests pass: `uv run --directory tools/taskrail pytest -q`.

All criteria are verified by pytest on the `pilot` fixture of `tests/test_autopilot_merged.py`
(criteria 1–7), which already has a host that squash-merges, `unmark` and `delete`; a `discard`
helper beside `finish` is added there.

## Affected areas

- `tools/taskrail/src/taskrail/autopilot/merged.py`
  - `_row_done` → `_row_status(project, task, rev)` returning the row's cell at `rev`; callers compare
    it with `Status.DONE.value` / `Status.DISCARDED.value`.
  - `recorded_merges(project) -> dict[str, str]`: task ID → `"done"` or `"discarded"` from the newest
    valid record (by `detected`), a missing `status` read as `done`.
  - `_latest_record`: unchanged selection; its `status` feeds `closed` in the recorded case.
  - `cmd_merged`: the guard accepts `✅` or `❌` at the head; `closed`, `status` in the written entry,
    `confirmations.row_discarded_on_mainline`, the new pending reason.
  - `_text`: the ` (discarded)` suffix.
  - `_cleanup` and `_dependents`: not changed.
- `tools/taskrail/src/taskrail/autopilot/status.py`
  - `done_on_mainline`: unions the IDs whose recorded status is `done`.
  - `discarded_on_mainline`: unions the IDs whose recorded status is `discarded`, cached under its own
    key beside `MERGED_KEY` (question 2).
  - `task_state`, `_handoff`, `WITH_BRANCH` and `WAITING`: not changed.
- `tools/taskrail/src/taskrail/autopilot/runs.py`: not changed (records are free-form lane keys).
- Tests: `tools/taskrail/tests/test_autopilot_merged.py` — new tests for criteria 1–7; the existing
  `test_text_and_json_forms` key set gains `closed`, and `test_confirmations_are_reported_and_never_prove`
  gains `row_discarded_on_mainline: False`.
- `tools/taskrail/DESIGN.md` §12.1, §12.4, §12.8 (question 1, exact text below).
- `tools/taskrail/CHANGELOG.md`: one *Unreleased* bullet. `docs/features/README.md`: this row.
- The `taskrail-autopilot` skill: not changed (question 3).

## Out of scope

- A new state for a merged discard, and any change to `task_state`'s precedence, `autopilot next`,
  the run's count or the hand-off queue.
- A recorded merge that outlives a later reopen on the mainline: a record still counts while its
  commit is on a mainline ref, for done and discarded alike, as since T031.
- Stacked dependents of a discarded task: `_dependents` lists them as for a done one, which is what
  their rebase needs, since the discarded branch's content did reach the mainline.
- The plain `taskrail` skill, which never runs `autopilot merged`.

## Open questions and risks

- **`discarded_on_mainline` gains an input.** It feeds `task_state` and T064's candidate skip in
  `dispatch.next_lanes`. A recorded discard merge now makes a task `discarded` there even when both
  mainline rows read `⬜`, as a recorded done merge already makes one `done-merged`; that is the
  symmetry question 2 asks about.
- **Newest record wins.** Today any valid record counts. Choosing the newest by `detected` changes
  nothing for a task with one record or only done records; it only settles the mixed case of
  criterion 5. `detected` is an ISO timestamp, compared as text as `_latest_record` already does.
- **Output shape.** `closed` and `row_discarded_on_mainline` are additions; no key is removed or
  renamed, so existing consumers keep working.

## Questions for the plan gate

1. **`DESIGN.md` texts a–d** below: approve as written, or drop or change parts.
2. **Recorded discard merges and `discarded_on_mainline`.** (recommended) a record with
   `status: "discarded"` also feeds `discarded_on_mainline`, so a hand-edited mainline row cannot turn
   a proven discard merge back into `discarded-branch` or a dispatchable task — the same protection a
   recorded done merge has; or (B) records with `discarded` feed nothing, and only the `❌` rows decide
   `discarded` (smaller, but a hand edit of the row makes the task `discarded-branch` again with no
   branch left to hand off).
3. **Skill text.** (recommended) no change: *After a merge* step 1 already runs
   `autopilot merged <ID> --cleanup --json` for whatever branch was merged, and *Close and hand off*
   already says a discarded branch is handed off like a done one; or add "— for a `done-branch` or
   `discarded-branch` task alike —" to step 1, with installed copies refreshed by `taskrail upgrade`
   and a prose assertion in `tests/test_autopilot_skill.py`.
4. **Output key.** (recommended) one new key `closed` (`"done"`, `"discarded"`, `null`) that also
   covers the recorded case with no branch left; or `discarded_at_head` (bool) mirroring
   `done_at_head`, which cannot say which status a branchless recorded merge had.

## DESIGN.md text (proposed)

Each replacement is one phrase; a phrase the file wraps across lines is replaced across them, keeping
the surrounding lines as they are.

**a. §12.1, `autopilot merged` row** — two phrases:

- replace "Reports `merged`, `via` (`ancestor`, `tree`, `patch-id`, `merge-tree`), the mainline
  `commit`, each check in `checks`, the `confirmations`, and both heads." with "Reports `merged`,
  `via` (`ancestor`, `tree`, `patch-id`, `merge-tree`), the mainline `commit`, each check in
  `checks`, `closed` (`done` or `discarded`: the status the head's row, or the recorded merge, closes
  the task with; T067), the `confirmations`, and both heads.";
- replace "A proven merge is recorded as `merged` in the lane of every run holding the task," with
  "A proven merge is recorded as `merged`, with that `status`, in the lane of every run holding the
  task,".

**b. §12.4, the `done-merged` bullet** — two phrases:

- replace "or a merge `autopilot merged`
    proved as in §12.8 and recorded in a run," with "or a merge of its ✅ branch `autopilot merged`
    proved as in §12.8 and recorded in a run, the task's newest such record deciding (*T067*),";
- replace "The record — `merged: {via, commit, head, mainline, detected}` in the lane — is evidence"
  with "The record — `merged: {via, commit, head, mainline, detected, status}` in the lane, `status`
  being `done` or `discarded` (`done` when absent) — is evidence".

**c. §12.4, the `discarded` bullet** — replace "under the same reopen rule (*T064*), so a
    discarded run task stays visible." with "under the same reopen rule (*T064*), or a recorded
    merge of its ❌ branch under the same rule as `done-merged` (*T067*), so a discarded run task
    stays visible.".

**d. §12.8, *Merge detection*** — two phrases:

- replace "and only for a head whose task row is ✅ —" with "and only for a head whose task row is ✅
  or ❌ (*T067*) —";
- replace "The ✅ row on the mainline and an `(ID)` pull request
  title confirm a merge" with "The ✅ row (❌ for a discarded task) on the mainline and an `(ID)` pull
  request title confirm a merge".
