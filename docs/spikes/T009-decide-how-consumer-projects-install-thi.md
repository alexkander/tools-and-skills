# T009 — Decide how consumer projects install this repository's skills

**Verdict: consumers copy `skills/<name>/` into their
project's `.claude/skills/<name>/` at a pinned commit of this repository, and record that commit
when they add or update the copy. It is the only mechanism measured to work for both Claude Code
and OpenCode from one committed copy. A Claude Code plugin marketplace stays an optional adapter,
not built now. If it is built later, it goes at the repository root with one `strict: false`
entry per skill whose source is `./skills/<name>`. Submodules and third-party installers are not
the documented path.**

**Decide gate:** the human accepted this recommendation. The human's decisions, recorded in the
[decision record](../autopilot/decisions/T009-decide-how-consumer-projects-install-thi.md):
- copy at a pinned commit;
- defer the marketplace;
- record the repository URL, path and full SHA in the commit that adds or updates the copy;
- follow-ups T041 and T042 only.

**Frame gate:** approved. The decisions are recorded in the
[decision record](../autopilot/decisions/T009-decide-how-consumer-projects-install-thi.md):
- both agents are in scope;
- `skills/` only;
- hands-on trials were isolated per agent;
- third-party installers were read, never run;
- mechanisms may be mixed by agent;
- the time box is 3 points.

## Question

How should a consumer project **get, pin, update, override and remove** a skill from
`skills/<name>/` in this repository, on each agent it uses (Claude Code first, OpenCode too)?
The canonical form must stay the agent-neutral `skills/<name>/SKILL.md` directory, and any
packaging for one agent must stay an adapter layer over it (CLAUDE.md, *Layout* and *Agent
portability*).

Sub-questions:
1. What "installed" means for each agent.
2. How the consumer pins a commit.
3. What an update costs.
4. Whether local overrides survive an update.
5. What removal leaves behind.

## Evidence

**Versions:**
- Claude Code 2.1.270
- OpenCode 1.15.13
- git 2.55.0
- Node 22.23.2 (the npm registry was not used)

**Trial fixture:** this repository at `9c87bc2`, with two throwaway commits in a `/tmp` clone:
- `t1` = `18c3da8` adds a trial `.claude-plugin/marketplace.json`;
- `t2` = `e9351a4` appends `<!-- TRIAL-MARKER v2 -->` to `skills/caveman/SKILL.md`, standing in
  for an upstream change.

Nothing from the fixture was committed here.

**Isolation:**
- Every Claude Code command ran with `HOME` and `CLAUDE_CONFIG_DIR` pointing at a throwaway
  directory.
- Every OpenCode command ran with `HOME` and `XDG_{CONFIG,DATA,CACHE,STATE}_HOME` pointing at
  another.
- MD5 digests of the real `~/.claude/settings.json`, `~/.claude/plugins/known_marketplaces.json`
  and the three files in `~/.config/opencode/` were identical before and after the trials.

**Sessions:** no agent session was started. Neither isolated home holds credentials, so the
approved "one short session per agent" could not run without copying credentials, which the
limits exclude. OpenCode has a listing command (`opencode debug skill`), so its discovery is
measured. Claude Code has no CLI that lists skills, so what a Claude Code session loads and how
it names a skill comes from its documentation. `claude plugin details` and
`claude plugin validate` are measured.

### Sources

All read on 2026-09-14. Quotations are short fragments.

