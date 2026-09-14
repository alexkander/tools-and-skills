# T043 — autopilot decisions

Decisions for this task while it ran in an autopilot lane. The human decided that caveman is kept
for use in this repository only, and that RTK is evaluated the same way; the orchestrator opened
epic E06, this task and T044, and discarded T008, T010, T042 and T011 on this branch. CLAUDE.md
changes are the human's.

## scope gate

Reviewed: the scope in `docs/chores/T043-move-caveman-to-claude-skills-for-use-in.md` (commit
`d4f1a42`) and its evidence: primary docs and isolated trials show a README next to `SKILL.md` does
not affect discovery by Claude Code or OpenCode, and `taskrail upgrade`, with or without `--force`,
leaves an unmanaged `.claude/skills/caveman/` byte-identical.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | README location | next to `SKILL.md` · `docs/` · folded into `SKILL.md` | **next to `SKILL.md`** (orchestrator) | Both agents ignore it, and attribution and the pin stay beside the vendored text without costing tokens on activation. |
| 2 | `SKILL.md` | unchanged · reword "consuming project" | **unchanged** (orchestrator) | The move stays a pure rename and the vendored text keeps its bytes. |
| 3 | Empty `skills/` | leave untracked, no placeholder · `.gitkeep` · stub README | **no placeholder** (orchestrator) | CLAUDE.md still defines the layout for future shareable skills; an empty directory needs no file. |
| 4 | Root README wording | as proposed · drop `skills/` from Layout | **as proposed** (orchestrator) | Keeps the README consistent with CLAUDE.md's Layout. |
| 5a | CLAUDE.md Layout note on `.claude/skills/` | in this task · separate chore · no change | **in this task** — decided by the human | Add the proposed sentence to Layout; the orchestrator shows the exact diff to the human before publishing. |
| 5b | CLAUDE.md Distribution | no change · change | **no change** (orchestrator) | It is the policy for future shareable skills. |
| 5c | CLAUDE.md vendored-content rules | no change · change | **no change** (orchestrator) | They still describe caveman. |
| 6 | Pull request title | `chore(caveman): …` · `chore(skills): …` | **`chore(caveman): …`** (orchestrator) | The change is about caveman's place in this repository. |

Change set approved with the CLAUDE.md Layout sentence added.

## close

The lane moved caveman as a pure rename, rewrote its README and the root README, and verified
discovery by both agents and that `taskrail upgrade` leaves it alone. It stopped short of editing
CLAUDE.md because the instruction was relayed; the orchestrator applied the checked patch, which is
exactly the sentence the human approved, and closed the task.
