# T042 — Document install, update and removal in each skill README

Kind: chore · Epic: E04 · Status: implemented

## Goal

T009 decided how consumer projects install this repository's skills, and the human accepted it
([spike](../spikes/T009-decide-how-consumer-projects-install-thi.md),
[decision record](../autopilot/decisions/T009-decide-how-consumer-projects-install-thi.md)):

- copy `skills/<name>/` into the consumer's `.claude/skills/<name>/` from a specific commit of
  this repository — the one project location both Claude Code and OpenCode discover;
- record the repository URL, the path and the full commit SHA in the commit that adds or updates
  the copy;
- update by re-copying at a newer commit and reviewing the diff; remove by deleting the directory;
- keep project-specific rules outside the copied directory.

Each skill README must let a consumer do exactly that, with commands they can paste, plus the two
OpenCode facts T009 measured or read: the Claude-compatible paths can be switched off by
environment variable, and OpenCode ignores `disable-model-invocation`, so caveman's
no-self-activation guarantee needs `permission.skill` there.

`skills/caveman/` is the only skill today, so "each skill README" is `skills/caveman/README.md`.

### What caveman's README says today

```markdown
## Install

Copy this directory into wherever the agent loads skills from — for Claude Code,
`.claude/skills/caveman/`.
```

It names only Claude Code's path, gives no commands, no pin, no update or removal, and no OpenCode
notes. Two other passages need to agree with the new steps:

- *What the local layer changes* ends: "A project needing more … states that alongside this file
  rather than editing the vendored text." A file placed *alongside* `SKILL.md` sits inside the
  copied directory, which an update replaces.
- *Portability* says that on an agent ignoring the Claude Code keys "the prose is the only
  enforcement", which is no longer the whole story on OpenCode.
- *Upstream* describes the pin to `JuliusBrussee/caveman` at `0574b85`. It is a different pin from
  the consumer's pin of this repository, and the README should not let the two be confused.

### Facts checked for this scope (beyond T009)

Read in OpenCode's source at tag `v1.15.13` (`385cb694419f98103af0e8fc6187ddcbcbb6eecb`), the
version T009 measured, via a sparse clone of https://github.com/anomalyco/opencode in `/tmp`:

- `packages/opencode/src/effect/runtime-flags.ts:30-31` — the Claude Code skills paths are gated by
  `broad: bool("OPENCODE_DISABLE_CLAUDE_CODE")` and `direct: bool("OPENCODE_DISABLE_CLAUDE_CODE_SKILLS")`.
- `packages/opencode/src/skill/index.ts:211-219` — `skills.paths` entries are scanned regardless of
  that flag; a relative entry resolves with `path.join(directory, expanded)`, i.e. from the
  directory OpenCode runs in, not from the git worktree root. `~/` is expanded.
- `packages/opencode/src/skill/index.ts:306-311` — `available(agent)` drops skills whose
  `permission.skill` evaluates to `deny`; `packages/opencode/src/tool/skill.ts` asks the `skill`
  permission with the skill name before loading it.
- `packages/opencode/src/command/index.ts:141-150` — every skill from `skill.all()` (unfiltered by
  permission) is also registered as a command named after the skill, `source: "skill"`, whose
  template is the skill's content. So with `"caveman": "deny"` the model cannot see or load
  caveman, while a human can still type `/caveman`. Read from source, not measured in a session.
- `packages/web/src/content/docs/skills.mdx` — `permission.skill` values: `allow` loads
  immediately, `deny` hides the skill and rejects access, `ask` prompts the user before loading.

This repository's public URL answers anonymously:

```text
$ GIT_TERMINAL_PROMPT=0 git ls-remote https://github.com/alexkander/tools-and-skills refs/heads/main
8eeb8dfad7a6a946c54016892d7d40e442e82a5f	refs/heads/main
```

Local tools for the verification: git 2.55.0, OpenCode 1.15.13, Claude Code at
`~/.local/bin/claude`; `/bin/sh` is bash, and neither `dash` nor `busybox` is installed.

## Change set

### 1. `skills/caveman/README.md`

Replace `## Install` with the four sections below, in this order, before `## Use`. Proposed text
(exact, subject to the decisions):

