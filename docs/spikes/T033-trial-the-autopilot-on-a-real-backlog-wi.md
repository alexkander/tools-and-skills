# T033 — Trial the autopilot on a real backlog with each supported agent

**Status: investigate — the trial kit is built and checked; the two agent runs wait for the human.**
The frame was approved at its gate ([decision record](../autopilot/decisions/T033-trial-the-autopilot-on-a-real-backlog-wi.md));
the verdict is written at the decide gate.

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

### Investigate: the trial kit

Built outside the repository at `/var/tmp/taskrail-t033-trial` (persistent across reboots,
throwaway) from [`T033-trial-kit/`](T033-trial-kit/RUNBOOK.md), which holds everything the trial
needs and nothing private:

| File | Role |
|---|---|
| [`RUNBOOK.md`](T033-trial-kit/RUNBOOK.md) | the human's steps for each run, including the D1 and D5 probes |
| [`ANSWERS.md`](T033-trial-kit/ANSWERS.md) | the prompts (P1–P4), planned and unplanned answers (A1–A10), the permission-prompt rule and the stop conditions |
| `prepare.sh` | exports taskrail at `977064f` with `git archive`, copies the scripts and bundles one seed repository, so both runs start from the same commit |
| `seed/` | `wordstat`, the synthetic tool: code, tests, changelog, `docs/policy.md` (`prepare.sh` writes `AGENTS.md` and `CLAUDE.md`, the taskrail install, config and backlog) |
| `new-run.sh` | one run from the bundle: an absolute bare remote, the orchestrator's clone, the allowlists, `evidence/` with the environment and a timeline |
| `enable-autopilot.sh` | sets `[autopilot].enabled = true` on the trial `main` after the D1 refusal |
| `squash-merge.sh` | stands in for a host's squash merge, logged to `evidence/merges.log` |
| `capture.sh`, `snapshot.sh`, `finish.sh` | status every minute; labelled snapshots (status, claims, run files, logs, worktrees); final checks on `main`, decision records and transcript copies |
| `claude-settings.local.json`, `opencode.json` | one allowlist rendered for each agent; OpenCode's also sets `github-copilot/claude-opus-5` |
| `check-kit.sh` | the CLI-only dry run below |

Choices made while building it:

- **Pinning.** `.taskrail/config.toml` pins `version = "local:.taskrail/src"`, a committed symlink
  to the exported source, so every worktree runs the same taskrail with no environment variable to
  forget.
- **Seed order.** `taskrail next` orders by points, then position, so points are set to make the
  first dispatch T001, T003 and T004 (1 point each) and leave T002 (stacked on T001) and T005 for
  the refill.
- **No hint of the trial** in anything the agents read: the seed's config, `AGENTS.md` and backlog
  read as an ordinary small project. The permission files are untracked (`.git/info/exclude`).
