# T048 — Add autopilot close to abandon a run

Kind: feature · Epic: E02 · Status: plan

Source: finding F7 of the
[T033 trial](../spikes/T033-trial-the-autopilot-on-a-real-backlog-wi.md) (*Findings* and
*Recommendation*, follow-up row T048). Builds on T029 (run files, `autopilot lane`, `decision`,
`status`, `claim --run`) and T030 (`autopilot next`, dispatches and resources). The gate decisions
are recorded in `docs/autopilot/decisions/T048-add-autopilot-close-to-abandon-a-run.md`.

## Behaviour

Today a run cannot be ended by anyone. In the T033 trial a conversation rewind restored the
orchestrator's conversation but not its run file: run `20260914-1` still recorded three dispatched
tasks holding all three lanes, and the rewound session had to start a second run and ask what to do.
A dispatch only frees its lane after `[git].claim_grace_minutes`, a resource value only when a later
`next --run` finds its lane ended, and `status` keeps listing the dead run forever, since runs are
never removed.

After this change, `taskrail autopilot close <R> --reason <text> [--json]` abandons run `R`:

1. **Records the close** in the run file as `closed: {at, by, reason}` — the UTC time, the caller's
   owner name (`claims.default_owner()`), and the trimmed reason. The run file stays on disk; runs are
   still never removed.
2. **Releases the run's dispatches and resources**, under the common-directory lock: every lane of
   the run loses its `dispatched` time and its `resources`. Each lane that had either is reported in
   `released` as `{id, dispatched, resources}` with the values it held.
3. **Leaves claims alone.** A claim is a lane's lock on work in a worktree, not run state. Live
   claims naming the run are reported in `claims` (`{id, owner, branch, worktree}`), so the human can
   decide whether to `taskrail release` each one; `close` never releases one.