| # | Source |
|---|---|
| S1 | Claude Code, Skills — https://code.claude.com/docs/en/skills.md |
| S2 | Claude Code, Create and distribute a plugin marketplace — https://code.claude.com/docs/en/plugin-marketplaces.md |
| S3 | Claude Code, Plugins reference — https://code.claude.com/docs/en/plugins-reference.md |
| S4 | Claude Code, Discover and install prebuilt plugins — https://code.claude.com/docs/en/discover-plugins.md |
| S5 | Claude Code, Settings reference — https://code.claude.com/docs/en/settings-reference.md |
| S6 | Claude Code, Environment variables — https://code.claude.com/docs/en/env-vars.md |
| S7 | OpenCode, Agent Skills — https://opencode.ai/docs/skills; source `packages/web/src/content/docs/skills.mdx` at https://github.com/anomalyco/opencode, branch `dev` at `228e909` |
| S8 | OpenCode source at tag `v1.15.13` (`385cb69`): `packages/opencode/src/skill/index.ts`, `skill/discovery.ts`, `config/skills.ts`, `cli/cmd/debug/skill.ts`, `effect/runtime-flags.ts` — https://github.com/anomalyco/opencode/tree/v1.15.13 |
| S9 | OpenCode, Plugins — `packages/web/src/content/docs/plugins.mdx` at `228e909` (same repository) |
| S10 | Agent Skills specification — https://agentskills.io/specification.md |
| S11 | `vercel-labs/skills` CLI at `d667282` (package version 1.5.26): `README.md`, `src/local-lock.ts`, `src/skill-lock.ts`, `src/update.ts`, `src/source-parser.ts`, `package.json` — https://github.com/vercel-labs/skills |

The trials only measured git's submodule behaviour; git's own documentation was not read for
this spike.

### E1 — What "installed" means in Claude Code

- **Locations** (S1, *Where skills live*):
  - enterprise;
  - personal `~/.claude/skills/<name>/SKILL.md`;
  - project `.claude/skills/<name>/SKILL.md`;
  - nested `<subdir>/.claude/skills/` (loaded once Claude works on files there);
  - `--add-dir`;
  - plugin `<plugin>/skills/<name>/SKILL.md`, "as `/plugin-name:skill-name`".

  `.agents/skills/` is not among them.
- **Symlinks** (S1): a project or personal skill entry "can be a symlink to a directory
  elsewhere on disk". `claude plugin validate` does not follow symlinks and warns (measured, E6).
- **No restart** for project and personal skills: S1, *Live change detection*, says a change is
  picked up "within the current session", unless the top-level skills directory is new.
  Plugin changes need `/reload-plugins` or a restart (S4). A shell `claude plugin install` or
  `update` prints "Restart to apply changes" (measured).
- **Removal** (S1): for a project skill, "delete the skill's directory". For a plugin skill,
  uninstall or disable the plugin.
- **Naming** (S1, command-name table):
  - a plugin skill is `/<plugin>:<name>`, and "the bare `/fancy` also invokes the skill unless
    another command already uses that name";
  - for a plugin whose root is a single `SKILL.md`, the frontmatter `name` gives the last
    segment (S3).

  So caveman packaged as a plugin keeps `/caveman`, as long as nothing else claims the name.
- **Invocation keys** (S3): plugin skills honour `disable-model-invocation`. Caveman's
  human-only rule therefore still holds as frontmatter under the plugin route.

### E2 — Claude Code plugins and marketplaces

- **Where the manifest lives** (S2): the marketplace file is `.claude-plugin/marketplace.json`,
  and relative sources resolve "relative to the marketplace root", meaning the directory that
  contains `.claude-plugin/`. Paths must not use `../`. A symlink that points outside the
  marketplace "is skipped for security" (S3). An adapter placed in a subdirectory could not
  reach `skills/` through relative paths; it would need `git-subdir` sources instead.
- **Entries without a plugin manifest** (S2, *Strict mode*): with `strict: false`, "the
  marketplace entry is the entire definition". No `plugin.json` is needed inside the item.
  A `source` of `"./"` combined with `"skills": ["./skills/code-review"]` limits an entry to
  the listed skills.
- **Pinning:**
  - "Git-based marketplace sources support `ref` (branch/tag) but not `sha`". Plugin sources
    inside a marketplace support both (S2).
  - Version resolution (S3): `plugin.json` `version`, then the marketplace entry's `version`,
    then "the git commit SHA of the plugin's source", which covers "relative-path sources in a
    git-hosted marketplace".
- **Team setup** (S4, S5): `.claude/settings.json` holds `extraKnownMarketplaces` and
  `enabledPlugins`. These are honoured "only after you accept the workspace trust dialog".
  Since v2.1.195, a plugin from an external source that only project settings enable "doesn't
  load until the team member installs it".
