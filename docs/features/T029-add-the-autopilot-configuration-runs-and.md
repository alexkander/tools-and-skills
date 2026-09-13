# T029 — Add the autopilot configuration, runs, and the start, lane and status commands

Kind: feature · Epic: E02 · Status: planned

Source: the accepted autopilot design, `tools/taskrail/DESIGN.md` §12 (§12.1 *Skill and CLI*,
§12.2 *Installation and opt-in*, §12.4 *State*, §12.9 *Configuration*, §12.10 *Delivery*), and
the evidence behind it in `docs/spikes/T007-design-taskrail-s-autopilot-from-existin.md`. Builds
on T017 (`done-branch`, stacked bases, `base` in the claim, `Claim.from_dict`).

## Behaviour

Today there is no `autopilot` command (`taskrail autopilot start --count 1` exits 2 with
`invalid choice: 'autopilot'`), and an `[autopilot]` table in `.taskrail/config.toml` is ignored
without any check, even `enabled = "yes"` or `max_lanes = -1` (see *Evidence*). An orchestrator
keeps the state of its lanes only in its own context.

After this change:

- **Configuration.** `.taskrail/config.toml` accepts an `[autopilot]` table, checked when the
  config loads like every other table: a wrong type or value exits 2 and names the key. Defaults
  are those of §12.9. Which keys this task parses is decision Q1.
- **Runs.** `taskrail autopilot start --count N [--kinds a,b]` creates a run file at
  `$(git rev-parse --git-common-dir)/taskrail/runs/<run>.json`, local and never committed, and
  prints the run ID (decision Q2 for its form). The file holds `id`, `started`, `owner`, `count`,
  `kinds`, `tasks` (per task: `handle`, `group`, `state`, `reason`, `updated`, `resources`),
  `handed_off` and `decisions`. It is created exclusively (`O_EXCL`), updated under the
  common-directory lock `reserve-id` already uses and replaced atomically, and read ignoring keys
  this version does not know, as claims are.
  - Unless `[autopilot].enabled` is `true`, `start` exits 5 naming `[autopilot].enabled` and
    creates nothing. That check comes first, so a disabled repository always gives the refusal
    the skill stops on, even without `--count`.
  - Without `--count`, or with a count below 1, it exits 2.
  - `--kinds` defaults to `[autopilot].kinds`; every kind named must be one the project resolves
    (defined and allowed), otherwise exit 2. An empty list means every allowed kind.
  - An invalid backlog exits 1, as for other commands.
- **`run` in the claim.** A claim gains `run`, the ID of the run that owns the lane, or `null`.
  How it gets there is decision Q3. A claim file without `run` still loads.
- **`taskrail autopilot lane <ID> --run R [--handle H] [--group G] [--state …] [--reason …]`**
  records the orchestrator's view of one lane in the run file and prints the lane. An unknown run
  or task exits 3. `--state` takes `running`, `gate`, `escalated` or `failed` (plus `handed-off`
  under decision Q4); `running` clears the reason; the rules for `--reason` and `--group` are
  decisions Q5 and Q6. `failed` changes nothing in the claim, so the task stays ineligible and its
  dependents stay blocked. `lane` does not require `enabled`: only `start` is gated.
