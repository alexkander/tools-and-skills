# T028 — Write the autopilot design into DESIGN.md

Kind: chore · Epic: E02 · Status: scoped

## Goal

The autopilot's architecture was accepted at T007's decide gate, but it lives only in the spike
document ([T007](../spikes/T007-design-taskrail-s-autopilot-from-existin.md)), next to the
evidence that justified it, while `tools/taskrail/DESIGN.md` still lists the autopilot as a
phase-2 non-goal with no design. The tasks that build it (T029–T032, then T024) need one
reference that states the design as taskrail's planned architecture, including the human's
decisions at that gate ([decision record](../autopilot/decisions/T007-design-taskrail-s-autopilot-from-existin.md)).

This chore moves the design, not the evidence, into `DESIGN.md`: marked throughout as planned
and not implemented, with the tasks that will implement each part, and linking to the spike for
evidence and the options considered.

## Change set

| File | Change |
|---|---|
| `tools/taskrail/DESIGN.md` §1 | The autopilot non-goal stays a v1 non-goal, and points to the planned design in the new section. |
| `tools/taskrail/DESIGN.md` §11 | Phase 2 names the autopilot's delivery tasks (T017, T027, T029–T032, T024, then the trial T033) and points to the new section. |
| `tools/taskrail/DESIGN.md` new §12 *Autopilot (planned)* | Appended after §11. Opens with a status line: planned, not implemented, accepted in T007, and that nothing in it describes current behaviour. Subsections, carried from the spike's design points 1–8 with the human's decisions applied: |
| | **12.1 Skill and CLI.** What the CLI computes and what the `taskrail-autopilot` skill judges; the `taskrail autopilot` command table (`start`, `next`, `lane`, `status`, `merged`, `notify`) with their exit-code behaviour; `autopilot` runs only on explicit request with a count, stated as a prose rule. |
| | **12.2 Installation and opt-in** (human's decision 4). `init` and `upgrade` install `taskrail-autopilot` in every repository. It is not an executor skill — no kind names it — so the §9 kind filter never leaves it out. `autopilot start` refuses with exit 5, naming `[autopilot].enabled`, until that key is true, and the skill stops on that refusal. |
| | **12.3 Orchestrator and lanes.** The agent-neutral lane contract; the Claude Code / OpenCode mapping table (lane, handle, resume, wake-up, lane cannot ask, lane model, no timer); OpenCode's blocking default meaning gates are answered in waves; agent-specific text in integration notes, agent definitions deferred. |
| | **12.4 State.** Derived states (`pending`, `running`, `done-branch`, `done-merged`); claims stay the only lock, gaining `base.commit` (T017, specified in §6) and `run`; the local run file under the git common directory and what it holds; two orchestrator sessions at once. |
| | **12.5 Decision records.** Path templates and index, committed on the task branch by the orchestrator only while the lane is stopped at a gate; section format; run-level decisions copied into each affected task's record and kept in the run file (human's decision 3). |
| | **12.6 Escalation, notification and supervision.** The escalation list, which conditions the CLI computes; the `notify` command contract; event-driven supervision with `silent_minutes`. |
| | **12.7 Resources.** `max_lanes`, `[[autopilot.group]]` (computed by column or assigned by judgement), `[[autopilot.resource]]` pools passed as `TASKRAIL_RESOURCE_<NAME>`, shared services started only by the orchestrator, sequential numbers through `reserve-id`. |
| | **12.8 Merge follow-through.** Lanes stop before publishing; sequential hand-off; `autopilot merged` and `rebase --onto` for stacked dependents; merge detection order ancestor → tree → patch-id → `merge-tree`, with the ✅ row and `(ID)` title as confirmation only; the three known conflict classes and T027 as the prerequisite for class 3. |
| | **12.9 Configuration.** The `[autopilot]`, `[[autopilot.group]]` and `[[autopilot.resource]]` keys with defaults, as a TOML block. It joins §4 when T029 implements it. |
| | **12.10 Delivery.** Which task implements which subsection, with dependencies; follow-ups not planned (lane agent definitions, `batch` hand-off, named counters); what would change the design, in one line each. Evidence (E1–E7) and rejected options are linked in the spike, not copied. |
| `docs/chores/T028-write-the-autopilot-design-into-design-m.md` | This artifact. |
| `docs/chores/README.md` | Index row for T028. |

