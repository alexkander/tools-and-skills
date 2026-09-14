# T005 — Import tasks from table-based backlogs without epics

Kind: feature · Epic: E02 · Status: plan

## Context

A project adopting taskrail usually already has a Markdown backlog: one or more pipe tables of
tasks under headings, with prose in between, but no `## Epics` table, its own column names
(`Status`, `Type`, `Estimate`) and its own status markers (`[ ]`/`[x]`, `todo`/`done`). taskrail
rejects such a file today: `validate` reports `epics-missing`, and a table with an `ID` column but
neither `✓` nor `Kind` is not even recognised as a task table, so its tasks are silently not
counted (`0 task(s)`). DESIGN.md lists the importer as a phase 2 non-goal of v1 (§1, §11); no
earlier design for it exists.

## Behaviour

`taskrail import <SOURCE>` converts a table-based Markdown backlog into a taskrail backlog file
that `validate` accepts, changing as few bytes as possible.

### Command surface

```bash
taskrail import BACKLOG.md                                  # dry run: converted file on stdout, summary on stderr
taskrail import BACKLOG.md --column "✓=Status" --column Kind=Type \
  --status "in progress=pending" --kind "tech debt=chore" --default-kind feature
taskrail import BACKLOG.md --write [--backlog NAME] [--json]
```

- **Dry run by default.** Without `--write` nothing is written: text output prints the converted
  file on stdout and the summary on stderr, so `taskrail import X > preview.md` works; `--json`
  returns the summary with the converted text in `content`.
- **`--write`** writes the result to the backlog's configured `file` (`--backlog` is required when
  the repository has several backlogs). The source may be that same file — an in-place
  conversion, the usual case after `taskrail init` left an existing `TODO.md` alone — or another
  file, which is then left untouched for the user to delete. The target is replaced only when it
  is the source, does not exist, or holds no epic and no task row (the file `init` seeds). The
  edit goes through the writer's validate-in-memory, atomic-replace path.
- **Mapping flags**, all repeatable and matched case-insensitively after trimming:
  - `--column CORE=HEADER` — the source header of a core column (`✓`, `ID`, `Kind`, `Pts`,
    `Depends On`, `Title`, `Description`), in the same direction as `[columns].aliases`. Without a
    flag, a header matching the core name or its configured alias is taken.
  - `--status VALUE=pending|done|discarded` — adds to the built-in markers below.
  - `--kind VALUE=KIND` — `KIND` must be a kind the repository resolves and allows (exit 2
    otherwise).
  - `--default-kind KIND` — the kind for rows whose table has no Kind column or whose Kind cell
    is empty. There is no default status: a status is never guessed.

### How the source is read

- **Task tables.** A table is a task table when, after column mapping, its header has both an
  `ID` and a `✓` column. Any other table stays as it is. A table with an `ID` column but no
  status column is listed in the summary, since it may be a task table whose status header was
  not mapped. Tables and headings inside fenced code are ignored, as `validate` ignores them.
- **Headings become epics.** Each task table belongs to the nearest heading above it whose level
  lies between 2 and the *epic level*. The epic level is `--epic-level N` (2–6), or by default the
  shallowest level among the nearest level-2-or-deeper heading of every task table. Each heading
  that owns at least one task table becomes one epic: its line is rewritten to
  `## E01 — <heading text>`, and every other line of its region stays. Headings that own no task
  table are kept as written. Level-1 headings are the document title and never become epics.
  Example: with `## Backlog` containing `### Auth` and `### Billing`, each holding a table, the
  epic level is 3 and the epics are Auth and Billing; with `## Auth` containing `### Pending` and
  `### Done` tables, the default gives epics Pending and Done, and `--epic-level 2` gives Auth.
- **Fallback epic.** Task tables with no qualifying heading above them — a single table under the
  title, or a source sectioned only by level-1 headings — form one epic, named by
  `--epic-name NAME` (default `Backlog`). Its heading is inserted on the line before its first
  table. Such tables can only precede every qualifying heading, so it is always the first epic.
- **Epic IDs** are `<epic_prefix>01`, `02`, … in order of appearance. A heading already shaped
  `E07 — Name` with the backlog's epic prefix keeps its ID; generated IDs skip taken ones.
- **The `## Epics` section** is inserted before the first level-2 heading of the result, below
  the title and any introductory prose, with `ID | Epic | Objective | File` columns: the heading
  text as name (with `|` escaped), `—` as objective and `—` as file.

### How cells are converted

- **Headers** of mapped core columns are renamed to the repository's configured name (the alias
  from `[columns].aliases`, else the core name); a header already equal to it case-insensitively
  is kept. Unmapped headers stay as custom columns; `column-undeclared` warnings are reported, and
  the summary names them for `[columns].custom`. Two source columns mapped to one core column
  refuse the import.
