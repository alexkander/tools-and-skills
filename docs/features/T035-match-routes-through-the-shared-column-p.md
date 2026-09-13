# T035 — Match routes through the shared column predicate

Kind: feature · Epic: E02 · Status: planned

Source: decision 6 of `docs/autopilot/decisions/T020-run-stages-conditionally-on-a-column-or.md`,
which opened this task so that taskrail stops having two matchers with different letter-case rules.

## Today

A `[[route]]` sends a task of its kind to another executor skill:

```toml
[[route]]
when = { Spec = "—" }
skill = "speckit-new-spec-pipeline"
```

`kinds.py` matches it with its own code, not with `predicates.py`:

- `when` maps one or more column names to **one string each**; every entry must hold.
- The column name is looked up **exactly** in the task's custom columns, so `stack` never finds a
  `Stack` header and reads as empty.
- The value compares **exactly**: case-sensitive, untrimmed. `"*"` is any non-empty cell, and
  `"—"`, `"-"` or `""` an empty one.
- The first route that matches wins; with none, the kind's `skill` applies.
- A column that `[columns].custom` does not declare is the warning `route-column-undeclared`, emitted
  once per column name, with no file.

Stage predicates (T020, DESIGN.md §5.4) are one column plus a list of values, trimmed and
case-insensitive, resolve the column case-insensitively, and refuse an undeclared column, a core
column or an alias with the error `stage-column-unknown`.

Observed in a throwaway repository (`[columns] custom = ["Stack"]`, `aliases = { Pts = "Size" }`),
with a local kind `svc` routing `Stack = "API"` → `svc-upper`, `Stack = "api"` → `svc-lower`,
`Stack = " ui "` → `svc-padded`, `stack = "*"` → `svc-lowercase-column`, default `svc-default`; and
a kind `odd` routing `Size = "3"` → `odd-alias`, `Owner = "*"` → `odd-undeclared`,
`Stack = ""` → `odd-empty-string`, default `odd-default`:

| Task | Cell | `skill` today | `skill` after this plan |
|---|---|---|---|
| T001 | `Stack` = `API` | `svc-upper` | `svc-upper` |
| T002 | `Stack` = `api` | `svc-lower` | `svc-upper` — `svc-lower` becomes unreachable |
| T003 | `Stack` = `Api` | `svc-default` | `svc-upper` |
| T004 | `Stack` = `ui` | `svc-default` | `svc-padded` |
| T005 | `Stack` = `—` | `svc-default` | `svc-default` |
| T006 | `Size` = `3`, `Owner` = `ana` | `odd-undeclared` | `validate` exits 1: `Stack = ""` is `kind-invalid`; without that route, `Size` and `Owner` are `route-column-unknown` and `odd` stays loaded |

