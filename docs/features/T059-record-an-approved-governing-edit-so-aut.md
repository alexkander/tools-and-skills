# T059 — Record an approved governing edit so autopilot status stops flagging it

Kind: feature · Epic: E02 · Status: plan

Source: finding F9 of the autopilot trial
([T033](../spikes/T033-trial-the-autopilot-on-a-real-backlog-wi.md), Findings table and
Recommendation), and question 4 of T049's plan gate
([decision record](../autopilot/decisions/T049-stop-flagging-governing-paths-once-a-tas.md)).
T049 made `autopilot status` drop the `governing` reason once a task is `done-branch`; this task
covers the gates before that. No prior work: `show` reported no artifact, branch or commit for T059.

## Premise, checked on the current mainline

On `origin/main` (`ff8e4e6`), `escalation.flags()` adds `governing` to `escalation` whenever
`governing_touched` is not empty and the state is not in `MOVED_ON` (`done-branch`, `handed-off`).
Nothing a caller can record changes that: the run file's lane keys are `handle`, `group`, `state`,
`reason`, `gate`, `updated`, `dispatched` and `resources`, and no `autopilot` command stores an
approval. A lane whose governing edit the human approved at one gate is therefore flagged again at
every later gate until `done`. The premise holds.

## Behaviour

After this change the orchestrator can record that the human approved a lane's governing edit, and
`autopilot status` stops raising it — until the approved content changes:

- **`taskrail autopilot approve-governing <ID> --run R [--path P]…`** records, in the task's lane
  of run R, each approved path with the blob ID of its current content, under the new lane key
  `governing_approved` (`{path: blob ID}`). Without `--path` it approves every path in the task's
  current `governing_touched`; with `--path` only the named ones. The blob ID is
  `git hash-object` of the file in the lane's worktree when that worktree exists — so an
  uncommitted edit is approved as it stands — else the blob at the branch tip; a path absent from
  both is recorded as `null` (an approved deletion). A later approval of a path replaces its blob
  ID; other approved paths are kept.
- **`autopilot status`** adds `governing_approved` to each task row: the files in
  `governing_touched` whose content, computed the same way, still has the recorded blob ID. The
  `governing` reason is in `escalation` only when some `governing_touched` file is not in
  `governing_approved` (and, as before, the task is not yet `done-branch`). The text form's
  `ESCALATE: governing …` names only the files not approved.
- **A later change flags again.** Editing an approved file (committed or not), deleting it,
  recreating a deleted one, or touching another governing path brings `governing` back, naming
  only those files. Re-approving clears it again.
- **The skill uses it.** The `taskrail-autopilot` skill's *Escalate* section tells the
  orchestrator to run `approve-governing` once the human's answer approves an edit and the files
  match it, and not to escalate again a flagged file whose applied content the task's record
  already shows approved, but to record the approval instead. The gate review's *Close* bullet
  uses `governing_approved` to find a governing file changed after its approval.

## Acceptance criteria

1. `approve-governing <ID> --run R` with no `--path` records every path of the task's current
   `governing_touched` with its blob ID in the lane's `governing_approved` in the run file, reports
   them in its JSON (`approved`, plus the lane's full `governing_approved`), and exits 0.
2. After that approval, `status` for the task in `running`, `gate`, `escalated` and `failed` keeps
   `governing_touched`, lists the same files in `governing_approved`, and has no `governing` in
   `escalation`; `escalate-gate` is unaffected; the text form prints no `ESCALATE: governing`.
3. Changing an approved file afterwards — a committed change, an uncommitted change, or deleting
   it — removes it from `governing_approved` and brings `governing` back into `escalation`; the
   text form names only that file.
4. A governing path first touched after the approval flags the task and is named alone in the
   text form, while the approved file stays in `governing_approved`.
5. `--path P` approves only P; a `--path` not in the task's `governing_touched` exits 2 and records
   nothing.
6. Approving again after a change records the new blob ID and clears the flag.
7. An approval of a committed file still holds after the lane's worktree is removed (the blob at
   the branch tip matches), and `governing_approved` is still reported at `done-branch`.
8. An unknown run, an unknown task, or a task outside the run exits 3; a task with an empty
   `governing_touched` exits 5; neither records anything.
9. `escalation.flags()` takes the approved files: unit tests show `governing` leaves `escalation`
   only when every governing file is approved, in every state before `done-branch`.