- **Allowlist.** The taskrail wrapper (relative and absolute), `git` (with `git push` always
  asking), the checks, `python3 -m wordstat`, `cd`, `ls`, `cat`, `head`, `tail`, `wc`, `grep`,
  `rg`, `diff`, `sort`, `pwd`, `echo`, `date`, and edits inside the clone. Claude Code checks each
  subcommand of a compound command and evaluates deny, then ask, then allow
  ([permissions](https://code.claude.com/docs/en/permissions)); OpenCode lets the last matching
  rule win ([permissions](https://opencode.ai/docs/permissions/)) and does not document whether it
  splits compound commands — **not verified**, so `cd * && …` may be broader on OpenCode.
- **Permission prompts are not recorded** in Claude Code transcripts (not documented), so the human
  logs each one in the timeline.

`check-kit.sh` after a clean `prepare.sh`, no agent involved (colour codes removed):

```text
PASS  new-run: seeded /var/tmp/taskrail-t033-trial/runs/dryrun
PASS  validate: 5 task(s) in 1 backlog(s): 0 error(s), 0 warning(s)
PASS  pinned taskrail runs through .taskrail/src (977064f)
PASS  start while disabled exits 5: taskrail: the autopilot is disabled; set [autopilot].enabled = true in .taskrail/config.toml to allow `autopilot start`
PASS  enable-autopilot: committed and pushed
PASS  start --count 5: run 20260914-1
PASS  next dispatches T001, T003, T004 with ports; limited_by: max_lanes skipped: []
PASS  lanes T001 and T004: worktrees created with --no-track and claimed with --run
PASS  status flags T004's uncommitted docs/policy.md change as a governing escalation
PASS  notify appends to evidence/notify.log
PASS  T001 lane: checks OK, done, review, publish pushed=True
PASS  review --json: no rebase needed
PASS  squash-merge: squash-merged T001-add-a-lines-flag-that-also-reports-the-l into main as 2ce8419: feat(wordstat): add a --lines flag that also reports the line count (T001)
PASS  merged --cleanup: merged via tree, worktree removed
PASS  status: T001 done-merged
PASS  capture: 3 status file(s) written
PASS  snapshot: 20260914T082358Z-dry-check
PASS  finish: checks pass on the remote's main
PASS  opencode reads the trial config: model and permissions
PASS  Claude Code settings file is valid JSON
removed /var/tmp/taskrail-t033-trial/runs/dryrun
```

Not exercised by the dry run, left to the agent runs: a stacked rebase with `--onto`, the
`escalate_gate` flag, rebase conflicts, and a merge detected by patch-id or `merge-tree` rather
than tree (T031's tests cover those). Two things surfaced while building, both kit bugs fixed before
the run and not taskrail findings: `git clone --bare` of a bundle leaves `HEAD` on `master`, and
the dry run's first edit broke the seed's own CLI test. OpenCode also lists a user-level skill
next to the six taskrail skills; `new-run.sh` records the list per run.

## Approach

Agreed at the frame gate. The human's decisions are in the
[decision record](../autopilot/decisions/T033-trial-the-autopilot-on-a-real-backlog-wi.md).

### Backlog

**Decided: a synthetic public backlog** in a throwaway repository with a local bare remote. Rejected:
a copy of this repository's backlog (few suitable pending tasks, 2–5 points each, implemented twice)
and a real consumer project (real merges, content that cannot be published, no like-for-like
comparison). A follow-up task may later run one agent on a consumer project once the findings are
fixed. The seed, as built:

| ID | Kind | Pts | Depends on | Title | Exercises |
|---|---|---|---|---|---|
| T001 | feature | 1 | — | Add a --lines flag that also reports the line count | D2, D3, D6, D9; a changelog bullet (conflict class 2) |
| T002 | feature | 2 | T001 | Add a --json flag that prints the statistics as one JSON object | a stacked base; D10 `rebase --onto` after T001's squash merge; D2 refill |
| T003 | bug | 1 | — | Stop miscounting words around repeated whitespace and newlines | the function T001 also changes: touch map (D6, D8) and a conflict outside the known classes unless the touch map avoids it (D10) |
| T004 | chore | 1 | — | Document the exit code for an unreadable file in the output policy | D7 governing escalation (`docs/policy.md`) |
| T005 | spike | 2 | — | Decide whether word counting should follow Unicode word boundaries | D7 `escalate_gates = ["spike:decide"]`; D2 refill; the D5 new-session probe |

Configuration: `enabled = false` until the D1 refusal is observed, `max_lanes = 3`,
`governing = ["AGENTS.md", "CLAUDE.md", "docs/policy.md"]`, `escalate_gates = ["spike:decide"]`,
`notify` appending to `evidence/notify.log`, a `PORT` pool of three values bound by a test,
checks `python3 -m unittest discover -s tests -q` and `python3 -m compileall -q wordstat tests`.

### Environment and roles

- **The human drives both orchestrator sessions** — top-level interactive sessions, since §12.3
  rejects a CLI that launches agents and headless runs deny or skip permission prompts — answers
  from the [answer sheet](T033-trial-kit/ANSWERS.md), and says "merged" after `squash-merge.sh`.
- **Remote:** a local bare repository at an absolute path; hand-offs carry a title and no link.
- **taskrail** pinned at `977064f` for both runs and not patched between them.
- **Models:** the same on both agents — Claude Code's default, OpenCode on
  `github-copilot/claude-opus-5`.
- **Permissions:** one trial-local allowlist on both agents, every prompt outside it counted, never
  a prompt-skipping flag.
- **No extra runs:** OpenCode's experimental background subagents stay off; no non-Claude run.
- **Order:** Claude Code first, then OpenCode.

### Recording

Raw evidence stays under `/var/tmp/taskrail-t033-trial/runs/<agent>/evidence/`, since transcripts
contain local paths and account details; the artifact quotes cleaned excerpts only.

- Both runs start from the same seed commit (`seed.bundle`), each in its own directory.
- `capture.sh` writes `autopilot status --json` every minute; `snapshot.sh` at escalations,
  hand-offs, merges, compaction and the new-session probe; `finish.sh` copies the final state,
  checks on `main`, decision records and transcripts (Claude Code's session and subagent JSONL
  files, OpenCode's `opencode export` per session).
- The human's timeline: every prompt, answer, permission prompt, merge and surprise, with the time
  and the answer-sheet row.

### Measures

Per run: wall time from P2 to `complete`; gates reached, answered by the orchestrator and escalated,
against the planned escalations; human interventions beyond the plan; permission prompts; lanes
dispatched and refilled; rebases, conflicts by class, and escalated conflicts; misreads of CLI
output (D11); procedure deviations (a lane rebasing or publishing, a record committed after
resuming, a run file edited by hand); tokens; and the end state (every task `done-merged`,
`validate` clean, checks passing on `main`, one decision record per task, no worktree left behind).

### Sequence

1. **investigate, preparation** — done: the kit above, checked through the CLI alone.
2. **Stop and hand the runbook over** — here. Running agent sessions needs the human, so the
   investigate stage stops although its gate is `none` (agreed at the frame gate).
3. **The human runs Claude Code, then OpenCode**, following the runbook.
4. **investigate, analysis** — this lane reads the evidence, fills D1–D12 for each run and writes
   the findings.
5. **decide** — verdict, findings as follow-up tasks, and changes proposed to §12.

## Limits

- **Time box:** 2 points of analysis for this lane; for the human, at most 3 hours per run from P2,
  plus setup.
- **Tasks per run:** five; one run per agent; no optional runs.
- **Out of scope:** lane model pinning and lane agent definitions; `batch` hand-off (only its cost
  case is measured); runs across machines, `claim_remote` and remote run files; host APIs and real
  pull requests; OpenCode's background subagents; T004's merge driver; fixing any finding here —
  findings become follow-up tasks; any consumer project.
- **Stop a run early** at the conditions in the [answer sheet](T033-trial-kit/ANSWERS.md): a write
  outside the run or a push anywhere but its bare remote; an agent merging or publishing other than
  through `review --publish`; a needed prompt-skipping flag or denied permission; a run that cannot
  continue without editing a run file or patching taskrail (recorded as a finding, not worked
  around); or 3 hours. If the first run shows a defect so severe the second would only repeat it,
  ask the human whether to fix first and rerun both, or run the second agent anyway.
- **Not verified yet:** whether a new Claude Code session can resume a previous session's
  background subagents (D5), whether OpenCode's compaction keeps task-tool handles usable, whether
  OpenCode splits compound commands for permissions, and the real cost of either run.
