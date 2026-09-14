# T044 — Evaluate using RTK in this repository

**Status: draft, frame stage. No verdict yet.** This document holds the question, the evidence
that would answer it, the approach and the limits, for the human to agree on before the
investigation starts.

## Question

**Should agents working on this repository run their shell commands through RTK?** And if they
should, how is it wired, for which agents, and with which exclusions?

The scope is this repository's own agent sessions, in Claude Code and OpenCode. Distributing
RTK, or recommending it to consumers of this repository's skills and tools, is out of scope.

Sub-questions:

1. **What changes in a session.** Which of the commands agents actually run here would RTK
   rewrite, and what would the agent then see instead of the raw output?
2. **What it saves.** How much output, measured in bytes and in RTK's estimated tokens, would
   those commands stop feeding the agent?
3. **Correctness.** Does it ever preserve less than the raw command?
   - exit codes;
   - error text;
   - exact machine-readable output, such as `taskrail … --json`;
   - git content that a procedure here reads, such as commit trailers.
4. **The known defects.** Evaluated against the current release, not as preconditions:
   - **PR #3577 is not merged.** It adds a "never-worse" exit-code guard across RTK's tool
     filters.
   - **Issue #3230 is open.** The hook rewrites the `command` bypass prefix.

   What do these two defects cost on this repository's commands, and can a configuration avoid
   them?
5. **Footprint and scope.** What does it install, and where?
   - Can it be enabled for this repository only, or only globally, for each agent?
   - What must a contributor have installed for a committed configuration to work, and what
     happens when they do not have it?
6. **Telemetry and local data.** What does it send, what does it store on disk, and what are
   the defaults?
7. **Licence.** Does the licence allow the use proposed here?
8. **Reversibility.** What does removal leave behind?
9. **Agent portability.** Can the same arrangement serve Claude Code and OpenCode without
   making either the canonical form (CLAUDE.md, *Agent portability*)?

## What RTK is (from its own documentation, preliminary)

This is read, not verified. The investigation checks each point against source at a pinned
commit.

- **The binary.** RTK is a "CLI proxy" in a single Rust binary. It runs a command and filters,
  groups, truncates or deduplicates its output before the agent reads it [R1].
- **The rewrite.** For hook-based agents, a rewrite turns `git status` into `rtk git status`
  before execution [R1].
- **What the hook covers.** Only Bash tool calls. Claude Code's built-in `Read`, `Grep` and
  `Glob` bypass it [R1].
- **Claude Code.**
  - `rtk init -g` installs a PreToolUse hook as a native binary command (`rtk hook claude`),
    plus an `RTK.md` file [R1].
  - `rtk init` without `-g` writes RTK instructions into the project's `./CLAUDE.md`, with
    "No hook, no global effect" [R2].
- **OpenCode.** `rtk init -g --opencode` installs a TypeScript plugin that uses
  `tool.execute.before` [R1]. Its source is `hooks/opencode/rtk.ts` [R3].
- **Where each agent can load such a hook.**
  - Claude Code reads hooks from `~/.claude/settings.json` (all projects) and from
    `.claude/settings.json` (single project, "can be committed to the repo") [C1].
  - OpenCode loads plugins from `.opencode/plugins/` ("Project-level") and from
    `~/.config/opencode/plugins/` ("Global") [O1].
  - So a per-repository wiring is possible in principle for both agents, even though RTK's own
    installer targets the global locations. Whether RTK's hook works when wired that way is
    for the investigation.
- **Configuration and local data.**
  - Configuration lives in `~/.config/rtk/config.toml`, with `[hooks] exclude_commands` [R1].
  - On failure, RTK saves the full unfiltered output in a local store that `rtk recall <id>`
    reads back [R1].
  - A local SQLite tracking database keeps 90 days of history by default [R4].
- **Telemetry: the sources disagree.**
  - The README [R1] and `docs/TELEMETRY.md` [R4] say telemetry is "disabled by default" and
    opt-in.
  - `DISCLAIMER.md` at the same commit says it "collects anonymous, aggregate usage metrics by
    default" [R5].
  - The source decides; the investigation reads it.
