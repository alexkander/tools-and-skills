# T061 — Separate the documents the orchestrator reads first from the paths that escalate

Kind: feature · Epic: E02 · Status: plan

Source: question 3 of T060's scope gate
([decision record](../autopilot/decisions/T060-remove-design-md-and-claude-md-from-the.md)), which
follows the autopilot trial ([T033](../spikes/T033-trial-the-autopilot-on-a-real-backlog-wi.md)).
No prior work: `show` reported no artifact, branch or commit for T061.

## Premise, checked on the current mainline

`[autopilot].governing` has two roles today. `escalation.py` matches its entries against each
lane's `touched` files and `status` raises `governing` (§12.6); and the `taskrail-autopilot` skill
tells the orchestrator, under *Before the first dispatch*, to "Read the governing documents: the
`[autopilot].governing` paths", as does `references/gate-review.md` ("Answer from the
`[autopilot].governing` documents"). DESIGN.md §4 and §12.9 comment the key "read first to answer
gates". T060 emptied `governing` in this repository so that edits to `CLAUDE.md` and
`tools/taskrail/DESIGN.md` stop escalating, and kept the reading list only in a config comment and a
`CLAUDE.md` *Backlog* bullet, which the skill does not read. The premise holds.

## Behaviour

- **A new key, `[autopilot].read_first`**: a list of repository-relative paths — files, directories
  or shell-style globs — that the orchestrator reads first to answer gates. It never escalates.
  `governing` keeps only its escalation role.
- **Fallback.** When `read_first` is absent, it takes the `governing` entries, so a repository
  configured before this change keeps its reading list. An explicit `read_first = []` means none.
- **`autopilot status`** reports the list at the top level of its JSON as `read_first`, and the
  entries that match nothing in the checkout as `read_first_missing`. The text form starts with
  `read first: …` when the list is not empty, and adds `read first missing: …` when an entry
  matches nothing. `status` already runs before the first dispatch, so the orchestrator gets the
  list without parsing TOML.
- **The skill** keeps its prose term: *the governing documents* are the `read_first` documents,
  and *a governing path* is a `governing` entry — the words condition 1 and condition 3 of
  *Escalate* already use. *Before the first dispatch* runs `status` first and reads the documents
  `read_first` lists, and tells the human about any `read_first_missing` entry;
  `references/gate-review.md` names `read_first` instead of `governing`.
- **This repository** sets `read_first = ["CLAUDE.md", "tools/taskrail/DESIGN.md"]`, keeps
  `governing = []`, and its `CLAUDE.md` *Backlog* bullet names the key (exact text in the gate
  questions).

## Acceptance criteria

1. `load_config` reads `read_first` as a tuple of strings; a value that is not a list of non-empty
   strings fails with `autopilot.read_first must be a list of non-empty strings`.
2. With `read_first` absent, `AutopilotConfig.read_first` equals the configured `governing` entries
   (empty when neither is set); with `read_first = []` it is empty even when `governing` is set.
3. `autopilot status --json` has a top-level `read_first` with the configured entries in order and
   `read_first_missing` with the entries that match no file or directory under the root (a glob
   counts as present when it matches anything); both are lists, also when there are no runs.
4. The text form of `autopilot status` starts with `read first: <entries>` when `read_first` is not
   empty, prints `read first missing: <entries>` when some are missing, prints neither line when
   the list is empty, and still says `no autopilot runs` when there are none.
5. `governing` escalation is unchanged: a `read_first` entry a lane touches raises nothing (a
   `status` test with a touched `read_first` path and empty `governing`).
6. The `taskrail-autopilot` skill source says, in *Before the first dispatch*, that the governing
   documents are the `read_first` entries from `autopilot status` and names `read_first_missing`;
   `references/gate-review.md` names `read_first`, not `[autopilot].governing`, for the documents
   to answer from; the copies `init` installs carry the same text. Asserted in
   `test_autopilot_skill.py`; this repository's installed copies are refreshed with
   `taskrail upgrade`.
7. All tests pass: `uv run --directory tools/taskrail pytest -q`; `taskrail validate` reports no
   errors.

## Affected areas

- `tools/taskrail/src/taskrail/config.py`: the `read_first` field of `AutopilotConfig` and its
  reading and fallback in `_autopilot` (the tuple of list keys).
- `tools/taskrail/src/taskrail/autopilot/commands.py`: `cmd_status` adds `read_first` and
  `read_first_missing` to the report beside `fetched`, and `_status_text` prints the two lines.
  `status()` in `status.py` (T051's area) and `escalation.py` (T059's area) are not edited.
- `tools/taskrail/src/taskrail/skills/taskrail-autopilot/SKILL.md`: the two bullets of
  *Before the first dispatch* only. `references/gate-review.md`: the *Governing documents first*
  bullet of *Every gate* only. Installed copies under `.claude/skills/taskrail-autopilot/` and
  `.taskrail/installed.json` through `taskrail upgrade`.
- `tools/taskrail/DESIGN.md`: the `[autopilot]` sample in §4 and in §12.9 (one added line each,
  and the `governing` comment); the `autopilot status` row of the §12.1 command table (one added
  sentence on `read_first`); a *Read-first documents* bullet added before *Governing paths* in
  §12.6, and condition 3 there naming them.
- `.taskrail/config.toml`: the `[autopilot]` block's `read_first` line and comment.
- `CLAUDE.md`: the autopilot bullet of *Backlog*.
- Tests: `tests/test_autopilot.py` (configuration and `status`), `tests/test_autopilot_skill.py`.
- `tools/taskrail/CHANGELOG.md` (one bullet), `docs/features/README.md` (one row).

## Out of scope

- Any change to how `governing` entries match or escalate (`escalation.py`, T059).
- The *Resume a run* section T055 adds to the skill: its "Read the governing documents" stays
  correct under the prose term above, so it needs no edit here or there.
- Validating `read_first` entries in `taskrail validate`, or failing `status` on a missing one.
- Putting `read_first` in `autopilot start` or `next` output, or in the lane brief: lanes do not
  answer gates.

## Open questions and risks

- **Term.** Keeping *governing documents* for the read-first list in prose, while `governing` names
  the escalating key, could confuse; the skill and DESIGN.md define both terms in one sentence each.
- **Fallback with globs.** A repository that relies on the fallback may have glob `governing`
  entries such as `src/**/policy-*.py`; they become read-first entries too, which is what the
  skill did before this change.
- **Overlap with T059**, which may add `[autopilot]` configuration of its own in `config.py` and
  DESIGN.md §12.6/§12.9: the edits are separate lines, a known class at worst.