- **Missing columns.** A table without `Kind` gets one, filled with `--default-kind` (refused
  without it); a table without `Depends On` gets one filled with `—`. Inserted after the `ID`
  column, Kind first. `Title` has no default: a table without it, or a row with an empty title,
  refuses the import.
- **Status** cells become `⬜`, `✅` or `❌`. Built-in markers: pending `⬜`, `[ ]`, `todo`,
  `pending`, `open`; done `✅`, `[x]`, `done`, `closed`; discarded `❌`, `discarded`, `cancelled`.
  Anything else, empty included, is *unmapped*.
- **Kind** cells equal to a resolved kind in another letter case (`Bug`) become that kind; a
  `--kind` value maps explicitly; anything else is unmapped.
- **Depends On** cells made only of this backlog's IDs separated by commas, semicolons or spaces
  become `T001, T002`; an empty cell, `-`, `–` or `—` becomes `—`; anything else is unmapped.
- **IDs are kept exactly.** Every ID must match the backlog's `prefix` followed by at least
  `id_digits` digits, and be unique in the source. IDs are never renumbered, padded or re-prefixed;
  the refusal names the offending IDs and suggests `id_digits` when only the padding differs.
- **Round trip.** Only cells whose value changes are rewritten, with the writer's `replace_cell`
  (it keeps a cell's width when the value fits). Every other byte stays: untouched cells, escaped
  pipes `\|`, spacing, row order, prose, lists, non-task tables, code fences and the source's line
  endings. Inserted lines use the source's line ending.

### Refusals and exit codes

All problems are collected and reported together, each with its file and line, then:

| Exit | When |
|---|---|
| 0 | converted (dry run or written), or nothing to do: the source already has `## Epics` and validates, or the target already holds exactly the result |
| 1 | the conversion succeeded but the result fails `validate` (for example `depends-unknown`, `task-points-scale`); the issues are printed and nothing is written |
| 2 | usage: unreadable or non-UTF-8 source, several backlogs without `--backlog`, a malformed flag, a `--column` key that is not a core column, a `--kind`/`--default-kind` kind that is not resolved or allowed, `--epic-level` outside 2–6 |
| 4 | an imported ID is reserved with `reserve-id` and not yet used; the reservation's owner is named |
| 5 | refused: no task table found; unmapped status, kind or dependency values (each distinct value with its count and first lines); an ID not matching the prefix or duplicated; a missing Title or Kind without default; a row with a different number of cells; the source has a `## Epics` section but does not validate (a partial conversion); with `--write`, a target other than the source that already holds epics or tasks and differs from the result |

### IDs and `reserve-id`

Once written, imported IDs are in the backlog file, so `reserve-id` and `new` count them (§6.3)
with no extra state. `--write` holds the ID lock while it checks reservations and writes, so a
concurrent `new` either reserved first (the import exits 4) or sees the imported IDs.

### Output

`--json` returns `source`, `target`, `backlog`, `written`, `unchanged`, `epic_level`, `epics`
(each `id`, `name`, `line`, `tasks`), `tasks`, `mapped` (`columns`, `statuses` and `kinds`, each
value with its count), `custom_columns`, `tables_skipped` (line and reason), `problems` (for
exit 5), `issues` (validation issues of the result, warnings included) and `content`. Text output
prints the same summary on stderr.

## Acceptance criteria

1. On a source with two level-2 headings, each followed by a task table using `Status`, `ID`,
   `Type`, `Title` and `Notes` headers and `[ ]`/`[x]` markers, `import --column "✓=Status"
   --column Kind=Type --write` produces a file that `validate` accepts with no errors, with epics
   E01 and E02 named after the headings, the tasks in source order with their IDs, statuses and
   kinds, and a `column-undeclared` warning for `Notes`.
2. Every line outside the changed task-table cells, the rewritten epic headings and the inserted
   `## Epics` section and fallback heading is byte-identical to the source: prose, lists,
   non-task tables, fenced code containing a table, cells with escaped pipes `\|`, spacing and
   CRLF line endings are preserved, and rows keep their order.
3. Without `--write` nothing is written; stdout holds exactly the content `--write` would write,
   and `--json` holds it in `content`, with `written: false`.
4. The epic level defaults to the shallowest nearest heading of the task tables: containers with
   task tables under level-3 headings give level-3 epics, and non-epic headings are kept as they
   were; `--epic-level 2` groups level-3 subsections under their level-2 heading; a heading
   without task tables never becomes an epic.
5. Task tables with no qualifying heading form one epic named `Backlog`, or `--epic-name`, whose
   heading is inserted right before its first table, and the `## Epics` section is inserted below
   the title and introductory prose.
6. A heading already shaped `E07 — Name` keeps E07, and generated epic IDs skip it.
7. Built-in status markers, `--status`, case-insensitive kind names, `--kind` and `--default-kind`
   map as described; a table missing Kind (with `--default-kind`) or Depends On gains the column
   after `ID`; Depends On cells separated by semicolons or spaces are normalised.
8. Unmapped statuses, kinds and dependency cells, a missing Title, an empty Kind without default,
   and a row with the wrong number of cells exit 5, list every distinct value with its count and
   lines in one report, and write nothing.
9. An ID that does not match the prefix or `id_digits`, or a duplicated ID, exits 5 naming it;
   IDs in the result are exactly the source's.
10. A result that fails validation, such as a dependency on a missing ID, exits 1 with the issues
    and writes nothing.
11. Running the same import twice is safe: in place, the second run exits 0 with
    `unchanged: true` and does not modify the file; into another target, the second run exits 0
    when the target equals the result, and exits 5 when the target holds other tasks. Importing
    the output of an import again changes nothing.
12. After `--write`, `reserve-id` returns an ID above the highest imported one; an import whose
    IDs include a pending reservation exits 4 and writes nothing.
13. Usage errors exit 2: several backlogs without `--backlog`, a `--column` key that is not a
    core column, a `--kind` target that is not an allowed kind, `--epic-level 1`, a missing
    source file.
14. With `[columns].aliases` configured (for example `"✓" = "Status"`), a source header matching
    the alias is kept, and a header mapped by `--column` is renamed to the alias.
15. The existing test suite passes unchanged.

## Affected areas

- `tools/taskrail/src/taskrail/importer.py` — new: heading scan, table detection, mapping,
  conversion, summary, and the `import` command's parser registration and handler.
- `tools/taskrail/src/taskrail/cli.py` — one hunk registering the command next to the autopilot
  registration, to keep conflicts with the lanes editing `cli.py` small.
- Reuses without changing: `markdown.split_row`/`parse_sections`, `backlog._index`,
  `writer.replace_cell`/`escape_cell`/`Edits`/`apply`, `ids.id_lock`/`reservations`,
  `project.load_project`.
- `tools/taskrail/tests/test_import.py` — new, fixtures from invented data only.
- Docs: `tools/taskrail/DESIGN.md` (a new §7.3 Import, the §7 command table, §1 and §11 no longer
  listing import as not done), `README.md` (an "Adopting an existing backlog" section),
  `CHANGELOG.md` (one bullet at the end of `## Unreleased`).

## Out of scope

- List-based backlogs (`- [ ] task`), tables without leading pipes, setext headings.
- Tables without IDs (assigning IDs), renumbering, padding or re-prefixing IDs.
- Status implied by the section (`## Done`) or a default status.
- Editing `.taskrail/config.toml` (aliases, custom columns, `id_digits`): the summary says what
  to add.
- Status aliases stored in the backlog: `validate` keeps accepting only `⬜`, `✅` and `❌` (§3.3).
- Merging a source into a backlog that already has tasks, or several sources into one run.
- Putting imported epics in their own files (`taskrail epic split` does it afterwards).
- Grouping every table into one epic whatever the headings (`--single-epic`); a candidate
  follow-up if a consumer needs it.
- Checking imported IDs against other branches: the working-tree result is what `reserve-id`
  scans from then on.
- A skill or skill section for adoption.

## Open questions and risks

- **Command surface.** Dry run to stdout by default with `--write` into the backlog's file,
  rather than always writing in place or taking an `--output` path.
- **Mapping by flags**, not a mapping file or new config: flags keep a plain contract an agent
  can iterate on from the dry-run report; a mapping file can be added later without breaking them.
- **`--column CORE=HEADER`** follows `[columns].aliases`' direction rather than `HEADER=CORE`.
- **Headers are renamed to the configured names** (alias or core), rather than kept and aliased
  automatically; a repository that wants its header keeps it by configuring the alias first.
- **Built-in status markers** are a small fixed list; anything else is explicit.
- **Task-table detection needs a status column.** A table with IDs but no status column is left
  alone and listed; if it also has a column taskrail reads as `Kind`, `validate` will then report
  it (`task-columns`, exit 1), and the user maps its status column.
- **Other branches.** An ID used on another local branch's backlog is not detected, because the
  source file itself may be committed there and would collide with itself.
- **Size.** The plan is at the upper end of 5 points; `--epic-level`, `--epic-name` and heading
  IDs could be dropped to shrink it, leaving nearest-heading epics and a fixed fallback name.
- **Parallel lanes** edit `cli.py`; this task adds only a registration hunk there.