- **Updates** (S4): third-party marketplaces have auto-update "disabled by default". Updates
  run through `claude plugin marketplace update` and `claude plugin update`.
- **Cache and removal** (S3): installed plugins are copied to `~/.claude/plugins/cache`. After
  an update or uninstall, the old version directory is removed "roughly 14 days later". The
  sweep runs "only while at least one plugin is installed".
- **Security** (S4): plugins "can execute arbitrary code on your machine with your user
  privileges". A skills-only plugin carries no hooks or MCP servers, but nothing in the
  mechanism stops a later upstream commit from adding them.

### E3 — OpenCode skills and plugins

- **Locations** (S7), confirmed in the v1.15.13 source (S8, `skill/index.ts`):
  - `.opencode/skills/`, `~/.config/opencode/skills/`;
  - **`.claude/skills/`**, `~/.claude/skills/`;
  - `.agents/skills/`, `~/.agents/skills/`.

  Project paths are found by walking up from the working directory to the git worktree root.
  The Claude-compatible paths are skipped when `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` or
  `OPENCODE_DISABLE_CLAUDE_CODE` is set (S8, `runtime-flags.ts`).
- **Scanning** (S8): external directories are scanned with the pattern `skills/**/SKILL.md`,
  with symlinks followed (`symlink: true`). The pattern is recursive; Claude Code's documented
  project layout is one level deep.
- **Extra config** (S8, `config/skills.ts`): `skills.paths` adds any directory, scanned with
  `**/SKILL.md`. `skills.urls` pulls an `index.json` of skills over HTTP into the cache. The
  downloader returns early `if (yield* fs.exists(dest))`, so a file already cached is never
  fetched again, and there is no update path.
- **Frontmatter** (S7): only `name`, `description`, `license`, `compatibility` and `metadata`
  are recognised; "Unknown frontmatter fields are ignored". `disable-model-invocation` has no
  effect there. A consumer can gate a skill with `permission.skill` (`allow`/`ask`/`deny`) in
  `opencode.json` (S7).
- **Plugins** (S9): the OpenCode plugins page does not mention skills. No documented plugin
  route delivers skills.
- **Claude Code plugin installs are invisible to OpenCode** (measured, E6-O3).

### E4 — The shared format

The Agent Skills specification (S10) defines the skill directory, `SKILL.md`, and the
frontmatter `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`.
It says nothing about installation locations, distribution, versioning or updates. Nothing in the
standard settles this question: install locations are per-agent conventions, and
`.claude/skills/` is the one project path the two agents share (E1, E3).

### E5 — Third-party cross-agent installer: `vercel-labs/skills`

Read only, never run, as the human decided. Findings from S11:

- **Invocation:** `npx skills add <source>`. Sources include a GitHub tree URL to one skill
  directory. It targets Claude Code (`.claude/skills/`) and OpenCode; its README table lists
  OpenCode's project path as `.agents/skills/`.
- **Install method:** symlinks from each agent's directory to a canonical copy by default, or
  `--copy`.
- **Pinning:** the project lock `skills-lock.json` (`src/local-lock.ts`) records `source`,
  `ref` ("Branch or tag ref used for installation"), `skillPath` and a `computedHash` of the
  files. **No commit SHA is recorded.**
- **Update:** project `update` (`src/update.ts`) re-runs `add <source> --skill <name> -y` for
  every updatable skill ("Refreshing N skill(s)"). An in-place local edit is overwritten, and I
  found no step that detects one.
- **Telemetry:** on by default; `DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1` turns it off
  (README).
- **Licence:** MIT.
- **Cost of use:** it runs code from the npm registry on each consumer machine.
- **Compatibility:** this repository's layout needs no change for the tool to find
  `skills/caveman/SKILL.md`.

### E6 — Measured behaviour

#### O3 — Claude Code marketplace adapter

**Fixture:** trial `marketplace.json` with two entries, both `strict: false`:
- `caveman`: `source: "./"`, `skills: ["./skills/caveman"]`;
- `caveman-dir`: `source: "./skills/caveman"`.

**Failed first attempt:**