- **Licence.** Apache-2.0 [R6].
- **Current state.**
  - The latest release is `v0.49.0`, published 2026-09-11, tag commit `b1c0dc0` [R7].
  - The default branch is `develop`, which publishes `dev-0.50.0-rc.*` pre-releases [R7].
  - PR #3577 is open and not merged [R8]. It targets exit codes masked by "all-green
    summaries" in the pytest, ruff, mypy, cargo, vitest/jest, tsc, go and golangci-lint filters.
  - Issue #3230 is open [R9]. `command grep …` becomes `command rtk grep …`, so the POSIX
    prefix used to reach the real binary routes back into RTK. The issue also notes that under
    Claude Code `command grep` is the usual way to reach the real `grep`.

## Evidence

Criteria, and what would count as an answer for each.

| # | Criterion | Evidence that answers it |
|---|---|---|
| E1 | Output savings on this repository's real commands | Raw versus RTK output size, in bytes and RTK's estimate, on the command set below |
| E2 | Exit codes preserved | `$?` of raw versus RTK for each command, in passing and in failing states: a failing test, a failing validation (exit 1), a not-found (exit 3) and a refusal (exit 5) |
| E3 | Errors not hidden | Whether the failing cases still show the failure text an agent needs to act, or only a pointer to `rtk recall` |
| E4 | Exact output untouched where procedures parse it | Byte-for-byte comparison of `.taskrail/bin/taskrail … --json` output; whether `git log` keeps the trailers that `git log --grep='^Reopens: <ID>$'` and review read |
| E5 | Rewrite coverage | `rtk rewrite '<cmd>'` for each command in the set: which ones are rewritten, which pass through, and how pipes, `cd … &&` chains and `uv run --directory` are handled |
| E6 | Bypass behaviour (#3230) | `rtk rewrite` on `command git …`, `command grep …`, `\git …` and absolute paths in `v0.49.0`, plus what `exclude_commands` and `rtk proxy` offer as an escape |
| E7 | Exit-code masking (#3577) | The PR's diff, set against the filters this repository's commands reach (pytest through `uv run` above all), and a failing-pytest case measured on `v0.49.0` |
| E8 | Footprint and scope | Files `rtk init` writes for each agent, global and local; whether a project-level hook or plugin works; behaviour when the binary is missing |
| E9 | Telemetry and local data | Source at the pinned commit: the default consent state, when the network is contacted, what the tracking database and recall store keep and where |
| E10 | Licence | `LICENSE` at the pinned commit, and whether any bundled hook or plugin file is licensed differently |
| E11 | Reversibility | What `rtk init -g --uninstall` removes, and what remains: config, database, recall store, `RTK.md` |
| E12 | Agent portability | Whether one arrangement serves both agents, and where agent-specific wiring would live |

**The command set** is taken from this repository's procedures and checks, not invented:

- `uv run --directory tools/taskrail pytest -q` (the configured `test` check), passing and with
  one failing test;
- `.taskrail/bin/taskrail show T044 --json`, `list --json`, `validate`, `next --json`, and
  error cases for exits 1, 3 and 5;
- `git status`, `git log --oneline -n 20`, `git log -n 5` (full messages with trailers),
  `git diff`, `git diff --stat`, `git worktree list`, `git log --grep='^Reopens: T006$'`;
- `grep -rn`, `ls`, `cat`, `find` on repository paths.

**Also recorded:** taskrail runs git itself through `subprocess`. The investigation confirms
from the hook's contract that only the agent's own Bash command string is rewritten, never a
program's child processes.

## Approach

1. **Pin.** Record the release (`v0.49.0`, tag commit `b1c0dc0`), the `develop` commit read,
   and PR #3577's head commit.
2. **Read.** Using primary sources only, read:
   - RTK's README, INSTALL.md, the guide pages on configuration and supported agents,
     `docs/TELEMETRY.md` and `LICENSE`;
   - the Claude Code and OpenCode hook sources under `hooks/`;
   - the rewrite registry, the exit-code handling, and the pytest, git and generic filters in
     `src/`;
   - the telemetry gate;
   - PR #3577's diff, and issue #3230 with its comments;
   - the Claude Code hooks and settings documentation, and the OpenCode plugins documentation.

   Every source gets a URL, the date read and, for code, the commit.
3. **Trial, if the human allows it (decision D2).** Run the command set raw and through RTK
   against a throwaway clone of this repository, recording commands, output sizes and exit
   codes. The trial covers `rtk rewrite` (a pure string transformation) and direct `rtk <cmd>`
   runs. No agent session is started.
4. **Compare** each criterion, then draft options, for example:
   - no adoption, with re-evaluation triggers;
   - explicit `rtk` use only, with no hook;
   - a project-level hook or plugin with exclusions;
   - a global install left to each contributor.
5. **Decide.** Write the verdict, recommendation, what would change it, and how to reproduce.
   Adoption itself becomes follow-up tasks.

## Limits

- **Time box:** 2 points.
- **No global install.** RTK is not installed on `PATH` or through a package manager, and
  `rtk init` is never run against the human's real home directory.
- **No change to the human's agent setup.** That covers agent settings, hooks, plugins, shell
  profile and `PATH`, during the frame and, unless D2 says otherwise, after it.
- **Nothing published:** no push, no pull request, no issue or comment on RTK's repository.
- **Sources.** Primary sources only: RTK's repository, and the official Claude Code and OpenCode
  documentation. No third-party write-ups, and nothing recorded in other local repositories.
- **Not covered:**
  - distributing RTK to consumers;
  - RTK on agents other than Claude Code and OpenCode;
  - billing or cost modelling beyond output size;
  - RTK's non-Bash commands (`rtk read`, `rtk smart`) as replacements for built-in agent tools;
  - pre-releases, except PR #3577's diff read as source.
- **Frame only so far.** No trial has run. Everything under *What RTK is* is documentation
  that has not been verified.

## Sources read during the frame

All read on 2026-09-14. Quotations are short fragments.

| # | Source |
|---|---|
| R1 | RTK README at `v0.49.0` — https://github.com/rtk-ai/rtk/blob/b1c0dc00649c50fbe8930f849c800d4d6ca12091/README.md |
| R2 | RTK INSTALL.md at `v0.49.0` — https://github.com/rtk-ai/rtk/blob/b1c0dc00649c50fbe8930f849c800d4d6ca12091/INSTALL.md |
| R3 | RTK `hooks/` directory at `v0.49.0` — https://github.com/rtk-ai/rtk/tree/v0.49.0/hooks |
| R4 | RTK docs/TELEMETRY.md at `v0.49.0` — https://github.com/rtk-ai/rtk/blob/b1c0dc00649c50fbe8930f849c800d4d6ca12091/docs/TELEMETRY.md |
| R5 | RTK DISCLAIMER.md at `v0.49.0` — https://github.com/rtk-ai/rtk/blob/b1c0dc00649c50fbe8930f849c800d4d6ca12091/DISCLAIMER.md |
| R6 | RTK LICENSE at `v0.49.0` — https://github.com/rtk-ai/rtk/blob/b1c0dc00649c50fbe8930f849c800d4d6ca12091/LICENSE |
| R7 | RTK releases — https://github.com/rtk-ai/rtk/releases/tag/v0.49.0 and https://api.github.com/repos/rtk-ai/rtk/releases |
| R8 | RTK PR #3577 — https://github.com/rtk-ai/rtk/pull/3577 (state `open`, `merged: false`) |
| R9 | RTK issue #3230 — https://github.com/rtk-ai/rtk/issues/3230 (state `open`) |
| C1 | Claude Code, Hooks reference — https://code.claude.com/docs/en/hooks.md |
| O1 | OpenCode, Plugins — https://opencode.ai/docs/plugins/ |

## Decisions for the frame gate

- **D1 — Question and scope.** Is the question above right: this repository's own sessions,
  in both Claude Code and OpenCode, with distribution out of scope?
- **D2 — Hands-on trials.**
  - *Recommended:* isolated trials of the `v0.49.0` release binary. The prebuilt
    `rtk-x86_64-unknown-linux-musl.tar.gz` is downloaded to a temporary directory and checked
    against the release's `checksums.txt`.
  - Every run uses throwaway `HOME` and `XDG_*` directories and `RTK_TELEMETRY_DISABLED=1`,
    against a temporary clone of this repository.
  - `rtk init` runs only inside the throwaway home, to observe the files it writes.
  - No agent session is started, and the human's files are hashed before and after.
  - *Alternatives:* documentation and source reading only; or also building PR #3577's head
    from source in the temporary directory, to measure the guard before it is released.
- **D3 — Disqualifying failures.** Does any exit-code change, or any change to
  `taskrail … --json` output, on a command in the set rule out a hook-based adoption? The
  alternative is to allow it with exclusions.
  - *Recommended:* yes, it rules the hook out, while still allowing an exclusion-based option
    to be recorded.
- **D4 — Time box.** Is 2 points still right, given that trials may be added?
