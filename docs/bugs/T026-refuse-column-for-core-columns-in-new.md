# T026 — Refuse --column for core columns in new

Kind: bug · Epic: E02 · Status: diagnosed

## Symptom

`taskrail new --column NAME=VALUE` is meant for custom columns. Given the name of a core task
column (`✓`, `ID`, `Kind`, `Depends On`, `Title`, `Pts`, `Description`) in a repository where
that column is not aliased, `new` exits 0 and either silently discards the value (`✓`, `ID`) or
silently writes it, overriding the dedicated flag (`Kind` over `--kind`, `Title` over
`--title`, `Pts` over `--pts`, …). The same name in another letter case (`id=T9`) fails with a
misleading message that the table has no such column. Only a core column that is **aliased**
in `[columns].aliases` is refused with a hint naming the flag to use (added by T021).

Expected: every core column is refused, whatever its case and whether or not it is aliased,
exiting 2 with a message naming the flag that fills it (or saying taskrail sets it), and
writing nothing.

## Reproduction

A throwaway git repository with this `.taskrail/config.toml`:

```toml
version = "taskrail-v0.1.0"

[[backlog]]
name = "main"
prefix = "T"
file = "TODO.md"

[columns]
custom = []
# plain:   no aliases line
# partial: aliases = { Pts = "Size" }
# full:    aliases = { "✓" = "Status", ID = "Key", Kind = "Type", Pts = "Size", "Depends On" = "Blocked By", Title = "Summary", Description = "Notes" }
```

and a `TODO.md` with epic `E01` holding one task table (`| ✓ | ID | Kind | Pts | Depends On |
Title | Description |`, with the `Pts` header renamed `Size` for *partial* and every header
renamed to its alias for *full*) and one row `T001`. A fresh copy per command, then:

```bash
taskrail --root <repo> new --epic E01 --kind bug --title "Negative totals" --column "<pair>"
```

## Evidence

Run at `ee38f5b` (origin/main). `row` is the row `new` appended, or `<none>`:

```
plain   --column "✓=✅"               exit=0 out=T002
        row: | ⬜ | T002 | bug     | —   | —          | Negative totals |             |
plain   --column "ID=T9"              exit=0 out=T002
        row: | ⬜ | T002 | bug     | —   | —          | Negative totals |             |
plain   --column "Kind=feature"       exit=0 out=T002
        row: | ⬜ | T002 | feature | —   | —          | Negative totals |             |
plain   --column "Depends On=T001"    exit=0 out=T002
        row: | ⬜ | T002 | bug     | —   | T001       | Negative totals |             |
plain   --column "Title=Other"        exit=0 out=T002
        row: | ⬜ | T002 | bug     | —   | —          | Other          |             |
plain   --column "Pts=3"              exit=0 out=T002
        row: | ⬜ | T002 | bug     | 3   | —          | Negative totals |             |
plain   --column "Description=Other"  exit=0 out=T002
        row: | ⬜ | T002 | bug     | —   | —          | Negative totals | Other       |
plain   --column "id=T9"              exit=2 out=taskrail: the task table has no column(s): id
        row: <none>
plain   --column "kind=feature"       exit=2 out=taskrail: the task table has no column(s): kind
        row: <none>
plain   --column "pts=3"              exit=2 out=taskrail: the task table has no column(s): pts
        row: <none>
partial --column "✓=✅"               exit=0 out=T002
        row: | ⬜ | T002 | bug     | —    | —          | Negative totals |             |
partial --column "ID=T9"              exit=0 out=T002
        row: | ⬜ | T002 | bug     | —    | —          | Negative totals |             |
partial --column "Kind=feature"       exit=0 out=T002
        row: | ⬜ | T002 | feature | —    | —          | Negative totals |             |
partial --column "Depends On=T001"    exit=0 out=T002
        row: | ⬜ | T002 | bug     | —    | T001       | Negative totals |             |
partial --column "Title=Other"        exit=0 out=T002
        row: | ⬜ | T002 | bug     | —    | —          | Other          |             |
partial --column "Pts=3"              exit=2 out=taskrail: --column cannot set core column Pts (named `Size` here); set it with --pts
        row: <none>
partial --column "Description=Other"  exit=0 out=T002
        row: | ⬜ | T002 | bug     | —    | —          | Negative totals | Other       |
partial --column "id=T9"              exit=2 out=taskrail: the task table has no column(s): id
        row: <none>
partial --column "kind=feature"       exit=2 out=taskrail: the task table has no column(s): kind
        row: <none>
partial --column "pts=3"              exit=2 out=taskrail: --column cannot set core column Pts (named `Size` here); set it with --pts
        row: <none>
full    --column "✓=✅"               exit=2 out=taskrail: --column cannot set core column ✓ (named `Status` here); taskrail sets it
full    --column "ID=T9"              exit=2 out=taskrail: --column cannot set core column ID (named `Key` here); taskrail sets it
full    --column "Kind=feature"       exit=2 out=taskrail: --column cannot set core column Kind (named `Type` here); set it with --kind
full    --column "Depends On=T001"    exit=2 out=taskrail: --column cannot set core column Depends On (named `Blocked By` here); set it with --depends-on
full    --column "Title=Other"        exit=2 out=taskrail: --column cannot set core column Title (named `Summary` here); set it with --title
full    --column "Pts=3"              exit=2 out=taskrail: --column cannot set core column Pts (named `Size` here); set it with --pts
full    --column "Description=Other"  exit=2 out=taskrail: --column cannot set core column Description (named `Notes` here); set it with --description
full    --column "id=T9"              exit=2 out=taskrail: --column cannot set core column ID (named `Key` here); taskrail sets it
full    --column "kind=feature"       exit=2 out=taskrail: --column cannot set core column Kind (named `Type` here); set it with --kind
full    --column "pts=3"              exit=2 out=taskrail: --column cannot set core column Pts (named `Size` here); set it with --pts
(every full row: <none>)
```

