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
