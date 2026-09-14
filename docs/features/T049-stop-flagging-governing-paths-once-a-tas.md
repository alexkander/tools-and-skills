# T049 — Stop flagging governing paths once a task is done on its branch

Kind: feature · Epic: E02 · Status: plan

Source: finding F9 of the autopilot trial
([T033](../spikes/T033-trial-the-autopilot-on-a-real-backlog-wi.md), Findings table and
Recommendation): a lane that edited a governing path kept `escalation: ["governing"]` in
`autopilot status` after the human had approved the edit, through `done-branch` and `handed-off`
until its merge, while `escalate_gate` is dropped once a task moves on. No prior work: `show`
reported no artifact, branch or commit for T049.

## Premise, checked on the current mainline

`tools/taskrail/src/taskrail/autopilot/escalation.py` `flags()` computes `governing_touched` from
`touched` with no regard to the state, and adds `governing` to `escalation` whenever that list is
not empty. `status.py` computes `touched` for every state in `WITH_BRANCH` — `running`, `gate`,
`escalated`, `failed`, `done-branch`, `handed-off` — so a task waiting in the hand-off queue is
flagged on every `status`. `escalate_gate`, by contrast, is set only in `gate` and `escalated`
(`GATE_STATES`). `done-merged` is already unflagged, because it has no `touched`. The premise
holds.

## Behaviour

After this change, `autopilot status` stops raising `governing` as an escalation reason for a task
that has moved on — `done-branch` or `handed-off` — just as `escalate_gate` is dropped then:

- **Before `done-branch`** (`running`, `gate`, `escalated`, `failed`) nothing changes: a lane whose
  `touched` files match a `governing` entry has those files in `governing_touched` and `governing`
  in `escalation`, and the text form ends its line with `ESCALATE: governing …`.
- **At `done-branch` and `handed-off`** `governing_touched` still lists the matching files — they
  are facts about the branch, and the orchestrator's close review needs them — but `escalation`
  no longer contains `governing`, and the text form prints no `ESCALATE:` for them.
- **The close review closes the gap this opens.** A governing path first changed after the lane's
  last gate (in a `verify` stage that did not stop, or in the close itself) was never flagged
  while the lane was stopped. The skill's close review therefore checks that every path in
  `governing_touched` was escalated and answered in the task's record, and escalates one that was
  not. The skill's escalation condition 1 reads the `governing` reason in `escalation`, not the
  bare list.

The text form's `ESCALATE:` part is built from the reasons in `escalation`, so the JSON and the
text always agree.

## Acceptance criteria

1. A lane in `running`, `gate`, `escalated` or `failed` whose `touched` matches a `governing`
   entry reports those files in `governing_touched` and `governing` in `escalation` (unchanged
   behaviour, `failed` newly covered by a test).
2. The same lane at `done-branch` reports the files in `governing_touched`, `escalation` without
   `governing`, and `escalate_gate` `null` — including when its last recorded gate is listed in
   `escalate_gates`.
3. The same lane at `handed-off` reports the same as at `done-branch`.
4. `autopilot status` in text form prints `ESCALATE: governing …` for a flagged lane before
   `done-branch` and no `ESCALATE:` for a `done-branch` or `handed-off` lane that touched a
   governing path.
5. `done-merged` stays unflagged with an empty `governing_touched` (existing test kept).
6. The `taskrail-autopilot` skill source says escalation condition 1 is the `governing` reason in
   `escalation`, and its gate review's *Close* section says a `governing_touched` path not
   escalated in the task's record escalates; a prose test in `test_autopilot_skill.py` asserts
   both, and the installed copies under `.claude/skills/` are refreshed with `taskrail upgrade`.
7. All tests pass: `uv run --directory tools/taskrail pytest -q`.

All criteria are verified by pytest with the existing `pilot` fixture repository, following the
pattern of `test_autopilot_notify.py` (a lane worktree, a commit touching a governing path,
`pilot.finish` to reach `done-branch`, `autopilot lane --state handed-off`).

## Affected areas