```
$ claude plugin marketplace add file:///tmp/t009/src#t1 --scope project
✘ Invalid marketplace source format. Try: owner/repo, https://..., or ./path
```

No server was started (lane rule), so the marketplace was added from a local checkout of `t1`,
and the update was measured by moving that checkout to `t2`. Ref pinning of a git-hosted
marketplace is documented (E2) but not measured.

**Validate:**

```
$ claude plugin validate /tmp/t009/src           → ✔ Validation passed with warnings (no marketplace description)
$ claude plugin validate /tmp/t009/src/skills    → ✔ Validation passed
```

**Add and install:**

```
$ claude plugin marketplace add /tmp/t009/mkt --scope project
✔ Successfully added marketplace: tas-trial (declared in project settings)
$ claude plugin install caveman@tas-trial --scope project --json      → "outcome":"ok"
$ claude plugin install caveman-dir@tas-trial --scope project --json  → "outcome":"ok"
```

The consumer's `.claude/settings.json` after both installs. This is the only thing committed in
the consumer:

```json
{
  "enabledPlugins": { "caveman@tas-trial": true, "caveman-dir@tas-trial": true },
  "extraKnownMarketplaces": { "tas-trial": { "source": { "source": "directory", "path": "/tmp/t009/mkt" } } }
}
```

**List, inventory and cache size:**

```
$ claude plugin list --json
  caveman-dir@tas-trial  version 18c3da894f1d  installPath …/.claude/plugins/cache/tas-trial/caveman-dir/18c3da894f1d
  caveman@tas-trial      version 18c3da894f1d  installPath …/.claude/plugins/cache/tas-trial/caveman/18c3da894f1d
$ claude plugin details caveman@tas-trial      → Skills (1)  caveman   Always-on: ~150 tok
$ claude plugin details caveman-dir@tas-trial  → Skills (1)  caveman   Always-on: ~151 tok
$ du -sh cache/tas-trial/*/*
1.9M  caveman/18c3da894f1d        ← source "./" copies the whole repository
20K   caveman-dir/18c3da894f1d    ← source "./skills/caveman" copies only the item
```

- **The version is the commit SHA**, as S3 says.
- **The exact version is recorded only in the user's `~/.claude/plugins/installed_plugins.json`,
  not in the consumer's repository.**
- The `source: "./"` cache copy includes this repository's `tools/taskrail` and its installed
  `.claude/skills/taskrail*` files. Only `skills/caveman` is exposed as a component.

**Update after moving the marketplace checkout to `t2`:**

```
$ claude plugin update caveman@tas-trial --scope project --json
  "Plugin \"caveman\" updated from 18c3da894f1d to e9351a47284e … Restart to apply changes."
$ claude plugin marketplace update tas-trial   → ✔ Successfully updated marketplace
$ claude plugin update caveman-dir@tas-trial --scope project --json  → updated 18c3da894f1d → e9351a47284e
$ git -C consumer-cc status --short   → ?? .claude/   (settings unchanged by the update)
```

**The update changed nothing in the consumer's repository.** Both cache versions stayed on
disk.

**Removal:**

```
$ claude plugin uninstall caveman@tas-trial --scope project --json     → "outcome":"ok"
$ claude plugin uninstall caveman-dir@tas-trial --scope project --json → "outcome":"ok"
$ claude plugin marketplace remove tas-trial   → ✔ Successfully removed marketplace
.claude/settings.json → { "enabledPlugins": {}, "extraKnownMarketplaces": {} }
cache/tas-trial/caveman/{18c3da894f1d,e9351a47284e} and caveman-dir/{…} still on disk
```

**OpenCode with a Claude Code plugin installed:** `caveman-dir` was reinstalled, and OpenCode
ran with `HOME` set to the Claude Code trial home:

```
$ opencode debug skill   → [('customize-opencode', '<built-in>')]
```

**The plugin's skill is not visible to OpenCode.**

#### O1 — Copy at a pinned commit

Consumer `consumer-oc`: a `.claude/skills/` copy serves both agents.

**Install at `t1`:**

