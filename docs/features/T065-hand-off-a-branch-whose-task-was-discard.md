# T065 — Hand off a branch whose task was discarded on it

Kind: feature · Epic: E02 · Status: planned

Source: the impact stage of [T062](../bugs/T062-treat-a-task-discarded-on-its-unmerged-b.md)
(*Proposed fix*, point 6, and *Impact*), decided in
[T062's autopilot decisions](../autopilot/decisions/T062-treat-a-task-discarded-on-its-unmerged-b.md),
diagnose gate question 6. Its dependency T053 (the hand-off queue ordered by the done commit) is
merged. No prior work: `show` reported no artifact, branch or commit for T065.

## Premise, checked on the current mainline

On `origin/main` (`33f3531`), `tools/taskrail/src/taskrail/autopilot/`:

- `status.task_state` returns `discarded-branch` for a `❌` at the task branch tip that is closed on
  neither mainline ref, before the recorded states. It never returns `handed-off` for it: that
  answer is inside the `done_on_branch` branch.
- `status.WITH_BRANCH` (`running`, `gate`, `escalated`, `failed`, `done-branch`, `handed-off`) omits
  `discarded-branch`, so `_lane_details` reports no `touched` files for it and it takes part in no
  `overlaps`.
- `status._handoff` queues only rows whose state is `done-branch`, and takes `in_review` only from a
  row whose state is `handed-off`; `_done_time` reads only `stack.done_on_branch` and looks for the
  commit that turns the row `✅`.
- `commands.cmd_lane` refuses `--state handed-off` with exit 5 unless the task is in
  `stack.done_on_branch`.
- `escalation.MOVED_ON` is `("done-branch", "handed-off")`.
- `tests/test_autopilot_next.py::test_a_task_discarded_on_its_unmerged_branch_is_closed_and_not_dispatched_again`
  asserts `touched == []` and an empty hand-off queue for the discarded branch, marked "not queued
  yet".

Found while checking: the hand-off itself runs `taskrail review <ID> --json` and
`review <ID> --publish` (skill, *Close and hand off* steps 1–2), and `cli.cmd_review` refuses any task
whose row is not `✅` on the branch (`run \`taskrail done <ID>\` first`, exit 5). A discarded branch
queued by `status` could not be published without it (question 2).

The premise holds.

## Behaviour

After this change, a task discarded on its own branch goes through the autopilot's hand-off like a
task done there:

- **Queued.** `autopilot status`'s `handoff.queue` holds the `discarded-branch` tasks not yet handed
  off, together with the `done-branch` ones, in the same order: dependencies first, then by the
  author time of the task's *closing* commit — the latest first-parent commit on its branch (local,
  else remote) and off its mainline that turns its row `✅` or, for a discarded task, `❌`. A rebase
  or a later commit on the branch leaves that time alone, as for `done` (T053).
- **Handed off.** `autopilot lane <ID> --run R --state handed-off` accepts a `discarded-branch` task
  and appends it to the run's hand-off order. Its state stays `discarded-branch` (question 1): the
  hand-off is shown by `handoff`, where `in_review` names it — the first task of the hand-off order
  that is still `handed-off` or `discarded-branch` — until its `❌` reaches a mainline ref and it reads
  `discarded`; it leaves the queue. It keeps using no lane and freeing its place in the run's count,
  so `autopilot next` needs no change.
- **Touched files, no governing flag.** A `discarded-branch` task reports `touched` (the files changed
  since the fork point, plus uncommitted ones), takes part in `overlaps` and `known_overlaps`, and
  lists `governing_touched`, but `governing` is not in its `escalation`: it has moved on, as a
  `done-branch` task has (T049).
- **Published.** `taskrail review <ID>` runs for a task whose row is `❌` on its branch, as for `✅`;
  without `--type`, the pull request title's type is `chore` for a discarded task rather than the
  kind's `commit_type` (question 2).

## Acceptance criteria

1. A lane that claims a task in a run, discards it and commits the discard reads `discarded-branch`
   in `autopilot status` with `touched` listing the files its branch changed (at least `TODO.md`) and
   `handoff.queue == [<ID>]`, `handoff.next == <ID>`.
2. `autopilot lane <ID> --run R --state handed-off` exits 0 for that task and lists it in
   `handed_off`; afterwards `status` reports the state `discarded-branch`, `handoff.in_review == <ID>`,
   the task out of `queue`, and `next` `null`.
3. Once the branch's `❌` reaches `origin/main` (pushed, local mainline not pulled, fetched), the task
   reads `discarded`, and `in_review` is `null` again with the next queued task in `next`.
4. `autopilot lane <ID> --state handed-off` still exits 5 for a task that is neither `done-branch` nor
   `discarded-branch` (a `running` one), with a message naming both states.