10. The `taskrail-autopilot` skill source names `approve-governing` in its *Escalate* section and
    `governing_approved` in the gate review's *Close* section; a prose test in
    `test_autopilot_skill.py` asserts both, and the installed copies are refreshed with
    `taskrail upgrade`.
11. All tests pass: `uv run --directory tools/taskrail pytest -q`.

Criteria 1–8 are verified by pytest with the `pilot` fixture repository of `test_autopilot.py`
(its own `[autopilot].governing`, a lane worktree, commits and uncommitted edits under a governing
path, `pilot.finish`), not with this repository's configuration, which T060 empties.

## Affected areas

Chosen to stay out of the functions and phrases the unmerged branches change (touch map).

- `tools/taskrail/src/taskrail/autopilot/approve.py` — **new module**: `cmd_approve_governing` and
  its `add_arguments`, as `merged.py` does. It loads the run and the task, computes the task's row
  with `status.run_status`, and writes `governing_approved` under `runs.update`.
- `tools/taskrail/src/taskrail/autopilot/commands.py` — two import lines at the top, one
  `add("approve-governing", …)` block in `register()` placed right after the `decision` block (T048
  adds its `close` block before `merged_arguments`, at the end), and `_escalation_text()` naming
  only the files not approved (T049's function; no unmerged branch edits it). `cmd_lane`,
  `cmd_decision`, `cmd_next`, `cmd_status` and `_status_text` are not touched.
- `tools/taskrail/src/taskrail/autopilot/escalation.py` — `flags()` gains an `approved` argument
  and returns `governing_approved`.
- `tools/taskrail/src/taskrail/autopilot/status.py` — a new `current_blobs()` helper, one key
  (`governing_approved`) in the dict `_lane_details()` returns, and `_flag_escalations()` passing
  it to `flags()`. `task_state`, `_closing` (T054) and `status()` (T051) are not touched.
- `tools/taskrail/src/taskrail/autopilot/runs.py` — **not changed**: the lane key is read with
  `.get()` and a type check, so `_lane` and `_normalize` (T048) stay as they are; unknown keys are
  already kept.
- Tests: a new `tools/taskrail/tests/test_autopilot_governing.py` (criteria 1–9), and one appended
  function in `tests/test_autopilot_skill.py` (criterion 10).
- Skill sources: `SKILL.md` *Escalate* section (condition 1 and the paragraph after the list; T055
  and T051 edit other sections) and the *Close* bullet of `references/gate-review.md`; then
  `.claude/skills/taskrail-autopilot/` and `.taskrail/installed.json` through
  `.taskrail/bin/taskrail upgrade`.
- `tools/taskrail/DESIGN.md` §12.1 (a new `approve-governing` row; the `escalation` phrase of the
  `status` row), §12.4 (the run-file lane bullet and key list) and §12.6 (*Governing paths*) — a
  governing path: the exact text is put to the gate and applied only once approved.
- `tools/taskrail/CHANGELOG.md` — one *Unreleased* bullet.
- `docs/features/README.md` — this document's row.

## Out of scope

- Recording who approved and why: that stays in the task's decision record; the run file keeps
  only what `status` computes from.
- Approving an `escalate_gate` or any other reason of §12.6.
- Refusing `approve-governing` on a run `autopilot close` ended: T048 (unmerged) adds closed runs.
  An approval in a closed run is harmless, since `status` hides a closed run unless it is named;
  whether to refuse it once both are merged is a question below.
- Changing `touched`, `overlaps`, the hand-off queue, or the behaviour at `done-branch` (T049).
- Symbolic links and files git filters differently per worktree: the blob ID is what
  `git hash-object` reports for the path, which follows git's own attribute handling.

## Open questions and risks

- **What is approved is content, not a path.** An approval recorded before the lane applies the
  approved text does nothing (the file is not yet in `governing_touched`, so the command exits 5);
  the orchestrator records it at the gate where the applied file matches the approved text. The
  skill text says so.
- **Race with a working lane.** The blob ID is read when the command runs; the orchestrator runs it
  while the lane is stopped at a gate, as it already commits decision records then.
- **Cost.** `status` hashes only files that have a recorded approval and are in `touched`: one
  `git hash-object` call per lane with approvals, or one `git rev-parse` per such file without a
  worktree.
- **Textual conflicts at hand-off.** The `autopilot status` row of DESIGN.md §12.1 is one long
  line that T051, T053 and T054 also edit, and the §12.4 key-list lines are rewritten by T048;
  each edit is a phrase-level addition resolved by keeping every branch's phrase.

## DESIGN.md text proposed (governing — applied only once approved)

**§12.1, new table row** — inserted right after the `autopilot decision …` row:

> | `autopilot approve-governing <ID> --run R [--path P]…` | *Implemented (T059).* Records that the human approved a lane's governing edit (§12.6), so `status` stops flagging it at later gates. Without `--path` it approves every path in the task's current `governing_touched`; with `--path` only those, and exit 2 for a path not in it. For each path it stores in the lane's `governing_approved` the blob ID of the path's current content: `git hash-object` of the file in the lane's worktree when that worktree exists, else the blob at the branch tip, or `null` for a path absent from both. A later approval of a path replaces its blob ID; other approved paths are kept. Exit 3 for an unknown run, an unknown task or a task outside the run, 4 when the lock cannot be taken, 5 when the task's `governing_touched` is empty; needs neither `enabled` nor a valid backlog. |

**§12.1, `autopilot status` row** — replace

> and `escalation` (`governing` when `governing_touched` is not empty and the task is not yet
> `done-branch`, `escalate-gate` when `escalate_gate` is set, or empty; T049); the text form adds
> `ESCALATE: …`, naming the reasons in `escalation`, to a flagged lane.

with

> `governing_approved` (the `governing_touched` files whose content still has the blob ID
> `approve-governing` recorded; T059) and `escalation` (`governing` when a `governing_touched`
> file is not in `governing_approved` and the task is not yet `done-branch`, `escalate-gate` when
> `escalate_gate` is set, or empty; T049); the text form adds `ESCALATE: …`, naming the reasons in
> `escalation` and only the governing files not approved, to a flagged lane.

(The `and` before `escalation` moves: the list reads "… `escalate_gate` (…), `governing_approved`
(…) and `escalation` (…)".)

**§12.4, run-file bullet** — replace

> - per task: the lane handle, the group, `gate`, `escalated` or `failed` with a reason, when
>   `next` dispatched it, and the allocated resources;

with

> - per task: the lane handle, the group, `gate`, `escalated` or `failed` with a reason, when
>   `next` dispatched it, the allocated resources, and the governing paths the human approved with
>   their blob IDs (T059);

**§12.4, key list** — replace `` `dispatched`, `resources`) `` with
`` `dispatched`, `resources`, `governing_approved`) `` in "per task: `handle`, `group`, …".

