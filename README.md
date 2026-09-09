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

## Third-party content

Some items are vendored from upstream projects. Those carry their own licence and attribution
inside their directory, pinned to a specific upstream commit. The MIT licence below covers the
original work in this repository, not the vendored parts.

## Licence

MIT — see [LICENSE](LICENSE).
