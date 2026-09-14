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

## close

The lane marked the recommendation accepted in the artifact, opened T041 (CLAUDE.md Distribution)
and T042 (skill README install steps) in E04 as decided, and closed T009. No rebase was needed
(`origin/main` is `9c87bc2`). Checked before publishing: the branch changes only documentation and
`TODO.md` (T009 `✅`, T041 and T042 added), `taskrail validate` 0 errors, no upstream.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Pull request type and scope | `docs(skills)` · `docs(taskrail)` | **`docs(skills)`** | The decision concerns the `skills/` items, not taskrail. |

## rebase after T004, T040 and T039

T004 (`fff3fe6`), T040 (`3f3b8d7`) and T039 (`b7a11a9`) were squash-merged into `main`. The
orchestrator rebased the branch onto `origin/main`.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Conflict in `docs/autopilot/decisions/README.md` | keep both rows · stop | **keep both** | Rows added on both sides. |

After the rebase: `TODO.md` differs from `main` in T009 `✅` and the added T041 and T042 rows, and
`taskrail validate` reports 0 errors over 42 tasks.