5. A `done-branch` task and a `discarded-branch` task are queued by the author time of their closing
   commit: a discard committed earlier than a done comes first, and a later commit on the discarded
   branch does not move it.
6. A `discarded-branch` task whose `touched` files match a `governing` entry lists them in
   `governing_touched` with an empty `escalation`, while the same lane before its discard (`running`)
   has `governing` in `escalation`.
7. `taskrail review <ID> --json` on the branch of a task discarded there exits 0, reports `head` and
   `rebase` as for a done task, and its `pull_request.title` starts with `chore` (and with `--type fix`,
   `fix`); a task still `⬜` on its branch is refused with exit 5 as before, naming `done` and `discard`.
8. The T062 test in `tests/test_autopilot_next.py` asserts the new `touched` and queue for its
   discarded branch instead of the empty ones (question 3).
9. All tests pass: `uv run --directory tools/taskrail pytest -q`.

All criteria are verified by pytest, on the `pilot` fixture of `tests/test_autopilot.py` next to the
hand-off queue tests (section 13), and on `task_repo` in `tests/test_review.py` for criterion 7.

## Affected areas

- `tools/taskrail/src/taskrail/autopilot/status.py`
  - `WITH_BRANCH`: add `discarded-branch`.
  - `_done_time` → `_closed_time`: read the task from `stack.done_on_branch` or
    `stack.discarded_on_branch`, and look for the commit that turns the row into that status.
  - `_handoff`: `waiting` takes `done-branch` rows and `discarded-branch` rows not in
    `run["handed_off"]`; `in_review` accepts a `discarded-branch` row as well as `handed-off`.
  - `task_state` is **not** changed.
- `tools/taskrail/src/taskrail/autopilot/escalation.py`: `MOVED_ON` adds `discarded-branch`.
- `tools/taskrail/src/taskrail/autopilot/commands.py` `cmd_lane`: the handed-off check accepts
  `stack.discarded_on_branch`; message
  `<ID> is neither done nor discarded on its branch (done-branch or discarded-branch), so it cannot be handed off`.
- `tools/taskrail/src/taskrail/cli.py` `cmd_review`: the status check accepts `Status.DISCARDED`, the
  default type is `chore` for it, and the refusal reads
  `<ID> is pending on this branch; run \`taskrail done <ID>\` or \`taskrail discard <ID>\` first`
  (only with question 2 approved).
