# T021 — Map a repository's column names onto taskrail's columns

Kind: feature · Epic: E05 · Status: planned

## Behaviour

A repository whose backlog already has established column headers — for example `Size` for
story points, where taskrail's core column is `Pts` — declares an alias in config instead of
renaming its headers:

```toml
[columns]
custom = ["Owner"]
aliases = { Pts = "Size", "Depends On" = "Blocked By" }
```

Each key is a core task column (`✓`, `ID`, `Kind`, `Depends On`, `Title`, `Pts`,
`Description`, matched case-insensitively) and each value is the header that repository uses
for it. One name per column.

With an alias in place:

- **Reading.** Every command that reads task tables — `validate`, `list`, `show`, `next`, ID
  allocation — resolves the aliased header to the core column, case-insensitively as today.
  `Size` feeds `points`; an aliased `ID`, `✓` or `Kind` still identifies a task table.
- **The alias replaces the name.** In that repository the column is called by its alias only.
  A task table that still uses the core name of an aliased column (a `Pts` header when `Pts` is
  aliased to `Size`) fails validation with a `column-alias` error naming the expected header,
  so the repository's convention is enforced rather than silently drifting.
- **Writing.** `new --pts 3` fills the `Size` cell; `done`, `discard` and `reopen` find an
  aliased `✓` column; a table created for an epic that has none, with no other table to copy,
  uses the alias names in its header.
- **Messages.** A missing required column is reported by the name the repository uses, with the
  core name alongside, for example `task table is missing column(s): Blocked By (Depends On)`.
- **Output is unchanged.** `--json` keeps its field names (`points`, `depends_on`, …) and
  `columns` keeps holding custom columns only, so callers do not depend on a repository's
  headers.

Conflicting configuration is refused at load time, like every other config error (exit 2):
an unknown key, an empty value or one containing `|`, an alias equal to another core column's
name, two columns given the same alias, or an alias equal to a `[columns].custom` entry — all
compared case-insensitively.

## Acceptance criteria

1. A backlog whose task tables use `Size` instead of `Pts`, with `aliases = { Pts = "Size" }`,
   validates with no errors and no `column-undeclared` warning, and `show --json` reports
   `points` from the `Size` cell.
2. An alias for each required column (`✓`, `ID`, `Kind`, `Depends On`, `Title`) and for
   `Description` is honoured: the table is recognised as a task table, the values are read into
   the same fields, and a missing aliased required column is reported by its alias and core
   name.
3. Alias headers match case-insensitively (`size`, `SIZE`).
4. With `Pts` aliased to `Size`, a task table whose header says `Pts` fails validation with a
   `column-alias` error at the table's line; without the alias, the same table validates as
   today.
5. `new --pts 3 --depends-on T001 --description D` appends a row whose `Size`, `Blocked By` and
   `Description` cells hold those values, in an existing table with aliased headers; the diff
   is that one row.
6. `new` in an epic with no task table, in a backlog with no table to copy, writes a header
   that uses the alias names.
7. `done`, `discard` and `reopen` change the status cell of a table whose `✓` column is
   aliased (for example to `Status`).
8. ID allocation sees the IDs of a table whose `ID` column is aliased, so `new` never reuses one
   — on the working tree and on scanned branches.
9. Config is refused with exit 2 and a message naming the problem for: an alias key that is not
   a core column; an empty alias or one containing `|`; an alias equal (case-insensitively) to
   another core column's name; two columns with the same alias; an alias equal to a custom
   column.
10. A repository without `aliases` behaves exactly as before (the existing test suite passes
    unchanged).

## Affected areas

- `tools/taskrail/src/taskrail/config.py` — parse and check `[columns].aliases` into a new
  `Config.column_aliases` (core name → header); one self-contained hunk next to `custom`.
- `tools/taskrail/src/taskrail/backlog.py` — `_index` and `_is_task_table` take an optional
  aliases mapping, applied to task tables only (the Epics table is untouched); `_parse_tasks`
  reports `column-alias` and names aliased columns in `task-columns`.
- `tools/taskrail/src/taskrail/ids.py` — pass the aliases when scanning for used IDs.
- `tools/taskrail/src/taskrail/writer.py` — pass the aliases in `set_status`, `add_task` and
  `_header_template`, and render alias names in a default header.
- `tools/taskrail/src/taskrail/install.py` — a commented `aliases` example in the `init` config.
- Tests: `tests/test_validate.py` (reading, conflicts), `tests/test_write.py` (writes),
  `tests/test_ids.py` (allocation).
- Docs: `tools/taskrail/DESIGN.md` (§3.2 Columns, §4 Configuration), `README.md` where config
  is described, and one line under `## Unreleased` in `CHANGELOG.md`.

## Out of scope

- Aliases for the Epics table columns (`ID`, `Epic`, `Objective`, `File`).
- Several aliases for one column, or aliases that differ per backlog in the same repository.
- Renaming the fields of `--json` output or the CLI flags (`--pts` stays `--pts`).
- `new --column Size=3` for an aliased core column: `--column` stays for custom columns and is
  refused with the existing "the task table has no column(s)" message; use `--pts`.
- Aliasing custom columns, or kinds routing (`when`) on an aliased core column.
- Rejecting duplicate header cells in general (a table naming the same column twice), which is
  pre-existing behaviour.
- A command that rewrites existing headers from one name to another.

## Open questions and risks

- **Replace versus add.** The plan makes the alias replace the core name (a `Pts` header is an
  error once `Pts` is aliased). The alternative accepts both names and needs a
  `column-duplicate` error for tables that name the column both ways; it is more forgiving of
  mixed files but no longer enforces a repository's fixed header. Decided at the plan gate.
- **Config shape.** `aliases` maps core name → repository header. The reverse direction
  (`Size = "Pts"`) reads naturally too; the chosen one keeps keys to a closed, checkable set.
- **Signature changes in shared helpers.** `_index` and `_is_task_table` gain an optional
  argument with a default, so callers that do not pass it keep today's behaviour; a missed call
  site would silently ignore aliases, which the write and ID tests are there to catch.
- **Parallel work.** T018 also edits config loading; the change here is one hunk beside
  `[columns].custom` to keep a rebase conflict small.