````markdown
## Install

Claude Code and OpenCode both discover skills in a project's `.claude/skills/<name>/`, so one
copy there serves both. Copy this directory from a specific commit of
[tools-and-skills](https://github.com/alexkander/tools-and-skills) and record that commit in the
commit that adds the copy. From the root of the consuming repository:

```sh
REPO=https://github.com/alexkander/tools-and-skills
SKILL=caveman
SHA=$(git ls-remote "$REPO" refs/heads/main | cut -f1)   # or any full commit SHA
TMP=$(mktemp -d)
git clone -q --filter=blob:none --no-checkout "$REPO" "$TMP"
git -C "$TMP" sparse-checkout set --no-cone "/skills/$SKILL/"
git -C "$TMP" checkout -q --detach "$SHA"
mkdir -p .claude/skills
rm -rf ".claude/skills/$SKILL"
cp -R "$TMP/skills/$SKILL" .claude/skills/
rm -rf "$TMP"
git add -A -- ".claude/skills/$SKILL"
git commit -m "Add the $SKILL skill" -m "Skill-Repository: $REPO
Skill-Path: skills/$SKILL
Skill-Commit: $SHA"
```

The three `Skill-*` lines are git trailers: keep them as the last paragraph of the message, under
whatever subject line the project's convention asks for. If the project squash-merges pull
requests, end the pull request description with them too, so they reach the merged commit. The
copy includes this README, so these steps travel with it.

## Update

Find the commit the copy came from:

```sh
git log -1 --grep='^Skill-Path: skills/caveman$' --format='%(trailers:key=Skill-Commit,valueonly)'
```

Run the install commands again with the newer `SHA`, and commit with a subject such as
`Update the caveman skill`, keeping the three trailers. Before committing, read
`git diff --staged -- .claude/skills/caveman`: it shows what changed upstream, and it also shows
as removed anything the project had changed inside the copy. Move such changes out of the copy
(see *What the local layer changes*) rather than committing them away.

## Remove

```sh
git rm -r -q .claude/skills/caveman
git commit -m "Remove the caveman skill"
```

Also remove the `caveman` entry from `permission.skill` in `opencode.json`, if the project added
one, and any project rule that mentions the skill.

## OpenCode

- **Discovery.** OpenCode skips `.claude/skills/` when `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` or
  `OPENCODE_DISABLE_CLAUDE_CODE` is set. In that case list the directory in `opencode.json` as
  `"skills": { "paths": [".claude/skills"] }`; a relative path resolves from the directory
  OpenCode runs in. `opencode debug skill` lists the skills it found.
- **Human invocation.** OpenCode ignores `user-invocable` and `disable-model-invocation`, so
  without configuration only the skill's prose keeps the model from activating it. Enforce it in
  `opencode.json` with `"permission": { "skill": { "caveman": "deny" } }`: the model no longer
  sees or loads the skill, and a human still invokes it as `/caveman`, because OpenCode offers
  every discovered skill as a command.
````

Other edits in the same file:

- **Intro, second line** — unchanged ("Self-contained: `SKILL.md` is the whole skill. …").
- **`## Use`** — unchanged; `/caveman` works on both agents.
- **`## What the local layer changes`, second paragraph** — "states that alongside this file
  rather than editing the vendored text" becomes "states that outside this directory — for
  example in its agent instructions file — rather than editing this copy: an update replaces the
  whole directory."
- **`## Portability`** — append one sentence: "On OpenCode, `permission.skill` can enforce it too
  (see *OpenCode*)."
- **`## Upstream`** — prefix the first sentence with "This directory itself is pinned to upstream
  commit `0574b85`, independently of the commit a consumer copies it from." (replacing "Pinned to
  commit `0574b85`.").

### 2. `skills/caveman/SKILL.md` — one phrase in *Local rules* (decision 3)

Lines 21-23, outside the `BEGIN`/`END` markers (a local addition, not vendored text):

- today: "A consuming project that needs more — its own pipeline names, its own governed documents
  — adds them alongside this file rather than editing the vendored text."
- proposed: "… adds them outside this skill's directory, such as in its own agent instructions,
  rather than editing this file."

No other change to `SKILL.md`: no install steps (they would cost tokens on every invocation and put
packaging inside the skill, which CLAUDE.md's *Agent portability* keeps out), no frontmatter
change (`user-invocable` and `disable-model-invocation` stay as Claude Code hints), and rule 1
already states the no-self-activation guarantee in prose, which is what every agent reads.
`permission.skill` is consumer configuration, so it belongs in the README, not in the skill.

### 3. `README.md` (repository root) — decision 2

- Tagline: "Reusable agent skills, tools and libraries, centralized so they can be shared across
  projects instead of being copied into each one." becomes "Reusable agent skills, tools and
  libraries, maintained in one place and shared across projects." Under the accepted decision
  consumers *do* copy, so the current wording contradicts the install steps.
- New section after `## Layout`:

  ```markdown
  ## Using an item

  Each item's README says how to install, update and remove it. Skills are copied into a
  project's `.claude/skills/<name>/` from a specific commit of this repository, with that commit
  recorded in the consumer's history.
  ```

  No commands here: they live in each item's README only.

### 4. Procedure files

- This artifact, and its row in `docs/chores/README.md`.
- `TODO.md` at close (`taskrail done`).

## Decisions needed

Approved as recommended at the scope gate; recorded in
[the decision record](../autopilot/decisions/T042-document-install-update-and-removal-in-e.md).

1. **Where the steps live.** Recommendation: **the full steps in each skill README**. CLAUDE.md
   requires every item to be self-contained ("a consumer takes one directory and it works"); the
   README is copied with the skill, so the consumer's copy carries its own update and removal
   steps. The cost is duplicated commands across future skill READMEs, which CLAUDE.md prefers to
   a cross-item dependency ("document the duplication"). Alternatives: steps in the repository
   README with each skill README linking to it (one place to maintain, but a consumer's copy then
   points out of itself, to a file that is not copied); or both (two copies to keep in sync).
2. **Root README.** Recommendation: **make the two small edits in change set 3** — the tagline
   contradicts copying, and a visitor landing on the repository finds no hint where install
   steps are. Alternative: leave the root README untouched (strictly the task title) and open a
   follow-up task for it.
3. **`SKILL.md` phrase.** Recommendation: **change "alongside this file" as in change set 2.**
   The task expected no prose change, and none is needed for installation itself; but this phrase
   tells an agent reading the skill to put project rules next to `SKILL.md`, inside the directory
   an update replaces. Such a file would not be lost silently — the update diff shows it removed
   — but the skill would be instructing the very placement its own README warns against.
   Alternative: leave `SKILL.md` unchanged and rely on the README.
4. **Fetch commands.** Recommendation: **the sparse, blobless clone T009 trialled** (O1 in its
   *How to reproduce*), with this repository's public HTTPS URL instead of `file://`, the pin taken
   from `refs/heads/main` unless the consumer names a commit, and `rm -rf` before `cp -R` so files
   dropped upstream disappear on update (the trial did the same). It downloads only
   `skills/<name>/`. Alternative: `git init` plus `git fetch --depth 1 "$REPO" "$SHA"` and
   `git checkout FETCH_HEAD -- "skills/$SKILL"` — fewer flags, but it needs the server to allow
   fetching an arbitrary SHA (GitHub does; not every host does) and downloads the whole commit's
   tree. Portability note: every line is POSIX shell except `mktemp -d`, which is not in POSIX but
   exists on Linux, macOS and the BSDs; the sparse-checkout flags need a reasonably recent git,
   which the verification records.
5. **How the pin is recorded.** Recommendation: **three git trailers, `Skill-Repository`,
   `Skill-Path`, `Skill-Commit`,** so `git log --format='%(trailers:…)'` can read them back and
   the update step can find the current pin. The `Skill-` prefix avoids confusion with caveman's
   own upstream pin. Alternative: the single free-form line T009 trialled,
   `Upstream: <url> skills/caveman @ <sha>` (readable, but not machine-readable, and "Upstream"
   already means `JuliusBrussee/caveman` in this README). The commit subject is left to the
   consumer's convention; the examples use plain imperative subjects.
6. **OpenCode permission value.** Recommendation: **`deny`**. Per the v1.15.13 source it removes
   caveman from the model's list and rejects a load, while `/caveman` stays available to a human,
   which is exactly rule 1. Alternative: `ask` — the model may still propose loading it and a
   human approves each time; weaker, and noisy. The claim that `/caveman` survives `deny` is read
   from source; see *Verification* for what can be measured without a session.
7. **Pull request title.** Recommendation: `docs(skills): document installing, updating and
   removing skills from their READMEs (T042)` — `docs` because only documentation changes,
   `skills` because it spans the skill and the root README's skills sentence, as T009 did.
   Alternative: `docs(caveman): …` if decision 2 drops the root README change.
8. **Future skills.** Nothing states that a new skill's README must carry these sections.
   Recommendation: **no new task now**; with one skill, caveman's README is the model, and the
   rule belongs in CLAUDE.md's *Layout*, which this task must not edit and T041 is editing in
   parallel. Alternative: open a follow-up chore "Require install, update and removal sections in
   every skill README" at the docs stage.

## Out of scope

- `CLAUDE.md` (T041 records the decision in *Distribution*, in parallel).
- A plugin marketplace or any other adapter (deferred at T009).
- Tools and libraries: `tools/taskrail` has its own installer and README.
- Replacing caveman copies in consumer projects (T010) and verifying caveman's live behaviour
  (T008).
- The vendored text between the `BEGIN`/`END` markers in `SKILL.md`, and the frontmatter.
- `.claude/skills/` in this repository (installed taskrail skills).
- A script or installer for the copy (T009's O5a, revisited only under its stated conditions).

## Verification

Every trial runs in `/tmp`, never in a real project, with agent homes isolated as in T009
(`HOME`/`CLAUDE_CONFIG_DIR` for Claude Code, `HOME`/`XDG_*_HOME` for OpenCode); MD5 digests of the
real `~/.claude/settings.json` and `~/.config/opencode/*` are compared before and after. No agent
session is started.

1. **Install, verbatim.** Extract the `sh` blocks from the edited README and run them with
   `sh -eu` in a fresh `git init` consumer against the public URL at `8eeb8df` (the current
   `origin/main`, which has caveman). Check: `diff -r` of the copy against `git archive 8eeb8df
   skills/caveman`; `git log -1 --format='%(trailers)'` shows the three trailers with the full SHA;
   the *Update* lookup command prints that SHA; `git status --short` is clean.
2. **Update over a local edit.** Commit an in-place edit to the copy, then re-run the install
   block with the new SHA pointing at this task's branch head through a `file://` clone of this
   worktree (the branch changes `SKILL.md` and `README.md`, so the diff is non-empty). Check
   `git diff --staged` shows the upstream changes and the local edit as removed; after committing,
   the lookup command prints the new SHA.
3. **Remove.** Run the *Remove* block; check `.claude/skills` is gone and the tree is clean.
4. **OpenCode, isolated.** `opencode debug skill` lists `caveman` from `.claude/skills/`; with
   `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` it does not; with that variable set and
   `"skills": {"paths": [".claude/skills"]}` in `opencode.json` it does again. With
   `"permission": {"skill": {"caveman": "deny"}}`, record whatever OpenCode's CLI exposes without
   a session (for example `opencode debug config` or an agent listing); what cannot be measured
   stays cited to the source lines above.
5. **Claude Code, isolated.** `claude plugin validate .claude/skills` on the installed copy.
6. **Portability.** Record `git --version` and whether the blocks ran under `sh -eu`; no `dash` is
   installed, so report bash-as-sh honestly rather than claiming a POSIX shell run.
7. **Publishing constraint.** `git diff origin/main` contains no URL other than this repository's
   public one, upstream caveman's and the OpenCode source already cited; no private names.
8. **Checks.** `test`: `uv run --directory tools/taskrail pytest -q` (nothing under `tools/`
   changes, run anyway). `lint`: not configured in this repository. `taskrail validate` reports 0
   errors.

### Results

Applied in `2334de2`: `README.md`, `skills/caveman/README.md` and `skills/caveman/SKILL.md`, as
approved. One deviation in punctuation only: in *What the local layer changes* the approved
"— for example in its agent instructions file —" became ", for example in its agent instructions
file," because the sentence already holds a pair of dashes.

Tools: git 2.55.0, OpenCode 1.15.13, Claude Code 2.1.270. Every trial ran under `/tmp/t042`, with
commits authored through `GIT_AUTHOR_*`/`GIT_COMMITTER_*` variables (no git configuration
written), and was removed afterwards together with `/tmp/t042-oc`.

**Isolation.** MD5 digests before and after all trials, identical:

```text
00727ef8abefed9be11fee6468d00b09  /home/…/.claude/settings.json
2687f204f925fff9c7629641902b0848  /home/…/.claude/plugins/known_marketplaces.json
1013d19ce8195663a389b6fc35418031  /home/…/.config/opencode/opencode.jsonc
61b57c05f50886da87c19601ad97c4a6  /home/…/.config/opencode/package.json
690960a5b0fb4c34e5378c12769e3a1c  /home/…/.config/opencode/package-lock.json
```

(`~/.claude/plugins/installed_plugins.json` does not exist, before or after.)

**1. Install, verbatim.** The three `sh` blocks were extracted from the committed README with
`awk` and run with `sh -eu` in a fresh consumer, against the public URL (the block pins
`refs/heads/main`, then `8eeb8df`):

```text
$ sh -eu blocks/1.sh
[master 50ea164] Add the caveman skill
 2 files changed, 279 insertions(+)
 create mode 100644 .claude/skills/caveman/README.md
 create mode 100644 .claude/skills/caveman/SKILL.md
exit=0
$ git log -1 --format='%(trailers)'
Skill-Repository: https://github.com/alexkander/tools-and-skills
Skill-Path: skills/caveman
Skill-Commit: 8eeb8dfad7a6a946c54016892d7d40e442e82a5f
$ sh -eu blocks/2.sh
8eeb8dfad7a6a946c54016892d7d40e442e82a5f
$ git status --short                                  (empty)
$ diff -r <git archive 8eeb8df skills/caveman> .claude/skills/caveman
identical
```

No `tmp.*` directory was left in `/tmp` by `mktemp -d`.

**2. Update over a local edit.** A committed in-place edit (`<!-- LOCAL OVERRIDE: consumer rule -->`
appended to the copy's `SKILL.md`), then block 1 again with only these lines changed, as the
*Update* section says (a `file://` clone of this repository, because the branch is not pushed):

```text
< REPO=https://github.com/alexkander/tools-and-skills
> REPO=file:///…/tools-and-skills
< SHA=$(git ls-remote "$REPO" refs/heads/main | cut -f1)   # or any full commit SHA
> SHA=2334de22015c51696537915fafff38ae88cdc106
< git commit -m "Add the $SKILL skill" -m "Skill-Repository: $REPO
> git commit -m "Update the $SKILL skill" -m "Skill-Repository: $REPO
```

Staged before committing (`warning: filtering not recognized by server, ignoring` is the local
transport, as in T009):

```text
$ git diff --staged --stat
 .claude/skills/caveman/README.md | 72 +++++++++++++++++++++++++++++++++++++---
 .claude/skills/caveman/SKILL.md  |  6 ++--
$ git diff --staged -- .claude/skills/caveman/SKILL.md
-needs more — its own pipeline names, its own governed documents — adds them alongside this
-file rather than editing the vendored text.
+needs more — its own pipeline names, its own governed documents — adds them outside this
+skill's directory, such as in its own agent instructions, rather than editing this file.
@@ -225,5 +225,3 @@
-
-<!-- LOCAL OVERRIDE: consumer rule -->
```

The upstream change and the removed local edit both show. After the commit:

```text
[master fff5595] Update the caveman skill
$ sh -eu blocks/2.sh
2334de22015c51696537915fafff38ae88cdc106
$ git status --short                                  (empty)
$ diff -r <git archive 2334de2 skills/caveman> .claude/skills/caveman   → identical
```

The lookup skipped the local-edit commit, which has no trailers. (A first attempt at the commit
failed with `SKILL: unbound variable` because the trial harness had split the block and dropped
its variable lines; re-run with them, it passed. The README block itself was not at fault.)

**3. Remove.**

```text
$ sh -eu blocks/3.sh
[master 95f5540] Remove the caveman skill
 2 files changed, 343 deletions(-)
exit=0
$ git status --short                                  (empty)
.claude gone
```

**4. OpenCode, isolated** (`HOME` and `XDG_{CONFIG,DATA,CACHE,STATE}_HOME` under `/tmp/t042/home-oc`).
A new consumer with the copy installed by block 1; `opencode debug skill` reduced to name and
location:

```text
A default                                      [('customize-opencode', '<built-in>'), ('caveman', '/tmp/t042/consumer-oc/.claude/skills/caveman/SKILL.md')]
B OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1        [('customize-opencode', '<built-in>')]
C OPENCODE_DISABLE_CLAUDE_CODE=1               [('customize-opencode', '<built-in>')]
D B + opencode.json {"skills":{"paths":[".claude/skills"]}}, from the repository root
                                               [('customize-opencode', '<built-in>'), ('caveman', '/tmp/t042/consumer-oc/.claude/skills/caveman/SKILL.md')]
E same as D, run from sub/                     [('customize-opencode', '<built-in>')]
F default, run from sub/                       [('customize-opencode', '<built-in>'), ('caveman', '/tmp/t042/consumer-oc/.claude/skills/caveman/SKILL.md')]
```

E confirms that a relative `skills.paths` entry resolves from the directory OpenCode runs in.

Permission, with `opencode.json` = `{ "permission": { "skill": { "caveman": "deny" } } }`:

```text
$ opencode debug config            → permission: {"skill": {"caveman": "deny"}}
$ opencode debug agent build       → { "permission": "skill", "pattern": "caveman", "action": "deny" }
$ opencode debug agent build --tool skill --params '{"name":"caveman"}'
exit=1
Error: Unexpected error, …
The user has specified a rule which prevents you from using this specific tool call. …
  {"permission":"skill","pattern":"caveman","action":"deny"} …
```

And with `opencode.json` = `{}`, the same tool call as the model would make:

```text
exit=0
"title": "Loaded skill: caveman"
```

So, measured: without `permission.skill`, OpenCode's model-side `skill` tool loads caveman despite
`disable-model-invocation: true`; with `deny` it is refused. Not measured, because it needs a
session or a server (not started): that `deny` also removes caveman from the model's
`<available_skills>` list (`skill/index.ts:306-311`) and that `/caveman` stays available as a
command (`command/index.ts:141-150`, commands built from the unfiltered `skill.all()`).
`opencode debug skill` still lists caveman under `deny`, as expected, since it prints `all()`.

**5. Claude Code, isolated** (`HOME`, `CLAUDE_CONFIG_DIR` under `/tmp/t042/home-cc`):

```text
$ claude plugin validate .claude/skills
Validating components in: /tmp/t042/consumer-oc/.claude/skills
✔ Validation passed
exit=0
```

**6. Portability.** `/bin/sh` is bash, which runs in POSIX mode when invoked as `sh`; no `dash` or
`busybox` is installed, so no run under a strictly POSIX shell was possible. `bash --posix -n` on
block 1 passes, and a grep for bash-only constructs (`[[`, `$((`, `local`, `function`, `source`,
`<<<`, `${var//}`, `pushd`, `echo -e`) in the three blocks finds none. The minimum git version for
`sparse-checkout set --no-cone` and `%(trailers:key=…,valueonly)` was not established; 2.55.0 works.

**7. Publishing constraint.** URLs added under `README.md` and `skills/`:

```text
$ git diff origin/main -- README.md skills | grep '^+' | grep -o -E '(https?|file)://[^ )`"]+' | sort -u
https://github.com/alexkander/tools-and-skills
```

**8. Checks.**

```text
$ uv run --directory tools/taskrail pytest -q
823 passed in 93.12s (0:01:33)
$ .taskrail/bin/taskrail validate
42 task(s) in 1 backlog(s): 0 error(s), 0 warning(s)
```

`lint`: not configured in this repository.