The column value wins over the flag, and the kind check can be sidestepped in `--workspace`:

```
$ taskrail new --epic E01 --kind bug --title T --pts 5 --column Pts=3
T002
exit=0
| ⬜ | T002 | bug     | 3   | —          | T              |             |

$ taskrail new --epic E01 --kind bug --title T --column Kind=feature --workspace
T002
workspace /tmp/.../.worktrees/T002-t on branch T002-t from main
exit=0
| ⬜ | T002 | feature | —   | —          | T              |             |
```

The post-write validation still catches a *value* that is invalid on its own:

```
$ taskrail new --epic E01 --kind bug --title T --column Kind=nonsense
TODO.md:14: error: kind `nonsense` is not defined (known: bug, chore, feature, spike) [task-kind-unknown]
taskrail: the change would leave the backlog invalid; nothing was written
exit=1

$ taskrail new --epic E01 --kind bug --title T --column Kind=feature   # kinds.allowed = [bug, chore]
TODO.md:14: error: kind `feature` is not allowed (kinds.allowed: bug, chore) [task-kind-disallowed]
taskrail: the change would leave the backlog invalid; nothing was written
exit=1
```

## Root cause

`cmd_new` in `tools/taskrail/src/taskrail/cli.py` builds a `values` dict keyed by core column
name and hands it to `writer.add_task`. Its `--column` loop refuses a name only when it matches
an entry of `project.config.column_aliases` (the core name or the alias of an **aliased**
column):

```python
aliased = next(
    (core for core, alias in project.config.column_aliases.items() if name.strip().lower() in (core.lower(), alias.lower())),
    None,
)
if aliased is not None:
    ...refuse, exit 2...
values[name.strip()] = value.strip()
```

Every other name falls through to `values[name.strip()] = value.strip()`, keyed by the user's
spelling. An unaliased core column is therefore never refused, and what happens next depends on
where its key collides in `values`:

- `Kind`, `Title` — set from the flags before the loop, so the column **overwrites** them.
- `Pts`, `Depends On`, `Description` — set before the loop only when their flag is given, so the
  column either fills the cell or **overwrites** the flag.
- `ID`, `✓` — set after the loop (`values["ID"] = task_id`, `values["✓"] = ...`), so the column
  value is **silently discarded**.
- Any other letter case (`id`, `kind`) matches no key; `writer.add_task` compares names against
  the header index, whose keys are canonical core names, and raises `the task table has no
  column(s): id` — refused, but with a message that is false for that table.

With `--workspace`, the kind used to check the kind and render the branch is `args.kind`, while
the row gets the `--column Kind` value, so the workspace can be opened for a different kind than
the row records.

## Ruled out

- **`writer.add_task`'s unknown-column check.** It only rejects names absent from the table's
  header index (`name not in columns`). Core names are always in that index, so it cannot catch
  them; it is where the value lands, not the cause.
- **Post-write validation (`_write` → `writer.apply`).** It rejects a row that is invalid on its
  own (an undefined or disallowed kind, above), but an overridden title, points or kind that is
  itself valid, and a discarded ID or status, leave a valid backlog. It cannot see that a flag
  was overridden.
- **argparse.** `--column` is `action="append"` of free strings; parsing `NAME=VALUE` and
  deciding what a name may be is `cmd_new`'s job by design.
- **Config: a custom column named like a core column.** `[columns].custom = ["Kind"]` validates
  cleanly (`1 task(s) in 1 backlog(s): 0 error(s), 0 warning(s)`), but the header index maps a
  `Kind` header to the core column regardless, so no repository can have a custom column that a
  core-name refusal would wrongly block.
- **The T021 alias refusal itself.** It behaves as specified for aliased columns (all *full*
  cases, *partial* `Pts`/`pts`); the defect is that its guard is limited to aliased columns.

## Affected areas

- `tools/taskrail/src/taskrail/cli.py` — `cmd_new`, the `--column` loop (the only code change).
- `tools/taskrail/DESIGN.md` §3.2 documents the refusal for aliased columns only (“`new` fills
  an aliased column through its usual flag (`--pts`), refusing `--column` for it”).
- No other command accepts `--column`.

## Proposed fix

In `cmd_new`'s `--column` loop, resolve the name case-insensitively against every core task
column (`CORE_TASK_COLUMNS` from `config.py`) and every alias, instead of the aliases alone, and
refuse any match before an ID is reserved, with exit 2 and a message naming the flag:

- unaliased: `taskrail: --column cannot set core column Kind; set it with --kind`
- aliased (unchanged): `taskrail: --column cannot set core column Pts (named `Size` here); set it with --pts`
- `✓` and `ID`: `...; taskrail sets it`

Regression test: parametrize `new --column <core>=<value>` over all seven core columns (plus a
lower-case spelling) in a repository without aliases, and over an unaliased core column in a
repository that aliases another one; assert exit 2, the flag hint in stderr, `TODO.md`
unchanged, and the next reserved ID not consumed. Add one `CHANGELOG.md` bullet and widen the
DESIGN.md sentence to all core columns.
