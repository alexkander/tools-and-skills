# T024 — Write the taskrail-autopilot skill with Claude Code and OpenCode notes

Kind: feature · Epic: E02 · Status: plan (awaiting approval)

Source: the accepted autopilot design, `tools/taskrail/DESIGN.md` §12 — §12.1 (skill and CLI
split), §12.2 (installed everywhere, exit-5 refusal), §12.3 (orchestrator, lanes, the Claude Code /
OpenCode table), §12.5 (decision records), §12.6 (escalation, notification, supervision), §12.7
(resources), §12.8 (merge follow-through, known conflict classes) — and the evidence in
`docs/spikes/T007-design-taskrail-s-autopilot-from-existin.md` (E5–E7, coverage matrix). The
decision records under `docs/autopilot/decisions/` show what an orchestrator actually does at each
gate and rebase; the skill generalises them. The questions this plan needs settled are Q1–Q10
below, each with a recommendation; the plan's wording assumes the recommendations.

**Workspace.** T024 depends on T030, T031 and T032, all merged into `main` (`a41ca8a`). The
branch starts from `origin/main` (`a41ca8a`), the base `show T024 --fetch` reports, and the task
was claimed without `--ignore-deps`. An earlier integration base built from the unmerged T031 and
T032 branches was discarded, with no work on it, once both merged.

## Today

- No `taskrail-autopilot` skill exists: `init --integration claude` in a fresh repository installs
  exactly `taskrail`, `taskrail-bug`, `taskrail-chore`, `taskrail-feature` and `taskrail-spike`.
- The installer copies only `SKILL.md` from each skill directory. A probe skill with
  `references/r.md` installed as `.claude/skills/probe-skill/SKILL.md` alone; the reference was not
  written.
- Integration notes are one file per agent (`integrations/claude.md`, `opencode.md`), and the whole
  file replaces the `<!-- taskrail:harness -->` marker in **any** skill carrying it. The probe skill
  received the core skill's Claude Code notes, so a second skill cannot get notes of its own.
- The CLI side is complete: `autopilot start` refuses a disabled autopilot with exit 5
  (`taskrail: the autopilot is disabled; set [autopilot].enabled = true in .taskrail/config.toml to
  allow `autopilot start``), and `start`, `next`, `lane`, `decision`, `status`, `merged`, `notify`,
  `claim --run` and `lane --gate` exist.
- Kind filtering (T025) already leaves a shipped skill in when no core kind names it, so the new
  skill installs regardless of `[kinds].allowed` without code for it; nothing tests that yet.

## Behaviour

After this change, `init` and `upgrade` install `taskrail-autopilot` in every repository, with each
integration. An agent that the human asks to "run the autopilot for N tasks" follows it as the
**orchestrator**:

1. **Start only when asked.** The skill runs only when the human explicitly asks for the autopilot
   and gives a task count; without a count it asks for one and does nothing else. It never starts
   on its own initiative, from `taskrail next`, or because the skill is installed. It runs
   `taskrail autopilot start --count N [--kinds …] --json`; on exit 5 it stops and reports the
   message — it never edits `[autopilot].enabled` itself.