```
$ git ls-remote file:///tmp/t009/src refs/tags/t1        → 18c3da894f1d3b1336070335f0a432d27d09e035
$ git clone -q --filter=blob:none --no-checkout file:///tmp/t009/src fetch
  warning: filtering not recognized by server, ignoring   (local transport; the filter is only an optimisation)
$ git -C fetch sparse-checkout set --no-cone /skills/caveman/ && git -C fetch checkout -q --detach <sha>
$ cp -R fetch/skills/caveman .claude/skills/caveman
$ git commit -m "chore(skills): vendor caveman" -m "Upstream: file:///tmp/t009/src skills/caveman @ <sha>"
$ opencode debug skill
  [('customize-opencode', '<built-in>'), ('caveman', '/tmp/t009/consumer-oc/.claude/skills/caveman/SKILL.md')]
$ claude plugin validate .claude/skills   → ✔ Validation passed
```

**Update to `t2` after an in-place local edit.** The local edit was committed first; then the
skill was re-copied at `t2`:

```
$ git diff
-<!-- LOCAL OVERRIDE: consumer rule -->
+<!-- TRIAL-MARKER v2 -->
$ git merge-file -p ours.md base.md theirs.md     (base = SKILL.md at t1)
+<<<<<<< ours.md
 <!-- LOCAL OVERRIDE: consumer rule -->
+=======
+<!-- TRIAL-MARKER v2 -->
+>>>>>>> theirs.md
```

**An in-place override is never lost silently.** Re-copying shows the loss in the diff, and a
three-way merge against the previous upstream brings it back as a conflict when it touches the
same lines. An override kept outside the copied directory is untouched by a re-copy by
construction.

**Removal:**

```
$ git rm -r .claude/skills/caveman && git commit      → working tree clean, .claude/skills gone
$ opencode debug skill   → [('customize-opencode', '<built-in>')]
```

#### O2 — git submodule plus a symlink

Consumer `consumer-sub`.

**Add at `t1` and link the skill:**

```
$ git submodule add file:///tmp/t009/src vendor/tools-and-skills   (checked out at t1)
$ ln -s ../../vendor/tools-and-skills/skills/caveman .claude/skills/caveman && git commit
$ opencode debug skill   → … ('caveman', '/tmp/t009/consumer-sub/.claude/skills/caveman/SKILL.md')
$ claude plugin validate .claude/skills
  ❯ directory: 1 entry here is a symlink and was not read — … A session loading this directory does follow them
  ✔ Validation passed with warnings
```

**Update to `t2`:**

```
$ git -C vendor/tools-and-skills checkout --detach t2; git diff --submodule=log
Submodule vendor/tools-and-skills 18c3da8..e9351a4:
  > trial: upstream change to caveman
```

**Fresh clones of the consumer:**

```
$ git clone --recurse-submodules …   → submodule at e9351a4, SKILL.md ends with the t2 marker
$ git clone …   (without --recurse-submodules)
  caveman -> ../../vendor/tools-and-skills/skills/caveman   → dangling symlink: skill missing
```

**OpenCode `skills.paths` instead of the symlink:**

```
$ opencode debug skill   → … ('caveman', '/tmp/t009/consumer-sub/vendor/tools-and-skills/skills/caveman/SKILL.md')
```

**Removal:**

```
$ git submodule deinit -f vendor/tools-and-skills; git rm -f vendor/tools-and-skills; rm .claude/skills/caveman; git commit
$ ls .git/modules/   → vendor      ← left behind
```

A submodule brings in the whole repository. That includes this repository's own installed
`.claude/skills/taskrail*`, which sit under `vendor/tools-and-skills/.claude/skills/`. Claude
Code documents loading a nested `.claude/skills/` once it works on files in that subdirectory
(S1). This is documented, not measured.

### E7 — git subtree

`git subtree` is available with git 2.55.0 but was not trialled within the time box. Like a
submodule, it brings in the whole repository unless a split branch is maintained. Unlike a
submodule, it gives no pin more precise than the merge commit that imported it. Neither
difference beats O1 for a single skill directory.

## Options considered

