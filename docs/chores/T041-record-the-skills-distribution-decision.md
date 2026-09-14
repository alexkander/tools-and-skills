# T041 — Record the skills distribution decision in CLAUDE.md

Kind: chore · Epic: E04 · Status: documented

## Goal

`CLAUDE.md` still says distribution is "Not yet decided". T009 decided how consumer projects
install this repository's skills, and the human accepted it at T009's decide gate
([spike](../spikes/T009-decide-how-consumer-projects-install-thi.md),
[decision record](../autopilot/decisions/T009-decide-how-consumer-projects-install-thi.md)):

- skills are installed by copying `skills/<name>/` into the consumer's `.claude/skills/<name>/`
  from a specific commit of this repository;
- the repository URL, path and full commit SHA are recorded in the consumer commit that adds or
  updates the copy;
- there is no plugin marketplace yet; if one is added later, it is an adapter at the repository
  root with one `strict: false` entry per skill whose source is `./skills/<name>`;
- tools and libraries remain undecided.

Record that decision in the *Distribution* section, so agents and contributors working in this
repository describe one install path, the same one T042 writes into the skill READMEs.

## Change set

One file: `CLAUDE.md`, section `## Distribution`. The section today is a single paragraph, which
is replaced whole. No other line of `CLAUDE.md` changes.

Current text (exact):

```markdown
## Distribution

Not yet decided — for now the repository is just the directory layout above, and consumers copy
from it. It will likely differ per kind: skills and tools can be installed or copied, while a
library is published to a package registry and depended on by version. A Claude Code plugin
marketplace (`.claude-plugin/marketplace.json`) is one option for the skills, but as an adapter
over the layout above, never as its canonical shape. Record each choice here once made.
```

Proposed text (exact):

```markdown
## Distribution

Decided per kind; record each choice here once made.

**Skills** are installed by copying: a consumer copies `skills/<name>/` into its project's
`.claude/skills/<name>/` — the one project location both Claude Code and OpenCode discover —
from a specific commit of this repository, and records the repository URL, path and full commit
SHA in the commit that adds or updates the copy. Updating is re-copying at a newer commit and
reviewing the diff; removing is deleting the directory. Project-specific rules stay outside the
copied directory. There is no plugin marketplace yet; if one is added, it is an adapter at the
repository root (`.claude-plugin/marketplace.json`) with one `strict: false` entry per skill
whose source is `./skills/<name>`, adding nothing inside the item and never becoming its
canonical shape. Evidence: [T009](docs/spikes/T009-decide-how-consumer-projects-install-thi.md).

**Tools and libraries** are not decided yet. Tools will likely be installed or copied like
skills, while a library is published to a package registry and depended on by version.
```

How the proposal maps to its sources:

- The *Skills* paragraph is the wording T009 proposed for this task, with two changes: "in the
  change that adds or updates the copy" becomes "in the commit …", matching the human's decision
  (the pin is recorded in the commit, not a lock file); and "never becoming its canonical shape"
  is added, carrying over the current text's rule that a marketplace is an adapter, never the
  canonical shape.
- The *Tools and libraries* paragraph keeps the current sentence about libraries and package
  registries, as T009 asked, and keeps tools as "likely installed or copied".
- The evidence link to the T009 spike is the one T009 asked to record. The path is relative to
  the repository root, where `CLAUDE.md` lives.
- The opening line keeps the current "Record each choice here once made".

Also, as the procedure requires:

- `docs/chores/README.md` — add the T041 row to the index.
- This artifact.

## Decisions needed

1. **Replacement wording.** Approve the proposed text above as written, or give changes.
2. **Pull request title type and scope.** Proposed: `docs(repo): record the skills distribution
   decision in CLAUDE.md (T041)`. `docs` because only documentation changes; `repo` because
   `CLAUDE.md` belongs to the repository itself, not to one of its items. The alternative is
   `docs(skills)`, which T009 used because its decision concerns `skills/`.
3. **Evidence link.** Proposed: keep it. `CLAUDE.md` does not link to any document elsewhere
   today; dropping the link would leave the decision without its evidence in this file.

## Decisions at the scope gate

Recorded in the
[decision record](../autopilot/decisions/T041-record-the-skills-distribution-decision.md):

- The proposed Distribution text is applied exactly as quoted, including the T009 evidence link.
- Pull request title: `docs(repo): record the skills distribution decision in CLAUDE.md (T041)`.

## Out of scope

- The rest of `CLAUDE.md`, including the intro's reminder to update the Distribution section
  "once a consumption mechanism is chosen" — still true, because tools and libraries are open.
- Skill READMEs and anything under `skills/` (T042, running in parallel).
- Building a plugin marketplace or any other adapter (deferred at T009).
- Deciding how tools or libraries are distributed.
- `.claude/skills/` and the taskrail sources — nothing about taskrail changes.

## Verification

- `git diff origin/main -- CLAUDE.md` shows only the lines of the `## Distribution` section's
  paragraph changing, and matches the approved text exactly.
- `git diff --stat origin/main` lists only `CLAUDE.md`, this artifact, `docs/chores/README.md`
  and, at close, `TODO.md`.
- The link resolves: `test -f docs/spikes/T009-decide-how-consumer-projects-install-thi.md`
  from the repository root.
- Consistency with T042: the paths, pin fields and marketplace shape match the T009 decision
  record, which T042 also follows.
- The stage's `test` check, `uv run --directory tools/taskrail pytest -q`, still passes (nothing
  under `tools/` changes). The `lint` check is not configured in this repository.
- `taskrail validate` reports 0 errors.

### Results

- The approved text was applied by a script that took the current and proposed blocks from this
  artifact and required the current block to occur exactly once in `CLAUDE.md`, so the result
  is the quoted text byte for byte.
- `git diff origin/main -- CLAUDE.md`: one hunk inside `## Distribution`, 14 lines added and 5
  removed (`git diff --numstat`); no other line of the file changes.
- `git diff --stat origin/main`: `CLAUDE.md`, this artifact, `docs/chores/README.md`, and the
  scope-gate decision record with its index row. `TODO.md` changes at close.
- `test -f docs/spikes/T009-decide-how-consumer-projects-install-thi.md` → `link-ok`.
- No new line in `CLAUDE.md` exceeds 96 characters; lines 3 and 47 already did on `origin/main`.
- Consistency with the T009 decision record: copy at a pinned commit into
  `.claude/skills/<name>/`; pin recorded in the commit; marketplace deferred, at the root with
  one `strict: false` entry per skill sourced from `./skills/<name>`. All three match.
- `uv run --directory tools/taskrail pytest -q` → 823 passed in 91.39s. `lint` is not configured.
- `.taskrail/bin/taskrail validate` → 42 task(s) in 1 backlog(s): 0 error(s), 0 warning(s).

## Docs

The change is itself the documentation. Nothing else describes distribution: a search of the
Markdown files outside T009's and this task's documents finds only `CLAUDE.md` and the E04 rows in
`TODO.md`. The root `README.md` has no install section, and per-skill install steps are T042. No
follow-up tasks were opened.
