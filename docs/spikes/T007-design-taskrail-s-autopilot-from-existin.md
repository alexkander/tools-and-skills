# T007 — Design taskrail's autopilot from existing orchestrators

**Verdict: pending — draft at the frame stage.**

## Question

What is the smallest agent-agnostic design for a taskrail autopilot — a skill plus CLI support,
installed with the other skills and opt-in per repository — that covers the
[reference behaviour](../research/autopilot-reference-behaviour.md) of two existing
orchestrators and the lessons of this repository's first autopilot run, and which tasks deliver
it?

The decision must settle, each with a recommendation and the alternatives rejected:

1. **Split between skill text and CLI support** — which parts are deterministic enough to be a
   command (eligibility, ordering, stacked base, merged-by-content detection, session state,
   resource allocation, decision-record scaffolding, merge follow-through) and which stay
   judgement in the skill (answering gates, reading diffs, resolving conflicts, escalating).
2. **Mapping of orchestrator and lanes onto each supported agent** — Claude Code subagents and
   OpenCode subagents: how a lane is started, resumed after a gate, and how the orchestrator
   learns that a lane ended its turn; what each agent cannot do (for example, polling on a
   timer).
3. **Where session state lives** — claims extended with lane state, a separate state file, or
   state derived from git and the backlog; and how two orchestrator sessions see each other.
4. **Decision records** — format and location, and whether taskrail renders them.
5. **Escalation and notification hooks** — the conditions that force a human, and the command
   contract for notifying.
6. **Resource arbitration** — lanes limit, the "one user-interface lane" rule generalised,
   databases, ports and emulators, and pre-assigned sequential numbers.
7. **Merge follow-through** — hand-off order, verifying a squash merge, cleaning up, and
   rebasing stacked dependents; which conflict classes resolve without a human.
8. **Configuration keys** — the `[autopilot]` table (or equivalent) and its defaults.
9. **Task breakdown** — tasks replacing or refining T024 (8 points), and how T017 (stacked base),
   T019 (executor-named branch) and T020 (conditional stages) fit, including whether any is a
   prerequisite, a follow-up, or unnecessary.

## Evidence that would answer it

- **Coverage matrix.** Every bullet of the reference behaviour and every lesson of the first run,
  each mapped to an existing taskrail primitive, a proposed CLI change, skill text, or an
  explicit exclusion with its reason.
- **First-run record.** What the four decision records under `docs/autopilot/decisions/` show the
  orchestrator actually did, decided and needed: gate criteria applied, conflict classes,
  rebase sequencing, the `installed.json` hazard.
- **Primitive behaviour, measured.** Running the current CLI (`next`, `list --eligible`, `show`,
  `claims`, `reserve-id`, `new --workspace`, `review`) in a throwaway repository with parallel
  worktrees, to confirm what the autopilot can rely on today and where it falls short — for
  example eligibility with a dependency done only on an unmerged branch, and ID reservation from
  two worktrees at once.
- **Merged-by-content detection, measured.** Whether a squash-merged branch can be recognised
  mechanically (tree comparison after rebase, `git cherry`/patch-id, the task's ✅ on the
  mainline plus the `(Txxx)` squash title), tried against this repository's real squash merges
  (#8–#11) and a throwaway repository.
- **Agent capabilities, verified.** For Claude Code (2.1.270 installed) and OpenCode (1.15.13
  installed): how subagents are launched, whether and how a stopped subagent is resumed with its
  context, whether the parent is notified when a subagent ends, whether a subagent can ask the
  human, and whether either agent can schedule a wake-up. From primary documentation, and by
  running a trivial subagent where it can be done without side effects.
- **Existing hazards reproduced.** `taskrail upgrade` with conflict markers in
  `.taskrail/installed.json`, in a throwaway repository, to record exactly what it deletes and
  what guard the CLI needs.

## Approach

1. Build the coverage matrix from the reference behaviour, the decision records, the lessons
   listed by the human, `tools/taskrail/DESIGN.md` and the CLI sources.
2. Run the measurements above in throwaway repositories under a temporary directory outside this
   repository; record exact commands, versions and output.
3. Check each agent's subagent model against its documentation and, where safe, a trivial run.
4. For each of the nine points, list the options, choose one, and state what would change it.
5. Draft the task breakdown: titles, kinds, points, dependencies, and the edited scope of T017,
   T019, T020 and T024 if the decision changes them.
6. Complete this document in the spike's decide format and stop at the `decide` gate. Follow-up
   tasks are opened only after the decision is accepted.

## Limits

- **Time box:** 3 points — one working session for investigation and write-up.
- **No production code.** No change to `tools/taskrail/src`, its tests, `DESIGN.md` or the
  skills; the design is written here, and moving it into `DESIGN.md` and the skills is follow-up
  work. Throwaway scripts live outside the repository.
- **No live autopilot run.** The design is not exercised end to end with parallel lanes here; the
  first run's records stand in for that, and a trial run belongs to the implementation tasks.
- **Two agents only:** Claude Code and OpenCode, the integrations taskrail ships. Other agents are
  considered only as "any agent that can run a shell and start a sub-session".
- **No host APIs.** Merging, CI status and pull request state through a host's API stay out of
  scope, as in DESIGN.md's non-goals; follow-through starts from the human saying a branch is
  merged, verified with git.
- **Reference behaviour taken as given.** The two source orchestrators are not re-read; their
  behaviour is what `docs/research/autopilot-reference-behaviour.md` records, and nothing private
  from them is named here.