- Tests: `tests/test_autopilot.py` (criteria 1–6), `tests/test_review.py` (criterion 7, and the
  existing refusal test's message), `tests/test_autopilot_next.py` lines 611 and 613 (criterion 8).
- Skill source `tools/taskrail/src/taskrail/skills/taskrail-autopilot/` (question 5), then
  `.taskrail/bin/taskrail upgrade` for `.claude/skills/` and `.taskrail/installed.json`, with a prose
  assertion in `tests/test_autopilot_skill.py`.
- `tools/taskrail/DESIGN.md` §7.1, §12.1, §12.4, §12.6 (question 4, exact text below).
- `tools/taskrail/CHANGELOG.md`: one *Unreleased* bullet. `docs/features/README.md`: this row.

Not touched, as the touch map gives them to T064 or T063: `autopilot/dispatch.py` (`next_lanes`,
`OCCUPYING`, `COUNTED`), `status.done_on_mainline`/`discarded_on_mainline`, the skill's *Close and
hand off* step 1, *After a merge* step 2, gate-review's *Never approve with failing checks* and
*Rebase* bullets, and `references/lane-brief.md`.

## Out of scope

- **`autopilot merged` for a discarded branch.** Its content detection needs `done_at_head`, and
  `recorded_merges` feeds `done_on_mainline` whatever the row says, so recording a proven merge of a
  discard would read `done-merged` and count toward `complete`. `status` does not need it: a squash
  merge brings the `❌` row to `<remote>/<mainline>`, which `discarded_on_mainline` reads, and that
  clears `in_review`. Cleanup (worktree, branch, claim) after the merge is left to a follow-up
  (question 6).
- A new state for a handed-off discard, and any change to `autopilot next` or the run's count.
- The plain `taskrail` skill's close step, which names `done` only.

## Open questions and risks

- **The state does not say that a discarded branch was handed off.** Only `handoff.in_review` and
  `run.handed_off` do. A resumed session reading rows alone could take a handed-off discard for one
  waiting; the skill's *Resume a run* step points it at `handoff.queue` instead (question 5).
- **A discard's pull request carries its artifact link and title** as a done one does; only the type
  differs. The orchestrator can still pass `--type`.
- **Conflicts.** `tests/test_autopilot_next.py` is T064's expected test file; the two assertions
  changed here sit in T062's test, which T064 is not expected to edit. The `DESIGN.md` §12.1
  `autopilot status` row is shared by many tasks' phrases; each replacement below is one phrase.

## Questions for the plan gate

1. **State after hand-off.** (A, recommended) keep `discarded-branch`, with `handoff.in_review` naming
   it; no change to `task_state`, `dispatch.py` or §12.7. (B) read `handed-off`, as a done branch does:
   needs `COUNTED` in `dispatch.py` to tell a discarded hand-off apart (T064's area), or a handed-off
   discard would retake its place in the run's count. (C) a new state such as `discarded-handed-off`:
   nothing in `dispatch.py` counts it, but it adds a state to every list in §7, §12.1, §12.4 and
   §12.7.
2. **`taskrail review` for a discarded task.** (recommended) include it here — accept `❌` in
   `cmd_review` and default the type to `chore` for a discard — since without it the queued branch
   cannot be published; or keep `review` as is and open a follow-up; or include it but keep the
   kind's `commit_type` as the default type.
3. **T062's test in `tests/test_autopilot_next.py`.** (recommended) change its two assertions
   (`touched == []` → `["TODO.md"]`, `queue == []` → `["T001"]`) here, since they state the behaviour
   this task replaces; or leave the file to T064 and ask it to change them.
4. **`DESIGN.md` texts a–f** below: approve as written, or drop or change parts.
5. **Skill text** (source `taskrail-autopilot`, refreshed with `taskrail upgrade`): approve as
   written, or leave the skill unchanged.
   - `SKILL.md` *Escalate*, condition 1 — replace "`status`, until the task is `done-branch`; the
     close review checks `governing_touched` after" with "`status`, until the task is `done-branch`
     or `discarded-branch`; the close review checks `governing_touched` after".
   - `SKILL.md` *Close and hand off*, a new paragraph between the opening paragraph and step 1:
     "A lane whose task was discarded stops after `taskrail discard` the same way; its task reads
     `discarded-branch`, is queued and handed off like a `done-branch` one, and is published with
     `--type chore`. Once handed off it keeps reading `discarded-branch`: `handoff.in_review` says it
     is in review."
   - `SKILL.md` *Resume a run*, step 4 — replace "a `done-branch` task has its close reviewed and is
     handed off" with "a `done-branch` or `discarded-branch` task in `handoff.queue` has its close
     reviewed and is handed off".
   - `references/gate-review.md` *Close*, third bullet — replace "`status` no longer flags a
     `done-branch` task" with "`status` no longer flags a `done-branch` or `discarded-branch` task".
6. **Follow-up** (recommended: open it at the verify or close stage with `taskrail new` on this
   branch): feature, E02, *Detect and clean up a merged branch whose task was discarded on it* —
   `autopilot merged` proves the merge of a `❌` branch, records it without reading `done-merged`, and
   `--cleanup` removes its worktree and branch; verified by a pytest that discards on a branch,
   squash-merges it and runs `merged --cleanup`. Alternatives: record only, or no follow-up.

## DESIGN.md text (proposed; question 4)

**a. §7.1, step 1** — replace "only once the task is done there;" with "only once the task is done or
discarded there (T065);".

**b. §7.1, title paragraph** — replace "the type from the kind's `commit_type` or `--type`," with "the
type from `--type`, else `chore` for a task discarded on the branch, else the kind's `commit_type`
(T065),".

**c. §12.1, `autopilot lane` row** — replace "`handed-off` appends the task to the run's hand-off
order once, and exits 5 unless the task is `done-branch`." with "`handed-off` appends the task to the
run's hand-off order once, and exits 5 unless the task is `done-branch` or `discarded-branch` (T065)."

**d. §12.1, `autopilot status` row** — two phrases:

- replace "`handoff`: `in_review`, `queue` (dependencies first, then in completion order: by the
  author time of the task's done commit — the latest first-parent commit on its branch, local or else
  remote, that turns its row ✅ —" with "`handoff`: `in_review` (the first task of the hand-off order
  still `handed-off` or `discarded-branch`), `queue` (the `done-branch` tasks and the
  `discarded-branch` ones not yet handed off; T065 — dependencies first, then in completion order: by
  the author time of the task's closing commit — the latest first-parent commit on its branch, local
  or else remote, that turns its row ✅, or ❌ for a discarded task —";
- replace "and the task is not yet `done-branch`," with "and the task is not yet `done-branch` or
  `discarded-branch`,".

**e. §12.4, the `discarded-branch` bullet** — replace "the lane has ended, it uses no lane and frees
its place, and it is not in the hand-off queue;" with "the lane has ended, it uses no lane and frees
its place; its branch is queued and handed off like a `done-branch` one and keeps this state once
handed off, while `handoff.in_review` names it (*T065*);".

**f. §12.6, *Governing paths*** — replace "A task that has moved on (`done-branch` and `handed-off`)
keeps its" with "A task that has moved on (`done-branch`, `handed-off` and `discarded-branch`; T065)
keeps its".