Style follows `DESIGN.md` as it is: numbered `###` subsections, tables for commands and
mappings, short bullets, `§` cross-references, no evidence transcripts.

## Decisions needed

1. **Where the section goes.** Recommended: append it as **§12 after §11 Phases**, so no
   existing section is renumbered while T017 edits §6 and §7 in parallel. No file in the
   repository references `§10` or `§11`, so the alternative — insert it as §11 before the
   phases and renumber Phases to §12 — is also safe, and reads better (phases last); it changes
   one more heading line.
2. **Rejected alternatives in DESIGN.md.** Recommended: **link to the spike's *Options
   considered*** rather than copy them, with one sentence each only for the two most likely to
   be re-proposed while building (a CLI that spawns agent CLIs itself; installing the skill only
   where enabled). Alternative: no rejected options at all in DESIGN.md, or copy the full table.
3. **`autopilot lane --group`.** The spike's design point 6 assigns group membership by
   judgement "with `autopilot lane --group`", but its command table's `lane` signature omits
   `--group`. Recommended: write `--group G` into the `lane` signature in §12.1, since point 6
   requires it. Alternative: carry the table as written and leave the gap to T029/T030.
4. **Conflicts outside the known classes as a CLI flag.** Design point 5 says only two escalation
   conditions are computed by the CLI (governing paths touched, `escalate_gates`), while T032's
   backlog description also says `status` flags "conflicts outside the known classes".
   Recommended: DESIGN.md follows the accepted design point 5 (conflict classification is
   judgement), and notes that T032 settles at its own gate whether a flag helps; this chore does
   not edit T032's row. Alternative: state it as a third computed flag.
5. **CHANGELOG.** Recommended: **no bullet**. `## Unreleased` lists changes to what taskrail
   does, and this change adds only planned design; T007 added none either. Alternative: one
   bullet noting the documented plan.
6. **README.md.** It does not mention the autopilot, planned or otherwise. Recommended: **no
   change**; the README gains the autopilot when T029 or T024 ships it.

## Out of scope

- DESIGN.md §6 (claims) and §7 (`show`, `next`, base): T017 specifies `done-branch`, the stacked
  base and `base.commit` there, in parallel. §12 refers to them without editing them.
- §2 concepts, §4 configuration, §7 command table, §8 skills and §10 layout: the planned
  commands, keys, skill and module stay in §12 until the tasks that implement them move them
  into those sections.
- The top-of-file status line (v1 released): unchanged.
- The spike document and the T007 decision record: unchanged; they keep the evidence.
- Code, skills, `TODO.md` rows (including T032's description), the README.

## Verification

- `git diff origin/main --stat` shows only `tools/taskrail/DESIGN.md`, this artifact and
  `docs/chores/README.md`.
- `git diff origin/main -- tools/taskrail/DESIGN.md` touches only §1, §11 and the new section,
  and no heading of §2–§10 changes.
- A point-by-point check of the spike's design points 1–8 against §12, including the human's
  decisions 3 and 4: every command, state, config key, default and escalation condition appears,
  and none appears that the spike does not have (except any addition approved above).
- Every task ID in §12 exists with the stated dependencies (`taskrail show` for T017, T024,
  T027, T029–T033), and every relative link in §12 resolves to a file.
- `grep -n 'autopilot' tools/taskrail/DESIGN.md` shows no sentence describing the autopilot as
  current behaviour.
- `.taskrail/bin/taskrail validate` passes, and the stage's `test` check
  (`uv run --directory tools/taskrail pytest -q`) passes unchanged. `lint` is not configured.
