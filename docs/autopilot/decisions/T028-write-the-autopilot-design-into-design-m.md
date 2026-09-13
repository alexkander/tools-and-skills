# T028 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## scope gate

Reviewed: `docs/chores/T028-write-the-autopilot-design-into-design-m.md` (commit `f2616b4`) — a
change set confined to `tools/taskrail/DESIGN.md` §1, §11 and a new planned-autopilot section,
leaving §6 and §7 to T017.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Position of the new section | append as §12 · insert as §11 and renumber | **append as §12** | No heading renumbering while T017 edits the same file. |
| 2 | Rejected alternatives in DESIGN.md | link plus one sentence for the two likeliest · none · full table | **link plus one sentence each** for an agent-launching CLI and enabled-only installation | Stops the two most likely re-proposals without duplicating the spike. |
| 3 | `autopilot lane --group` | add to §12.1 · copy the table as is | **add** | The accepted design point 6 uses it; the table omitted it by oversight. |
| 4 | "Conflicts outside the known classes" as a computed flag | follow design point 5 · computed flag | **follow design point 5** and note that T032 settles it at its own gate | The accepted design keeps conflict classification as judgement; the design document must not quietly amend it. |
| 5 | Changelog bullet | none · one bullet | **none** | `Unreleased` lists behaviour changes; this documents a plan. |
| 6 | README change | none · mention | **none** | README describes current use only. |

Approved: the change set and its boundary as scoped.
