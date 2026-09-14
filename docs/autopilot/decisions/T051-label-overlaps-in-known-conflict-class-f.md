# T051 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## escalated to the human

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Who decides changes to the governing documents (`DESIGN.md`, `CLAUDE.md`) proposed by this run's lanes | the human per text · the orchestrator for this run · remove them from `governing` | **the orchestrator decides every `DESIGN.md` and `CLAUDE.md` change in this run; the human reviews them in the pull request. Also open a separate task removing both files from `[autopilot].governing` (T060)** | The human delegated the decisions to keep the lanes moving, and chose to make the change permanent. |

Answered by the human (repository owner), in the orchestrator session.

## plan gate

Reviewed: the plan in `docs/features/T051-label-overlaps-in-known-conflict-class-f.md` (commit
`80446ca`), its seven acceptance criteria, the lane's capture of this run's `overlaps` (13 files, 7 of
them backlog, index, changelog or installed files), and `mergedriver.attribute_paths()` on
`origin/main` (`1631ab8`). DESIGN §12.6 records why T032 gave conflicts no computed flag: the known
classes are defined by content, so a path-based label would also call a real edit inside a backlog or
changelog "known". The task row, from T033's recommendation, asks for the path-based separation
anyway; the label must say it is by path. No code changed, so no checks were re-run.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | DESIGN.md §12.1 `autopilot status` overlaps phrase | approve as written · reword | **approve with one addition**: after "and `tasks` (T051)" add "; the label is by path, so a rebase still resolves such a file only when its conflict is one of those classes by content" | Keeps §12.6's caveat true: `known_overlaps` sorts attention, it does not pre-approve a conflict. Decided by the orchestrator under the human's delegation. |
| 2 | Include class 3 (`installed`) | include from the manifest's `files` · leave in `overlaps` | **as recommended (include)** | §12.8 lists it as a known class, and both files overlapped in this run; an unreadable manifest yields no `installed` paths. |
| 3 | Skill *Supervise* bullet | approve as written · no change | **approve as written** | The orchestrator reads `status` from the skill; T055 rewrites other skill text and must leave this bullet to T051. |
| 4 | JSON shape | narrow `overlaps` and add `known_overlaps` · subset · objects | **as recommended (narrow and add)** | Readers of `overlaps` get the signal the finding asked for; the shape of each map stays simple. The CHANGELOG bullet must say `overlaps` no longer lists known-class files. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T051 owns `status()` and a new helper in `autopilot/status.py`, the overlaps lines at the end of `_status_text()` in `commands.py`, the `attribute_paths`/`known_conflict_paths` split in `mergedriver.py`, `tests/test_autopilot_overlaps.py` plus the expected dict of `test_status_without_runs_and_for_an_unknown_run`, the *Supervise* `overlaps` bullet of the skill, and the overlaps phrase of the DESIGN §12.1 `autopilot status` row. T048 owns the run header of `_status_text`, `run_status`'s `closed`, `runs.py` and `dispatch.py`'s closed-run filter; T054 `task_state`/`_closing` and the dispatch skip; T053 `_handoff`/`_done_time`; T049 `_escalation_text` and *Escalate* condition 1; T055 the remaining skill text.** | Built from the gates reached so far; the same §12.1 row now carries phrases from T049, T053, T054 and T051, all kept at hand-off. |
| 2 | Installed skill copies, `installed.json`, CHANGELOG, TODO.md, index READMEs | resolve at hand-off by the known classes · serialize | **resolve at hand-off** | Known conflict classes 1–3. |
