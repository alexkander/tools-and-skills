# T025 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T025-skip-installing-skills-for-kinds-a-repos.md` (commit
`9b3b7ae`), its nine criteria, and the lane's reproduction (`kind list` showing only `bug` and
`chore` while all five skills stay installed).

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Filter always, or only when `[kinds].allowed` is set | always · only with `allowed` | **always**: a shipped executor skill installs when a resolved kind names it | One rule instead of two; a skill no kind uses is noise for the agent. The only visible change without `[kinds]` is an override pointing a core kind at another skill, where not installing the unused one is the right outcome. |
| 2 | Report the executor skills left out | note · docs only | **note** | An agent looking for a skill should find out why it is missing from the install report, not only from the docs. |
| 3 | A typo in `allowed` | use the resolved set · install everything on errors | **neither as proposed: install from the resolved set, but remove nothing while kind resolution reports errors**, and say so in a note | The first run showed the hazard of an install step deleting skills from bad input. A typo must not delete copies; once the config is fixed, the next run removes what is no longer wanted. |
| 4 | Approve the plan | approve · with changes | **approve with changes**: criterion 8 follows decision 1; criterion 9 becomes "with kind resolution errors, nothing is removed and a note says why" | Keeps the plan and makes decision 3 testable. |