- **`taskrail autopilot status [--run R] [--fetch]`** reports every run (decision Q7), newest
  first, and for each run task:
  - `state`, derived with this precedence: `done-merged` (the row is `✅` on the local mainline
    or `<remote>/<mainline>`), `handed-off` (done on its branch and in the run's hand-off order),
    `done-branch` (T017), then the recorded `failed`, `escalated` or `gate`, then `running` (a
    claim of this task, whatever the run file says), then `pending`, with `blocked_by`. A `❌`
    row reports `discarded` (decision Q8). A task belongs to the run when the run file lists it
    or its claim names the run.
  - the lane's `handle`, `group`, `reason` and `resources` (empty until T030), its `branch` and
    `worktree` (from the claim, else the kind's branch template through the existing lookup), and
    the claim with its `stale` reason, if any;
  - `idle_minutes`: minutes since the latest of the branch tip's commit time, the modification
    time of any file `git status` reports changed in the worktree, the claim's creation and the
    lane's last `lane` update; `silent` is true when a `running` lane is idle past
    `[autopilot].silent_minutes`. A lane stopped at a gate, escalated or failed is never silent;
  - `touched`: files changed on the branch since its fork point — `git merge-base` with the base
    the claim recorded, or with `show`'s base once the claim is released — plus uncommitted
    changes in its worktree (decision Q9). A stacked branch does not list its dependency's files;
  - `decisions` and `decisions_index`, rendered from `[autopilot]` for the task.

  Across all reported runs, `overlaps` maps each file touched by more than one lane to their IDs.
  Per run, `handoff` gives `mode` (`sequential`), `in_review` (a handed-off task not yet
  `done-merged`), `queue` (`done-branch` tasks not handed off: dependencies first, then by the
  branch tip's commit time) and `next` (the head of the queue, or `null` while a branch is in
  review). `status` reads local git only; `--fetch` first fetches each backlog mainline's remote.
  It needs no `enabled`, exits 3 for an unknown `--run`, reports no runs as an empty list with
  exit 0, and like `list` refuses an invalid backlog with exit 1 unless `--allow-invalid`.
- **Code shape for the next tasks.** A new package `taskrail/autopilot/`: `runs.py` (run files),
  `status.py` (derived states, activity, touched files, hand-off queue), `commands.py` (argparse
  registration and handlers for `start`, `lane`, `status`). T030 (`next`), T031 (`merged`) and
  T032 (`notify`) each add a module and one registration line, without restructuring. `cli.py`
  only registers the group and passes `--run` to the claim.

## Acceptance criteria

1. Without `[autopilot]`, the loaded config has `enabled` false and the other §12.9 defaults for
   the keys Q1 settles. Each of these exits 2 from any command and names the key: a non-table
   `[autopilot]`; a value of the wrong type; `max_lanes` below 1; negative `silent_minutes`;
   `handoff` other than `sequential`; a `kinds` entry that is not a kind name; and, if Q1 includes
   them, an `escalate_gates` entry not shaped `kind:stage` and a `notify_on` value outside
   `escalation`, `lane-done`, `lane-failed`.
2. `autopilot start --count 2`, with `enabled` absent or `false`, exits 5, stderr names
   `[autopilot].enabled`, and no `runs` directory exists afterwards; without `--count` it still
   exits 5.
3. With `enabled = true`: no `--count`, or `--count 0`, exits 2 and writes nothing.
4. With `enabled = true`, `start --count 2 --json` exits 0 and the run file under the git common
   directory holds the ID printed, `count` 2, `kinds` `[]`, `started`, `owner`, empty `tasks`,
   `handed_off` and `decisions`; a second `start` returns a different ID; `start` run inside a task
   worktree writes into the same common directory; the text form prints only the ID.
5. `start --kinds bug,chore` stores those kinds; `--kinds nope`, or a kind `[kinds].allowed`
   excludes, exits 2 and writes nothing; without `--kinds`, `[autopilot].kinds` is stored and
   checked the same way. With an invalid backlog `start` exits 1.
6. Per Q3, a claim made for run R records `run: "R"`, a claim for an unknown run exits 3 and
   writes no claim, a claim outside a run records `run: null`, and a claim file without `run`
   loads.
7. `lane T002 --run R --handle H1 --state gate --reason "plan gate" --json` records all four in
   the run file with `updated`; a later `lane T002 --run R --state running` keeps `H1` and clears
   the reason; `--group ui` is stored per Q6; an unknown run or task exits 3; `--reason` rules
   follow Q5; `--state failed` leaves the claim file unchanged.
8. `status --run R --json` reports each state in a scenario built for it: `pending` (listed, no
   claim), `running` (claim naming R, not yet listed by `lane`), `gate`, `escalated`, `failed`,
   `done-branch`, `handed-off` (per Q4), `done-merged` (`✅` on `main`, and separately only on
   `origin/main`), `discarded` (per Q8); a task recorded `failed` but done on its branch reports
   `done-branch`.
9. A `running` lane whose branch tip, worktree files, claim and lane update are all older than
   `silent_minutes` is `silent` with `idle_minutes` above it; modifying a file in its worktree
   makes it not silent; the same lane recorded at `gate` is never silent.
10. Two lanes changing the same file, one committed on its branch and one uncommitted in its
    worktree, both list it in `touched` and `overlaps` names it with both IDs; a lane stacked on
    an unmerged dependency does not list the dependency's files.
11. With two `done-branch` tasks, one depending on the other, `handoff.queue` lists the dependency
    first and `next` is it; after it is handed off, `in_review` is it and `next` is `null`; once
    its row is `✅` on `main`, `next` is the other task.
12. `decisions` and `decisions_index` are rendered for each task from the defaults, and from a
    custom `[autopilot].decisions` template.
13. `status` without runs prints an empty list and exits 0; `--run X` for an unknown run exits 3;
    `status` lists every run newest first per Q7; without `--fetch` it does not update
    `origin/main` after the remote moved, and with `--fetch` it does; `status` and `lane` work
    while `enabled` is `false`.
14. The whole existing suite still passes; the only change to existing output is the claim's new
    `run` key.
15. `DESIGN.md` §4 lists the implemented `[autopilot]` keys, §6.1 the claim's `run`, §7 the new
    commands and `claim`'s run option, and §12 marks what T029 implemented; `README.md` shows the
    three commands; `CHANGELOG.md` has one bullet under *Unreleased*.

## Affected areas

- `tools/taskrail/src/taskrail/autopilot/` (new package): `__init__.py`, `runs.py`, `status.py`,
  `commands.py`.
- `tools/taskrail/src/taskrail/config.py` — an `AutopilotConfig` dataclass, `Config.autopilot`,
  and its parsing and checks.
- `tools/taskrail/src/taskrail/claims.py` — `Claim.run` and the `run` argument of `claim()`.
- `tools/taskrail/src/taskrail/cli.py` — one call registering the `autopilot` group in
  `build_parser`, and passing the run to the claim (Q3).
- Reused, not changed: `stack.done_on_branch`, `stack.task_branch`, `stack._read_statuses`,
  `query.base_dict`, `query.blocked_by`, `review.resolve_remote`, `ids.id_lock`,
  `templates.render`, `claims.stale_reason`.
- `tools/taskrail/DESIGN.md` §4, §6.1, §7 and §12 (status line and the parts implemented);
  `tools/taskrail/README.md`; `tools/taskrail/CHANGELOG.md`.
- `tools/taskrail/tests/test_autopilot.py` (new), against throwaway repositories with worktrees
  and a local bare `origin`; no network.

## Out of scope

- `autopilot next`, kinds filtering at dispatch, `max_lanes` enforcement, `[[autopilot.group]]`
  and `[[autopilot.resource]]` tables, resource allocation (T030). Groups reuse T020's column
  predicate, which is still being built.
- `autopilot merged`, content-based merge detection and cleanup (T031); until then `done-merged`
  is only `✅` on a mainline ref.
- `autopilot notify` and the escalation flags in `status` — governing files touched,
  `escalate_gates` (T032).
- The `taskrail-autopilot` skill and its integration notes (T024); the core skill is unchanged.
- Removing or archiving old runs.
- T019's branch naming and T020's conditional stages.

## Open questions and risks

Decisions for the plan gate, each with a recommendation:

- **Q1 — Which `[autopilot]` keys T029 parses.** Recommended: every scalar key of §12.9
  (`enabled`, `max_lanes`, `kinds`, `governing`, `escalate_gates`, `decisions`,
  `decisions_index`, `silent_minutes`, `handoff`, `notify`, `notify_on`), with DESIGN.md §4 noting
  that `max_lanes`, `governing`, `escalate_gates`, `notify` and `notify_on` take effect with T030
  and T032; the `group` and `resource` tables stay with T030 so they reuse T020's predicate. This
  keeps `config.py` out of T030/T031/T032, which will run in parallel, where a code conflict is
  outside the known conflict classes and escalates. Alternatives: only the keys T029 uses
  (`enabled`, `kinds`, `decisions`, `decisions_index`, `silent_minutes`, `handoff`); or every key
  including the two tables.
- **Q2 — Run ID form.** Recommended: `YYYYMMDD-N`, the UTC date and the first free number that
  day, created with `O_EXCL` (e.g. `20260913-1`): short to pass as `--run`, readable, and never
  reused unless a file is deleted by hand. Alternatives: a UTC timestamp with a random suffix
  (`20260913T142501Z-3f9a`); a clone-wide counter (`R1`).
- **Q3 — How `run` reaches the claim.** Recommended: `taskrail claim <ID> --run R`, exit 3 when
  the run file does not exist; the lane brief (T024) passes it. The remote claim copy carries
  `run` too, since a run ID reveals nothing about the machine. Alternatives: `claim` reads
  `TASKRAIL_RUN` from the environment (invisible, and may leak into later sessions); or
  `autopilot lane` writes `run` into an existing claim (the orchestrator may call `lane` before
  the lane has claimed).
- **Q4 — Recording `handed-off` and run-level decisions.** §12.4 stores both in the run file, but
  no command in §12.1 writes them. Recommended: `lane <ID> --run R --state handed-off` appends the
  task to the run's hand-off order once, and exits 5 unless the task is `done-branch`; run-level
  decisions get an empty `decisions` list in the run file now and a way to write it with T024,
  when the skill defines what it records. §12.1 is updated to match. Alternatives: an
  `autopilot decision --run R --text …` command now; or letting the skill edit the JSON file.
- **Q5 — `--reason`.** Recommended: required with `failed` and `escalated` (exit 2 without),
  optional with `gate`, cleared by `running`. Alternatives: required for all three; always
  optional.
- **Q6 — `--group` before groups exist.** Recommended: T029 stores the name as given; T030
  refuses a name that is not a configured judgement group (one without `column`). Alternative:
  leave `--group` entirely to T030.
- **Q7 — Which runs `status` lists without `--run`.** §12.4 says every run in the common
  directory, which grows forever. Recommended: follow it — every run, newest first, each with
  `complete: true` once `count` of its tasks are `done-merged` — and add no pruning now.
  Alternative: only incomplete runs, with a new `--all` flag.
- **Q8 — States outside §12.1's list.** Recommended: a run task whose row is `❌` reports
  `discarded`; a stale claim still counts as `running`, with the stale reason shown. Alternatives:
  leave discarded tasks out of `status`; or report a stale claim as `pending`.
- **Q9 — What `touched` covers.** Recommended: committed changes since the fork point plus
  uncommitted changes in the worktree, since lanes commit little before their implement gate;
  overlaps include backlog files and changelogs, which the skill classifies as known conflict
  classes. Alternatives: committed changes only; or excluding backlog files from `overlaps`.

Risks:

- **Parallel lanes.** T019 changes branch lookup in `claims.py` and `cli.py`'s claim path, where
  this task adds `run` and `--run`: small textual conflicts are likely, resolved at rebase.
  `status` calls `stack.task_branch` rather than a lookup of its own, so it follows T019's change.
  T020 edits one sentence in §12.7; this task marks §12's status line and §12.1, §12.4, §12.9,
  not §12.7.
- **Cost.** `status` runs a few git commands per lane (merge-base, diff, status, log). Fine for a
  handful of lanes; not meant for hundreds.
- **Clock.** Idle time mixes commit times with local file modification times; a lane on another
  machine is out of scope (§12.10 names a remote run file as a future change).

## Evidence

On this branch's base (`a9ae799`), in a throwaway repository with `[autopilot]` holding
`enabled = "yes"` and `max_lanes = -1`:

```
$ taskrail validate
1 task(s) in 1 backlog(s): 0 error(s), 0 warning(s)
exit=0
$ taskrail autopilot start --count 1
usage: taskrail [-h] [--version] [--root ROOT]
                {validate,list,show,next,claim,release,claims,reserve-id,unreserve-id,init,upgrade,integration,self,new,done,discard,reopen,review,epic,kind}
                ...
taskrail: error: argument command: invalid choice: 'autopilot' (choose from validate, list, show, next, claim, release, claims, reserve-id, unreserve-id, init, upgrade, integration, self, new, done, discard, reopen, review, epic, kind)
exit=2
```

The suite on the base: `300 passed`.
