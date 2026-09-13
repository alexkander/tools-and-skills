# T029 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## plan gate

Reviewed: the plan in `docs/features/T029-add-the-autopilot-configuration-runs-and.md` (commit
`0726c56`), its fifteen acceptance criteria, against `tools/taskrail/DESIGN.md` §12.1, §12.2,
§12.4 and §12.9.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| Q1 | `[autopilot]` keys parsed now | every single-value key in §12.9 · only the keys T029 uses · also the group and resource tables | **every single-value key; tables stay with T030** | T030–T032 run in parallel, and a code conflict in `config.py` is outside the known classes; the tables need T020's column predicate. §4 says which keys take effect with which task. |
| Q2 | Run ID | `YYYYMMDD-N` · timestamp plus random suffix · clone-wide counter | **`YYYYMMDD-N`** (UTC date) | Short enough to type in `--run`; created exclusively, so two orchestrators starting together take the next free number instead of colliding. |
| Q3 | How `run` reaches the claim | `claim --run R` · `TASKRAIL_RUN` · `lane` writes it | **`claim <ID> --run R`, exit 3 for an unknown run; the remote copy carries `run`** | Explicit in the lane's brief and visible in its transcript; an environment variable leaks into unrelated claims. A run ID names no machine detail. |
| Q4 | Writing `handed-off` and run-level decisions | `lane --state handed-off` · new command · skill edits JSON | **`lane --state handed-off` (exit 5 unless `done-branch`, order kept); plus a minimal `autopilot decision --run R --question … --decision … --reason …` that appends to the run's `decisions`** | State files are written by the CLI only, never by hand; without a writer, the accepted "run-level decisions copied into each record" has nowhere to live. Update §12.1 for both. |
| Q5 | `--reason` | required for `failed` and `escalated` · required for all three · optional | **required for `failed` and `escalated`; optional for `gate`; cleared by `running`** | A failure or escalation without a reason cannot be acted on; a gate's reason is the lane's report. |
| Q6 | `--group` before groups exist | store as given · leave to T030 | **store as given** | §12.7 allows judgement-assigned groups with no configuration; T030 checks names against configured groups. |
| Q7 | Runs listed without `--run` | every run, newest first, `complete` flag · incomplete runs plus `--all` | **every run, newest first, with `complete`** | Follows §12.4; run files are small and local. Pruning waits for a real need. |
| Q8 | States outside the §12.1 list | `discarded` for ❌; stale claim stays `running` with the stale reason · omit discarded · stale as `pending` | **as recommended** | A discarded run task must stay visible to count against the target; a stale claim still blocks dispatch, so calling it `pending` would mislead. Add `discarded` to §12.1's list. |
| Q9 | `touched` | committed since the fork point plus uncommitted · committed only | **committed plus uncommitted; overlaps include backlog files and changelogs** | Lanes stop at gates with work in progress; the skill decides which overlaps are known conflict classes. |

Plan approved with the Q4 addition. The lane must remove its scratch repositories under a
temporary directory when it no longer needs them.
