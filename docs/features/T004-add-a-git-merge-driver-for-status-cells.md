# T004 — Add a git merge driver for status cells and appended rows

Kind: feature · Epic: E02 · Status: plan

Source: the core skill's step 8 (how an agent resolves backlog conflicts by hand today),
`tools/taskrail/DESIGN.md` §3 (file format), §6.3 (IDs are never reused, so an ID is a stable row
key), §7.1 (review hand-off and the rebase it asks for), §9 (install and extras), §11 (phase 2
lists this driver) and §12.8 (known conflict classes 1 and 2). No prior work: `show` reported no
artifact, branch or commit for T004.

## Behaviour

Today two task branches that both touch a backlog file conflict whenever their edits are adjacent
lines — both append a row to the same epic table, one flips a status cell next to a row the other
appends, or a rebase replays a commit that opens a row already present upstream. Git sees line
hunks, not rows, so the agent resolves each one by hand with the rule in step 8.

After this change a repository opts in with `taskrail init --merge-driver`, and git resolves those
conflicts itself during `git merge`, `git rebase`, `git cherry-pick` and `git pull`, leaving
standard conflict markers only where a human decision is really needed.

### The driver: `taskrail merge-driver`

```
taskrail merge-driver <base> <current> <other> [--marker-size N] [--path P]
                      [--base-label L] [--current-label L] [--other-label L]
```

Git's contract for custom merge drivers: the three arguments are temporary files holding the
common ancestor, the current side and the other side; the merged result is written over
`<current>`; the exit status is **0** for a clean merge and **1** when conflicts are left, marked
with standard `<<<<<<<` / `=======` / `>>>>>>>` markers of `--marker-size` characters (default 7)
labelled with the three labels. It never exits with any other status once it has started: every
internal failure — undecodable input, an unexpected exception — falls back to exactly what
`git merge-file` does with the same inputs, and a one-line warning on stderr names the path. It
does not read or write the index, the working tree (other than `<current>`) or any ref, and needs
no network.

The installed git configuration (see *Installing*) is:

```
[merge "taskrail"]
	name = taskrail backlog tables
	driver = .taskrail/bin/taskrail merge-driver %O %A %B --marker-size %L --path %P --base-label %S --current-label %X --other-label %Y; rc=$?; [ $rc -le 1 ] && exit $rc; git merge-file --marker-size %L -L %X -L %S -L %Y %A %O %B
```

Git runs the driver through the shell from the top of the worktree being merged, so the relative
wrapper path runs that worktree's pinned taskrail, and quotes each placeholder as one argument
(both verified, *Evidence* E1, E3). The trailing fallback covers only a taskrail that cannot
start at all (for example `uvx` missing: the wrapper exits 2): the file then gets an ordinary
`git merge-file` result instead of being left conflicted with no markers.

### How a file is merged

1. **Tables.** Every pipe table outside fenced code is read with `markdown.parse_sections`. A
   table's identity is its section — the epic ID for a `## E## — …` heading, so renaming an epic
   does not break it; otherwise the heading text, or the text before the first level-2 heading —
   plus its position among that section's tables.
2. **Which tables are merged row by row.** A table present on both the current and the other side
   whose header cells are equal (trimmed, case-insensitive), whose rows all have the header's cell
   count, and whose key column holds unique, non-empty values on each side. The key column is
   `ID` (through `[columns].aliases` when the repository's config can be read from the working
   tree, core names otherwise), else the first column — so the `## Epics` table and artifact index
   tables (`| Task | Title | Document |`) merge too. The base is the same table in the ancestor when
   it has the same header, else an empty table. Any other table is left to step 5 untouched.
3. **Rows, united by key.**
   - A key on both sides: identical rows are kept; otherwise each cell is merged three-way against
     the base row — equal values stay, a side that left a cell as in the base takes the other side's
     value — and a cell both sides changed differently is **unresolved**, except the status cell
     (step 4).
   - A key on one side only: added when the base lacks it; removed when the base has it and the
     side that kept it left it unchanged; **unresolved** when that side changed it (modify/delete).
   - A key only in the base: removed by both sides.
   - Order: the current side's rows, with each row only the other side has inserted after its
     nearest preceding row in the other side that is already placed, and after any rows new on the
     current side that follow that one. Both sides appending to the same table therefore gives the
     current side's rows first, then the other's; in a rebase, the mainline's rows first.
   - A merged row is the current side's line with only the cells taken from the other side
     replaced, keeping cell widths as `taskrail` writes do (`writer.replace_cell`).
