# caveman

Response compression for chat prose: terse fragment style, technical substance kept exact.
Vendored from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (MIT).

Self-contained: `SKILL.md` is the whole skill. No installer, hooks, statusline, CLI or proxy.

## Install

Copy this directory into wherever the agent loads skills from — for Claude Code,
`.claude/skills/caveman/`.

## Use

`/caveman [lite|full|ultra|wenyan-lite|wenyan-full|wenyan-ultra]`, `stop caveman` to turn it
off. The default here is `lite`, not upstream's `full`. It never activates on its own.

## What the local layer changes

`SKILL.md` is the upstream body reproduced verbatim between `BEGIN`/`END` markers, under a
"Local rules" section that overrides it. Those rules: human invocation only, `lite` by default,
chat prose only (never anything persisted), off inside a subagent whose output another agent
relays to a human, artifact language untouched, and nothing but this file vendored.

The rules are project-neutral. A project needing more — its own pipeline names, its own
governed documents — states that alongside this file rather than editing the vendored text.

## Portability

`user-invocable` and `disable-model-invocation` are Claude Code frontmatter keys; other agents
ignore them. That is why "never self-activate" is also written in the skill's prose, where
every agent reads it. On an agent that ignores the keys, the prose is the only enforcement.

## Upstream

Pinned to commit `0574b85`. Re-syncing is a diff of the text between the `BEGIN`/`END` markers
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
