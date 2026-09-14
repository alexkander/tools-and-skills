# T060 — Remove DESIGN.md and CLAUDE.md from the autopilot's governing paths

## Goal

`[autopilot].governing` in `.taskrail/config.toml` lists `CLAUDE.md` and
`tools/taskrail/DESIGN.md`. The key has two roles (DESIGN.md §12.6 and the `taskrail-autopilot`
skill): the documents the orchestrator reads first to answer gates, and paths whose change
escalates to the human. In the T033 trial the `governing` flag also stayed on after the human had
approved the edit (F9). The human decided that edits to both documents are decided by the
orchestrator at the gate and reviewed by the human in the pull request, permanently.

This chore empties `governing` in this repository's config, keeps both documents named as what the
orchestrator reads first, and adds an automated check for both, without making the
`tools/taskrail` tests depend on this repository's own config.

## Change set

- `.taskrail/config.toml` — `governing = []`, with a comment saying why it is empty and where the
  read-first documents are named:

  ```toml
  # Nothing escalates by path: the orchestrator decides lane edits to CLAUDE.md and
  # tools/taskrail/DESIGN.md at the gate and the human reviews them in the pull request.
  # The orchestrator still reads both first; CLAUDE.md (Backlog) names them.
  governing = []
  ```

- `CLAUDE.md` — one bullet at the end of the *Backlog* section, the place every agent working on
  this repository reads, whatever the agent:

  ```markdown
  - The autopilot is enabled here (`[autopilot]` in `.taskrail/config.toml`). Its orchestrator
    answers lane gates from this file and `tools/taskrail/DESIGN.md` first. Neither is a
    `governing` path: a lane may change them when its task needs it, the orchestrator decides that
    change at the gate, and the human reviews it in the pull request.
  ```

- `.taskrail/tests/test_config.py` — new, a repository-level pytest module that uses only the
  standard library (`tomllib`, `pathlib`) and locates the repository from its own path. It asserts:
  - `[autopilot].enabled` is `true` and `[autopilot].governing` is `[]`;
  - `CLAUDE.md` has a line under `## Backlog` naming the autopilot, `tools/taskrail/DESIGN.md` and
    `governing`, and both documents exist.

  It lives with this repository's taskrail setup, outside `tools/taskrail`, so the tool's own tests
  never read this repository's config. `taskrail upgrade` manages only the files listed in
  `.taskrail/installed.json` (`.taskrail/bin/taskrail` and the installed skills), so it does not
  touch this directory. It runs with the pytest already in taskrail's environment:
  `uv run --directory tools/taskrail pytest -q <repo>/.taskrail/tests`.

- `CLAUDE.md` *Commands* — one line documenting that invocation, next to the `tools/taskrail`
  commands.

- This artifact and its row in `docs/chores/README.md`.

## Decisions needed

1. **Where the read-first role is kept.** Recommended: a bullet in `CLAUDE.md` *Backlog* plus a
   comment on the empty key in the config. `CLAUDE.md` is loaded by Claude Code and read by
   OpenCode, so the orchestrator sees it without relying on the skill's pointer to the key; the
   comment explains the empty key to whoever reads the config. Alternatives: (a) the config comment
   only — the skill tells the orchestrator to read the `governing` paths, and with none it may not
   look at comments; (b) `CLAUDE.md` only — the empty key then looks like an omission; (c) a new
   `tools/taskrail` key separating "read first" from "escalate" — the generic fix, but it changes
   the tool, DESIGN.md and the autopilot skill that other lanes are editing, so it is proposed as a
   follow-up (question 3), not done here.
2. **How the check is automated.** Recommended: `.taskrail/tests/test_config.py` run with taskrail's
   pytest, as above. Alternatives: (a) a root `tests/` directory — conventional, but the root
   layout in `CLAUDE.md` holds only `skills/`, `tools/` and `libs/` items, and this test is about
   the repository's taskrail setup; (b) a test under `tools/taskrail/tests` that reads
   `../../.taskrail/config.toml` — rejected: it makes the tool's tests depend on this repository;
   (c) also running it from the configured `test` check, by changing
   `[checks].test` to collect both directories — it would run on every lane of every kind, but it
   changes the check the lanes of run 20260914-1 are using and pytest's rootdir handling with two
   distant paths; not recommended now.
3. **Follow-up task.** Open, in epic E02, a feature: *Separate the documents the orchestrator reads
   first from the paths that escalate* — a `[autopilot].read_first` key (or similar) that the
   skill reads, leaving `governing` for escalation only; verified by pytest on config loading,
   `status` output and the skill source and installed copies. Recommended: yes, opened by this lane
   at the docs stage, or by the orchestrator if it prefers to allocate the ID itself. Alternative:
   no follow-up, since the `CLAUDE.md` bullet covers this repository.

## Out of scope

- Anything under `tools/taskrail/` (code, DESIGN.md, CHANGELOG, the autopilot skill sources) and
  the installed copies under `.claude/skills/`: the default `governing = []` already exists, and
  lanes of run 20260914-1 are editing those files.
- The `escalate_gates`, `max_lanes` and `enabled` values, which stay as T058 set them.
- The T058 artifact, which records what was decided then.
- F9 itself (the lasting `governing` flag), which T049 fixes.

## Verification

- The new test is observed failing against the current config (`governing` still lists both
  documents) and passing after the change:
  `uv run --directory tools/taskrail pytest -q <repo>/.taskrail/tests`.
- `.taskrail/bin/taskrail validate` loads the config with an empty `governing` without errors.
- `.taskrail/bin/taskrail autopilot status --json` from the worktree loads the config, and no task
  reports a `governing` escalation.
- The configured `test` check (`uv run --directory tools/taskrail pytest -q`) passes; `lint` is not
  configured.