2. **Read the governing documents** (`[autopilot].governing`, the kinds' skills, the task rows)
   before answering anything.
3. **Dispatch.** `autopilot next --run R --json` names the tasks to start now. For each, the
   orchestrator fills the lane brief template (`references/lane-brief.md`) from that task's fields
   (ID, title, kind, executor skill, branch, worktree, `base`, `environment`, decision-record path)
   plus the run ID, the other live lanes and the touch map agreed so far, launches the lane as a
   sub-session, and records `autopilot lane <ID> --run R --handle H --state running`. It starts any
   shared service a lane needs; lanes never do.
4. **Supervise on every wake-up** with `autopilot status --run R --json`: lanes stopped at a gate,
   silent lanes (read their worktree; escalate if stuck), overlaps and the escalation flags.
5. **Answer gates.** When a lane stops: `autopilot lane <ID> --run R --state gate --gate <stage>`;
   escalate if §12.6 applies (below); otherwise review by the gate checklist
   (`references/gate-review.md`), write the decisions into the task's record before giving them
   (`references/decision-record.md`), commit the record on the task branch in the lane's worktree
   while the lane is stopped, resume the lane with `continue <ID>` plus the answers, and record
   `--state running`. Conditional gates with nothing to decide do not stop a lane. At a lane's first
   gate the orchestrator builds or extends the **touch map** (which lane edits which files or
   sections, and the conflict classes agreed), records it with `autopilot decision`, copies it into
   each affected record, and tells every live lane.
6. **Escalate** — `autopilot lane --state escalated --reason …`, `autopilot notify --event
   escalation`, then ask the human — when a lane touches a governing path, the gate is in
   `escalate_gates`, the governing documents reserve the decision to humans, two lanes contradict
   each other, a conflict falls outside the known classes, a task row rests on a false premise, or
   a base has diverged. The answer is recorded under `## escalated to the human`. Other lanes keep
   going. A lane that cannot finish is recorded `failed` with a reason; it keeps its claim, branch
   and worktree.
7. **Close and hand off, one branch at a time.** Lanes stop after `taskrail done` and
   `taskrail review <ID> --json` and do not rebase. When `status` names the branch as
   `handoff.next`, the orchestrator rebases it onto `rebase.onto` if needed, resolves only the known
   classes, re-runs the checks and `taskrail validate`, records the rebase, runs
   `taskrail review <ID> --publish --type … --scope …` in the lane's worktree, records
   `--state handed-off`, runs `autopilot notify --event lane-done`, and gives the human the exact
   pull request title and link. It never merges. Freed lanes are refilled with `next --run R`.
8. **Follow through** when the human says a branch is merged: `autopilot merged <ID> --cleanup
   --json`; each stacked dependent listed is rebased with the `git rebase --onto` command reported,
   retested and republished with a lease; then the next branch is handed off. The run ends when
   `status` reports it `complete`.

The **known conflict classes** are the three of §12.8: backlog rows united by ID with `✅` winning
unless a `Reopens:` commit exists; appended index rows and changelog bullets kept on both sides;
installed skill copies and `.taskrail/installed.json` — make the manifest valid, merge the sources,
run `taskrail upgrade --force`. Anything else escalates.

**Agent-specific notes** (installed at the skill's harness marker, not in the portable text):

- Claude Code: a lane is a background general-purpose subagent launched with the Agent tool; its
  handle is the agent ID; resume with `SendMessage`; a completion notification wakes the
  orchestrator; lanes cannot ask the human (`AskUserQuestion` is removed from subagents), the
  orchestrator asks with it at escalations; the lane model is the Agent tool's `model` parameter;
  never use subagent worktree isolation; no timer — a tool that waits on a condition may re-run
  `status`, but nothing relies on it.
- OpenCode: a lane is a task tool call with `general` (or a lane agent definition); the handle is
  its `task_id`; resume by calling the task tool with the same `task_id`; task calls block by
  default, so lanes launched together return together and gates are answered in waves — correct but
  slower; the experimental background subagents notify instead and are not required; lanes cannot
  ask (`question` is denied); the lane model is set in a lane agent definition.

## Acceptance criteria

1. `init --integration claude` in a fresh repository installs
   `.claude/skills/taskrail-autopilot/SKILL.md` and its reference files; `--integration opencode`
   alone installs them under `.opencode/skills/`; with both, one copy under `.claude/skills/`, and
   the `.opencode` copies (references included) are removed.
2. With `[kinds].allowed` limited (for example `["bug"]`), `init` and `upgrade` still install
   `taskrail-autopilot`, and the "not installing" note does not name it.
3. Reference files are managed files: recorded with a digest in `installed.json`; a second `init`
   changes nothing; a locally edited reference is skipped and kept unless `--force`; a managed
   reference no longer shipped is removed under the same rule as a skill; creating or changing one
   triggers the restart note. Kind filtering removes an executor skill's reference files with its
   `SKILL.md`.
4. Integration notes are per skill: the installed `taskrail-autopilot` skill carries its own
   `## On Claude Code` and `## On OpenCode` sections (as installed for each integration), the core
   `taskrail` skill carries exactly today's notes and none of the autopilot's, executor skills carry
   none, and no `<!-- taskrail:harness -->` marker is left in any installed file.
5. The portable text — the source `SKILL.md` and every reference — names no agent or agent tool
   (`Claude`, `OpenCode`, `AskUserQuestion`, `SendMessage`, `Agent tool`, `task_id`, `subagent`).
6. The skill's frontmatter uses only the portable keys; its `description` says what it does, that it
   is used only when the human explicitly asks to run the autopilot with a number of tasks, and
   stays within 1024 characters.
7. `SKILL.md` states in prose that the autopilot runs only when the human asks and gives a task
   count, that it never starts on its own initiative, and that it stops and reports when
   `autopilot start` exits 5, without enabling `[autopilot].enabled` itself.
8. The lane brief template carries the §12.3 lane contract — one task ID with the `taskrail` skill
   and its executor skill; worktree created with git and `claim <ID> --run <run>` inside it; end the
   turn at every gate with the full gate report; resumed with `continue <ID>`; never
   `review --publish`, never merge, never start shared services, never touch another lane's
   worktree; stop after `taskrail done` and `review --json` without rebasing — and placeholders for
   the branch, worktree, base, resource environment, decision-record path, other lanes and touch
   map.
9. The gate checklist covers every gate type (a plan-like gate: `plan`, `scope`, `diagnose`,
   `frame`, `decide`; `implement`/`fix`; `verify`; close and rebase) with, at least: governing
   documents first; never approve with failing checks; read the diff by commit range rather than the
   lane's summary; re-run the checks in the lane's worktree while its resources are its own; a test
   observed failing before the code (and before the fix, for a bug); verification in the real
   runtime; premises of the task row checked.
10. The decision-record template has the §12.5 structure: an introduction saying each decision is
    recorded before it is given; `## <stage> gate` with a `Reviewed:` paragraph and a
    `# | Question | Options | Decision | Reason` table; `## Conflict handling agreed for all lanes`;
    `## rebase after …`; `## escalated to the human`; and says records are committed on the task
    branch only while the lane is stopped, plus an index row at `decisions_index`.
11. `SKILL.md` lists the seven escalation conditions of §12.6, the three known conflict classes of
    §12.8 with "anything else escalates", sequential hand-off, and follow-through with
    `autopilot merged <ID> --cleanup` and `git rebase --onto`.
12. Every `taskrail autopilot <command>` the skill and its references show exists in the CLI, with
    every `--flag` shown accepted by that command (and by `claim`, `review`, `lane`); every
    `autopilot` subcommand appears in the skill.
13. `pytest -q` passes, `taskrail validate` is clean, and `upgrade` in this repository installs the
    new skill copy under `.claude/skills/taskrail-autopilot/`, committed like the other copies.

## Affected areas

- `tools/taskrail/src/taskrail/skills/taskrail-autopilot/` — new: `SKILL.md`,
  `references/lane-brief.md`, `references/gate-review.md`, `references/decision-record.md`.
- `tools/taskrail/src/taskrail/integrations/claude.md`, `opencode.md` — split into per-skill
  sections (Q3); the core skill's text unchanged.
- `tools/taskrail/src/taskrail/install.py` — `skill_files` renders every file of a skill directory
  and injects only that skill's notes; removal, the kind filter and the restart note work on all
  files under a skill directory, not only `SKILL.md`. No change to kind selection itself.
- `tools/taskrail/tests/test_install.py` (the `SKILLS` list, reference files, per-skill notes) and a
  new `tests/test_autopilot_skill.py` (prose invariants, portability, command drift).
- `tools/taskrail/DESIGN.md` — §8 (the skill list, per-skill notes), §9 (reference files are
  managed), §10 layout, §12 intro and §12.2/§12.3/§12.5/§12.8 marks, §12.10 row (Q9).
- `tools/taskrail/README.md` (skills and autopilot paragraph), `tools/taskrail/CHANGELOG.md` (one
  bullet, appended last).
- `.claude/skills/taskrail-autopilot/` and `.taskrail/installed.json` in this repository, regenerated
  by `taskrail upgrade`.

## Out of scope

- Any change to the `autopilot` commands, `claim` or `review` (T029–T032 are done).
- Editing the core `taskrail` skill or the executor skills (T038 is changing the core skill's
  step 3 on its own branch).
- Lane agent definitions (`.claude/agents/`, `.opencode/agents/`), plugin manifests, hooks.
- The merge driver for backlog conflicts (T004), a `batch` hand-off mode, counters beyond task IDs.
- Running a real autopilot end to end on either agent (T033).

## Questions to settle

| # | Question | Options | Recommendation | Why |
|---|---|---|---|---|
| Q1 | Skill structure | **a)** `SKILL.md` (procedure, escalation, conflict classes, hand-off) plus `references/lane-brief.md`, `references/gate-review.md`, `references/decision-record.md` · b) one long `SKILL.md` · c) `SKILL.md` with the gate checklist inline and two references | **a** | The orchestrator reads the procedure on every wake-up but the brief only at dispatch and the templates only at gates; references are the portable skill convention this repository already names in `CLAUDE.md`. |
| Q2 | Installing reference files | **a)** the installer copies every file of a skill directory as a managed file; the harness marker is replaced only in `SKILL.md` · b) Q1 b, no installer change | **a** | Without it, references never reach a consumer (probe above). The digest, skip and removal rules stay the same, applied per file. |
| Q3 | Where each skill's agent notes live | **a)** sections in `claude.md` / `opencode.md`, each opened by `<!-- taskrail:skill <name> -->`; a skill's marker receives only its section, or is dropped when it has none · b) one file per skill and agent, `integrations/<skill>/<agent>.md` · c) one note per agent shared by all skills | **a** | Keeps one adapter file per agent — what someone porting to a third agent writes — as the brief names them. c would put orchestrator instructions into every lane's core skill. |
| Q4 | How the lane brief is produced | **a)** a template in the skill, filled from `autopilot next --run R --json` · b) a `brief` rendered by `autopilot next` | **a** | Writing the brief is judgement (touch map, other lanes, answers so far) and prose for an agent; a CLI-rendered brief would move instructions into Python, need per-agent wording and change a finished command. |
| Q5 | Gate criteria | as in criterion 9, per gate type, taken from the decision records (re-run the suite in the lane's worktree, read the diff by range, deliberate breakage of new tests when in doubt, real-runtime check in a scratch environment, branch without an upstream before publishing) · a blanket "review and approve" | **per gate type** | The reference behaviour demands per-gate criteria, not blanket approval. |
| Q6 | Who rebases at close | **a)** the lane stops after `review --json` and reports `rebase`; the orchestrator rebases once, at hand-off · b) the lane rebases at close, as the core skill's step 8 says, and again at hand-off if needed | **a** | Under sequential hand-off every earlier merge moves the mainline again, so a close-time rebase is usually repeated; the brief states the override explicitly. |
| Q7 | The rebase section's table | **a)** `File / Conflict / Resolution` for known-class resolutions, as §12.5 says, plus the checks re-run; a `# | Question | …` row only for anything decided · b) the question table the records here use | **a** | Mechanical resolutions are not decisions; anything that needed judgement still gets a row. |
| Q8 | Tests for a skill | install behaviour, per-skill notes, prose invariants by phrase, portability (no agent names in the portable text), command drift against the CLI parser · also snapshot the whole text | **without a snapshot** | Invariants catch the rules that matter; a snapshot fails on every wording edit and tests nothing specific. |
| Q9 | DESIGN §12 status | **a)** mark the skill parts of §12.2, §12.3, §12.5, §12.6, §12.8 *implemented (T024)* and the section heading *implemented*, leaving T033 as a trial · b) keep "partly implemented" until T033 | **a** | T033 builds nothing; every part of §12 then exists. |
| Q10 | Starting a task with several unmerged dependencies from an integration base (what this lane first did, before T031 and T032 merged) | **a)** one paragraph: only on the human's explicit instruction; merge the branches into the lane's base, record the merge commit as the fork point for `git rebase --onto`, claim with `--ignore-deps --run R` · b) leave it out until T033 | **a** | It has happened; the fork point is easy to lose, and `next` never offers such a task, so the rule "never on its own" needs saying. |

## Open questions and risks

- **Installer regression.** `skill_files` and removal serve every install; the change is covered by
  the existing T025 and integration tests plus criterion 3.
- **Class-3 conflict with T038.** T038 changes the core skill source and its installed copy;
  this branch adds a new installed skill and changes `installed.json`. The rebase after T038 merges
  is class 3: make the manifest valid, keep both sources, run `taskrail upgrade --force`.
- **OpenCode facts** rest on the spike's E6 run (1.15.13) and documentation; the trial (T033) is
  where they are checked end to end. The notes say "experimental" and require nothing experimental.
- **Size.** Five points: one skill, three references, two note sections, an installer change and
  tests. If the gate checklist grows past a short page, it stays a reference rather than splitting
  the task.