4. **Status cells.** In a task table (a key `ID` plus a `✓` column), when the two sides' status
   values differ and neither equals the base's (or the base has no such row):
   - one side is `✅` → `✅`, unless the other side is `⬜` and has a `Reopens: <ID>` commit the `✅`
     side lacks, then `⬜`;
   - anything else (for example `⬜` against `❌` with no base row) is unresolved;
   - when the two sides cannot be resolved to commits, a conflict the rule would decide with the
     reopen check is left unresolved rather than guessed.

   *Sides as commits.* While the driver runs, `MERGE_HEAD`, `REBASE_HEAD` and `CHERRY_PICK_HEAD`
   do not exist yet, and `ORIG_HEAD` is the pre-merge `HEAD` or the whole pre-rebase branch (E1),
   so none of them identifies the other side. The labels do: `%X` is `HEAD` and `%Y` is the merged
   name (`topic`, `origin/main`, or a full hash for `FETCH_HEAD`) in a merge, and
   `<short hash> (<subject>)` in a rebase or cherry-pick (E1, E3). Each label's first word is
   resolved with `git rev-parse --verify --quiet <word>^{commit}`.
   *The check.* One `git log --left-right --cherry-pick --grep=^Reopens: <current>...<other>`, run
   only when a status conflict needs it and at most once per file. `--cherry-pick` drops commits
   patch-equivalent to one on the other side, so a reopen already replayed by the same rebase
   counts as present on both sides. The trailer is matched as `review.REOPENS` does.
5. **Everything else.** The driver builds three new inputs in which every table merged row by row
   holds the merged rows — identical in all three, so they are plain context — except unresolved
   rows, which appear at their merged position with each version's own line (absent where that
   version has no such row). It then runs `git merge-file --marker-size N -L <current> -L <base>
   -L <other>` on them. Prose, headings, new sections and tables not merged in step 2 are merged by
   git's ordinary algorithm; conflicts are marked only around unresolved rows and genuinely
   conflicting text, and the exit status is 0 or 1 from that result. Making the merged table
   identical in the base too matters: with it only on the two sides, a one-line prose edit right
   after the table conflicts with the table change (E2, case 2).

The driver does not validate the backlog: the other backlog files may not be merged yet when it
runs. Rules that span tables or files — an ID moved into two different epics, a dependency on a
task the other side removed — remain `taskrail validate`'s job, which step 8 already runs after
the rebase.

### Installing

