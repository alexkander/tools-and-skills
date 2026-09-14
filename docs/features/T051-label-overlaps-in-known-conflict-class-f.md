# T051 — Label overlaps in known conflict-class files

Kind: feature · Epic: E02 · Status: plan (awaiting approval). Record:
`docs/autopilot/decisions/T051-label-overlaps-in-known-conflict-class-f.md`.

Source: finding F12 of `docs/spikes/T033-trial-the-autopilot-on-a-real-backlog-wi.md`:
"`CHANGELOG.md`, `TODO.md` and the index READMEs overlap between every pair of lanes, which buries
the one real overlap". Builds on T029 (`autopilot status`, `touched` and `overlaps`) and T004's
merge driver, whose `attribute_paths()` already lists the backlog files, epic files, artifact
indexes and changelogs the known conflict classes of DESIGN §12.8 cover.

## Today

`status()` in `tools/taskrail/src/taskrail/autopilot/status.py` puts every path that more than one
lane touched into `overlaps`, and `_status_text()` in `autopilot/commands.py` prints them all under
one heading. In this repository's own run `20260914-1`
(`taskrail autopilot status --run 20260914-1 --json`, taken while this plan was written),
`overlaps` had 13 entries. Five are class 1 or 2 files — `TODO.md`,
`docs/autopilot/decisions/README.md`, `docs/bugs/README.md`, `docs/features/README.md`,
`tools/taskrail/CHANGELOG.md` — and two are class 3 files — `.claude/skills/taskrail-autopilot/SKILL.md`
and `.taskrail/installed.json`. The six left (`DESIGN.md`, `commands.py`, `dispatch.py`,
`status.py`, the skill source and `test_autopilot_skill.py`) are the ones the touch map has to
answer for.

## Behaviour

After this change, `taskrail autopilot status [--json]`:

- keeps `overlaps` as `{path: [task IDs]}`, but only for files outside the known conflict classes;
- adds `known_overlaps`, `{path: {"class": <class>, "tasks": [task IDs]}}`, for files in them,
  with the class:
  - `backlog` — each backlog file and each epic in its own file;
  - `index` — each kind's `artifact_index` and `[autopilot].decisions_index` that does not depend on
    the task (the same templates the merge driver lists);
  - `changelog` — a file named `CHANGELOG.md` in any letter case;
  - `installed` — `.taskrail/installed.json` and the files it records (subject to D2);
- in text, prints real overlaps first under `files touched by more than one lane:`, then
  `known conflict classes touched by more than one lane (resolved at hand-off):` with one line
  per file, `  TODO.md (backlog): T049, T053`. Each heading appears only when it has entries.

The backlog, index and changelog sets come from one function shared with the merge driver's
`.gitattributes` block, so both stay in step. A file touched by a single lane is in neither map,
as today.

## Acceptance criteria

1. Two scripted lane worktrees that both change the backlog file, a changelog, a kind's artifact
   index, the decision-record index and one source file: `overlaps` holds only the source file, and
   `known_overlaps` holds the other four with classes `backlog`, `changelog`, `index`, `index` and
   both task IDs.
2. An epic in its own file that both lanes change is `backlog`; a `CHANGELOG.md` created only on
   the lanes' branches (not tracked in the main checkout) is still `changelog`.
3. Both lanes changing `.taskrail/installed.json` and an installed skill copy it records gives
   class `installed` for both (only if D2 is approved as recommended).
4. A known-class file touched by a single lane appears in neither map; a non-class file touched by
   two lanes stays in `overlaps` exactly as before (the existing T029 test passes unchanged).
5. With no runs, `status --json` is `{"runs": [], "overlaps": {}, "known_overlaps": {}, "fetched": []}`.
6. The text form lists the real overlap under its heading before the known-class heading, each
   known line carrying its class; with only known-class overlaps, the real-overlap heading is absent.
7. The merge driver's `attribute_paths()` returns the same list as before for the existing merge
   driver tests, and equals the backlog, index and changelog keys of the shared function.

All verified by pytest with scripted worktrees; no manual trial.

## Affected areas

- `tools/taskrail/src/taskrail/autopilot/status.py` — `status()` only (the overlaps computation),
  plus a new private helper for the class of a path. Not `task_state`, `_closing`, `_handoff`,
  `_done_time` or `run_status`.
- `tools/taskrail/src/taskrail/autopilot/commands.py` — the overlaps lines at the end of
  `_status_text()` only. Not the run header line (T048), `_escalation_text` (T049) or `_gate_problem`.
- `tools/taskrail/src/taskrail/mergedriver.py` — `attribute_paths()` split into a
  `known_conflict_paths(project)` returning `{path: class}` and a thin `attribute_paths(config)`
  that keeps its signature and result.
- `tools/taskrail/src/taskrail/skills/taskrail-autopilot/SKILL.md` — the `overlaps` bullet of
  *Supervise* (D3), and the installed copy through `taskrail upgrade`.
- `tools/taskrail/DESIGN.md` — the overlaps phrase of the §12.1 `autopilot status` row (D1).
- Tests: a new `tools/taskrail/tests/test_autopilot_overlaps.py` reusing the `pilot` fixture, and
  the one expected dict in `test_status_without_runs_and_for_an_unknown_run` in
  `tests/test_autopilot.py` (adds `known_overlaps`).
- `tools/taskrail/CHANGELOG.md` (one bullet), `docs/features/README.md` (index row), `TODO.md`
  (close).

## Out of scope

- Deciding for the orchestrator: known-class overlaps are still reported, only apart.
- A configuration key for extra known-class paths.
- Hiding a source file because its installed copy is known-class: the skill source stays a real
  overlap.
- Any change to `touched`, the escalation flags or the hand-off queue.

## Open questions and risks

- **D1 — DESIGN.md text** (governing): in the §12.1 `autopilot status` row, replace
  "`touched`, the files changed since the fork point plus uncommitted ones, with `overlaps` between
  lanes across the runs listed;" with "`touched`, the files changed since the fork point plus
  uncommitted ones, with `overlaps` between lanes across the runs listed, except files of the known
  conflict classes of §12.8, which go to `known_overlaps` with their `class` — `backlog` (backlog
  and epic files), `index` (artifact and decision-record indexes), `changelog`, `installed`
  (`.taskrail/installed.json` and the copies it records) — and `tasks` (T051);"
- **D2 — class 3.** The task row names backlog, changelog and index files; §12.8 also lists
  installed skill copies and `.taskrail/installed.json`, and both overlapped in run `20260914-1`.
  Recommended: include them as `installed`, read from the manifest's `files` (an unreadable
  manifest gives no `installed` paths rather than an error). Alternative: leave them in `overlaps`.
- **D3 — skill text.** Replace the *Supervise* bullet with: "`overlaps`: compare them with the touch
  map; an overlap the map does not cover is a question for the lanes involved, or an escalation when
  they contradict each other. `known_overlaps` are files of the known conflict classes: expected,
  and resolved at hand-off." Alternative: no skill change.
- **D4 — JSON shape.** Recommended: `overlaps` narrowed and a separate `known_overlaps`, so a
  consumer reading `overlaps` sees only real overlaps. Alternatives: keep every file in `overlaps`
  and add `known_overlaps` as a subset (noise stays for current readers), or change `overlaps`
  values to objects with a class (breaks the shape).
- **Risk: other lanes.** T048 and T054 edit `status.py` and T048 the run header of `_status_text`;
  this change stays in `status()` and the overlaps lines, and puts its tests in a new file.
- **Risk: cost.** The changelog set runs `git ls-files`; it is computed only when some file has more
  than one lane.
