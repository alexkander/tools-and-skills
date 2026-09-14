# T047 — Keep a stacked task's fork point after done

Kind: feature · Epic: E02 · Status: planned

Source: finding F1 of `docs/spikes/T033-trial-the-autopilot-on-a-real-backlog-wi.md` (Findings
table and Recommendation), and `tools/taskrail/DESIGN.md` §12.4 (*Claims*) and §12.8 (*Stacked
dependents*). Builds on T017 (`base` in the claim) and T031 (`autopilot merged` and its
`dependents`).

## Problem

A stacked dependent's fork point — the dependency commit its branch started from — lives only in
its claim's `base.commit`, and `taskrail done` releases the claim. `autopilot merged <dependency>`
then falls back to `git merge-base <dependent> <dependency head>`. That fallback is right only while
the dependency's branch is unchanged. The autopilot's own hand-off (§12.8) rebases the dependency
onto a mainline carrying every earlier merge before publishing it, so for every stacked task in a
run the merge-base drops back to an old mainline commit: the dependent is reported
`stacked: false`, `fork_source: merge-base`, `command: null`, and the orchestrator has to work out
`git rebase --onto` itself. In the T033 trial, T002 (stacked on T001) got exactly that output after
T001 was rebased onto T003's merge.

## Behaviour

- **The run keeps the claim's base.** `taskrail claim <ID> --run R`, when it creates the claim,
  already lists the task in run R's file; it now also stores the claim's `base` —
  `{onto, commit, dependency}`, or `null` when the claim has none — in that lane as `base`. The run
  file is never removed and `done` does not touch it, so the fork point outlives the claim. A claim
  without `--run` writes no run file, as today; an `already held` claim rewrites nothing.
- **`autopilot merged` reads it before `merge-base`.** For each stacked dependent the fork point is
  the first of:
  1. the live claim's `base.commit` (`fork_source: "claim"`), as today;
  2. **new:** the `base.commit` kept in a run's lane for the dependent, reading runs newest first
     (`fork_source: "run-base"`);
  3. `git merge-base <dependent> <dependency head>` (`"merge-base"`), as today;
  4. the `head` a run recorded for the dependency (`"run"`), as today.

  Sources 1 and 2 count only when their `base.dependency` is the merged task, the commit exists,
  and the dependent's head still contains it — so a dependent already rebased gets no second
  rebase command, exactly as the claim source behaves today.
- **Result.** A dependency rebased at hand-off and then squash-merged still yields
  `stacked: true`, `fork: <base.commit>`, `command: "git rebase --onto <onto> <base.commit>"` for a
  dependent claimed with `--run`, and running that command leaves only the dependent's own commits
  on top of the mainline. No JSON key is added or removed; `fork_source` gains the value
  `run-base`.

## Acceptance criteria

1. `claim <ID> --run R` that creates a claim writes `tasks.<ID>.base` in run R equal to the claim's
   `base` (`onto`, `commit`, `dependency`); for a task claimed from a dependency branch,
   `base.dependency` is that dependency and `base.commit` its tip. An `already held` claim with
   `--run` leaves the lane's `base` as it was, and a claim without `--run` writes no run file.
2. **F1 scenario, scripted with git:** T001 is finished; T002 is claimed with `--run` from T001's
   branch, worked and marked done (claim released); an unrelated commit lands on the mainline; T001
   is rebased onto the new mainline, force-pushed and squash-merged. `autopilot merged T001 --run R`
   reports T002 with `stacked: true`, `fork` equal to T001's pre-rebase tip, `fork_source:
   "run-base"`, `onto: "origin/main"` and `command: "git rebase --onto origin/main <fork>"`; running
   that command in T002's worktree leaves exactly T002's own commits in `origin/main..HEAD`. This
   test is shown failing on the base commit (`stacked: false`, `fork_source: "merge-base"`) before
   the fix.
3. After that rebase, `autopilot merged T001` again reports T002 `stacked: false` with no command:
   the kept base no longer counts once the dependent's head does not contain it.
4. A run lane `base` is ignored — and the older sources apply — when its `dependency` is another
   task, when its `commit` does not exist in the repository, or when the lane has no `base` (a run
   file written before this change).
5. A live claim's `base` still takes precedence (`fork_source: "claim"`), and a dependent claimed
   without `--run` still falls back to `merge-base` and then the run-recorded head, as today.
6. The whole suite passes: `uv run --directory tools/taskrail pytest -q`.

## Affected areas

- `tools/taskrail/src/taskrail/cli.py`, `cmd_claim`: only the `if created and args.run is not None:`
  block (lines 252–258 at base `1631ab8`), which gains one assignment of `claim.base` to the lane's
  `base`. The `--run` existence check (lines 225–228, T048's area) is not touched.
- `tools/taskrail/src/taskrail/autopilot/merged.py`: `_dependents` (fork-point selection), a small
  helper reading the kept bases from `runs.read_all`, and the module docstring if needed.
  `runs.py` is not changed: the lane key is read with `.get("base")`, so `_lane`/`_normalize` keep
  their defaults and older run files load unchanged.
- Tests: `tools/taskrail/tests/test_autopilot_merged.py` (new tests for criteria 2–5; the existing
  `test_a_finished_dependent_forks_from_the_dependency_head_even_after_cleanup` claims T002 without
  `--run` so it keeps covering the `merge-base` and `run` sources it was written for) and
  `tools/taskrail/tests/test_autopilot.py` (criterion 1, next to the other `claim --run` tests).
- `tools/taskrail/DESIGN.md` §12.4 *Claims* bullet and §12.8 *Stacked dependents* bullet — exact
  text proposed at the plan gate, edited only once approved.
- `tools/taskrail/CHANGELOG.md` (one *Unreleased* bullet), `docs/features/README.md` (index row),
  this document.

## Out of scope

- Recording a base for claims made without `--run`, or keeping claims' bases anywhere else after
  release (a non-autopilot user still has `merge-base`).
- Exposing the kept `base` in `autopilot status` or `show`.
- Changing `review`'s rebase suggestion, `done`, or the run-file keys `_lane` defaults.
- The skill text: `taskrail-autopilot`'s *After a merge* step already runs the `command` that
  `merged` reports, so it needs no change (and T055 owns that file).
- The several-unmerged-dependencies case (a merge commit as fork point), which the skill handles by
  hand.

## Open questions and risks

- **Source name.** `run-base` sits next to the existing `run` (the dependency's recorded head); the
  alternative is renaming nothing and reusing `claim`, which would hide that the claim is gone.
- **DESIGN keys sentence.** §12.4's per-task key list in the run file does not list `merged`
  (T031 documented it in the `done-merged` bullet instead). Documenting `base` in the *Claims*
  bullet follows that precedent and stays out of T048's run-file bullets; adding it to the key list
  as well would conflict with T048 at hand-off.
- **Several runs hold the dependent.** The newest run whose lane base qualifies wins; since all
  of them copy a claim of the same task, they differ only after a re-claim, where the newest is the
  one that matters.
- **Existing test expectations move.** Any test that claims a dependent with `--run`, releases it
  and expects `merge-base` changes to `run-base` with the same `fork`; only the one named above
  exists today.