`validate` today: exit 0 with warnings `route-column-undeclared` for `Owner`, `Size` and `stack` —
although `Size` can never match (core columns are not in a task's custom columns) and `stack` is
the declared `Stack` in another letter case. `when = { Stack = ["web", "api"] }` is `kind-invalid`
("`when` must map column names to strings"), which also drops the kind and reports every task of
it as `task-kind-unknown`.

## Behaviour

Routes match through `predicates.py`, with the same rules as stage predicates:

- **Shape.** `when` stays a table: each entry is one column predicate, its key the `column` and its
  value the `match` — a string or a non-empty list of strings. A route holds when **every** entry
  holds (and across columns), and an entry holds when the cell equals **any** of its values (or
  within a column):

  ```toml
  [[route]]
  when = { Area = ["ui", "ux"], Spec = "—" }
  skill = "new-screen-pipeline"
  ```

- **Values** are trimmed and compare case-insensitively; `"*"` is any non-empty cell and `"—"` or
  `"-"` an empty one. `""`, a blank string and an empty list are `kind-invalid`, as in `match`.
- **Columns** resolve case-insensitively to their declared spelling. A column that is not a
  declared custom column is the error `route-column-unknown` at the descriptor's path, naming the
  route and — when it is one — the core column or alias. The kind stays loaded. The warning
  `route-column-undeclared` is removed.
- **Order.** Routes are tried in the order the descriptor lists them; the first that holds gives
  the skill, and the kind's `skill` applies when none does. A route that can never be the first to
  hold, because an earlier route of the same kind holds for every task it holds for, is the
  warning `route-unreachable`, naming both routes.
- **Output.** `show --json` and `kind list --json` keep `routes` as
  `[{"when": {<column>: <value>}, "skill": …}]`. The column is the declared spelling, and the value
  is the trimmed string when the route has one value, and a list when it has several. Text `show`
  keeps printing the resolved `skill` line only.

## Acceptance criteria

1. A route `when = { Stack = "api" }` holds for cells `api`, `API` and ` Api `, and not for `web`
   or an empty cell; a route value `" ui "` holds for a `ui` cell.
2. `when = { Stack = ["web", "api"] }` holds when the cell is either value; a one-element list
   behaves as the string.
3. `when = { Stack = "*", Spec = "—" }` holds only when both entries hold; `"*"` never holds for an
   empty cell, `—` or `-`, and `"—"`/`"-"` hold for an empty cell and for a table without the
   column.
4. The first route that holds gives `show --json`'s `skill`, in descriptor order; with none, the
   kind's `skill`.
5. `when = { stack = "*" }` with `Stack` declared loads with no issue and holds for a non-empty
   `Stack` cell.
6. A `when` column that `[columns].custom` does not declare is the error `route-column-unknown` at
   the descriptor's path, naming the route; a core column or an alias of one (any letter case)
   gives the same code with a message naming the core column. The kind stays loaded (no
   `task-kind-unknown`), `validate` and `show` exit 1, and `route-column-undeclared` no longer
   appears.
7. `when` that is not a table, is empty, has a value that is not a string or list of strings, or an
   empty string, blank string or empty list as a value, or names the same column twice in
   different letter case, is `kind-invalid` naming the route.
8. A route whose every entry is covered by an earlier route's entries for the same columns — for
   example `Stack = "api"` after `Stack = "API"`, or `{ Stack = "api", Spec = "—" }` after
   `Stack = "*"` — is the warning `route-unreachable` naming both route numbers; `Stack = "*"` after
   `Stack = "api"` is not.
9. `show --json` and `kind list --json` report `routes` with declared column names, a string value
   for a single value and a list for several; the shipped spec-kit example's routes report exactly
   as today.
10. `predicates.py` still imports nothing else from taskrail, and `parse_column_predicate`'s
    signature and messages are unchanged.
11. DESIGN.md §5.1 and §5.4 describe routes as column predicates, with order and the new codes, and
    no longer say routes match exactly; README's *Task kinds* mentions it; CHANGELOG has one
    bullet flagged "Behaviour change".

## Affected areas

- `tools/taskrail/src/taskrail/predicates.py` — a `match`-value parser that takes the key to name in
  its message (so routes say `when.Stack`), which `parse_column_predicate` calls unchanged; a
  `covers` check between two predicates on the same column for `route-unreachable`.
- `tools/taskrail/src/taskrail/kinds.py` — `Route` holds a tuple of `ColumnPredicate`s; `_parse`
  builds, resolves and checks them; `Route.matches`, `Kind.to_dict` routes output;
  `columns_used_by_routes` removed.
- `tools/taskrail/src/taskrail/project.py` — the `route-column-undeclared` loop and its import go.
- `tools/taskrail/DESIGN.md` §5.1, §5.4; `tools/taskrail/README.md` *Task kinds*;
  `tools/taskrail/CHANGELOG.md` one bullet.
- `tools/taskrail/tests/test_routes.py` (new); `tests/test_kinds.py`'s existing route test keeps
  passing unchanged.

## Out of scope

- Routes on core columns (`Pts`, `Kind`, …), on the epic, or conditions other than "all entries,
  any value" (negation, or across columns).
- Warning about a task cell that no route and no `skill` covers, or a per-column set of allowed
  values.
- Changing stage predicates, the core skill, or the autopilot's groups (T029).
- A compatibility switch that keeps exact matching for one repository.

## Open questions and risks

Decisions needed at this gate are listed in the gate report and, once taken, recorded in the
autopilot decisions file. Risks:

- **Tasks change executor silently.** A cell that differs from a route value only in case or
  padding (T003, T004 above) now routes. `route-unreachable` catches routes a case-insensitive
  earlier route fully covers (T002), but not a partial overlap, such as
  `{ Stack = "API", Area = "x" }` before `{ Stack = "api" }`. The CHANGELOG bullet is the only
  notice for those.
- **A backlog that validated may now fail.** A route on an undeclared column that the task table
  has worked with two warnings; it becomes an error that blocks `show` and `claim` until the
  column is added to `[columns].custom`.
- **Parallel lanes.** T029 may call `parse_column_predicate` for `[[autopilot.group]]`; keeping its
  signature and messages unchanged avoids a conflict there. T019 does not touch kinds or §5.
