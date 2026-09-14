# T042 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## scope gate

Reviewed: the scope in `docs/chores/T042-document-install-update-and-removal-in-e.md` (commit
`0beeb16`), the public URL check, and the OpenCode source reading at `v1.15.13`: the two variables
that disable `.claude/skills/`, `skills.paths` resolved from the working directory, and a `deny`
skill permission that hides a skill from the model while a person can still run its slash command.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Where the steps live | each skill README · repository README with links · both | **each skill README** | CLAUDE.md requires self-contained items, and the README travels with the consumer's copy. |
| 2 | Root README tagline and "Using an item" pointer | include · follow-up | **include** | The current tagline contradicts the copy decision; the pointer has no commands to drift. |
| 3 | The "alongside this file" phrase in caveman's local rules | change · leave | **change** | It tells an agent to put project rules inside the directory an update replaces; the edit stays outside the vendored block. |
| 4 | Fetch commands | sparse blobless clone at the SHA, `rm -rf` before `cp -R` · `fetch --depth 1` by SHA | **sparse clone** | The trialled path, and it does not depend on the host allowing fetch by SHA. |
| 5 | Pin record | `Skill-Repository`, `Skill-Path`, `Skill-Commit` trailers · free-form `Upstream:` line | **trailers** | Readable back with git, matches CLAUDE.md's "URL, path and full commit SHA in the commit", and avoids reusing "Upstream", which already names caveman's origin. |
| 6 | OpenCode permission | `deny` · `ask` | **`deny`** | Keeps caveman from activating itself while a person can still invoke it. |
| 7 | Pull request title | `docs(skills)` · `docs(caveman)` | **`docs(skills)`** | The change includes the root README. |
| 8 | Rule for future skills | no task now · follow-up chore | **no task now** | That rule belongs in CLAUDE.md's Layout, which changes only with the human; raise it when a second skill arrives. |

Change set approved. In verification, isolate agents as in T009 and compare the digests of the real
agent settings before and after.

## implement gate

Reviewed: commits `2334de2` (caveman README Install/Update/Remove/OpenCode sections and wording
fixes, the local-rules phrase in `SKILL.md` outside the vendored block, the root README tagline and
"Using an item") and `b0656c6` (verification). The README's own `sh` blocks ran against the public
URL: install with the three trailers read back, update over a committed local edit showing the edit
removed in the staged diff, and removal. OpenCode discovery was measured with and without the two
variables and `skills.paths`, and a `deny` permission refused loading the skill. The digests of the
human's agent settings were identical before and after.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Approve `2334de2`, including the punctuation change | approve · changes | **approve** | Matches the approved change set and T041's CLAUDE.md wording. |
| 2 | "a person can still invoke `/caveman`" under `deny` | keep as is · qualify as read from the source | **qualify it** (for example "per OpenCode 1.15.13's source") | Only the model-side refusal was measured; public install docs should not state an unmeasured behaviour as fact. |
| 3 | Minimum git version | none · research and state one | **none** | Not established; git 2.55.0 is recorded in the task document. |
