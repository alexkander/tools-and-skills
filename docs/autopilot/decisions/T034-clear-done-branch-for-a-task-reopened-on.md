# T034 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## diagnose gate

Reviewed: the write-up `docs/bugs/T034-clear-done-branch-for-a-task-reopened-on.md` (commit
`99ba96e`), the reproduction (a task reopened on `main` stays `done-branch`, hidden from `next`,
and `claim` exits 5, through the local branch or its remote copy alone), and the probe of the
proposed git query, including a second done on a branch that contains the reopen.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Diagnosis and fix | approve · changes | **approve** | Drop a ✅ tip when a mainline ref has a `Reopens: <ID>` commit the tip lacks; run only for tasks that would otherwise be `done-branch`, on local refs, cached. It matches the backlog conflict rule. Also cover in a test the reopen of a task whose earlier reopen the stale tip already contains (a second reopen cycle). |
| 2 | Clear the recorded branch on reopen | no · follow-up about guidance · clear in `reopen` | **no, and no follow-up** | Records survive `reopen` by design (§6.4) and clearing wouldn't fix this. When the old branch still exists, the skill's "stop and ask" is the right outcome: a human decides whether to delete or reuse a stale branch. |
| 3 | Trailer match | tolerate whitespace like `review.REOPENS` · exact | **tolerate whitespace** | Squash bodies edited in a web UI can carry trailing spaces or CRLF; one pattern for taskrail's own code. |

Diagnosis approved. The lane must remove its scratch repositories under a temporary directory
when it no longer needs them.