- `tools/taskrail/src/taskrail/autopilot/escalation.py` — `flags()`: omit `governing` from
  `escalation` when the state is `done-branch` or `handed-off`.
- `tools/taskrail/src/taskrail/autopilot/commands.py` — `_escalation_text()`: build `ESCALATE:`
  from the reasons in `escalation`.
- `tools/taskrail/tests/test_autopilot_notify.py` — tests for criteria 1–5.
- `tools/taskrail/tests/test_autopilot_skill.py` — prose assertions for criterion 6.
- `tools/taskrail/src/taskrail/skills/taskrail-autopilot/SKILL.md` (*Escalate*, condition 1) and
  `references/gate-review.md` (*Close*), then `.claude/skills/taskrail-autopilot/` through
  `.taskrail/bin/taskrail upgrade`.
- `tools/taskrail/DESIGN.md` §12.4 (`autopilot status` row) and §12.6 (*Governing paths*) — a
  governing path, changed only with the human's approval of the exact text at the plan gate.
- `tools/taskrail/CHANGELOG.md` — one *Unreleased* bullet (behaviour change).
- `docs/features/README.md` — this document's row.

`status.py` is not changed: `touched`, `overlaps` and the hand-off queue stay as they are, so the
area T053 changes there is left alone.

## Out of scope

- **Acknowledging an approved governing edit before `done-branch`.** Between the human's approval
  at an early gate and `done`, the lane is `running` or `gate` and is still flagged, so the
  orchestrator sees the flag again at later gates. The spike's proposal named "or after a
  recorded approval"; the task row narrows T049 to the move to `done-branch`. Recording an
  approval needs its own design (what is approved — paths or their content — and where it is
  stored), proposed as a follow-up below.
- `escalate_gate` behaviour, the other escalation reasons of §12.6, `touched` and `overlaps`.
- The `--gate close` stop (T050) and the hand-off queue order (T053).

## Open questions and risks

- **A governing edit made after the last gate is no longer flagged by `status`.** Mitigated by the
  close-review rule of criterion 6, which is judgement in the skill rather than a computed flag.
  The alternative that keeps a computed flag at `done-branch` is what F9 reports as the problem.
- **Overlap with T050**, which is likely to touch the skill's close stop: both may edit the *Close*
  section of `references/gate-review.md`. The edit here is one bullet.
- **Proposed follow-up** (only if approved; verifiable by pytest): *Record the human's approval of
  a governing edit so `autopilot status` stops flagging it before `done-branch`* — for example
  `autopilot lane <ID> --approve-governing` storing the approved paths with their blob IDs in the
  run file, so a later change to the same path flags again.

## Proposed DESIGN.md text

**§12.4, `autopilot status` row** — replace

> Per task, the escalation reasons of §12.6: `gate` (the recorded stage), `governing_touched` (the
> `touched` files a `governing` entry matches), `escalate_gate` (`kind:stage` when the task is
> `gate` or `escalated` at a stage `escalate_gates` lists, else `null`) and `escalation`
> (`governing`, `escalate-gate`, or empty); the text form adds `ESCALATE: …` to a flagged lane.

with

> Per task, the escalation reasons of §12.6: `gate` (the recorded stage), `governing_touched` (the
> `touched` files a `governing` entry matches), `escalate_gate` (`kind:stage` when the task is
> `gate` or `escalated` at a stage `escalate_gates` lists, else `null`) and `escalation`
> (`governing` when `governing_touched` is not empty and the task is not yet `done-branch`,
> `escalate-gate` when `escalate_gate` is set, or empty; T049); the text form adds `ESCALATE: …`,
> naming the reasons in `escalation`, to a flagged lane.

**§12.6, *Governing paths* bullet** — append after "that is the configuration's choice.":

> A task that has moved on (`done-branch` and `handed-off`) keeps its `governing_touched`, but
> `governing` leaves its `escalation`, as `escalate_gate` does: the edit was escalated while the
> lane worked, and a branch waiting for hand-off would otherwise raise it again on every `status`
> (T033 finding F9; T049). A governing path first changed after the lane's last gate is caught by
> the close review instead, which escalates any `governing_touched` path the task's record does
> not show escalated.
