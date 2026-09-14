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
