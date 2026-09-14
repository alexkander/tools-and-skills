# caveman

Response compression for chat prose: terse fragment style, technical substance kept exact.
Vendored from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (MIT).

Self-contained: `SKILL.md` is the whole skill. No installer, hooks, statusline, CLI or proxy.

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
  sees or loads the skill. Per OpenCode 1.15.13's source, a human still invokes it as
  `/caveman`, because OpenCode offers every discovered skill as a command.

## Use

`/caveman [lite|full|ultra|wenyan-lite|wenyan-full|wenyan-ultra]`, `stop caveman` to turn it
off. The default here is `lite`, not upstream's `full`. It never activates on its own.

## What the local layer changes

`SKILL.md` is the upstream body reproduced verbatim between `BEGIN`/`END` markers, under a
"Local rules" section that overrides it. Those rules: human invocation only, `lite` by default,
chat prose only (never anything persisted), off inside a subagent whose output another agent
relays to a human, artifact language untouched, and nothing but this file vendored.

The rules are project-neutral. A project needing more — its own pipeline names, its own
governed documents — states that outside this directory, for example in its agent instructions
file, rather than editing this copy: an update replaces the whole directory.

## Portability

`user-invocable` and `disable-model-invocation` are Claude Code frontmatter keys; other agents
ignore them. That is why "never self-activate" is also written in the skill's prose, where
every agent reads it. On an agent that ignores the keys, the prose is the only enforcement.
On OpenCode, `permission.skill` can enforce it too (see *OpenCode*).

## Upstream

This directory itself is pinned to upstream commit `0574b85`, independently of the commit a
consumer copies it from. Re-syncing is a diff of the text between the `BEGIN`/`END` markers
against that path upstream; local rules live outside the markers and are unaffected.

Upstream is split-licensed — the skill is MIT, the engine and proxy are BSL-1.1. Only the MIT
skill text is used. Upstream's separate CLI sends anonymous telemetry by default; it is not
part of this skill.

## Known limitations

- **Enforcement is text only.** Nothing outside the model's compliance stops it applying to a
  file write. Human-only invocation reduces the exposure; it does not remove it.
- **Live behaviour is unvalidated.** Worth confirming in an interactive session that `/caveman
  lite` compresses without touching code or error strings, that `stop caveman` restores normal
  prose, and — the likeliest failure — that asking the agent to "be brief" does **not** activate
  it.
- **The saving is small.** Adopted for readability. Upstream itself notes output-only savings,
  a 1–1.5k input-token cost per turn, and that already-terse work can come out behind.
