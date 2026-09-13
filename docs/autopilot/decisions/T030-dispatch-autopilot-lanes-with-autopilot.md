# T030 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T030-dispatch-autopilot-lanes-with-autopilot.md` (commit
`8c9a232`), its seventeen acceptance criteria and Q1–Q14, against DESIGN.md §12.1, §12.4, §12.7
and §12.9 and T029's decision record. The lane fast-forwarded its empty branch onto T035 before
committing; the claim's `base.commit` still names the earlier fork point, which is harmless for a
branch based on the mainline.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| Q1 | Lanes in use | `running` (stale included), `gate`, `escalated`, plus unclaimed dispatches within grace · also `failed` · live claims only | **as recommended** | Counting `failed` stalls a run nothing can free; counting only claims dispatches a task twice while its lane starts. |
| Q2 | Scope of `max_lanes` and group limits | across every run in the clone · per run | **across runs** | Two orchestrators on one machine share the same machine's limits. |
| Q3 | The run's `count` | respect it, `failed` and `discarded` free a place · ignore · respect, nothing frees | **respect it; `discarded` frees a place, `failed` keeps counting** | The human's count bounds how much work starts. A failed lane keeps its claim and waits for a human, so replacing it would start more work than asked; a discarded task is no work. |
| Q4 | What `next` records | `dispatched` and `resources`, expiring after `[git].claim_grace_minutes` · new key · no expiry · nothing | **as recommended** | Prevents double dispatch before the lane claims, without a new setting. |
| Q5 | Resource release | lazily in `next`, when a lane stops counting · hold until `done-merged` · also on `failed` | **lazily in `next`**, and document that the orchestrator re-runs a lane's checks before its next `next` | Holding values through review would starve dispatch; a released value must never be shared by two live lanes. |
| Q6 | `status` shows `dispatched` | change `status.py` · leave | **change it** | One branch; otherwise `status` calls a dispatched task `pending`, which invites a second dispatch by hand. |
| Q7 | Kinds dispatched | run's kinds, else config's, else all · intersection | **intersection when both are set**; otherwise whichever is set, else every allowed kind | `[autopilot].kinds` is the repository's limit on what the autopilot may drive; a run can narrow it, never widen it. |
| Q8 | Stacked bases and failures | reuse `query.eligible`; skip diverged or missing bases and tasks `failed` in R, with reasons | **agree** | One eligibility rule for people and the autopilot. |
| Q9 | Judgement groups before a lane exists | `lane --group` before `next`, validated · `next --group` · any name | **`lane --group`, exit 2 for an unknown or column group**; update T029's test | Replaces "store as given" now that groups exist; one command writes group membership. |
| Q10 | `next` without `--run` | preview, writes nothing, exit 5 when disabled · newest run · preview while disabled | **as recommended** | A preview must never allocate; the disabled refusal stays a CLI guarantee. |
| Q11 | Exit codes | 5 disabled, 1 invalid, 3 unknown run, 4 lock, 0 even when nothing dispatches | **as recommended** | Consistent with `start` and §7.1. |
| Q12 | Names and values | group names like kind names, resource names valid env suffixes, string values · integers too | **strings only** | Values end up in environment variables; TOML integers would round-trip ambiguously. |
| Q13 | §12.1 "`show`'s fields plus `base.commit`" | reword · keep | **reword** | `show`'s `base` already carries `commit`. |
| Q14 | Size | one task · split groups and resources | **one task** | Dispatch without the limits is not usable; points order work, they do not budget it. |

Plan approved with Q3 and Q7 changed. The lane must remove its scratch repositories under a
temporary directory when it no longer needs them.
