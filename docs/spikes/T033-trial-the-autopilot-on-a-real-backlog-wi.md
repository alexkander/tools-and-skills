# T033 — Trial the autopilot on a real backlog with each supported agent

**Status: draft at the frame gate.** The question, the backlog, the environment and the approach
below are proposals awaiting the human's agreement; the verdict is written at the decide gate.

## Question

Does the autopilot as designed in [DESIGN.md §12](../../tools/taskrail/DESIGN.md) — the
`taskrail autopilot` commands (T029–T032) and the `taskrail-autopilot` skill with its Claude Code
and OpenCode notes (T024) — carry a small backlog from "run the autopilot for N tasks" to N
squash-merged tasks on **both** Claude Code and OpenCode, and where does it not?

"What the design got wrong" is made concrete as twelve checks. Each one names the part of the
design it tests; a check fails when an agent following the skill and CLI literally cannot do what
the design says, or does it only with help the text does not give.

| # | Check | Design |
|---|---|---|
| D1 | **Opt-in.** Asked without a count, the orchestrator asks for one and does nothing else. With `[autopilot].enabled` unset, `autopilot start` exits 5 and the orchestrator stops, without working the tasks some other way. | §12.1, §12.2 |
| D2 | **Dispatch.** It runs `autopilot next --run R`, fills the lane brief from its JSON, launches the lanes of one dispatch together, records each handle at once, refills a freed lane, and never starts more than the count. | §12.1, §12.7 |
| D3 | **Lane contract.** Each lane branches with `--no-track`, claims with `--run R`, ends its turn at every `always` gate with a full report, and stops after `done` and `review --json` without rebasing or publishing. | §12.3 |
| D4 | **Resume at gates.** Lanes are resumed by handle with their context intact (Claude Code: `SendMessage` to the agent ID; OpenCode: the task tool with the same `task_id`), and on OpenCode the cost of answering in waves is measured. | §12.3 table |
| D5 | **Handles across compaction.** After the orchestrator's context is compacted mid-run, it rebuilds its view from `autopilot status` and the run file and resumes lanes by their stored handles. Whether a *new* orchestrator session can resume the previous session's lanes is probed on each agent. | §12.3, §12.4 |
| D6 | **Gate review and decision records.** Checks are re-run by the orchestrator in the lane's worktree; each decision is written to the task's record and committed on the task branch while the lane is stopped, before it is resumed; the touch map goes through `autopilot decision` and into every affected record. | §12.5, gate review |
| D7 | **Escalation.** A governing-path touch and an `escalate_gates` stage are flagged by `status` and escalated (`lane --state escalated`, `notify`, a direct question); judgement escalations (contradicting lanes, false premise) are raised; other lanes keep going. | §12.6 |
| D8 | **Supervision.** `status` runs on every wake; `silent` and `overlaps` are acted on. | §12.6 |
| D9 | **Hand-off.** One branch at a time in `handoff.next` order: rebase when needed, re-run checks, `review --publish`, exact title and link, never a merge. | §12.8 |
| D10 | **Merge follow-through.** When told a branch is merged, `autopilot merged --cleanup` proves the squash merge by content, stacked dependents are rebased with `--onto`, known conflict classes are resolved and anything else escalates. | §12.8 |
| D11 | **CLI outputs.** Every place the orchestrator or a lane misreads a JSON field or an exit code, or needs a value no command prints. | §12.1 |
| D12 | **Friction and cost.** Human interventions beyond the planned ones, permission prompts, wall time, tokens, and whether sequential hand-off caught anything worth its rebases (the §12.10 condition for adding `batch`). | §12.8, §12.10 |

Each finding is classified as in T001 — **design**, **skill text**, **CLI bug**, **CLI gap**,
**integration note**, **agent limitation** — or as a **model slip**: a one-off mistake the text
already forbids, which does not reproduce on the other agent. Model slips are recorded but are not
evidence that the design is wrong.

## Evidence that would answer it

- For each agent, one complete run whose checks D1–D12 each have a pass, a fail with a finding, or
  "not exercised" with the reason.
- For each fail: the transcript excerpt, the `autopilot status --json` snapshot and the git state at
  that moment, enough for someone else to see the same thing.
- A comparison table of the two runs on the measures below.
- A list of findings, each proposed as a follow-up task or as a change to §12's "The design changes
  if".

### Environment checked at the frame

Checked on the trial machine without installing or starting any agent session; the versions are the
ones T007's evidence (E5, E6) was gathered with, so that evidence still describes these binaries.

