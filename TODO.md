# TODO

## Epics

| ID  | Epic | Objective | File |
|-----|------|-----------|------|
| E03 | caveman skill | A verified caveman skill that consumer projects take from here | —    |
| E04 | Distribution | Decide how consumers get skills and tools from this repository | —    |
| E06 | Repository tooling | Agent skills and tools this repository itself uses while it is worked on | —    |

## E03 — caveman skill

Done when: live behaviour is verified and no consumer keeps its own copy.

| ✓  | ID   | Kind    | Pts | Depends On | Title                          | Description                    |
|----|------|---------|-----|------------|--------------------------------|--------------------------------|
| ❌ | T008 | spike   | 1   | —          | Verify caveman's live behaviour, including that "be brief" does not activate it | Check lite compression, stop caveman, and no self-activation; review the ASD-STE100 register. |
| ❌ | T010 | chore   | 2   | T008, T009 | Replace vendored caveman copies in consumer projects with this one | Point each consumer at the central skill and delete its copy. |

## E04 — Distribution

Done when: the mechanism is documented in CLAUDE.md and used by one consumer.

| ✓  | ID   | Kind    | Pts | Depends On | Title                          | Description                    |
|----|------|---------|-----|------------|--------------------------------|--------------------------------|
| ✅ | T009 | spike   | 3   | —          | Decide how consumer projects install this repository's skills | Compare a plugin marketplace, installer commands and copying. |
| ❌ | T011 | spike   | 2   | —          | Re-evaluate RTK once its filter-wide exit-code guard lands | Reopen only when rtk-ai/rtk PR #3577 is merged and issue #3230 is closed. |
| ✅ | T041 | chore   | 1   | —          | Record the skills distribution decision in CLAUDE.md | Replace the first paragraph of Distribution with the copy-at-a-pinned-commit wording proposed in [T009](docs/spikes/T009-decide-how-consumer-projects-install-thi.md); tools and libraries stay undecided. |
| ❌ | T042 | chore   | 1   | —          | Document install, update and removal in each skill README | Start with caveman: copy into `.claude/skills/<name>/` at a commit, record repository URL, path and full SHA in that commit, and note `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` and `permission.skill` for OpenCode, per [T009](docs/spikes/T009-decide-how-consumer-projects-install-thi.md). |

## E06 — Repository tooling

Done when: caveman is usable here and the decision on RTK is recorded

| ✓  | ID   | Kind    | Pts | Depends On | Title                          | Description                    |
|----|------|---------|-----|------------|--------------------------------|--------------------------------|
| ✅ | T043 | chore   | 1   | —          | Move caveman to .claude/skills for use in this repository only | caveman is used here, not distributed: move skills/caveman to .claude/skills/caveman keeping its upstream pin, markers and licence, and drop the consumer install wording. |
| ✅ | T044 | spike   | 2   | —          | Evaluate using RTK in this repository | Decide whether agents working on this repository use RTK, not whether to distribute it; start once rtk-ai/rtk PR #3577 is merged and issue #3230 is closed. |