- **`taskrail init --merge-driver`** (idempotent, and adds to what is installed like the other
  extras):
  - writes a marked block into `.gitattributes` at the repository root, creating the file if
    needed and keeping every line outside the block:
    ```
    # >>> taskrail >>>
    /TODO.md merge=taskrail
    /todo/E02-auth.md merge=taskrail
    /docs/features/README.md merge=taskrail
    # <<< taskrail <<<
    ```
    one line per backlog `file`, per epic file named in an Epics table, and per artifact index
    (each resolved kind's `artifact_index` rendered per backlog, and `[autopilot].decisions_index`),
    sorted and de-duplicated, with paths quoted when they contain spaces;
  - sets `merge.taskrail.name` and `merge.taskrail.driver` with `git config --local`, which every
    worktree of the clone shares;
  - records `extras.merge_driver = true` in `.taskrail/installed.json`.
- **The block is committed; the driver definition is not.** Git keeps merge driver definitions in
  local config only. A clone whose config does not define `taskrail` merges those files with git's
  built-in text merge exactly as before (E4), so committing the block is harmless, and each clone
  opts in by running `taskrail init --merge-driver` once.
- **`taskrail upgrade`** (and `init` without the flag) refreshes the block when the extra is
  recorded, so it follows new epic files and kinds, and rewrites `merge.taskrail.driver` only in a
  clone that already defines it, never adding it.
- **`taskrail epic add --own-file` and `taskrail epic split`** add the new epic file to the block
  in the same write when the block exists, so the attribute travels in the commit that creates the
  file.
- Outside a git repository the git config step is skipped with a note. The report lists
  `.gitattributes` and `git config merge.taskrail` as created, updated or unchanged.

### Documentation

- Core skill, step 8: when `git config merge.taskrail.driver` is set, the backlog conflicts that
  remain are the ones the driver could not resolve; resolve those by the existing rule, then run
  `taskrail validate` as today. The rule itself stays in the skill for clones without the driver.
- DESIGN: a new §7.4 *Merge driver* (contract, algorithm, sides and `Reopens:`), the `init` row of
  the §7 table, the extras bullet of §9, §11's phase-2 wording, and §12.8's classes 1 and 2
  (class 1 implemented; index rows implemented, changelog bullets not).
- README: the `--merge-driver` extra. CHANGELOG: one bullet at the end of `## Unreleased`.

## Acceptance criteria

Each criterion is tested against real `git merge`, `git rebase` or `git cherry-pick` in a
throwaway repository with the driver installed, unless it says *unit*, which calls the merge
function on three strings.

1. Both sides append rows to the same epic table: `git merge` and `git rebase` complete with no
   conflict, the result holds every row once, the current side's rows first, and `taskrail validate`
   passes.
2. One side marks a row `✅` (`taskrail done`) while the other appends a row right after it or edits
   another cell of the same row: both changes are kept, no conflict.
3. A rebase replays a commit that opens a row already present upstream with the same content: one
   copy remains, no conflict.
4. The same ID on both sides with no base row, `✅` against `⬜`: the result is `✅`; with a
   `Reopens: <ID>` commit only on the `⬜` side, `⬜`; with a patch-equivalent reopen on both sides
   (a rebase that already replayed it), `✅`.
5. Status conflicts with a base: base `⬜`, `✅` against `❌` → `✅`; base `✅`, `⬜` against `❌` →
   conflict markers around that row only, exit 1.
6. Labels that are not commits (*unit*: `--current-label local --other-label other`) leave a status
   conflict that needs the reopen check marked, and resolve everything else.
7. The same cell changed differently on both sides (for example two titles): markers around that
   row only, every other row and prose change merged, exit 1, markers of `%L` length with the
   labels git passed.
8. Prose and heading changes merge as git would: an edit on one side directly after a table another
   side changed merges cleanly; two different edits of the same prose line conflict with standard
   markers.
9. A table that cannot be merged row by row — header changed on one side, duplicate keys, a row
   with the wrong cell count, its section removed on one side — gives the same result as
   `git merge-file` on the original three inputs (*unit*, compared byte for byte).
10. A row deleted on one side and unchanged on the other is removed; deleted on one side and
    changed on the other is marked.
11. One side moves a row from one table of the file to another while the other side appends a row
    near it: no duplicate row, no conflict.
12. The `## Epics` table and an artifact index table, both sides appending: merged cleanly.
13. `[columns].aliases` for `✓` and `ID` are honoured; with an unreadable config the core names are
    used (*unit* plus one merge).
14. A file with no tables, undecodable bytes or an internal error produces exactly the
    `git merge-file` result and exit status (*unit*, the error injected); the driver never exits
    with a status other than 0 or 1.
15. `init --merge-driver` writes the `.gitattributes` block (keeping existing lines), both git config
    keys and the manifest extra; a second run reports them unchanged; `init` without the flag and
    without the recorded extra writes neither.
16. With the extra recorded, `upgrade` refreshes the block after an epic file is added by hand and
    updates `merge.taskrail.driver` only in a clone that defines it; `epic add --own-file` and
    `epic split` add their file to an existing block.
17. A clone with the committed block but no driver definition merges those files with git's text
    merge, without errors.

## Affected areas

- `tools/taskrail/src/taskrail/mergedriver.py` (new): the row-by-row table merge (pure functions
  over three strings), the driver entry (label resolution, the `Reopens:` check, the
  `git merge-file` calls and fallback), and the `.gitattributes` block and git config helpers.
- `tools/taskrail/src/taskrail/cli.py`: registration of `merge-driver` (a thin hunk, like
  `import`), `--merge-driver` on `init`, and the block refresh after `epic add --own-file` and
  `epic split`.
- `tools/taskrail/src/taskrail/install.py`: a small `merge_driver` parameter and extra, calling the
  helpers in `mergedriver.py`; nothing near `skill_files`.
- Reused without change: `markdown.parse_sections`, `backlog._index`/`_is_task_table`,
  `writer._cell_spans`/`replace_cell`, `review.REOPENS`, `gitutil.run`.
- `tools/taskrail/src/taskrail/skills/taskrail/SKILL.md` step 8, then `taskrail upgrade` for the
  installed copy under `.claude/skills/`.
- `tools/taskrail/DESIGN.md`, `tools/taskrail/README.md`, `tools/taskrail/CHANGELOG.md`.
- Tests: `tools/taskrail/tests/test_merge_driver.py` (new), plus install cases in
  `tests/test_install.py`.

## Out of scope

- **Changelog bullets** (the rest of §12.8 class 2). A changelog is not a file taskrail knows, and
  "keep both" duplicates a bullet one side moved; a follow-up task (Q7).
- **Installed skill copies and `installed.json`** (§12.8 class 3).
- **Rules across files or tables** — a row moved to another epic file on one side and changed on
  the other conflicts; an ID left in two epics is reported by `validate`.
- **Re-resolving a file already conflicted** in a clone without the driver (reading stages 1–3 from
  the index); the orchestrator can install the driver instead. Not proposed as a follow-up unless
  asked.
- **Adopting the driver in this repository** (committing a `.gitattributes` block here): a separate
  decision once the driver is merged (Q9).
- Reformatting or re-aligning tables, which the minimal-diff rule of §7.1 forbids.

## Open questions and risks

Decisions for the plan gate, each with a recommendation:

- **Q1 — Driver contract.** Recommended: options for the marker size, path and labels as above,
  exit 0/1 only, and an internal fallback to `git merge-file`. Alternative: positional arguments in
  git's `%O %A %B %L %P %S %X %Y` order (shorter config line, less readable).
- **Q2 — Shell fallback in the git config** for a taskrail that cannot start. Recommended: yes;
  without it git leaves such a file conflicted holding only the current side, with no markers.
  Alternative: the bare command, documenting `git checkout --conflict=merge <path>`.
- **Q3 — Files.** Recommended: backlog files, epic files and artifact indexes (with the autopilot
  decisions index), which covers class 2's index rows at no extra algorithmic cost. Alternative:
  backlog and epic files only, leaving indexes to the follow-up.
- **Q4 — Where the driver is installed.** Recommended: opt-in with `init --merge-driver`; the
  committed `.gitattributes` block is refreshed by `upgrade`; the local git config is added only by
  `init --merge-driver` and merely kept current by `upgrade`. Alternative: `upgrade` also adds the
  git config in any clone where the extra is recorded, so a new clone gets the driver without
  opting in — convenient, but it starts running repository code on merges without that clone
  asking for it.
- **Q5 — Identifying the sides for `Reopens:`.** Recommended: the `%X`/`%Y` labels resolved to
  commits, with `--cherry-pick` symmetric difference, and an unresolved conflict when they do not
  resolve. Alternatives considered: `MERGE_HEAD`/`REBASE_HEAD`/`CHERRY_PICK_HEAD` (absent while the
  driver runs, E1); `ORIG_HEAD` (the pre-merge `HEAD`, or the whole old branch in a rebase); the
  last `pick` of `.git/rebase-merge/done` (rebase only, and an internal file format).
- **Q6 — Keeping the block current.** Recommended: `epic add --own-file` and `epic split` update an
  existing block, and `upgrade` repairs anything else. Alternative: `upgrade` only, plus a
  `validate` warning when a recorded block misses a backlog or epic file.
- **Q7 — Changelog bullets.** Recommended: a follow-up feature in E02, "Merge appended changelog
  bullets without duplicating moved ones", created with `taskrail new` on this branch after the
  plan is approved. Alternative: include it here, which pushes the task past 5 points.
- **Q8 — Validation.** Recommended: the driver never validates (other files may still be
  unmerged); step 8 keeps running `taskrail validate` after the merge or rebase. Alternative: a
  per-file duplicate-ID check that turns a clean result into exit 1 — but git would then mark the
  file conflicted without any markers to find.
- **Q9 — This repository.** Recommended: do not install or commit the block here in this task.

Risks:

- **Running repository code on merge.** The driver runs the checked-out wrapper and the taskrail
  version it pins, like the `--pre-commit` hook; that is why the git config is per-clone opt-in.
  With a release pin and no matching installed CLI, the first run goes through `uvx` and may need
  the network.
- **Git before 2.44** has no `%S`/`%X`/`%Y`; they reach the driver literally, labels do not resolve,
  markers carry those literal labels, and status conflicts needing the reopen check stay marked.
  Everything else works. This machine runs git 2.55.
- **Criss-cross merges.** merge-ort calls the driver to build a virtual ancestor with labels that
  are not commits; the driver still merges rows, and leaves reopen-dependent status conflicts to
  git's handling of the virtual base.
- **Cost.** One process per file both sides changed; the wrapper with a `local:` pin starts in
  about 0.13 s here (E5).
- **Size.** Five points is tight. If it has to shrink, drop Q6's epic-command hook and the index
  files of Q3 first; the table merge, the status rule and `init --merge-driver` are the core.
- **Parallel lanes.** T024 edits `install.py` (skill and reference files) and the skills; this task
  touches `install.py` only in `install()`'s extras and edits step 8 of the core skill, so a
  rebase conflict with T024 is possible there and small.

## Evidence

Throwaway repositories under `/tmp`, git 2.55.0, deleted afterwards.

**E1 — What a driver sees.** A driver script defined as `probe.sh %O %A %B %L %P %S %X %Y` logged
its arguments, working directory, `GIT_*` variables and pseudo-refs during a merge, a rebase and a
cherry-pick of a conflicting `f.md`:

```
##### MERGE
=== driver args: .merge_file_y9xmks .merge_file_nEZPHt .merge_file_GzqlTA 7 f.md bf431f2 HEAD topic
cwd=/tmp/t004-probe.GV0A/r
GIT_REFLOG_ACTION=merge topic
HEAD=9b57ed91f3b93b90a4660235f98b6f74440a78ac
MERGE_HEAD=
REBASE_HEAD=
CHERRY_PICK_HEAD=
ORIG_HEAD=9b57ed91f3b93b90a4660235f98b6f74440a78ac
##### REBASE
=== driver args: .merge_file_SOer7n .merge_file_eHEicB .merge_file_Q59YBu 7 f.md parent of 4378fa4 (t1) HEAD 4378fa4 (t1)
cwd=/tmp/t004-probe.GV0A/r
HEAD=9b57ed91f3b93b90a4660235f98b6f74440a78ac
MERGE_HEAD=
REBASE_HEAD=
CHERRY_PICK_HEAD=
ORIG_HEAD=0d39259191dcb4ae6cef1df5443c1123d89dece3
rebase-merge/done:
pick 4378fa48798d2e07def2ee1be131d14f21ddebd5 # t1
##### CHERRY-PICK
=== driver args: .merge_file_q3vk7f .merge_file_Cn8dV9 .merge_file_Qlqvjb 7 f.md parent of 4378fa4 (t1) HEAD 4378fa4 (t1)
MERGE_HEAD=
REBASE_HEAD=
CHERRY_PICK_HEAD=
ORIG_HEAD=0d39259191dcb4ae6cef1df5443c1123d89dece3
```

(`ORIG_HEAD` in the rebase is `0d39259`, the tip of the two-commit branch, not the commit being
replayed.)

**E2 — `git merge-file` on pre-merged tables.** A table `| 1 | a |`, `| 2 | b |` between `intro` and
`outro`:

```
case1 exit=0      # tables identical on both sides, one side also edits the line above the header
case2 exit=1      # identical tables on both sides only, one side edits the line right after the table
| 3 | c |
<<<<<<< R2
OUTRO
=======
outro
>>>>>>> B2
case3 exit=1      # both sides edit that prose line differently: markers on the prose only
case4 exit=1      # one row differs between the sides: markers on that row only
<<<<<<< R4
| 2 | A |
=======
| 2 | B |
>>>>>>> B4
case2 with O' = resolved table: exit=0     # the merged table also in the base: clean
intro
| ID | T |
|--|--|
| 1 | a |
| 2 | X |
| 3 | c |
OUTRO
case4 with O': exit=1                      # unresolved row still marked alone
```

**E3 — Label quoting.** A driver printing `sys.argv[1:]`:

```
['.merge_file_APZXYl', '.merge_file_KRRZCN', '.merge_file_lAXCVE', '7', 'f.md', 'c5a9fbb', 'HEAD', 'lbl']                                      # git merge lbl
['.merge_file_bUKsVP', '.merge_file_uw3aRS', '.merge_file_xhE9Iv', '7', 'f.md', 'c5a9fbb', 'HEAD', 'f7daaf6cfafce79ed6ac32f8913541d4ba764868'] # git merge FETCH_HEAD
['.merge_file_dlInAZ', '.merge_file_1EyY4s', '.merge_file_Bb5BZT', '7', 'f.md', 'parent of f7daaf6 (lbl)', 'HEAD', 'f7daaf6 (lbl)']           # git rebase main
```

**E4 — An attribute naming an undefined driver.** With `f.md merge=taskrail` committed and no
`merge.taskrail.driver` in config, a merge of two non-overlapping edits:

```
Auto-merging f.md
Merge made by the 'ort' strategy.
 f.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
exit=0
```

**E5 — Wrapper start-up and test baseline.**

```
$ time .taskrail/bin/taskrail --version
taskrail 0.2.0.dev0
real	0m0.132s
$ uv run --directory tools/taskrail pytest -q
641 passed in 76.07s (0:01:16)
```
