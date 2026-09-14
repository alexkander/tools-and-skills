# tools-and-skills

Reusable agent skills, tools and libraries, centralized so they can be shared across projects
instead of being copied into each one.

Nothing here is tied to a single agent. Claude Code is the first target, but items are written
so another agent can load them, and agent-specific packaging is kept out of the items
themselves.

## Layout

```
skills/   Agent skills (SKILL.md + any references or scripts they load)
tools/    Standalone scripts and utilities that are invoked
libs/     Libraries that are imported: versioned, with their own package manifest
```

Every item is one self-contained directory, grouped with everything it needs and depending on
nothing else in this repository. Taking one directory is enough to use it; siblings never have
to come along.

`.claude/skills/` is not part of that layout. It is this repository's own agent configuration,
loaded by the agents that work on it — the skills taskrail installs (sources in
`tools/taskrail`) and a vendored copy of caveman — and nothing in it is distributed.

## Third-party content

Some content is vendored from upstream projects, such as caveman under `.claude/skills/`. It
carries its own licence and attribution inside its directory, pinned to a specific upstream
commit. The MIT licence below covers the original work in this repository, not the vendored
parts.

## Licence

MIT — see [LICENSE](LICENSE).
