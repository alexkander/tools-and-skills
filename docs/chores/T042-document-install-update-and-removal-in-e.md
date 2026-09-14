# T042 — Document install, update and removal in each skill README

Kind: chore · Epic: E04 · Status: scoped

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
