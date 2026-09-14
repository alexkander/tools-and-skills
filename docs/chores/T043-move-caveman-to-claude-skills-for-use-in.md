# T043 — Move caveman to .claude/skills for use in this repository only

Kind: chore · Epic: E06 · Status: done

## Goal

caveman is in this repository so that agents use it **while working on this repository**. It is
not a shareable item for other projects to install from here. Today it lives only at
`skills/caveman/` (`README.md` and `SKILL.md`), and no agent loads it there: the project skill
location both Claude Code and OpenCode read is `.claude/skills/`, which today holds only
taskrail's installed skills, managed by `.taskrail/installed.json`.

Move it to `.claude/skills/caveman/`. Keep the upstream pin, the `BEGIN`/`END` markers, the
upstream licence text and the separation between local rules and the vendored text. Drop the
consumer install wording, and say that it is this repository's own agent configuration.

## Findings that shape the change set

### F1 — A README next to SKILL.md does not break discovery

Primary documentation:

- Claude Code, *Extend Claude with skills* (https://code.claude.com/docs/en/skills.md), read
  through a fetch: "Every skill needs a `SKILL.md` file with instructions. This is the only
  required file." and "Skills can include multiple files in their directory." Supporting files
  are loaded only when `SKILL.md` references them; caveman's `SKILL.md` does not reference its
  `README.md`, so the README is never loaded into context. Project location:
  `.claude/skills/<skill-name>/SKILL.md`, "Sessions in this repository".
- Agent Skills specification (https://agentskills.io/specification.md), *Directory structure*:
  "A skill is a directory containing, at minimum, a `SKILL.md` file", with
  "`└── ...  # Any additional files or directories`", and *Optional directories*: "A skill
  directory may contain any files and directories beyond the required `SKILL.md`."

Measured, in a throwaway repository with an isolated `HOME` (Claude Code 2.1.270, OpenCode
1.15.13), `skills/caveman/` copied as-is into `.claude/skills/caveman/`:

```text
$ ls -la .claude/skills/caveman
-rw-r--r-- 1 abigail abigail  2556 set 14 06:29 README.md
-rw-r--r-- 1 abigail abigail 14798 set 14 06:29 SKILL.md
$ HOME=/tmp/t043/home … claude plugin validate .claude/skills
Validating components in: /tmp/t043/repo/.claude/skills

✔ Validation passed
exit=0
$ HOME=/tmp/t043/home claude plugin validate --strict --json .claude/skills
{
  "success": true,
  "strict": true,
  "target": "/tmp/t043/repo/.claude/skills",
  "manifest": null,
  "contents": []
}
exit=0
$ HOME=/tmp/t043/home XDG_CONFIG_HOME=… XDG_DATA_HOME=… XDG_CACHE_HOME=… XDG_STATE_HOME=… opencode debug skill
[ { "name": "customize-opencode", "location": "<built-in>", … },
  { "name": "caveman", …, "location": "/tmp/t043/repo/.claude/skills/caveman/SKILL.md", "content": "\n## Local rules\n…" } ]
exit=0
```

OpenCode reports exactly one skill from the directory, read from `SKILL.md`; the README is not
surfaced as a skill. (The `opencode debug skill` output above is abridged to the names and
locations; the full run printed both skills' descriptions and bodies.)

How much `claude plugin validate` checks, as a control: it reads each `SKILL.md` (a skill with no
`description` gets a warning) but did **not** reject malformed YAML frontmatter:

```text
$ printf -- '---\nname: [unclosed\ndescription: x\n---\nbody\n' > .claude/skills/broken/SKILL.md
$ claude plugin validate .claude/skills
✔ Validation passed
exit=0
$ printf -- '---\nname: nodesc\n---\nbody\n' > .claude/skills/nodesc/SKILL.md   (broken/ removed)
$ claude plugin validate .claude/skills
Validating skill: /tmp/t043/neg/.claude/skills/nodesc/SKILL.md
⚠ Found 1 warning:
  ❯ description: No description in frontmatter. …
✔ Validation passed with warnings
exit=0
```

So a passing `validate` is weak evidence on its own; OpenCode's discovery output above is the
stronger proof that the frontmatter parses and the README is ignored.

### F2 — `taskrail upgrade` leaves an unmanaged `.claude/skills/caveman/` alone

From `tools/taskrail/src/taskrail/install.py`:

- `skill_files()` renders only the directories under the package's own `skills/`
  (`SKILLS_SOURCE`), so the installer only ever writes `taskrail*` paths.
- Removal walks `installer.files`, the paths recorded in `.taskrail/installed.json`, and only
  those whose skill is no longer wanted; caveman is never recorded there.
- `managed()` refuses to overwrite an existing file it did not write ("exists and was not written
  by taskrail; --force replaces it"), so even a future taskrail skill named `caveman` would be
  skipped rather than clobber it — except under `--force`.

Measured in a throwaway clone of this branch, after `git mv skills/caveman .claude/skills/caveman`
and a commit:

```text
$ sha256sum .claude/skills/caveman/*
8f9b735a8363ac43f02dfa25eb7bdffb9d15b0e6aea345c6020f85c50b8600e6  .claude/skills/caveman/README.md
dcbcb605d0b6df4726ad6bf210e7ffb176364a56d93dfb24a32bc0750e49f7bf  .claude/skills/caveman/SKILL.md
$ .taskrail/bin/taskrail upgrade --json
{
  "created": [],
  "updated": [],
  "unchanged": [
    ".taskrail/config.toml",
    "TODO.md",
    ".taskrail/bin/taskrail",
    ".claude/skills/taskrail/SKILL.md",
    ".claude/skills/taskrail-autopilot/SKILL.md",
    ".claude/skills/taskrail-autopilot/references/decision-record.md",
    ".claude/skills/taskrail-autopilot/references/gate-review.md",
    ".claude/skills/taskrail-autopilot/references/lane-brief.md",
    ".claude/skills/taskrail-bug/SKILL.md",
    ".claude/skills/taskrail-chore/SKILL.md",
    ".claude/skills/taskrail-feature/SKILL.md",
    ".claude/skills/taskrail-spike/SKILL.md"
  ],
  "skipped": [],
  "removed": [],
  "notes": []
}
exit=0
$ sha256sum .claude/skills/caveman/*
8f9b735a8363ac43f02dfa25eb7bdffb9d15b0e6aea345c6020f85c50b8600e6  .claude/skills/caveman/README.md
dcbcb605d0b6df4726ad6bf210e7ffb176364a56d93dfb24a32bc0750e49f7bf  .claude/skills/caveman/SKILL.md
$ git status --porcelain | wc -l
0
$ grep -c caveman .taskrail/installed.json
0
$ .taskrail/bin/taskrail upgrade --force --json   (summarised: unchanged counted)
{'created': [], 'updated': [], 'unchanged': 12, 'skipped': [], 'removed': [], 'notes': []}
exit=0
  (same two sha256 sums; git status --porcelain | wc -l → 0)
$ HOME=/tmp/t043/home claude plugin validate --strict .claude/skills
✔ Validation passed
exit=0
$ opencode debug skill   (names and locations only)
[('customize-opencode', '<built-in>'), ('taskrail-autopilot', '…/.claude/skills/taskrail-autopilot/SKILL.md'),
 ('taskrail-feature', …), ('taskrail-spike', …), ('taskrail-bug', …),
 ('caveman', '/tmp/t043/clone/.claude/skills/caveman/SKILL.md'), ('taskrail-chore', …), ('taskrail', …)]
```

### F3 — The empty `skills/` directory

git tracks no directories: after the move, `git ls-files skills` is empty, a fresh clone has no
`skills/`, and only the working tree keeps an empty directory (measured: `ls -la skills` → `total 0`).

### F4 — caveman's local rules still hold here

Every local rule applies unchanged to use inside this repository: human invocation only; `lite`
by default; chat prose only (this repository's artifacts under `docs/` are exactly what rule 3
protects); off in a relayed subagent (this repository runs taskrail autopilot lanes, the case
rule 4 was written for); artifact language untouched (matches CLAUDE.md's language policy);
nothing but the file vendored. The "project-neutral" wording in the rules' introduction ("A
consuming project that needs more … adds them alongside this file") is still true with this
repository as the project using it, and keeping `SKILL.md` byte-identical makes the move a pure
rename and leaves a future re-sync or re-extraction unaffected.

## Change set

1. **Move** — `git mv skills/caveman .claude/skills/caveman`, committed on its own so git records
   both files as pure renames (100% similarity). Then remove the empty `skills/` directory left
   in the working tree (`rmdir skills`; nothing tracked changes).
2. **`.claude/skills/caveman/SKILL.md`** — no change. Frontmatter (`metadata.source`,
   `upstream-pin: "0574b85"`, `license`), the "Local rules" section, the `BEGIN`/`END` markers
   and the "Upstream licence" section stay byte-identical. Its mentions of
   `skills/caveman/SKILL.md` name the **upstream** path and stay.
3. **`.claude/skills/caveman/README.md`** — stays next to `SKILL.md` (F1). Wording changes only:
   - Replace the `## Install` section ("Copy this directory into wherever the agent loads skills
     from — for Claude Code, `.claude/skills/caveman/`.") with a short statement under the intro:
     this directory is part of this repository's own agent configuration; agents working on this
     repository load it from `.claude/skills/caveman/` (Claude Code directly, OpenCode through
     its `.claude/skills` scan); it is not one of the repository's shareable items and is not
     meant to be installed elsewhere from here; `taskrail upgrade` does not manage or touch it.
   - In `## What the local layer changes`, replace "The rules are project-neutral. A project
     needing more — its own pipeline names, its own governed documents — states that alongside
     this file rather than editing the vendored text." with: the rules are project-neutral, and
     anything specific to this repository belongs in its agent instructions (`CLAUDE.md`), never
     in the vendored text.
   - Everything else stays: *Use*, *Portability*, *Upstream* (pin `0574b85`, re-sync by diffing
     the text between the markers, split licence, CLI telemetry note) and *Known limitations*
     (including "Live behaviour is unvalidated", which is still true now that T008 is discarded).
4. **`README.md` (root)** — docs stage:
   - *Layout*: after the code block, add one paragraph: `.claude/skills/` is not part of that
     layout; it is this repository's own agent configuration, loaded by the agents that work on
     it — the skills taskrail installs (sources in `tools/taskrail`) and a vendored copy of
     caveman — and nothing in it is distributed. The `skills/` line stays as the place for
     shareable skills (it matches CLAUDE.md's *Layout*, which this task does not edit).
   - *Third-party content*: "Some items are vendored from upstream projects. Those carry …" →
     "Some content is vendored from upstream projects, such as caveman under `.claude/skills/`.
     It carries its own licence and attribution inside its directory, pinned to a specific
     upstream commit." The licence sentence that follows is unchanged.
5. **This artifact and `docs/chores/README.md`** — the index row.

## Decisions needed

1. **README location.** Keep `README.md` inside `.claude/skills/caveman/` next to `SKILL.md`?
   *Recommended: yes* — both agents ignore it (F1), the Agent Skills specification allows any
   extra file, and the attribution, pin and known limitations stay with the vendored text.
   Alternatives: move it to `docs/` (splits the item's attribution from its text), or fold it
   into `SKILL.md` (adds ~600 input tokens to every activation for text only humans need).
2. **`SKILL.md` local rules.** Leave `SKILL.md` unchanged (F4)? *Recommended: yes.* Alternative:
   reword the introduction's "A consuming project" to "A project using it" — cosmetic, and it
   costs the pure-rename history.
3. **Empty `skills/`.** Leave it untracked and absent, with no placeholder? *Recommended: yes* —
   the root README and CLAUDE.md already document `skills/<name>/` as the shareable layout, and
   the directory reappears with the first shareable skill. Alternatives: `skills/.gitkeep`, or a
   stub `skills/README.md` (noise to maintain, and neither is an item).
4. **Root README wording** as in change set item 4? *Recommended: yes.* Alternative: drop
   `skills/` from the Layout block while it is empty — rejected because CLAUDE.md's *Layout* would
   then describe a directory the README omits.
5. **CLAUDE.md** (for the human; this task does not edit it). After the move:
   - *Layout* lists `skills/`, `tools/`, `libs/` and says nothing about `.claude/skills/`; only
     *Backlog* mentions `.claude/skills/taskrail*` as installed copies. *Recommended:* add one
     sentence to *Layout*: "`.claude/skills/` is not an item directory: it holds the skills
     agents use while working on this repository — taskrail's installed copies (see *Backlog*)
     and caveman, vendored under the rules below — and nothing there is distributed." Either the
     human edits it, or a follow-up chore in E06 does. Alternative: no change, relying on the
     root README and caveman's README.
   - *Distribution* (skills are installed by copying `skills/<name>/`, marketplace sources
     `./skills/<name>`) is a policy for future shareable skills and stays correct with `skills/`
     empty. *Recommended: no change.*
   - *Vendored third-party content* is written for "items"; its rules (pin, markers, licence,
     separate local overrides) still describe caveman. *Recommended: no change*; optionally the
     same *Layout* sentence covers it by saying caveman is vendored under those rules.
6. **Pull request title** at close (not needed now): *recommended*
   `chore(caveman): move caveman to .claude/skills for use in this repository only (T043)`.
   Alternative scope: `skills`.

## Out of scope

- Verifying caveman's live behaviour (discarded T008).
- Editing `CLAUDE.md` (decision 5 above).
- Historical records that mention `skills/caveman` as it was: the T009 spike, the T041 chore and
  their decision records under `docs/`. They document what was true then and stay unchanged.
- The E03 epic row, whose objective still speaks of consumer projects and whose tasks are all
  discarded, and the other backlog commits on this branch (E06, T044, discards).
- A plugin marketplace adapter, any change to taskrail, and T044 (RTK).

## Verification

Implement stage:

- `git show --stat -M HEAD~n` for the move commit: both files reported as renames with no
  content change; `diff <(git show origin/main:skills/caveman/SKILL.md) .claude/skills/caveman/SKILL.md`
  prints nothing (pin, markers and licence byte-identical).
- `git grep -n "skills/caveman" -- ':!docs'` shows only the new location and the upstream path
  inside `SKILL.md`; `git grep -n "Copy this directory"` prints nothing.
- In a throwaway clone of the branch, with an isolated `HOME`: `claude plugin validate --strict
  .claude/skills` passes, and `opencode debug skill` lists `caveman` at
  `.claude/skills/caveman/SKILL.md` alongside the seven taskrail skills.
- In the same clone: `.taskrail/bin/taskrail upgrade --json` reports nothing created, updated,
  skipped or removed; caveman's sha256 sums are unchanged; `git status --porcelain` is empty.
- Checks: `uv run --directory tools/taskrail pytest -q` (configured `test`; no code changes, run
  anyway); `lint` is not configured in `.taskrail/config.toml` and will be reported as such.
- `.taskrail/bin/taskrail validate`.

Docs stage: re-read the root README and caveman's README for any remaining consumer framing.

### Results

Scope approved with decisions 1–4 and 6 as recommended, 5b and 5c unchanged, and 5a — the
CLAUDE.md *Layout* sentence — added to this task
([decision record](../autopilot/decisions/T043-move-caveman-to-claude-skills-for-use-in.md)).

Commits: `a42d7da` (move), `6eee43f` (caveman README wording), and the root README commit.

```text
$ git show --stat -M --format='%h %s' a42d7da
a42d7da chore(caveman): move caveman to .claude/skills (T043)

 {skills => .claude/skills}/caveman/README.md | 0
 {skills => .claude/skills}/caveman/SKILL.md  | 0
 2 files changed, 0 insertions(+), 0 deletions(-)
$ diff <(git show origin/main:skills/caveman/SKILL.md) .claude/skills/caveman/SKILL.md
diff-exit=0
$ grep -n 'BEGIN vendored\|END vendored\|upstream-pin\|^## Upstream licence\|^## Local rules' .claude/skills/caveman/SKILL.md
9:  upstream-pin: "0574b85"
15:## Local rules
101:<!-- BEGIN vendored upstream text — JuliusBrussee/caveman @ 0574b85, skills/caveman/SKILL.md, body reproduced verbatim. Do not edit: local rules belong in "Local rules" above. -->
186:<!-- END vendored upstream text -->
190:## Upstream licence
$ git grep -n "skills/caveman" -- ':!docs'
.claude/skills/caveman/README.md:7:repository load it from `.claude/skills/caveman/` — Claude Code directly, OpenCode through its
.claude/skills/caveman/SKILL.md:8:  source: "https://github.com/JuliusBrussee/caveman/blob/0574b85/skills/caveman/SKILL.md"
.claude/skills/caveman/SKILL.md:101:<!-- BEGIN vendored upstream text — … skills/caveman/SKILL.md, … -->
.claude/skills/caveman/SKILL.md:194:`skills/caveman/SKILL.md`. Upstream is split-licensed: the skill is MIT, while the engine,
TODO.md:97:| ⬜ | T043 | … | … move skills/caveman to .claude/skills/caveman … |
$ git grep -n "Copy this directory"
docs/chores/T043-move-caveman-to-claude-skills-for-use-in.md:173:   … (this artifact quoting the removed text)
docs/chores/T043-move-caveman-to-claude-skills-for-use-in.md:252:   … (this artifact's verification plan)
$ git ls-files skills | wc -l
0
```

The remaining `skills/caveman` mentions are the upstream path inside `SKILL.md` and the task row;
"Copy this directory" survives only in this artifact's quotations.

Throwaway clone of the branch at `6eee43f`, isolated `HOME` and XDG directories:

```text
$ claude plugin validate --strict .claude/skills
Validating components in: /tmp/t043/verify/.claude/skills

✔ Validation passed
exit=0
$ opencode debug skill   (names and locations)
[('customize-opencode', '<built-in>'), ('caveman', '/tmp/t043/verify/.claude/skills/caveman/SKILL.md'),
 ('taskrail-autopilot', '/tmp/t043/verify/.claude/skills/taskrail-autopilot/SKILL.md'),
 ('taskrail-bug', '/tmp/t043/verify/.claude/skills/taskrail-bug/SKILL.md'),
 ('taskrail-spike', '/tmp/t043/verify/.claude/skills/taskrail-spike/SKILL.md'),
 ('taskrail-chore', '/tmp/t043/verify/.claude/skills/taskrail-chore/SKILL.md'),
 ('taskrail', '/tmp/t043/verify/.claude/skills/taskrail/SKILL.md'),
 ('taskrail-feature', '/tmp/t043/verify/.claude/skills/taskrail-feature/SKILL.md')]
exit=0
$ sha256sum .claude/skills/caveman/*
cd93ca097c106fff99cf17e7f7d59322388c48f794781d81fe640e3668737d2c  .claude/skills/caveman/README.md
dcbcb605d0b6df4726ad6bf210e7ffb176364a56d93dfb24a32bc0750e49f7bf  .claude/skills/caveman/SKILL.md
$ .taskrail/bin/taskrail upgrade --json
{"created": [], "updated": [], "unchanged": [".taskrail/config.toml", "TODO.md", ".taskrail/bin/taskrail",
 ".claude/skills/taskrail/SKILL.md", ".claude/skills/taskrail-autopilot/SKILL.md",
 ".claude/skills/taskrail-autopilot/references/decision-record.md",
 ".claude/skills/taskrail-autopilot/references/gate-review.md",
 ".claude/skills/taskrail-autopilot/references/lane-brief.md", ".claude/skills/taskrail-bug/SKILL.md",
 ".claude/skills/taskrail-chore/SKILL.md", ".claude/skills/taskrail-feature/SKILL.md",
 ".claude/skills/taskrail-spike/SKILL.md"], "skipped": [], "removed": [], "notes": []}
exit=0
$ sha256sum .claude/skills/caveman/*   → the same two sums
$ git status --porcelain | wc -l
0
```

Checks: `uv run --directory tools/taskrail pytest -q` → `823 passed in 95.60s (0:01:35)`, exit 0.
`lint` is not configured in `.taskrail/config.toml`.

The CLAUDE.md *Layout* sentence (decision 5a) is not yet applied: the lane that implemented this
task did not edit CLAUDE.md on a relayed instruction. The sentence goes after the list of item
directories:

```diff
@@ -40,6 +40,10 @@ Grouped by artifact kind, one self-contained directory per item, each with its o
 - `libs/<lib-name>/` — libraries that are *imported*: versioned, with their own package
   manifest, meant to be depended on rather than copied.
 
+`.claude/skills/` is not an item directory: it holds the skills agents use while working on this
+repository — taskrail's installed copies (see *Backlog*) and caveman, vendored under the rules
+below — and nothing there is distributed.
+
 The tools/libs split is about how a consumer uses the thing, not how big it is: a tool is run,
 a library is linked against. A library needs a version and a changelog; a tool usually does not.
```

## CLAUDE.md sentence

The lane did not edit CLAUDE.md on a relayed instruction and left a checked patch instead. The human
had decided the sentence directly with the orchestrator (decision 5a), so the orchestrator applied
that patch unchanged as `docs(repo): note what .claude/skills holds in CLAUDE.md (T043)`: four added
lines in *Layout*, after the list of item directories, and nothing else in CLAUDE.md.