| Criterion | O1 copy at a pinned commit | O2 submodule + symlink | O3 Claude Code marketplace adapter | O4 OpenCode's own mechanisms | O5a own installer tool | O5b `vercel-labs/skills` |
|---|---|---|---|---|---|---|
| Both agents from one install | **Yes**: `.claude/skills/` is read by both (measured) | Yes via symlink (measured); OpenCode also via `skills.paths` | **No**: OpenCode does not see plugin skills (measured) | OpenCode only (`.opencode/`, `skills.paths`, `skills.urls`) | Yes, by design | Yes (documented; not run) |
| Nothing agent-specific inside `skills/<name>/` | Yes | Yes | Yes with `strict: false` entries at the repository root | Yes | Yes | Yes |
| Pin reviewable in the consumer's repository | Yes, if the commit is recorded (convention) | Yes, the gitlink | **No**: the exact SHA lives in `~/.claude/plugins/installed_plugins.json`; the repository holds at most a branch or tag `ref` | `skills.urls`: none | Yes, in its own lock | Branch or tag plus content hash; no SHA |
| Update cost | Re-copy and review the diff (measured) | Checkout and commit the gitlink; the log shows the range (measured) | One command, but no diff in the consumer (measured) | `skills.urls`: never refreshes cached files (source) | One command | One command; overwrites local edits (source) |
| Removal | Delete the directory; clean (measured) | deinit, rm, symlink; `.git/modules` left (measured) | uninstall and remove; cache versions left, swept ~14 days later only while a plugin is installed (measured + S3) | Delete the config entry | One command | One command |
| Local overrides | Outside the copy survive; in-place edits show in the diff (measured) | Cannot edit the submodule without forking | Cannot edit the cached copy; overrides live elsewhere | — | Depends on the design (taskrail detects local edits by digest) | In-place edits lost on update (source) |
| Trust and security | Reviewed text in the consumer's own diff | Upstream commits reach the consumer only when the gitlink moves | Workspace trust dialog; plugins "can execute arbitrary code"; auto-update off for third parties | `skills.urls` fetches over HTTP | Runs this repository's code | Runs npm code; telemetry on by default |
| Prerequisites | git | git; clones need `--recurse-submodules` or the skill is silently missing (measured) | Claude Code, plus an install step per machine for external sources (S4) | OpenCode | The tool's runtime | Node and npm |
| Maintenance here | None beyond each README's install section | None | One manifest entry per skill, kept in sync and validated | None | A new versioned tool | None |
| Frontmatter guarantees | As the agent reads them; OpenCode ignores `disable-model-invocation` (S7) | Same as O1 | Kept in Claude Code (S3) | Same as O1 | Same as O1 | Same as O1 |

## Recommendation

1. **Adopt O1 as the documented mechanism for skills.**
   - Copy `skills/<name>/` into the consumer's `.claude/skills/<name>/` from a specific commit of
     this repository, and record the repository URL, the path and the full commit SHA in the
     change that adds or updates the copy.
   - Update by re-copying at a newer commit and reviewing the diff, and remove by deleting the
     directory.
   - Keep project-specific rules outside the copied directory, as `skills/caveman/README.md`
     already asks. An in-place change still shows up as a diff or a merge conflict on update
     rather than being lost.
   - It is the only option measured to serve both agents from one committed copy with a
     reviewable pin. It adds no files or releases here, and it matches what T010 needs to
     migrate consumers' caveman copies.
2. **Do not build the Claude Code marketplace adapter now.** It serves one agent, keeps the pin
   outside the consumer's repository, and adds a manifest to maintain.
   - Build it when a consumer wants user-scope installs on Claude Code across many projects.
   - It then goes at the repository root with one `strict: false` entry per skill whose
     `source` is `./skills/<name>`. That form copies only the item (20K against 1.9M for
     `"./"`) and keeps `/caveman` working through the bare-name rule.
   - Validate it with `claude plugin validate .`.
3. **Do not document submodules, subtrees, OpenCode `skills.urls` or third-party installers.**
   - Submodules: silently missing skills in plain clones, the whole repository vendored, and
     leftovers after removal.
   - `skills.urls`: no update path.
   - `vercel-labs/skills`: no SHA pin, overwrites local edits, runs npm code with telemetry on.

   A consumer may still use these tools, since the layout needs no change for them.