**§12.6, *Governing paths* bullet** — append after "…which escalates any `governing_touched` path
the task's record does not show escalated.":

> Before that, an edit the human approved stops flagging once the orchestrator records it with
> `autopilot approve-governing`, which stores each approved path with the blob ID of its content:
> `status` lists a file whose content still has that blob ID in `governing_approved` and leaves it
> out of the `governing` reason, while a later change to the file, its deletion, or a governing
> path not approved flags the task again (T033 finding F9; T059).

## Skill text proposed

**`SKILL.md`, *Escalate*, condition 1** — replace

> 1. a lane's branch touches a governing path (`governing` in `escalation` in `status`, until the
>    task is `done-branch`; the close review checks `governing_touched` after that);

with

> 1. a lane's branch touches a governing path not yet approved (`governing` in `escalation` in
>    `status`, until the task is `done-branch`; the close review checks `governing_touched` after
>    that);

**`SKILL.md`, *Escalate*, after** "Record the answer in the task's record, naming who gave it." —
add:

> When the answer approves a governing edit, read the edited files, and once they hold what was
> approved, run `taskrail autopilot approve-governing <ID> --run <R>` (with `--path` for each file
> when the answer covers only some), so later gates do not raise it again. A flagged file whose
> content the task's record already shows approved is not a new escalation: record the approval
> the same way. A later change to an approved file flags it again.

**`references/gate-review.md`, *Close*** — replace

> - Every path in the task's `governing_touched` was escalated and answered in its decision record.
>   `status` no longer flags a `done-branch` task, so a governing path changed after the last gate
>   escalates now.

with

> - Every path in the task's `governing_touched` was escalated and answered in its decision record.
>   `status` no longer flags a `done-branch` task, so a governing path changed after the last gate
>   escalates now; a path missing from `governing_approved` was never approved or changed after
>   its approval.
