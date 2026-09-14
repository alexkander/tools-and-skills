# T009 — autopilot decisions

Decisions for this task while it ran in an autopilot lane. Its decision is reserved to the human
(CLAUDE.md leaves Distribution undecided); gates that involve running code on the human's machine
were taken to the human too.

## frame gate

Reviewed: the frame in `docs/spikes/T009-decide-how-consumer-projects-install-thi.md` (commit
`8c87f22`): the question and five sub-questions, options O1–O5, criteria, evidence E1–E7 and limits.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Question and sub-questions | both agents · Claude Code only | **both agents** (orchestrator) | Only a comparison across both shows whether one mechanism serves them. |
| 2 | Scope | `skills/` only · include `tools/` | **`skills/` only** (orchestrator) | Libraries are depended on by version and taskrail has its own installer. |
| 3 | Hands-on trials (E6) in `/tmp` | isolated per agent, listing commands first, at most one short session per agent, no prompt-skipping flags · docs only | **isolated trials** — decided by the human | Update and removal behaviour must be measured; the human's settings, plugins and caches stay untouched, and an agent that cannot be isolated falls back to docs. |
| 4 | Running a third-party installer | read docs and source, do not run · run pinned in `/tmp` | **read, do not run** — decided by the human | No code from a package registry runs on this machine; its update and removal behaviour is described, not measured. |
| 5 | Mixed mechanisms by agent | allowed · one mechanism for all | **allowed** (orchestrator) | Every mechanism stays an adapter over the same directory, which is what CLAUDE.md requires. |
| 6 | Time box | 3 points · other | **3 points** (orchestrator) | Matches the row. |

Frame approved.

## decide gate — decided by the human

Reviewed: the completed artifact (commit `aa6bbd0`) with eleven sources read on 2026-09-14 and the
isolated trials: a Claude Code marketplace installed, updated and removed in a throwaway home; a
pinned copy discovered by OpenCode and validated for Claude Code, updated over a local edit and
removed; a submodule with a symlink. The human's settings, plugin records and OpenCode configuration
had the same digests before and after.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | How consumers install skills | copy at a pinned commit into `.claude/skills/<name>/` · Claude Code marketplace · submodule | **copy at a pinned commit** — decided by the human | The only option shown to serve both agents from one committed copy, with the pin and every update reviewable in the consumer. |
| 2 | Claude Code marketplace | defer · build now | **defer** — decided by the human | It serves Claude Code only and keeps the exact commit outside the consumer; build it when a consumer needs many-project installs, at the root with one `strict: false` entry per skill sourced from `./skills/<name>`. |
| 3 | Where the pin is recorded | the commit that adds or updates the copy · a lock file | **the commit** — decided by the human | No new file in the consumer's layout. |
| 4 | Follow-up tasks | CLAUDE.md Distribution chore · skill README docs · marketplace feature | **CLAUDE.md Distribution and skill READMEs** — decided by the human | The marketplace is deferred. |