4. **Revisit an installer tool (O5a) only under the conditions below.** taskrail's installer is
   the reference design: recorded digests and local-edit detection.

## What would change the decision

- **More copying:** a consumer maintains more than a handful of copied skills, or copies drift
  unnoticed. That points to a small standalone installer (O5a) that writes a lock with the SHA
  and detects local edits.
- **One agent only:** consumers standardise on Claude Code and want user-scope installs. That
  makes the O3 adapter worth its manifest.
- **Claude Code gains a commit pin:** consumer-side marketplace sources accept a `sha`, or
  settings record the installed commit. Either fixes O3's pin gap.
- **Discovery changes:**
  - OpenCode documents skill delivery through plugins, or stops reading `.claude/skills/`;
  - or Claude Code starts reading `.agents/skills/`, which would give a second shared location.
- **A skill ships scripts or hooks** that need a runtime installed. Copying then no longer
  suffices on its own.
- **`vercel-labs/skills` records a commit SHA** and preserves or detects local edits on update.

## Follow-up work

Created after the human accepted the decision. The marketplace task was not created, because the
human deferred the marketplace.

1. **T041, chore — Record the skills distribution decision in CLAUDE.md.** Replace the first paragraph
   of *Distribution* with wording such as:

   > Skills are installed by copying: a consumer copies `skills/<name>/` into its project's
   > `.claude/skills/<name>/` — the one project location both Claude Code and OpenCode discover —
   > from a specific commit of this repository, and records the repository URL, path and full
   > commit SHA in the change that adds or updates the copy. Updating is re-copying at a newer
   > commit and reviewing the diff; removing is deleting the directory. Project-specific rules
   > stay outside the copied directory. There is no plugin marketplace yet; if one is added, it is
   > an adapter at the repository root (`.claude-plugin/marketplace.json`) with one
   > `strict: false` entry per skill whose source is `./skills/<name>`, adding nothing inside the
   > item. Tools and libraries are not decided yet.

   Keep the sentence about libraries and registries, and record the evidence link to this
   document.
2. **T042, chore (no docs kind is allowed) — Document install, update and removal in each
   skill README**, starting with `skills/caveman/README.md` (today it names only Claude Code's
   path). Include:
   - how to record the commit;
   - the OpenCode notes on `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` and `permission.skill`.
3. **T010** (existing) uses the mechanism above. It needs no change.

## How to reproduce

Run from a shell with Claude Code 2.1.270, OpenCode 1.15.13 and git 2.55.0. None of it touches
the real agent configuration.

