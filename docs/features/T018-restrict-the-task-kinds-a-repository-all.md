# T018 — Restrict the task kinds a repository allows

Kind: feature · Epic: E05 · Status: planned

## Behaviour

A repository can state the closed set of task kinds it allows, in `.taskrail/config.toml`:

```toml
[kinds]
allowed = ["spec", "bug", "chore"]   # omit the table, or the key, to allow every defined kind
```

taskrail always ships the core kinds `bug`, `chore`, `feature` and `spike`. Today a repository
whose own rules name exactly three kinds cannot make taskrail enforce that: every core kind is
always resolved, so a `feature` row passes `validate`. With `allowed` set:

- **Resolution.** Kinds are still resolved in layers (core, then `.taskrail/types/`, then
  `.taskrail/overrides/`), and every descriptor is still parsed and checked. The allowlist is
  applied to the resolved set afterwards, so it covers core, local and overridden kinds the same
  way. A kind that is not allowed is left out of the project: `kind list` does not show it,
  `show` has no descriptor for it, and no command resolves it.
- **Validation.** A task whose kind is defined but not allowed is an error with its own code,
  `task-kind-disallowed`, reported with file and line and naming the allowed kinds — distinct
  from `task-kind-unknown`, which stays for kinds nothing defines. As with every validation
  error, commands that refuse an invalid backlog (`show`, `claim`, `new`, `done`, `review`, …)
  refuse it too.
- **A stale allowlist.** A name in `allowed` that no core, local or override kind defines is a
  validation error, `kind-allowed-unknown`, so a typo cannot silently shrink the set.
- **Unused local work.** A kind defined under `.taskrail/types/` or `.taskrail/overrides/` that
  `allowed` leaves out is a warning, `kind-not-allowed`: the repository wrote a descriptor it
  then excluded, which is most likely a mistake. Excluded core kinds are silent — excluding them
  is the point of the setting.
- **Creating tasks.** `taskrail new --kind feature` in such a repository writes nothing: without
  `--workspace` the in-memory validation reports `task-kind-disallowed` (exit 1); with
  `--workspace` it refuses before creating a branch, saying the kind is not allowed (exit 2).
- **Configuration errors.** `[kinds]` must be a table; `allowed` must be a non-empty list of
  kind names (lowercase letters, digits and dashes) without repeats. Anything else is a
  configuration error (exit 2), like the rest of `config.toml`.

Without `[kinds]`, behaviour is unchanged.

## Acceptance criteria

1. With no `[kinds]` table, the resolved kinds and validation results are exactly as today.
2. With `allowed = ["bug", "chore"]`, `load_kinds` resolves only `bug` and `chore`, and
   `kind list --json` lists only those two.
3. A task of a core kind left out of `allowed` fails `validate` with `task-kind-disallowed` at
   its file and line, and the message names the allowed kinds; a task of a kind nothing defines
   still fails with `task-kind-unknown`.
4. A local kind under `.taskrail/types/` that is named in `allowed` resolves and validates its
   tasks; one that is not named is excluded and produces a `kind-not-allowed` warning.
5. An override of a kind that `allowed` leaves out is excluded and produces a
   `kind-not-allowed` warning; an override of an allowed kind still replaces it.
6. A name in `allowed` that no layer defines fails `validate` with `kind-allowed-unknown`.
7. `[kinds]` that is not a table, `allowed` that is not a list, is empty, holds a non-string or a
   malformed name, or repeats a name, raises a configuration error naming the problem.
8. `new --kind <disallowed>` writes nothing and exits non-zero, both without `--workspace`
   (exit 1) and with it (exit 2, before any branch or worktree is created).

## Affected areas

- `tools/taskrail/src/taskrail/config.py` — a new `allowed_kinds: tuple[str, ...]` field on
  `Config` and a self-contained block parsing `[kinds]`. Kept to small, separate hunks because
  T021 (column aliases) edits the same file in parallel.
- `tools/taskrail/src/taskrail/kinds.py` — `load_kinds` applies the allowlist after resolution
  and reports `kind-allowed-unknown` and `kind-not-allowed`. Its signature does not change.
- `tools/taskrail/src/taskrail/project.py` — `_check_tasks` reports `task-kind-disallowed`.
- `tools/taskrail/src/taskrail/cli.py` — the `new --workspace` refusal message distinguishes a
  disallowed kind from an undefined one.
- `tools/taskrail/tests/test_kinds.py`, `test_validate.py`, `test_cli.py` or `test_write.py` —
  tests for the criteria.
- `tools/taskrail/DESIGN.md` (§3.3 `Kind` value, §4 configuration example, §5.2 resolution),
  `tools/taskrail/README.md` (Task kinds) and one line under `## Unreleased` in
  `tools/taskrail/CHANGELOG.md`.

## Out of scope

- Skipping the executor skills of disallowed core kinds when `init` or `upgrade` installs
  skills: `taskrail-feature` and `taskrail-spike` are still installed. Installation does not
  read the resolved kinds today; this would be a follow-up task if wanted.
- A denylist (`disabled = [...]`) alongside the allowlist. An allowlist matches rules that name a
  closed set, and a core kind added by a later taskrail release stays excluded instead of
  appearing silently.
- Per-backlog allowlists; `[kinds]` applies to every backlog in the repository.
- Adding a commented `[kinds]` example to the config that `taskrail init` writes.
- Migrating or rewriting existing rows whose kind becomes disallowed.

## Open questions and risks

- **Closed tasks of a disallowed kind.** A repository adopting taskrail with history may have
  done or discarded rows of a kind it no longer allows. The plan rejects them like pending ones,
  consistent with `task-kind-unknown` today, which ignores status. The alternative is a warning
  for closed tasks and an error only for pending ones.
- **Name of the setting.** `[kinds] allowed` follows the task title; `enabled` would read
  equally well.
- **Parallel edits to `config.py`.** T021 also changes config loading; the hunks here are kept
  small so a rebase conflict, if any, is mechanical.
