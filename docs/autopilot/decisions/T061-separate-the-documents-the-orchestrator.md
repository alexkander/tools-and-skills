# T061 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## escalated to the human

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Who decides changes to `DESIGN.md` and `CLAUDE.md` proposed by autopilot lanes | the human per text · the orchestrator · remove them from `governing` | **the orchestrator decides them and the human reviews them in the pull request; both files were removed from `governing` (T060)** | The human's instruction during run 20260914-1, made permanent by T060. |
| 2 | Continue the autopilot with the follow-up tasks | — | **run 20260914-2 with T059, T061, T062 and T063, each dispatched once its row reaches `main`** | The human's instruction. |

Answered by the human (repository owner), in the orchestrator session.

## plan gate

Reviewed: the plan in `docs/features/T061-separate-the-documents-the-orchestrator.md` (commit
`7b3e58c`), its seven acceptance criteria, and on `origin/main` (`502ea3b`) the two roles of
`[autopilot].governing`: `escalation.py` matches it against touched files, and the skill's *Before the
first dispatch* and `gate-review.md` read it as the documents to answer from. With this repository's
list now empty (T060), the skill points the orchestrator at nothing. The premise holds. No code
changed, so no checks were re-run.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Approve the plan with the key `read_first` | `read_first` · `guidance` · `documents` · `reference_documents` | **as recommended (`read_first`)** | Matches the wording the configuration and design already use. |
| 2 | Absent `read_first` | falls back to `governing` · means empty | **as recommended (fall back)** | Existing repositories keep their reading list without a behaviour change. |
| 3 | Report `read_first_missing` | yes · no | **as recommended (yes)** | A renamed document must not drop out silently. |
| 4 | Wording of the two lists | "governing documents" = `read_first`, "governing path" = `governing` · rename everywhere | **as recommended (keep the wording)** | Matches escalation conditions 1 and 3 and leaves T055's *Resume a run* correct without edits on either branch. |
| 5 | This repository's key and the `CLAUDE.md` bullet | set it and update the bullet · leave the bullet · remove the bullet | **as recommended (set it, bullet as proposed)** | Agents outside the autopilot read `CLAUDE.md`, and the bullet carries the policy; the configuration is the machine-readable list. Decided under the human's delegation of `CLAUDE.md` decisions. |
| 6 | `.taskrail/config.toml` text | as proposed · other | **as proposed** | States both roles next to the keys. |
| 7 | DESIGN.md §4 and §12.9 samples, §12.1 `autopilot status` sentence, §12.6 condition 3 and new *Read-first documents* bullet | approve as written · other | **approve as written** | Decided under the human's delegation. The §12.1 row is also edited by T051, T053, T054 (unmerged) and T059 (running); each phrase is kept at hand-off. |
| 8 | Skill *Before the first dispatch* bullets and gate-review *Governing documents first* bullet | approve as written · other | **approve as written** | Sections no other lane edits. |

## Conflict handling agreed for all lanes

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Which lane edits which files | per-plan areas · free | **T061 owns `AutopilotConfig.read_first` and its reading in `config.py` `_autopilot`, `cmd_status` and `_status_text` in `commands.py` for the new fields, the skill's *Before the first dispatch* bullets, gate-review's *Governing documents first* bullet, its tests in `tests/test_autopilot.py` and `tests/test_autopilot_skill.py`, the approved DESIGN text, the `[autopilot]` block of `.taskrail/config.toml` and the last *Backlog* bullet of `CLAUDE.md`. T059 owns `escalation.py`, `approve.py`, `_escalation_text` and `governing_approved` in `status.py`; T051 (unmerged) `status()` and the overlaps lines of `_status_text` plus the no-runs expected dict in `test_autopilot.py`; T048 (unmerged) the run header line of `_status_text` and `cmd_status`'s closed-run filter.** | `cmd_status` and `_status_text` are shared with T048 and T051: add the new fields in separate lines so the hand-off keeps every change. |
| 2 | Installed skill copies, `installed.json`, CHANGELOG, TODO.md, index READMEs, same-line DESIGN rows | resolve at hand-off · serialize | **resolve at hand-off, keeping every phrase** | Known conflict classes 1–3; row edits apply phrase by phrase. |