```bash
T=/tmp/t009; mkdir -p $T && cd $T
git clone -q <this repository> src && cd src && git checkout -q 9c87bc2 && git switch -q -c trial
mkdir -p .claude-plugin && cat > .claude-plugin/marketplace.json <<'EOF'
{ "name": "tas-trial", "owner": { "name": "trial" }, "plugins": [
  { "name": "caveman", "source": "./", "skills": ["./skills/caveman"], "strict": false },
  { "name": "caveman-dir", "source": "./skills/caveman", "strict": false } ] }
EOF
git add .claude-plugin && git commit -qm "trial: marketplace adapter" && git tag t1
printf '\n<!-- TRIAL-MARKER v2 -->\n' >> skills/caveman/SKILL.md && git commit -qam "trial: upstream change" && git tag t2
git worktree add -q --detach $T/mkt t1

# isolated agents
cc() { env HOME=$T/home-cc CLAUDE_CONFIG_DIR=$T/home-cc/.claude DISABLE_AUTOUPDATER=1 claude "$@"; }
oc() { H=${OC_HOME:-$T/home-oc}; env HOME=$H XDG_CONFIG_HOME=$H/.config XDG_DATA_HOME=$H/.local/share \
       XDG_CACHE_HOME=$H/.cache XDG_STATE_HOME=$H/.local/state OPENCODE_DISABLE_AUTOUPDATE=1 opencode "$@"; }

# O3: marketplace adapter
mkdir -p $T/consumer-cc && cd $T/consumer-cc && git init -q
cc plugin validate $T/src; cc plugin validate $T/src/skills
cc plugin marketplace add $T/mkt --scope project
cc plugin install caveman@tas-trial --scope project --json; cc plugin install caveman-dir@tas-trial --scope project --json
cat .claude/settings.json; cc plugin list --json; cc plugin details caveman-dir@tas-trial; du -sh $T/home-cc/.claude/plugins/cache/tas-trial/*/*
git -C $T/mkt checkout -q --detach t2; cc plugin update caveman@tas-trial --scope project --json
cc plugin marketplace update tas-trial; cc plugin update caveman-dir@tas-trial --scope project --json; git status --short
cc plugin uninstall caveman@tas-trial --scope project --json; cc plugin uninstall caveman-dir@tas-trial --scope project --json
cc plugin marketplace remove tas-trial; cat .claude/settings.json; find $T/home-cc/.claude/plugins/cache -maxdepth 3
cc plugin marketplace add $T/mkt --scope project; cc plugin install caveman-dir@tas-trial --scope project --json
OC_HOME=$T/home-cc oc debug skill

# O1: copy at a pinned commit
mkdir -p $T/consumer-oc && cd $T/consumer-oc && git init -q
SHA=$(git ls-remote file://$T/src refs/tags/t1 | cut -f1)
git clone -q --filter=blob:none --no-checkout file://$T/src $T/fetch
git -C $T/fetch sparse-checkout set --no-cone /skills/caveman/ && git -C $T/fetch checkout -q --detach $SHA
mkdir -p .claude/skills && cp -R $T/fetch/skills/caveman .claude/skills/ && git add -A && git commit -qm vendor -m "Upstream: skills/caveman @ $SHA"
oc debug skill; cc plugin validate .claude/skills
printf '\n<!-- LOCAL OVERRIDE: consumer rule -->\n' >> .claude/skills/caveman/SKILL.md && git commit -qam override
git -C $T/fetch checkout -q --detach t2 && rm -rf .claude/skills/caveman && cp -R $T/fetch/skills/caveman .claude/skills/ && git diff
git rm -qr .claude/skills/caveman && git commit -qm remove && oc debug skill

# O2: submodule plus symlink
mkdir -p $T/consumer-sub && cd $T/consumer-sub && git init -q && git commit -q --allow-empty -m init
git -c protocol.file.allow=always submodule add -q file://$T/src vendor/tools-and-skills
git -C vendor/tools-and-skills checkout -q --detach t1
mkdir -p .claude/skills && ln -s ../../vendor/tools-and-skills/skills/caveman .claude/skills/caveman && git add -A && git commit -qm add
oc debug skill; cc plugin validate .claude/skills
git -C vendor/tools-and-skills checkout -q --detach t2 && git diff --submodule=log && git commit -qam update
git -c protocol.file.allow=always clone -q file://$T/consumer-sub $T/c2 && test -e $T/c2/.claude/skills/caveman/SKILL.md || echo dangling
git submodule deinit -qf vendor/tools-and-skills && git rm -qf vendor/tools-and-skills && rm .claude/skills/caveman && git commit -qam remove && ls .git/modules

rm -rf $T   # clean up
```

Read the sources S1–S11 at the URLs and commits listed above. For the third-party installer,
read `src/local-lock.ts` and `src/update.ts` at `d667282`.

## Limits

- **Time box:** 3 points, spent within it. `git subtree` was reasoned about, not trialled.
- **Scope:** skills only; `tools/` and `libs/` are out.
- **Agents:** Claude Code 2.1.270 and OpenCode 1.15.13 only.
- **No sessions:** no agent session was run. Claude Code skill loading and naming in a session
  are from documentation (S1, S3).
- **Ref pinning** of a git-hosted marketplace (`owner/repo@tag`) is documented, not measured: the
  CLI refused a `file://` URL, and no git server was started.
- **Third-party installer:** read, not run, as the human decided.
- **Nothing else touched:** no consumer project, no other local repository, no publishing or
  pushing, and no change to CLAUDE.md, `skills/`, `tools/` or the installed skills. Trial
  directories under `/tmp` were removed after the run.
