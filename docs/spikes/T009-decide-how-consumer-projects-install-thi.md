# T009 — Decide how consumer projects install this repository's skills

**Status: draft at the frame gate.** No verdict yet: this document holds the question, the
evidence that would answer it, the approach and the limits, for the human to agree on before
any investigation starts. No source listed below has been read yet.

## Question

How should a consumer project **get, pin, update, override and remove** a skill from
`skills/<name>/` in this repository, on each agent it uses — Claude Code first, OpenCode too —
while the canonical form stays the agent-neutral `skills/<name>/SKILL.md` directory and any
agent-specific packaging stays an adapter layer over it (CLAUDE.md, *Layout* and *Agent
portability*)?

It breaks down into five sub-questions:

1. **What "installed" means per agent.** Which paths and scopes (project, user, plugin) each
   agent discovers skills from, whether a skill must be restarted into a session, and how an
   installed skill is named and invoked (for example, whether packaging it as a plugin changes
   `/caveman` into a namespaced name).
2. **Pinning.** How a consumer fixes the exact commit or tag it uses, and how that pin is
   visible and reviewable in the consumer's own repository.
3. **Update.** What moving to a newer commit costs, what it shows the consumer before applying
   it, and whether anything updates without the consumer asking.
4. **Local overrides.** Where a consumer puts project-specific rules (CLAUDE.md, *Vendored
   third-party content*: "Project-specific overrides belong in the consuming project") and
   whether they survive an update.
5. **Removal.** Whether removing a skill leaves files, settings or caches behind.

The outcome is a recommended mechanism — possibly one per agent, over the same canonical
directory — with the conditions that would change it, for the human to decide and record in
CLAUDE.md's *Distribution* section as follow-up work.

## Options to compare

- **O1 — Copy (vendor) with a pinned commit.** The status quo that `skills/caveman/README.md`
  describes: copy the directory into the agent's skills path and record the commit it came
  from. Includes whether a documented one-line fetch (for example `git archive` of one path at
  a commit) makes it cheap and reproducible.
- **O2 — git submodule or git subtree.** The consumer tracks this repository (or one path of
  it) at a commit, and the agent's skills path points at it — directly, or through a symlink,
  whose handling by each agent is part of the evidence.
- **O3 — Claude Code plugin marketplace as an adapter.** A marketplace manifest in this
  repository whose entries point at the existing `skills/<name>/` directories without adding
  agent-specific files inside them; consumers add the marketplace and enable a plugin at
  project scope. To establish: whether an entry can reference a directory with no plugin
  manifest of its own, where the marketplace file must live, how a version or commit is
  pinned, update and auto-update behaviour, trust prompts, and the namespacing of skill names.
- **O4 — OpenCode's own mechanisms.** OpenCode's skill discovery paths, whether it reads Claude
  Code's paths or plugins, and whether its plugin system can deliver skills at all. This may
  turn out to be a variant of O1/O2 rather than an option of its own.
- **O5 — An installer command.** Either (a) a small standalone installer in this repository —
  a `tools/` item run by the consumer that copies a skill at a pinned commit into each agent's
  path and records what it wrote — or (b) an existing cross-agent skills installer, including
  `npx`-style tools, **only if** its own documentation or source repository establishes how it
  pins, updates and removes. taskrail's installer (`taskrail init`/`upgrade`, recorded digests,
  local-edit detection; `tools/taskrail/DESIGN.md` §9) is a reference for (a), not an option.

Options may combine: for example O3 for Claude Code users and O1 or O5 for every other agent,
all reading the same directory.

## Criteria

Each option is scored against the same list:

| Criterion | What is compared |
|---|---|
| Agent portability | Works for Claude Code and OpenCode without a second copy of the skill's text; adds nothing agent-specific inside `skills/<name>/` |
| Pinning | An exact commit or tag, recorded in the consumer's repository and reviewable in a diff |
| Update cost | Steps to move to a newer commit; whether the change is visible before it applies; no unrequested updates |
| Removal | Steps to remove; what is left behind (files, settings, caches) |
| Local overrides | Where project rules live and whether they survive an update untouched |
| Security and trust | Prompts shown, code that runs at install or at session start, what a compromised upstream could do |
| Consumer prerequisites | Tools each machine, CI runner or agent sandbox needs |
| Maintenance here | Files and release steps this repository takes on, and how they stay in sync with `skills/` |
| Guarantees | Whether frontmatter-only guarantees (such as `disable-model-invocation` on caveman) survive the packaging |

