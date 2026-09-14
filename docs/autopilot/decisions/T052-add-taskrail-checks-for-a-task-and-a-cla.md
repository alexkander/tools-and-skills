# T052 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## escalated to the human

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Who decides changes to the governing documents (`DESIGN.md`, `CLAUDE.md`) proposed by this run's lanes | the human per text · the orchestrator for this run · remove them from `governing` | **the orchestrator decides every `DESIGN.md` and `CLAUDE.md` change in this run; the human reviews them in the pull request. Also open a separate task removing both files from `[autopilot].governing` (T060)** | The human delegated the decisions to keep the lanes moving, and chose to make the change permanent. |

Answered by the human (repository owner), in the orchestrator session.

## plan gate

Reviewed: the plan in `docs/features/T052-add-taskrail-checks-for-a-task-and-a-cla.md` (commit
`3ed347e`), its eight acceptance criteria and seven questions, and finding F11 of T033 (permission
prompts dominated because compound commands cannot match an allowlist). On `origin/main`
(`1631ab8`) there is no command that runs a task's checks, and the Claude Code notes say nothing
about command shape, so the premise holds. This run's own orchestrator hit the same limit. No code
changed, so no checks were re-run.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Exit code for a failing check | new exit 6 · exit 1 · pass through | **as recommended (exit 6)** | Exit 1 already means an invalid backlog to every skill; passing a check's code through collides with taskrail's codes. |
| 2 | Whose configuration defines the checks | the worktree's own, else the caller's · always the caller's | **as recommended (the worktree's own)** | A branch that changes its checks must run them, as this repository's `local:` pin runs a branch's own code. |
| 3 | Check output with `--json` | captured per check in `output` · streamed to stderr | **as recommended (captured)** | stdout stays one JSON document for agents. |
| 4 | Claude Code note text in both sections | approve as written · only the `taskrail` section | **approve as written** | The orchestrator needs the same shape; the notes stay in `integrations/claude.md`, outside the portable text. |
| 5 | DESIGN.md §7 row, new §7.5 and the §8 `claude` row | approve as written · only the §7 row | **approve as written** | Decided by the orchestrator under the human's delegation; a new exit code and lookup rules belong in the design. |
| 6 | Name `taskrail checks` in the core skill's step 5 and add exit 6 to its table | yes · no | **as recommended (yes)** | Every executor reads step 5; the command is a CLI contract any agent can call, so it belongs in the portable text. |
| 7 | Lane brief and autopilot re-run steps | follow-up chore after T055 · fold in at hand-off | **as recommended (follow-up)**: open it with `taskrail new`, kind chore, epic E02, depending on T052 and T055, verified by an assertion on the shipped text, committed on this branch | Those lines are T055's; folding them in at hand-off would be an edit outside any gate. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T052 owns the new `checks.py`, `EXIT_CHECK_FAILED` and `cmd_checks` with its parser registration in `cli.py`, `integrations/claude.md`, step 5 and the exit-code table of the core `taskrail` skill, `tests/test_checks.py`, `CORE_CLAUDE_NOTES` and one new test in `tests/test_autopilot_skill.py`, DESIGN §7's new row, §7.5 and the §8 `claude` row, and one README line. T047 adds one line in `cmd_claim`; T048 changed its `--run` check; T055 owns the lane brief and the autopilot skill's re-run steps; T056 the OpenCode note and §8 `opencode` row.** | Built from the gates reached so far. |
| 2 | Installed skill copies, `installed.json`, CHANGELOG, TODO.md, index READMEs, adjacent new tests | resolve at hand-off · serialize | **resolve at hand-off, keeping every entry** | Known conflict classes 1–3; adjacent new test functions kept side by side. |