| Tool | Found | Version | Notes |
|---|---|---|---|
| `claude` | yes | 2.1.270 (Claude Code) | `claude auth status`: logged in through a claude.ai account. |
| `opencode` | yes | 1.15.13 | `opencode auth list`: credentials for four providers (GitHub Copilot, OpenAI, LMStudio, OpenCode Go), none for Anthropic directly. `opencode models` lists Claude models through GitHub Copilot, including `github-copilot/claude-opus-5` and `github-copilot/claude-sonnet-5`. |
| `git` | yes | 2.55.0 | At least 2.38, so the `merge-tree` check of §12.8 runs. |
| `uv` | yes | 0.11.16 | Runs taskrail from source. |
| Python | yes | 3.14.7 | |
| `gh` | no | — | Not needed with a local remote. |

CLI behaviour checked in a throwaway repository under `/tmp` (since removed), with taskrail from
`977064f`:

- `taskrail init --integration claude --integration opencode` writes both agents' notes into the
  same files under `.claude/skills/`; in that repository `opencode debug skill` lists all six
  taskrail skills, so OpenCode discovers them from there.
- `opencode debug agent general` still shows `{"permission": "question", "action": "deny"}`, as in
  E6: a lane cannot ask the human on OpenCode.
- `taskrail autopilot start --count 1 --json` in a fresh repository exits 5 with
  ``taskrail: the autopilot is disabled; set [autopilot].enabled = true in .taskrail/config.toml to allow `autopilot start` ``.
- With a local bare remote, `taskrail review T001 --publish --json` pushed the branch
  (`git push --set-upstream origin HEAD:refs/heads/T001-base-task`) and returned
  `pull_request.provider` `none`, a title and a body, and `url` `null`: the hand-off carries no
  link, and a merge must be made by hand.
- Setup note: a bare remote added with a relative path (`../origin.git`) makes `taskrail review`
  fail inside a task worktree (`git fetch origin failed: fatal: '../origin.git' does not appear to
  be a git repository`), because git resolves the relative path from the worktree's directory. The
  trial uses an absolute path. T007's reproduction script uses a relative one but never ran
  `review` from a worktree.
- This repository has no `[autopilot]` table, no run file exists in its clone, and T033's own
  claim has `run: null`: the run that started this lane is orchestrated without the CLI's run
  state, like the runs behind `docs/autopilot/decisions/`. It is not the trial.

## Approach

### Backlog

| Option | For | Against |
|---|---|---|
| **(a) Synthetic public backlog** in a throwaway repository: a tiny Python tool with tests and five or six small tasks seeded so that each check is exercised | Identical for both agents, so the comparison is fair; every path can be seeded (stacked dependency, governing touch, escalated gate, known and unknown conflicts); no real merges, no risk to anything; small tasks keep the cost down; fully publishable, so the seed script can go into *How to reproduce*. | Not the "real backlog" the row names; trivial tasks make gate reviews shallow and may hide friction that only real work produces; the seed's author chooses what is tested. |
| **(b) A copy of this repository's backlog** with a local remote | Real governing documents (DESIGN.md, CLAUDE.md) and real review depth. | Few suitable pending tasks: T004, T012 and T014 already have worktrees and branches in this clone, T003 needs a consumer project, T011 waits on an upstream merge; the remaining tasks are 2–5 points each and each agent would implement them separately, doubling the cost; two copies of real implementations invite confusion with the real branches; the paths in (a) would still have to be seeded by hand. |
| **(c) A real consumer project chosen by the human** | The most realistic friction, and real work delivered. | Real merges into a real project; its content cannot appear in this public artifact, so every finding must be abstracted; the two agents cannot both do the same tasks, so the comparison is not like for like; it overlaps T003 (install taskrail in a first consumer project). |

**Recommendation: (a)**, with tasks that are small but real enough for a review to read code and
tests, and a follow-up task for one short single-agent run on a consumer project once the findings
are fixed. Proposed seed (names and content are generic and written for the trial):

| Seed task | Kind | Depends on | Exercises |
|---|---|---|---|
| S1 add a flag to the tool | feature | — | D2, D3, D6, D9; a CHANGELOG bullet (known conflict class 2) |
| S2 extend S1's flag with a second output format | feature | S1 | a stacked base; D10 `rebase --onto` after S1 is squash-merged |
| S3 fix an off-by-one in the function S1 also changes | bug | — | a touch-map overlap with S1 (D6, D8), and a conflict outside the known classes unless the touch map prevents it (D10) |
| S4 update a policy document listed in `governing` | chore | — | D7 governing escalation |
| S5 choose between two approaches for a later change | spike | — | D7 `escalate_gates = ["spike:decide"]`; dispatched only when a lane frees (D2 refill) |

Trial configuration: `[autopilot] enabled = true`, `max_lanes = 3`, `governing` the policy
document, `escalate_gates = ["spike:decide"]`, a `notify` command appending to a log file, a small
`[[autopilot.resource]]` pool read by the tests (so D2 checks the environment reaches the lane),
`[checks] test` running pytest. Prompt, verbatim on both agents: *"Run the autopilot for 5 tasks."*
D1 is exercised first in each run: the same prompt without a count, then with `enabled = false`,
then enabled.

### Environment and roles

