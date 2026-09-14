# T044 — autopilot decisions

Decisions for this task while it ran in an autopilot lane. The human asked to start it before its
upstream condition was met (rtk-ai/rtk PR #3577 still open and issue #3230 open on 2026-09-14), so
both are evaluated as risks against release v0.49.0. Running third-party code on the human's machine
and the final decision are the human's.

## frame gate

Reviewed: the frame in `docs/spikes/T044-evaluate-using-rtk-in-this-repository.md` (commit
`0f50187`): the question, criteria E1–E12, the command set drawn from this repository's own work,
the primary sources read on 2026-09-14, and the limits.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| D1 | Question and scope | this repository's agent sessions, Claude Code and OpenCode, distribution out · other | **as proposed** (orchestrator) | Matches the human's instruction that RTK is evaluated for use here. |
| D2 | Hands-on trials | official v0.49.0 musl binary in a temporary directory, checked against `checksums.txt`, throwaway `HOME`/`XDG_*`, `RTK_TELEMETRY_DISABLED=1`, a temporary clone, `rtk rewrite` and direct runs only, `rtk init` only in the throwaway home, no agent session, checksums of the human's configuration before and after · also build PR #3577 · docs only | **isolated binary trials** — decided by the human | Savings and exit-code and `--json` preservation must be measured, without touching the human's setup. |
| D3 | Disqualifying failures | any changed exit code or taskrail `--json` output rules out a hook · allow with exclusions | **rules out the hook** — decided by the human | The autopilot and the backlog procedure depend on exact exit codes and JSON; an option with exclusions is still recorded. |
| D4 | Time box | 2 points · 3 with a PR build | **2 points** (orchestrator) | Follows D2. |

Frame approved.

## decide gate — decided by the human

Reviewed: the completed artifact (commit `7226f68`): 53 raw-versus-rewritten cases with RTK v0.49.0
in isolation, the hook payload and install/uninstall footprint in a throwaway home, and source
reading at `b1c0dc0`, `develop` `d402152` and PR #3577's diff. Exit codes were kept in every case,
but `uv run … taskrail … --json` came out as invalid JSON, `git log` lost a `Reopens:` trailer, and
`git diff` and `head` were truncated. The human's shell and agent configuration digests matched,
except Claude Code's `known_marketplaces.json`, whose only field is a refresh timestamp; RTK never
ran with the real home, so that change is attributed to Claude Code, not proven.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Verdict | no adoption · hook with per-user exclusions | **no adoption** — decided by the human | The rewritten `--json` output breaks under the frame's rule, and exclusions are per user and would leak into other projects. |
| 2 | Follow-ups | CLAUDE.md note · taskrail `--json` test through `uv run` · none | **both** — decided by the human | The note protects contributors who install RTK globally; the test guards the JSON contract procedures here rely on. The CLAUDE.md wording is shown to the human before publishing. |

## close

The lane marked the decision accepted in the artifact, opened T045 and T046 in E06, and closed
T044. No rebase was needed (`origin/main` is `d3833e7`). Checked before publishing: the branch
changes only documentation and `TODO.md`, the artifact names no local user, host or path,
`taskrail validate` 0 errors, no upstream.