4. **Hides the run** from the commands that plan work:
   - `autopilot next`, with or without `--run`, ignores closed runs entirely: their lanes do not
     occupy `max_lanes`, count toward groups, hold resource values, or make a task "dispatched in run
     …"; nothing in them is released or written;
   - `autopilot status` without `--run` lists only open runs, so `overlaps` ignore closed ones too;
     `status --run R` still shows a closed run, with its `closed` record (and `closed …` in the text
     form's run line), so its history stays readable.
5. **Refuses new work in a closed run** with exit 5: `autopilot next --run R`, `autopilot lane <ID>
   --run R`, `autopilot decision --run R`, and `taskrail claim <ID> --run R` (checked before the
   claim is taken, so nothing is written).
6. **Exit codes:** 0 closed; 2 for an empty `--reason`; 3 for an unknown run; 4 when the lock cannot
   be taken; 5 when the run is already closed (nothing changes). `close` needs neither
   `[autopilot].enabled` nor a valid backlog: abandoning a run must work in a repository that has
   since disabled the autopilot or broken its backlog.

Unchanged: `autopilot merged` still records a proven merge in a closed run that holds the task, and
recorded merges in closed runs still count toward `done-merged` (they are evidence, not lane state);
`autopilot notify` is unaffected.

## Acceptance criteria

Each is verified by pytest on fixture repositories and run files (`tests/test_autopilot_close.py`).

1. `autopilot close R --reason …` writes `closed` with `at`, `by` and `reason` into the run file, keeps
   every other key (unknown keys included), and exits 0; `--json` reports `run`, `closed`,
   `released` and `claims`.
2. After closing a run with dispatched lanes, every lane of the run has `dispatched` null and empty
   `resources`, and `released` lists each of those lanes with the dispatch time and values it held.
3. A live claim naming the run is still present after `close`, and is listed in `claims`.
4. With run A closed while it held all `max_lanes` dispatches and every resource value, `autopilot
   next --run B` for an open run B dispatches up to `max_lanes` tasks — including the tasks A had
   dispatched — and gets the first resource values again; a preview `next` sees the same free lanes.
5. A task claimed with `--run A`, a group member recorded in A, and a `gate` lane recorded in A do not
   occupy a lane or a group place in `next` once A is closed.
6. `autopilot status` without `--run` omits a closed run (and its files from `overlaps`);
   `status --run A` shows it with its `closed` record, and the text form says `closed`.
7. `next --run A`, `lane <ID> --run A`, `decision --run A` and `claim <ID> --run A` exit 5 for a closed
   run A and write nothing (no run-file change, no claim).
8. `close` exits 3 for an unknown run, 2 for an empty or blank `--reason`, and 5 for a run already
   closed, leaving the first `closed` record unchanged.
9. `close` works with `[autopilot].enabled = false` and with an invalid backlog.
10. A merge recorded in a closed run still makes its task `done-merged` in `status` of an open run
    holding it.

## Affected areas

- `tools/taskrail/src/taskrail/autopilot/runs.py`: `closed` defaulted to null in `_normalize`; an
  `is_closed(run)` helper; a `close(run, reason, owner, now)` function that records the close and
  clears the lanes, returning what it released.
- `tools/taskrail/src/taskrail/autopilot/commands.py`: new `cmd_close` and its `add("close", …)` in
  `register`; a closed-run refusal (exit 5) at the start of `cmd_lane`, `cmd_decision` and
  `cmd_next`; the default listing of `cmd_status` filtered to open runs; the run line of
  `_status_text`. Not touched: `_gate_problem` and `--gate` help (T050), `_escalation_text` (T049).
- `tools/taskrail/src/taskrail/autopilot/dispatch.py`: `next_lanes` drops closed runs from
  `every_run` before deriving states, and raises for a `run_id` that is closed (the lock-held
  re-check behind `cmd_next`'s refusal).
- `tools/taskrail/src/taskrail/autopilot/status.py`: only the dictionary `run_status` returns gains
  `closed`. Not touched: `_handoff`, `_done_time` (T053), `task_state`.
- `tools/taskrail/src/taskrail/cli.py`: `cmd_claim`'s existing `--run` check refuses a closed run
  with exit 5.
- `tools/taskrail/tests/test_autopilot_close.py`: new.
- `tools/taskrail/DESIGN.md` §12.1 (a new `autopilot close` table row), §12.4 (the `closed` run-file
  key), §12.7 (lanes counted across open runs) — exact text proposed at the plan gate.
- `tools/taskrail/src/taskrail/skills/taskrail-autopilot/SKILL.md` and its installed copies, only if
  the plan gate approves the one-line command reference (question at the gate).
- `tools/taskrail/CHANGELOG.md` (one bullet), `docs/features/README.md` (index row).

## Out of scope

- Releasing claims, removing worktrees or branches of a closed run's lanes: that stays
  `taskrail release` and `autopilot merged --cleanup`, on a human's decision.
- Reopening a closed run, or deleting run files.
- Skill text on dispatch expiry and on resuming a run from a new session (T055).
- Detecting a stale orchestrator automatically, or closing a run on a timer.
- `autopilot notify` and `autopilot merged` behaviour for closed runs.

## Open questions and risks

- **Claims left behind.** A lane that claimed before the close keeps its claim, so its task stays out
  of `next`'s candidates although its lane no longer counts. That is the intended trade: the claim
  protects the worktree's work, and `close` reports it.
- **Race with a claiming lane.** `claim --run R` reads the run before claiming; a close landing in
  between leaves a claim naming a closed run, which `next` then ignores as a lane and `close`'s
  report would have missed. Accepted: the window is one command, and the claim still shows in
  `taskrail claims`.
- **Merge with sibling lanes.** T049, T050 and T053 edited other functions of `commands.py` and
  `status.py` and other rows of DESIGN §12.1; this plan adds a row and keeps to separate hunks, so
  a rebase should see at most adjacent-line conflicts in the table.
