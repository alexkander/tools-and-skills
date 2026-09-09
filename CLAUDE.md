# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **public** collection of reusable agent skills, tools and libraries, extracted from other
(often private) projects so they can be shared and reused across them. It is a library, not
an application: there is no single product to build or deploy. Each tool or skill is
self-contained and should be usable by copying or referencing it from another project.

The repository is MIT-licensed and public. **Update this file as it grows** — especially the
Commands section, once anything is buildable or testable, and the Distribution section once a
consumption mechanism is chosen.

## Language policy

- **Everything committed to the repository is in English** — code, identifiers, comments,
  documentation, skill descriptions, commit messages, PR titles and bodies, file names.
- **Conversation with the user mirrors the language they write in.** They may write in
  Spanish or English; answer in that same language. This never changes what goes in the files.

## Publishing constraint

Content arrives here by extraction from other projects, and this repository is public.
When importing anything, strip what does not belong in the open: internal hostnames, private
URLs and repo paths, client or employer names, ticket IDs, sample data derived from real
records, and any assumption about a private project's directory layout. Generalize a tool so
it stands on its own before committing it, rather than committing it and cleaning up later.

## Layout

Grouped by artifact kind, one self-contained directory per item, each with its own README:

- `skills/<skill-name>/` — an agent skill: `SKILL.md` with YAML frontmatter (`name`,
  `description`) plus any `references/` or scripts it loads. The `description` is what makes
  the skill discoverable, so it must state both what the skill does and when to invoke it.
- `tools/<tool-name>/` — standalone scripts or utilities that are *invoked*, each documenting
  its runtime, dependencies and invocation.
- `libs/<lib-name>/` — libraries that are *imported*: versioned, with their own package
  manifest, meant to be depended on rather than copied.

The tools/libs split is about how a consumer uses the thing, not how big it is: a tool is run,
a library is linked against. A library needs a version and a changelog; a tool usually does not.

Every item is one self-contained directory, grouped with everything it needs and depending on
nothing else here: a consumer takes one directory and it works, with no sibling coming along. If two items need shared code, that is a signal to document the
duplication rather than introduce a cross-dependency.

## Agent portability

Claude Code is the first target, not the only one. Each item's canonical form must not assume a
particular agent:

- **Keep agent-specific packaging out of the item itself.** Marketplace manifests,
  `plugin.json`, hook wiring and installers belong in a separate adapter layer, so the same
  skill or tool can be wired into a second agent without being rewritten.
- **`SKILL.md` plus YAML frontmatter is the portable core** — many agents read it. Claude-only
  frontmatter keys are ignored elsewhere, which is fine for hints but **not** for guarantees:
  a skill whose safe behaviour depends on `disable-model-invocation` or `user-invocable` is
  unsafe on an agent that ignores those keys. State such a rule in the skill's prose too, where
  every agent will read it.
- **Prefer plain contracts for tools** — arguments, stdin/stdout, exit codes — over
  agent-specific integrations, so any agent can call them through a shell.

## Vendored third-party content

Some items are copied from upstream projects rather than written here. For each one:

- Pin the exact upstream commit and record it in the item's frontmatter or README, and delimit
  the copied text with `BEGIN`/`END` markers so a re-sync is a cheap diff.
- Reproduce the upstream licence in full, and state plainly which parts are local additions.
- Keep local overrides **separate from the copied text**, and keep them free of any single
  project's specifics — a rule that names another repo's directories or pipelines is not
  reusable. Project-specific overrides belong in the consuming project.
- Check the upstream licence covers what is being taken: a project may licence its skill and
  its runtime differently.

## Distribution

Not yet decided — for now the repository is just the directory layout above, and consumers copy
from it. It will likely differ per kind: skills and tools can be installed or copied, while a
library is published to a package registry and depended on by version. A Claude Code plugin
marketplace (`.claude-plugin/marketplace.json`) is one option for the skills, but as an adapter
over the layout above, never as its canonical shape. Record each choice here once made.

## Commands

None yet — the repository has no build, lint, or test setup. Tools are expected to carry their
own (per-directory) instructions. Record any repository-wide command here once one exists.