- **The human plays the human.** The orchestrator must be a top-level interactive session: §12.3
  rejects a CLI that launches agents, and a headless run (`claude -p`, `opencode run`) denies or
  skips permission prompts. This lane has no channel to a session and cannot drive one. The human
  starts each orchestrator session, answers the planned escalations from a written answer sheet so
  both runs get the same answers, and merges branches.
- **Merges** go through a throwaway helper script that squash-merges a task branch into the bare
  remote's `main` with the pull request title as the commit, then tells the orchestrator "merged".
  A throwaway private hosted repository with real pull requests is the alternative (more realistic
  squash, but it needs `gh` or the web UI and adds network variables).
- **Remote:** a local bare repository at an absolute path.
- **taskrail** pinned to one commit (`977064f` unless the human says otherwise) for both runs,
  through a `local:` copy or `TASKRAIL_BIN`, settled when the seed is built. taskrail is not
  patched between runs, even when a finding is obvious.
- **Models:** Claude Code on its default model; OpenCode on `github-copilot/claude-opus-5`, so both
  runs use the same model family and the difference measured is the agent, not the model. A third,
  optional OpenCode run on a non-Claude model would test the skill text's portability separately.
- **Permissions:** never a flag that skips prompts (`--dangerously-skip-permissions`, OpenCode's
  `--auto`). Either default prompts, which measures real friction but makes the human approve every
  lane command, or the same trial-local allowlist on both agents (`.taskrail/bin/taskrail`, `git`,
  `uv run`, `pytest` inside the trial repository), with every prompt outside it counted.
- **OpenCode background subagents** (`OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS`) stay off in the
  main run, since the design does not require them; an optional short second OpenCode run with the
  flag measures what waves cost.

### Recording

Raw evidence is kept outside the repository, since transcripts contain local paths and account
details; the artifact quotes scrubbed excerpts only.

- The seed as a script, the helper merge script, the answer sheet and the trial configuration —
  committed into *How to reproduce*, since they are synthetic.
- Both runs start from the same seed commit (a git bundle), each in its own fresh copy.
- A shell loop outside the agents writes `autopilot status --json` every minute, plus one snapshot
  at every gate and merge; the run file, the notify log, `git log --all --graph` of the bare remote
  and every decision record are copied at the end.
- Transcripts: Claude Code's session and subagent JSONL files; OpenCode's `opencode export` for the
  orchestrator and each child session, and `opencode stats` for tokens.
- A timeline kept by the human during the run: each intervention with the time and what prompted it.

### Measures

Per run: wall time from the prompt to `complete`; gates reached, answered by the orchestrator and
escalated, against the planned escalations; human interventions beyond the plan; permission
prompts; lanes dispatched and refilled; rebases, conflicts by class, and escalated conflicts;
misreads of CLI output (D11); procedure deviations (a lane rebasing or publishing, a record
committed after resuming, a run file edited by hand); tokens; and the end state (every task
`done-merged`, `validate` clean, tests passing on `main`, one decision record per task, no worktree
left behind).

### Sequence

1. **investigate, preparation** — build the seed, helper scripts, answer sheet and capture loop;
   dry-run the seed through the CLI alone (`autopilot next` preview, `status` flags, a squash merge
   detected by `merged`) so that no agent time is spent on a broken seed.
2. **Stop and hand the runbook over.** Running agent sessions needs the human, so the investigate
   stage stops here although its gate is `none`.
3. **The human runs Claude Code, then OpenCode** (or the other order), with this lane's runbook.
4. **investigate, analysis** — this lane reads the evidence, fills D1–D12 for each run and writes
   the findings.
5. **decide** — verdict, findings as follow-up tasks, and changes proposed to §12.

## Limits

- **Time box:** 2 points of analysis for this lane; for the human, one run per agent of at most
  3 hours wall time each, plus setup.
- **Tasks per run:** five; one run per agent. Optional runs (OpenCode with background subagents,
  OpenCode on a non-Claude model) only if the human wants them.
- **Out of scope:** lane model pinning and lane agent definitions; `batch` hand-off (only its cost
  case is measured); runs across machines, `claim_remote` and remote run files; host APIs and real
  pull requests; T004's merge driver; fixing any finding here — findings become follow-up tasks;
  any consumer project.
- **Stop a run early when:** anything writes outside the trial copy or pushes anywhere but its bare
  remote; an agent merges, or publishes other than through `review --publish`; a permission bypass
  is proposed and would be needed to continue; the run cannot continue without editing a run file
  by hand or patching taskrail (recorded as a finding, not worked around); or the wall-time limit is
  reached. If the first run shows a defect so severe the second would only repeat it, ask the human
  whether to fix first and rerun both, or run the second agent anyway for its agent-specific
  evidence.
- **Not verified at the frame:** whether a new Claude Code session can resume a previous session's
  background subagents (D5), whether OpenCode's compaction keeps task-tool handles usable, and the
  real cost of either run.
