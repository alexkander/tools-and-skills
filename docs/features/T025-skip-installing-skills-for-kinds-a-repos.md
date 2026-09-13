# T025 — Skip installing skills for kinds a repository does not allow

Kind: feature · Epic: E05 · Status: planned

## Behaviour

T018 added `[kinds].allowed`, but `taskrail init` and `taskrail upgrade` still install every
skill shipped under `src/taskrail/skills/`. A repository allowing only `bug` and `chore` is
therefore still offered `taskrail-feature` and `taskrail-spike`, and its agent may pick them up
for work the repository does not accept.

Afterwards, installation installs the executor skills the repository's kinds actually use:

- **Which skills are executor skills.** A shipped skill is an *executor skill* when a core kind
  descriptor names it, in its `skill` field or in a `[[route]]`'s `skill`. The mapping comes
  from the descriptors, never from the directory name. Today that is `taskrail-bug`,
  `taskrail-chore`, `taskrail-feature` and `taskrail-spike`.
- **Which executor skills install.** An executor skill installs when a kind in the repository's
  resolved set — core, local and overrides, after `[kinds].allowed` is applied, exactly what
  `load_kinds` returns — names it in `skill` or a route. So a local `research` kind that routes
  to `taskrail-spike` installs `taskrail-spike` even when `spike` itself is not allowed.
- **Everything else always installs.** The core `taskrail` skill, and any future shipped skill
  that no core kind names, installs whatever the kinds are.
- **Skills taskrail does not ship.** A local kind naming a skill taskrail does not ship (such as
  a Spec Kit pipeline skill) is ignored by installation, as today: nothing is written and
  nothing is reported.
- **Changing `allowed`.** On the next `init` or `upgrade`, a skill that is no longer wanted is
  removed through the existing manifest rule (`Installer.remove_managed`): an unedited copy is
  deleted with its directory and listed under `removed`, and the report asks for an agent
  restart; a locally edited copy is left in place, listed under `skipped` ("no longer installed
  here, but edited locally; left in place") and stays tracked in the manifest; `--force`
  deletes it. Widening `allowed` again reinstalls the skill.
- **Report.** When executor skills are left out, the report carries one note naming them, for
  example `not installing skills for kinds outside kinds.allowed: taskrail-feature,
  taskrail-spike`, so the absence is explained rather than silent.
- **First `init`.** `init` seeds `.taskrail/config.toml` before reading it, and the seeded config
  has no `[kinds]` table, so a first `init` installs every skill, as today. A repository that
  already has a config with `[kinds]` gets the filtered set on its first `init`.
- **Invalid configuration.** A `config.toml` that fails to load already stops `init` and
  `upgrade`; that does not change. Kind *validation issues* (for example `kind-allowed-unknown`)
  do not stop installation; the resolved set is used as it is, and `validate` reports them.

Without `[kinds]` and without an override that changes a core kind's `skill`, the installed
files are exactly as today.

## Acceptance criteria

1. Without `[kinds]`, `init --integration claude` installs all five skills (`taskrail`,
   `taskrail-bug`, `taskrail-chore`, `taskrail-feature`, `taskrail-spike`), and a second run
   reports nothing created, updated, removed or skipped, and no "not installing" note.
2. With `allowed = ["bug", "chore"]` in an existing config, `init --integration claude` installs
   exactly `taskrail`, `taskrail-bug` and `taskrail-chore`; the same holds under
   `.opencode/skills` for `--integration opencode`. The report has a note naming
   `taskrail-feature` and `taskrail-spike`. A second run changes nothing.
3. In a repository installed with every skill, setting `allowed = ["bug", "chore"]` and running
   `upgrade` deletes `taskrail-feature/SKILL.md` and `taskrail-spike/SKILL.md` and their
   directories, lists both under `removed`, drops them from `.taskrail/installed.json`, and adds
   the restart note.
4. If `taskrail-feature/SKILL.md` was edited locally before that `upgrade`, it stays on disk,
   appears under `skipped` with the "edited locally; left in place" reason and remains in the
   manifest; `upgrade --force` then deletes it.
5. Removing `[kinds]` again and running `upgrade` reinstalls the removed skills under `created`.
6. A local kind in `.taskrail/types/` whose `skill` — or one of whose routes — names
   `taskrail-spike`, allowed alongside `bug`, makes `taskrail-spike` install although `spike` is
   not allowed.
7. The core `taskrail` skill installs even when `allowed` names only a local kind whose skill
   taskrail does not ship; that unshipped skill name produces no file and no error.
8. An override of an allowed core kind that replaces its `skill` with a skill taskrail does not
   ship stops that core kind's executor skill from installing (for example `bug` overridden to
   `skill = "my-bug"` no longer installs `taskrail-bug`). *(Depends on decision 1 at the plan
   gate.)*
9. A config whose `allowed` names a kind no layer defines (`kind-allowed-unknown`) does not stop
   `init`/`upgrade`: installation proceeds with the resolved set.

## Affected areas

- `tools/taskrail/src/taskrail/install.py` — `skill_files()` gains a parameter for the skills to
  leave out (or to keep); `install()` computes it from the loaded config's resolved kinds and
  adds the report note. The existing removal loop already handles skills that stop being wanted.
- `tools/taskrail/src/taskrail/kinds.py` — possibly a small read-only helper returning the skill
  names a set of kinds uses (`skill` plus route skills), shared by the core-executor and
  resolved-kind computations. No change to `load_kinds`.
- `tools/taskrail/tests/test_install.py` — tests for the criteria. `cli.py` is not changed.
- `tools/taskrail/DESIGN.md` (§5.2 resolution, §9 distribution), `tools/taskrail/README.md`
  (Task kinds) and one bullet under `## Unreleased` in `tools/taskrail/CHANGELOG.md`.

## Out of scope

- Installing skills that local kinds name but taskrail does not ship; a repository provides those
  itself.
- An `init` option to set `[kinds].allowed` or to choose skills directly, and adding a commented
  `[kinds]` example to the seeded config.
- Filtering skills per backlog; `[kinds]` applies to the whole repository.
- Changing how the core `taskrail` skill describes kinds, or rewriting executor skills to mention
  the allowlist.
- Removing unmanaged skill directories that taskrail did not write.

## Open questions and risks

- **Decision 1 — filter whenever, or only with `allowed`.** The plan applies one rule at all
  times: an executor skill installs when a resolved kind names it. The side effect is criterion
  8: an override that points a core kind at a different skill stops installing the core skill,
  even without `[kinds]`. The alternative applies the filter only when `[kinds].allowed` is set
  and keeps "install every executor skill" otherwise, so nothing at all changes for repositories
  without the table.
- **Decision 2 — the report note.** The plan adds a note naming the executor skills left out, on
  every run where some are. The alternative is no note, relying on README and DESIGN.
- **A typo in `allowed`.** `allowed = ["bgu", "chore"]` resolves only `chore`, so `upgrade`
  removes `taskrail-bug` (unless edited) while `validate` reports `kind-allowed-unknown`. Fixing
  the typo and re-running `upgrade` restores it. The alternative — install every skill whenever
  kind resolution reports an error — is safer against typos but lets a broken config silently
  keep disallowed skills; the plan does not take it.
- **Skill named by a disallowed kind and an allowed one.** A skill installs if any resolved kind
  names it, so sharing a skill across kinds is safe.