## Evidence

What would answer the question, each item with its source kind. Every source will be recorded
with its URL and the date it was read; quotations stay short.

- **E1 — Claude Code skills.** Discovery locations and scopes, restart behaviour, naming and
  invocation of project, user and plugin skills. Source: Claude Code's official documentation.
- **E2 — Claude Code plugins and marketplaces.** Marketplace manifest schema and location,
  plugin sources (git, subdirectory, a directory without a plugin manifest), version and ref
  pinning, project-scope enablement through committed settings, update and auto-update, trust
  prompts, removal and caches. Sources: official documentation and the CLI's own help for the
  installed version.
- **E3 — OpenCode skills and plugins.** Discovery paths, compatibility with `.claude/skills`,
  symlinks, and whether plugins can ship skills. Sources: OpenCode's official documentation and
  its source repository.
- **E4 — The SKILL.md format as a shared standard.** Whether a published specification defines
  the directory layout both agents read, and which frontmatter keys are portable. Source: the
  specification itself, if one exists.
- **E5 — Existing cross-agent installers.** For any candidate found: pinning, update, removal,
  where it writes, telemetry, licence. Sources: the tool's documentation and source repository
  only; a candidate with no primary documentation is dropped and named as dropped.
- **E6 — Behaviour, measured.** Each surviving option run end to end with `skills/caveman` in a
  throwaway repository: install at one commit, confirm each agent discovers the skill, apply a
  local override, update to a later commit, remove. Exact commands and output recorded.
- **E7 — git mechanics.** Submodule, subtree and single-path fetch behaviour for update and
  removal, from git's own documentation, measured in E6.

## Approach

1. Read the primary sources for E1–E5 and record each URL with its read date.
2. Build a local, unpublished test fixture under `/tmp`: a clone of this repository at this
   branch's base, plus — only for O3 — a marketplace manifest written in the clone as a
   throwaway, never committed here.
3. For each option that the documentation does not rule out, run the E6 sequence in a separate
   throwaway consumer repository under `/tmp`. Keep the agents' user configuration untouched:
   use an isolated configuration or home directory where the agent allows it, and fall back to
   documentation only (and say so) where it does not.
4. Confirm discovery with the least session use possible — CLI listing commands first, one
   short non-interactive session per agent only where no listing exists — and never with a
   flag that skips permission prompts.
5. Fill a comparison matrix of options against the criteria, then write the verdict, the
   options considered, the recommendation, what would change it and how to reproduce it.
6. Propose follow-up tasks for adopting the decision (recording it in CLAUDE.md's
   *Distribution* section, any adapter files, and T010's migration of consumer copies), without
   doing any of them here.

## Limits

- **Time box: 3 points**, the task's estimate.
- **Skills only.** `tools/` and `libs/` are out of scope: CLAUDE.md already expects a library
  to be depended on by version from a package registry, and taskrail already has its own
  installer. A skill that ships scripts is in scope as a skill.
- **Agents:** Claude Code (2.1.270 installed) and OpenCode (1.15.13 installed). Other agents are
  mentioned only where a primary source for an option names them; none is run.
- **No consumer project is touched**, and no other local repository is read; T010 does the
  migration after this decision.
- **Nothing is published or pushed:** no marketplace, no package, no tag, no branch push.
- **No production change:** no edit to CLAUDE.md, `skills/`, `tools/` or the taskrail skills.
  Throwaway manifests and scripts live under `/tmp` only.
- **No change to this machine's agent configuration** (user settings, installed plugins,
  marketplaces, caches); any run that would need one is replaced by documentation and noted.
- **Primary sources only**, as listed in *Evidence*; secondary write-ups and other projects'
  notes are not used.
