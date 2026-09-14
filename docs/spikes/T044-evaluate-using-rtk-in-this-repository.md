# T044 — Evaluate using RTK in this repository

**Verdict: agents working on this repository do not use RTK. That means no Claude Code hook, no
OpenCode plugin, and no RTK instructions. We re-evaluate when the triggers below are met.**

The reasons, all measured on RTK `v0.49.0`:

- **The hook breaks taskrail's `--json` output.** The hook rewrites
  `uv run … taskrail … --json` to `rtk uv run …`, the invocation this repository's CLAUDE.md
  documents. That form cut taskrail's JSON to its first and last 25 lines, which left it
  invalid. It also moved taskrail's error messages from stderr to stdout. The human's frame decision D3 makes either
  change disqualifying for a hook.
- **It hides text that procedures here read.**
  - `git log` dropped a `Reopens:` trailer.
  - `git diff` truncated additions.
  - `head -20` returned 10 lines.
  - The pytest filter reported "Pytest: 1 passed" for a run that exited 1.
- **What still held.** Exit codes were preserved in all 53 measured command pairs, and
  `.taskrail/bin/taskrail` itself is never rewritten.
- **Exclusions do not rescue the hook.**
  - They can only be set per user, in `~/.config/rtk/config.toml`, never per repository.
  - Excluding `uv` does not stop `uv run pytest` from becoming `uv run rtk pytest`.
  - Issue #3230 still routes `command git …` into RTK unless that git subcommand is also
    excluded.
  - The option is recorded below, but it is not recommended.

**Decide gate:** accepted by the human: no adoption of RTK. The two follow-ups, a CLAUDE.md note
and a test that `--json` output stays parseable through `uv run`, are done in this task. The
decisions are
in the [decision record](../autopilot/decisions/T044-evaluate-using-rtk-in-this-repository.md).

**Frame gate:** approved. The decisions are in the
[decision record](../autopilot/decisions/T044-evaluate-using-rtk-in-this-repository.md):

- **D1:** scope as proposed.
- **D2:** isolated binary trials (decided by the human).
- **D3:** any changed exit code or changed taskrail `--json` output rules out a hook-based
  adoption, and an option with exclusions is still recorded (decided by the human).
- **D4:** a 2-point time box.

## Question

**Should agents working on this repository run their shell commands through RTK?** The scope
is this repository's own Claude Code and OpenCode sessions. Distributing RTK is out of scope.

Sub-questions:

1. What changes in a session?
2. What does it save on this repository's real commands?
3. Does it ever preserve less than the raw command: exit codes, error text, taskrail's
   `--json` output, git content?
4. What do the known defects cost here: PR #3577 not merged, and issue #3230 open?
5. What does it install, and can it be scoped to this repository?
6. Telemetry and local data.
7. Licence.
8. Reversibility.
9. Agent portability.

## Evidence

### Versions and pins

- **RTK release.** `v0.49.0`, published 2026-09-11, tag commit
  `b1c0dc00649c50fbe8930f849c800d4d6ca12091`.
  - Binary: `rtk-x86_64-unknown-linux-musl.tar.gz`, SHA-256
    `7278231dfd7e6a730a4ab7f847b195bcf02289c2d57622b0dab75a6411100c8f`. It matches the release's
    `checksums.txt` (`sha256sum -c --ignore-missing checksums.txt` printed `OK`).
  - The checksum file ships in the same release, so it proves the download is intact, not who
    published it.
  - The extracted `rtk` is a static-pie ELF, SHA-256
    `a051b22361c7cfa36022bc3f06bb41cdc88e58a07263dc340d8bd3468c41befe`.
  - `rtk --version` printed `rtk 0.49.0`.
- **RTK source read.** A shallow clone of tag `v0.49.0`, which resolved to the commit above.
- **RTK `develop`, checked for #3230.** `d402152ffa050ca3753672e3d49c3f2ff498a07b`.
- **PR #3577.** Head `9d19364994b55f5878392847c99dad50eca4b24b`, base `develop`,
  `mergeable_state: unstable`, 761 additions and 48 deletions. Its diff was read, not built.
- **This repository.** A throwaway clone at `d3833e7`.
- **Tools.** git 2.55.0, uv 0.11.16, Python 3.12.13, pytest 9.1.1. Commands ran inside a Claude
  Code 2.1.270 Bash session, but no RTK-hooked agent session was started.

### Isolation (frame decision D2)

- **One environment for everything.** Every `rtk` run, and every raw command it was compared
  with, went through one wrapper that set:
  - `HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME` and `XDG_STATE_HOME` to
    directories under `/tmp/t044`;
  - `GIT_CONFIG_GLOBAL` to a throwaway file;
  - `RTK_TELEMETRY_DISABLED=1`;
  - `PATH` with `/tmp/t044/bin` first.
- **Where it ran.** The working directory was a clone of this repository at `/tmp/t044/clone`.
- **`rtk init` stayed isolated.** It ran only inside that throwaway home.
- **No agent session.** None was started.
- **Checksums of the human's configuration.** MD5 digests were taken before the trials and
  checked afterwards (`md5sum -c`).
  - Files: `~/.claude/settings.json`, `~/.claude/plugins/known_marketplaces.json`, the three
    files in `~/.config/opencode/`, `~/.bashrc` and `~/.bash_profile`.
  - Results:
    - `~/.claude/settings.json`: OK.
    - The three OpenCode files: OK.
    - `~/.bashrc` and `~/.bash_profile`: OK.
    - `known_marketplaces.json`: FAILED.
- **The one changed file.** `known_marketplaces.json` holds a single `lastUpdated` field,
  `2026-09-14T12:47:21.110Z`, which equals the file's modification time. That is Claude Code
  refreshing its official plugin marketplace. Neither RTK's source nor the binary's strings
  mention the file, and no RTK process ran with the real `HOME`. The cause is attributed, not
  proven: only a digest of the earlier version was kept, not a copy.
- **Absence checks.** These paths were absent before and after:
  - `~/.config/rtk`, `~/.local/share/rtk`, `~/.cache/rtk`;
  - `~/.claude/RTK.md`, `~/.claude/hooks`;
  - `~/.local/bin/rtk`;
  - `~/.config/opencode/plugins`.
- **`rtk` on the human's PATH.** `command -v rtk` found nothing, and the string `rtk` appears in
  none of the human's settings, OpenCode config or shell profile files.
- **What was read, not written.** The throwaway clone's `.venv` was built by uv from a Python
  interpreter already on the human's `PATH`. That reads the human's files but does not change
  them. uv's package cache went to the throwaway `XDG_CACHE_HOME`.

### Method

A throwaway script ran every case the same way:

1. Ask `rtk rewrite "<command>"` what the hook would execute. `rtk rewrite` is the same function
   both the Claude Code hook and the OpenCode plugin call.
2. Run the raw command and the rewritten command with `sh -c` in the clone, under the wrapper.
3. Record both exit codes, stdout and stderr sizes, and whether stdout was byte-identical.

Sizes below are stdout plus stderr, with ANSI colour codes stripped from both sides, so colour
escapes are not counted as savings. `rtk rewrite` exits 3 ("Ask rule matched — hook rewrites
but lets Claude Code prompt") for every rewrite here, because the throwaway home has no Claude
Code permission rules. Exit 1 means no rewrite.

**Trial fixtures, all only in the clone:**

- `tools/taskrail/tests/test_t044_trial_fail.py`: one failing assertion.
- `tests/test_t044_trial_syntax.py`: a syntax error.
- `tests/test_t044_trial_import.py`: an import error. The syntax and import files were removed
  before `p06`.
- `tools/taskrail/tests_t044_trial/`: a passing test, plus a `conftest.py` whose
  `pytest_sessionfinish` sets the exit status to 1. It is outside `testpaths`, so the full suite
  does not collect it.
- An empty commit with a body ending in `Reopens: T006`, for `g15`–`g17`.

### Measurements (E1–E5)

**Columns.**

- *Exit* is raw / RTK.
- *Bytes* is raw → RTK, ANSI-stripped, with the reduction in brackets.
- *Stdout* is a byte comparison of stdout alone, before ANSI stripping. So pytest rows can say
  "differs" when only colour differs.

| ID | Command | Hook runs | Exit | Bytes | Stdout |
|---|---|---|---|---|---|
| g01 | `git status` | `rtk git status` | 0 / 0 | 63 → 55 (13%) | differs |
| g02 | `git log --oneline -n 20` | `rtk git log --oneline -n 20` | 0 / 0 | 1866 → 1866 (0%) | identical |
| g03 | `git log -n 5` | `rtk git log -n 5` | 0 / 0 | 12680 → 1819 (86%) | differs |
| g04 | `git log --grep='^Reopens: ' --format='%H %s'` | `rtk git log …` | 0 / 0 | 0 → 1 (—) | differs |
| g05 | `git diff HEAD~3 --stat` | `rtk git diff HEAD~3 --stat` | 0 / 0 | 937 → 936 (0%) | differs |
| g06 | `git diff HEAD~3` | `rtk git diff HEAD~3` | 0 / 0 | 85701 → 34927 (59%) | differs |
| g07 | `git worktree list` | `rtk git worktree list` | 0 / 0 | 40 → 40 (0%) | identical |
| g08 | `git show HEAD` | `rtk git show HEAD` | 0 / 0 | 39555 → 18700 (53%) | differs |
| g09 | `git log -n 5 --format=%B` | `rtk git log -n 5 --format=%B` | 0 / 0 | 10914 → 10914 (0%) | identical |
| g10 | `git log nonexistent-ref` | `rtk git log nonexistent-ref` | 128 / 128 | 196 → 197 | identical |
| g11 | `git diff nonexistent-ref` | `rtk git diff nonexistent-ref` | 128 / 128 | 196 → 196 | identical |
| g12 | `git commit -m nothing-staged` | `rtk git commit -m nothing-staged` | 1 / 1 | 63 → 63 | differs (moved to stderr) |
| g13 | `git fetch origin` | `rtk git fetch origin` | 0 / 0 | 0 → 11 | differs |
| g14 | `command git log -n 5` | `command rtk git log -n 5` | 0 / 0 | 12680 → 1819 (86%) | differs |
| g15 | `git log -n 1` | `rtk git log -n 1` | 0 / 0 | 328 → 157 (52%) | differs |
| g16 | `git log --grep='^Reopens: T006$' --format=%H` | `rtk git log …` | 0 / 0 | 41 → 41 (0%) | identical |
| g17 | `git log --grep='^Reopens: T006$'` | `rtk git log --grep='^Reopens: T006$'` | 0 / 0 | 328 → 156 (52%) | differs |
| g18 | `git show --stat HEAD` | `rtk git show --stat HEAD` | 0 / 0 | 328 → 328 (0%) | identical |
| p01 | `uv run --directory tools/taskrail pytest -q` (823 pass) | `rtk uv run --directory tools/taskrail pytest -q` | 0 / 0 | 991 → 991 (0%) | differs (colour only) |
| p02 | `uv run --directory tools/taskrail pytest -q tests/test_validate.py` | `rtk uv run …` | 0 / 0 | 99 → 99 (0%) | differs (colour only) |
| p03 | `… pytest -q tests/test_t044_trial_fail.py` | `rtk uv run …` | 1 / 1 | 630 → 267 (58%) | differs |
| p04 | `… pytest -q tests/test_t044_trial_syntax.py` | `rtk uv run …` | 2 / 2 | 1794 → 758 (58%) | differs |
| p05 | `… pytest -q tests/test_validate.py -k zzznomatch` | `rtk uv run …` | 5 / 5 | 24 → 23 (4%) | differs |
| p06 | `uv run --directory tools/taskrail pytest -q` (1 failing) | `rtk uv run --directory tools/taskrail pytest -q` | 1 / 1 | 1533 → 290 (81%) | differs |
| p07 | `cd tools/taskrail && uv run pytest -q tests/test_t044_trial_fail.py` | `cd tools/taskrail && uv run rtk pytest -q …` | 1 / 1 | 630 → 257 (59%) | differs |
| p08 | `… pytest -q tests/nope.py` | `rtk uv run …` | 4 / 4 | 74 → 50 (32%) | differs |
| p09 | `… pytest -q tests/test_t044_trial_import.py` | `rtk uv run …` | 2 / 2 | 970 → 327 (66%) | differs |
| p10 | `… pytest -q tests/test_validate.py tests/test_t044_trial_import.py` | `rtk uv run …` | 2 / 2 | 970 → 327 (66%) | differs |
| p11 | `cd tools/taskrail && uv run pytest -q tests/test_t044_trial_syntax.py` | `… uv run rtk pytest -q …` | 2 / 2 | 1794 → 1713 (5%) | differs |
| p12 | `uv run --directory tools/taskrail pytest -q tests_t044_trial` | `rtk uv run …` | 1 / 1 | 157 → 156 (1%) | differs |
| p13 | `cd tools/taskrail && uv run pytest -q tests_t044_trial` | `… uv run rtk pytest -q tests_t044_trial` | 1 / 1 | 157 → 17 (89%) | differs |
| p14 | `cd tools/taskrail && uv run pytest tests_t044_trial` | `… uv run rtk pytest tests_t044_trial` | 1 / 1 | 448 → 17 (96%) | differs |
| s01 | `grep -rn taskrail docs/spikes` | `rtk grep -rn taskrail docs/spikes` | 0 / 0 | 9327 → 6333 (32%) | differs |
| s02 | `grep -rn zzznomatchzzz docs` | `rtk grep …` | 1 / 1 | 0 → 0 | identical |
| s03 | `grep -rn taskrail no-such-dir` | `rtk grep …` | 2 / 2 | 45 → 54 | identical |
| s04 | `ls -la` | `rtk ls -la` | 0 / 0 | 671 → 166 (75%) | differs |
| s05 | `ls .claude/skills` | `rtk ls .claude/skills` | 0 / 0 | 96 → 103 (−7%) | differs |
| s06 | `cat CLAUDE.md` | `rtk read CLAUDE.md` | 0 / 0 | 7676 → 7676 (0%) | identical |
| s07 | `cat tools/taskrail/src/taskrail/cli.py` | `rtk read tools/taskrail/src/taskrail/cli.py` | 0 / 0 | 60733 → 60733 (0%) | identical |
| s08 | `head -20 TODO.md` | `rtk read TODO.md --max-lines 20` | 0 / 0 | 1232 → 483 (61%) | differs |
| s09 | `cat no-such-file` | `rtk read no-such-file` | 1 / 1 | 45 → 58 | identical |
| s10 | `find . -name '*.md' -not -path './.git/*'` | `rtk find …` | 0 / 0 | 6293 → 2170 (66%) | differs |
| s11 | `command grep -rn taskrail docs/spikes` | `command rtk grep -rn taskrail docs/spikes` | 0 / 0 | 9327 → 6333 (32%) | differs |
| t01 | `.taskrail/bin/taskrail show T044 --json` | not rewritten | 0 / 0 | 3075 → 3075 | identical |
| t02 | `.taskrail/bin/taskrail list --json` | not rewritten | 0 / 0 | 56733 → 56733 | identical |
| t03 | `.taskrail/bin/taskrail show T999 --json` | not rewritten | 3 / 3 | 25 → 25 | identical |
| t04 | `.taskrail/bin/taskrail claim T011 --json` | not rewritten | 5 / 5 | 41 → 41 | identical |
| t05 | `uv run --directory tools/taskrail taskrail --root <clone> show T044 --json` | `rtk uv run …` | 0 / 0 | 3075 → 1402 (54%) | **differs: invalid JSON** |
| t06 | `uv run --directory tools/taskrail taskrail --root <clone> show T999 --json` | `rtk uv run …` | 3 / 3 | 25 → 25 | **differs: stderr moved to stdout** |
| t07 | `uv run --directory tools/taskrail taskrail --root <clone> validate` | `rtk uv run …` | 0 / 0 | 53 → 53 | identical |
| t08 | `cd tools/taskrail && uv run taskrail --root ../.. next --json` | `cd tools/taskrail && rtk uv run taskrail …` | 0 / 0 | 3730 → 1471 (61%) | **differs: invalid JSON** |
| t09 | `uv run --directory tools/taskrail taskrail --root <clone> claim T011 --json` | `rtk uv run …` | 5 / 5 | 41 → 41 | **differs: stderr moved to stdout** |
| t10 | `.taskrail/bin/taskrail next --json \| head -c 200` | not rewritten | 0 / 0 | 200 → 200 | identical |

Across all 53 cases, the ANSI-stripped total was 338630 bytes raw against 224693 through RTK, a
34% reduction. Most of it came from three commands:

- `git diff HEAD~3` (g06);
- `git show HEAD` (g08);
- `git log -n 5` (g03, and g14 through `command`).

### Findings by criterion

**E1 — Savings.**

- **Where the bytes go.** The large reductions fall on `git diff`, `git show`, `git log`,
  `find`, `ls -la` and failing pytest runs. RTK's own `rtk gain` estimated 35.4K of 76.4K input
  tokens saved (46.4%) over its 46 recorded commands. Its tokens are `bytes / 4`, so the figure is an estimate.
- **Where nothing is saved.** On the configured `test` check when it passes (p01, 823 tests),
  RTK saved nothing beyond stripping colour codes. It saved nothing on `.taskrail/bin/taskrail`
  (never rewritten), on `cat` (`rtk read` returned identical bytes), or on
  `git log --format=…`.

**E2 — Exit codes.** Preserved in all 53 cases:

- 0, 1, 2, 3, 4, 5 and 128;
- pytest failures, collection errors, usage errors and "no tests";
- taskrail's not-found (3) and refusal (5);
- git's fatal errors.

This holds on `v0.49.0` without PR #3577.

**E3 — Errors hidden.**

- **p13/p14, the #3577 class.** `cd tools/taskrail && uv run pytest -q tests_t044_trial` is
  CLAUDE.md's documented test invocation pointed at the trial directory. The hook rewrites it to
  `uv run rtk pytest`, which printed only `Pytest: 1 passed` for a run that exited 1.
  - The raw output carried the reason: `T044 trial: session hook forces exit 1 after tests
    passed`.
  - The source explains it. At `v0.49.0`, `src/cmds/python/pytest_cmd.rs` falls back to raw
    output only when a failed run parses as "No tests collected".
  - PR #3577 replaces this with `guard_exit`, which renders `<tool>: failed (exit N)` whenever a
    green summary meets a non-zero exit.
- **Failing tests and collection errors.** p03, p04, p06, p07, p09 and p11 kept the failing
  assertion or error, with a `[full output: rtk recall <hash>]` pointer.
- **Moved streams.** t06/t09 moved taskrail's stderr message onto stdout, and g12 moved git's
  stdout onto stderr. On failure, `src/cmds/python/uv_cmd.rs` scans the two streams merged,
  because splitting a Python traceback "would break frame ordering".

**E4 — Exact output where procedures parse it.**

- **The wrapper is safe.** `.taskrail/bin/taskrail … --json` is never rewritten, so its bytes
  and exit codes were identical (t01–t04, t10). A pipe into another program was not rewritten
  either (t10, and the rewrite list below).
- **`uv run … taskrail … --json` is not.** This form is in CLAUDE.md's Commands section
  (`uv run taskrail --root <repo> validate`). Through the hook it became `rtk uv run …`, and the
  output was invalid JSON (t05, t08).
  - Excerpt of the RTK output: `... (56 lines omitted)` in the middle, and
    `[+81 hidden: rtk recall 3c865fd24d2b]` at the end.
  - `python3 -m json.tool` failed on it: `Expecting property name enclosed in double quotes:
    line 26 column 1`.
  - The cause: `uv_cmd.rs` says successful output is "passed through unchanged", but caps it at
    `CAP_INVENTORY` = 50 lines (`src/core/truncate.rs`).
  - **Under D3 this alone rules out a hook-based adoption.**
- **Commit trailers.**
  - `rtk git log -n 1` on a commit whose body ends in `Reopens: T006` printed three body lines
    and `[+4 lines omitted]`, so the trailer was not shown (g15, g17).
  - Across the last five squash commits (g03), 96 trailer lines became 10.
  - `--format=%H` and `--format=%B` passed through unchanged (g09, g16).
  - The taskrail skill's `git log --grep='^Reopens: <ID>$' <side>` check only needs a match,
    and g17 still listed the matching commit. But the trailer itself is not visible in RTK's
    default `git log`.
- **Other content.**
  - `rtk git diff` truncated hunks: `... (42 additions truncated)`,
    `... (262 additions truncated)`, `... (more changes truncated)` (g06, g08).
  - `head -20 TODO.md` became `rtk read TODO.md --max-lines 20` and printed 10 lines plus
    `[88 more lines]` (s08).
  - `find` ended in `[+54 hidden: rtk recall …]` (s10).
  - `grep` elided long lines and matches (s01).

**E5 — Rewrite coverage.** From `rtk rewrite` on the command set:

- **Rewritten:**
  - `git status/log/diff/show/worktree/fetch/commit`;
  - `grep`, `rg`, `ls`, `find`;
  - `cat` → `rtk read`, `head -N` → `rtk read --max-lines N`;
  - `uv run --directory …` → `rtk uv run …`;
  - `uv run pytest` → `uv run rtk pytest`;
  - `env git status` → `env rtk git status`.
- **Not rewritten:**
  - `.taskrail/bin/taskrail …`;
  - `git rebase origin/main`;
  - `\git status`, `/usr/bin/git status`;
  - `find … -print0 | xargs -0 …`;
  - a command piped into `python3`.
- **Rewritten on the producer side of a pipe:** `git log --oneline | head -5` →
  `rtk git log --oneline | head -5`.

**E6 — The `command` bypass (#3230).**

- **Measured on `v0.49.0`.**
  - `command git log -n 5` → `command rtk git log -n 5`: the same 86% cut output as without the
    prefix (g14).
  - `command grep …` → `command rtk grep …` (s11).
  - A real Claude Code hook payload fed to `rtk hook claude` returned
    `"updatedInput":{"command":"command rtk git log -n 5"}`.
- **Still unfixed upstream.** `SHELL_KEYWORD_PREFIXES` still lists `"command"` on `develop` at
  `d402152` (`src/discover/registry.rs:1345`).
- **Escapes that do work.** `\git` and absolute paths are left alone.
- **What config can and cannot do.**
  - `[hooks] exclude_commands` cannot name `command` itself: with `"command"` excluded,
    `command git log` was still rewritten.
  - Excluding the underlying command does work: with `"git log"` excluded,
    `command git log -n 5` passed through.

**E7 — Exit-code masking (#3577).**

- **What the PR covers.** Its diff adds `src/core/guard.rs::guard_exit` and applies it to pytest,
  ruff, mypy, cargo, vitest, lint, go, golangci-lint and gradlew.
- **What it does not cover.** The `uv run` filter, the `git` filters and `rtk read`.
- **Effect here.** It would fix p13/p14. It would not fix the JSON truncation (t05, t08), the
  trailer loss or the diff truncation, which are successful runs with exit 0.

**E8 — Footprint and scope.**

- **Claude Code.** `rtk init -g --auto-patch` in the throwaway home:
  - wrote `~/.claude/settings.json` (a `PreToolUse` hook, matcher `Bash`, command
    `rtk hook claude`);
  - wrote `~/.claude/RTK.md`;
  - wrote `~/.claude/CLAUDE.md` containing `@RTK.md`;
  - wrote `~/.config/rtk/filters.toml`.
- **What `RTK.md` tells the agent:** "Treat it as the complete result". That instruction runs
  against E4.
- **OpenCode.** `rtk init -g --opencode` wrote `~/.config/opencode/plugins/rtk.ts`.
- **Per-project wiring for each agent.**
  - Claude Code documents `.claude/settings.json` as a committable, single-project hook
    location [C1].
  - OpenCode documents `.opencode/plugins/` as project-level [O1].
  - RTK's hook is a plain stdin-JSON → stdout-JSON command, measured with `rtk hook claude`, and
    its plugin only shells out to `rtk rewrite` [R3]. So both could be committed per project.
    No agent session confirmed that.
  - RTK's own non-global `rtk init` writes RTK instructions into `./CLAUDE.md` [R2]. This
    repository forbids that file as a delivery point for agent-specific packaging.
- **Exclusions are per user.** RTK's configuration path is `dirs::config_dir()/rtk/config.toml`
  (`src/core/config.rs:458`), with no per-repository override and no environment variable for
  it. So an exclusion list would apply to every project of that user.
- **Without the binary.**
  - A committed Claude Code hook would fail to start on a contributor without the binary. Claude
    Code documents that as a non-blocking error: "the action proceeds", with a hook error notice
    on each call [C1].
  - The OpenCode plugin logs `rtk binary not found in PATH — plugin disabled` and does nothing.
- **Local data.** Even with telemetry off, RTK wrote to `$XDG_DATA_HOME/rtk/`:
  - `history.db`, table `commands`: `original_cmd`, `rtk_cmd`, token counts, `project_path`.
    It also has a `hook_decisions` table with `session_id` and `raw_cmd`.
  - `recall.db`, table `recall`: the full unfiltered output blob of elided runs, with `command`,
    `cwd` and `exit_code`. It held 10 rows after the trials.

**E9 — Telemetry.** The source settles the documentation contradiction.

- **The gates.** `src/core/telemetry.rs::maybe_ping` returns early unless all of these hold:
  1. an endpoint was compiled in (line 35);
  2. `RTK_TELEMETRY_DISABLED` is unset (line 40);
  3. `consent_given == Some(true)` (line 51);
  4. `telemetry.enabled` is true (line 57).
- **The defaults.** `test_telemetry_default_disabled` in `src/core/config.rs` asserts
  `enabled` defaults to false. `consent_given` defaults to `None`.
- **The prompt.** `rtk init` asks for consent only on an interactive terminal, and never when
  `RTK_TELEMETRY_DISABLED` is set (`src/hooks/init.rs`, `prompt_telemetry_consent`).
- **In the trial.** `rtk telemetry status` printed `consent: never asked`, `enabled: no`,
  `env override: RTK_TELEMETRY_DISABLED=1 (blocked)`.
- **The release binary can reach the network.** The release workflow injects `RTK_TELEMETRY_URL`
  (`.github/workflows/release.yml`), and the binary contains the string
  `https://telemetry.rtk-ai.app/ping`. It pings once a day only after explicit consent.
- **Conclusion.** The README and `docs/TELEMETRY.md` ("disabled by default") are right.
  `DISCLAIMER.md` ("collects … by default") is stale.

**E10 — Licence.** `LICENSE` at `v0.49.0` is Apache-2.0. The `hooks/` files carry no separate
licence header. Using the binary locally, or committing a copy of the thin hook or plugin, is
allowed with attribution. No licence obstacle was found.

**E11 — Reversibility.**

- **What uninstall removed.** After installing both integrations, `rtk init -g --uninstall`
  printed:
  - `RTK.md: …/.claude/RTK.md`;
  - `CLAUDE.md: removed (was empty after cleanup)`;
  - `settings.json: removed RTK hook entry`;
  - `OpenCode plugin: …/.config/opencode/plugins/rtk.ts`.
- **What it left.**
  - `settings.json` with an empty `"PreToolUse": []`;
  - `settings.json.bak`, which still holds the RTK hook;
  - `~/.config/rtk/filters.toml`;
  - `history.db`, `recall.db` and `.hook_warn_last`;
  - the binary itself.

**E12 — Agent portability.** Both integrations delegate to one `rtk rewrite` function, so they
behave the same. But each needs its own agent-specific file (a settings hook, a TypeScript
plugin), plus a binary every contributor must install. Under this repository's *Agent
portability* rule, that wiring belongs in an adapter layer. Nothing about RTK is agent-neutral
at the repository level.

### Sources

All read on 2026-09-14. Quotations are short fragments.

| # | Source |
|---|---|
| R1 | RTK README at `v0.49.0` — https://github.com/rtk-ai/rtk/blob/b1c0dc00649c50fbe8930f849c800d4d6ca12091/README.md |
| R2 | RTK INSTALL.md at `v0.49.0` — https://github.com/rtk-ai/rtk/blob/b1c0dc00649c50fbe8930f849c800d4d6ca12091/INSTALL.md |
| R3 | RTK `hooks/` (`hooks/opencode/rtk.ts`, `hooks/claude/README.md`) at `v0.49.0` — https://github.com/rtk-ai/rtk/tree/b1c0dc00649c50fbe8930f849c800d4d6ca12091/hooks |
| R4 | RTK docs/TELEMETRY.md at `v0.49.0` — https://github.com/rtk-ai/rtk/blob/b1c0dc00649c50fbe8930f849c800d4d6ca12091/docs/TELEMETRY.md |
| R5 | RTK DISCLAIMER.md at `v0.49.0` — https://github.com/rtk-ai/rtk/blob/b1c0dc00649c50fbe8930f849c800d4d6ca12091/DISCLAIMER.md |
| R6 | RTK LICENSE at `v0.49.0` — https://github.com/rtk-ai/rtk/blob/b1c0dc00649c50fbe8930f849c800d4d6ca12091/LICENSE |
| R7 | RTK release `v0.49.0` and `checksums.txt` — https://github.com/rtk-ai/rtk/releases/tag/v0.49.0 |
| R8 | RTK PR #3577 and its diff — https://github.com/rtk-ai/rtk/pull/3577 (open, not merged) |
| R9 | RTK issue #3230 — https://github.com/rtk-ai/rtk/issues/3230 (open) |
| R10 | RTK source at `v0.49.0`: `src/core/telemetry.rs`, `src/core/config.rs`, `src/hooks/init.rs`, `src/hooks/hook_cmd.rs`, `src/hooks/rewrite_cmd.rs`, `src/cmds/python/pytest_cmd.rs`, `src/cmds/python/uv_cmd.rs`, `src/core/truncate.rs`, `.github/workflows/release.yml` — https://github.com/rtk-ai/rtk/tree/b1c0dc00649c50fbe8930f849c800d4d6ca12091 |
| R11 | RTK `src/discover/registry.rs` on `develop` at `d402152` — https://github.com/rtk-ai/rtk/blob/d402152ffa050ca3753672e3d49c3f2ff498a07b/src/discover/registry.rs |
| C1 | Claude Code, Hooks reference — https://code.claude.com/docs/en/hooks.md |
| O1 | OpenCode, Plugins — https://opencode.ai/docs/plugins/ |

### Not verified

- **No agent session.** No session ran with the hook or plugin loaded, as D2 required. So these
  rest on documentation plus the measured hook contract:
  - that a project-level `.claude/settings.json` hook or `.opencode/plugins/rtk.ts` plugin
    actually loads;
  - how an agent reacts to the rewritten output.
- **Telemetry was not observed on the network.** Only the source gates and the binary's strings
  were read, because the trials kept `RTK_TELEMETRY_DISABLED=1`.
- **PR #3577 was not built** (D2). Its effect on p13/p14 is read from the diff.
- **No session colour.** Output sizes were measured in a non-interactive shell. A real session's
  colour behaviour may differ, which is why sizes are compared ANSI-stripped.

## Options considered

1. **No adoption.** No hook, plugin or RTK instructions. Agents run commands raw.
   - Cost: none.
   - Keeps every output exact.
   - Gives up about 34% of bytes on the measured set, concentrated in large `git diff` and
     `git show` output.
2. **Hook or plugin with every default rewrite.** Ruled out by D3: it produced invalid taskrail
   JSON (t05, t08) and moved taskrail's error text to stdout (t06, t09). It also hid a
   `Reopens:` trailer, diff hunks and a failure reason (p13).
3. **Hook or plugin with exclusions.** Recorded, as D3 asked.
   - **What it takes.** Exclusions that keep every measured problem out:
     `exclude_commands = ["uv", "pytest", "git log", "git diff", "git show", "head", "find"]`.
     The trial confirmed that `uv`, `pytest`, `git log`, `git diff`, `git show` and `head` each
     stop their rewrite, including `cd tools/taskrail && uv run pytest` and `command git log`.
     `find` was not tested. What it leaves rewritten:
     - `git status`, `ls` and `grep`;
     - `command git status` → `command rtk git status` (#3230).
   - **Why it is not worth it.** What remains measured 13%, 75% and 32% on small outputs
     (g01, s04, s01), a few hundred bytes to a few kilobytes.
   - **The list is fragile.** It lives in each user's global config, not in this repository. It
     would silently apply to their other projects. And every new RTK filter a release adds is
     rewritten by default until someone excludes it.
4. **Explicit `rtk <cmd>` only, no hook.** Agents may call `rtk git diff` and similar
   themselves.
   - It needs the binary on every contributor's `PATH`, and instructions somewhere
     agent-neutral.
   - It brings back the truncation for exactly the large outputs where it saves anything.
   - It adds a per-command decision agents get wrong.
5. **Leave it to each contributor's global install.** Not something this repository can adopt.
   It is also a hazard: on a machine with `rtk init -g`, the `uv run … taskrail … --json` form
   breaks as measured.

## Recommendation

**Option 1: agents working on this repository do not use RTK.** Nothing is installed, and no
hook or plugin is committed.

- **Keep the safe invocation in procedures.** Keep using `.taskrail/bin/taskrail` for anything
  that parses `--json`. It is what the taskrail skills already use, and RTK never rewrites it.
- **Keep git output unfiltered.** Keep `git log --format=…` wherever a procedure reads trailers.

Adopting nothing needs no follow-up work. The two items below only reduce exposure for
contributors who install RTK globally on their own.

### Follow-ups (done in this task)

At the decide gate the human chose to do both items in this task rather than open new backlog
tasks.

- **A note in CLAUDE.md.** A short note saying RTK's hook or plugin must not be used with this
  repository, citing this spike. The human approved the wording, and it was applied at the end
  of CLAUDE.md's *Commands* section.
- **A contract test for `uv run`.** `tools/taskrail/tests/test_json_through_uv_run.py` runs
  `uv run --directory tools/taskrail taskrail --root <tmp repo> <show|list|next> --json` in a
  subprocess. It checks that:
  - stdout is complete JSON, and the exit code is 0;
  - `show --json` is long enough (more than 60 lines) that a line cap like RTK's 50-line cap
    would break it;
  - `show T999 --json` exits 3, with nothing on stdout and the message on stderr.

  It is skipped when `uv` is not on `PATH`.
  - **Against the real command:** 5 passed in 1.16s. The full suite: 828 passed.
  - **Against a temporary variant** piping stdout through `head -c 200`, removed afterwards: all 5
    failed, with `JSONDecodeError`, `assert 12 > 60` and `assert 0 == 3`.

## What would change the decision

- **Truncation.** `rtk uv run` stops capping successful output. Measured: t05 and t08 produce
  byte-identical, valid JSON on a released version.
- **Trailers.** `rtk git log` keeps trailers, or leaves bodies whole. Measured: g15 shows
  `Reopens: T006`.
- **Exit guard.** PR #3577 (or an equivalent guard) lands in a release. Measured: p13 no longer
  reports a pass for an exit-1 run.
- **Bypass.** Issue #3230 is fixed in a release. Measured: `command git …` is not rewritten.
- **Per-repository exclusions.** RTK gains per-repository configuration for exclusions. That
  would make option 3 a committable, reviewable adapter rather than a per-user setting.
- **Evidence from real sessions.** Sessions here start losing real work to context size on
  `git diff` and `git show`. That would raise the value side enough to revisit option 3 or 4.

## How to reproduce

**1. Fetch and verify the release, isolated.**

```sh
mkdir -p /tmp/t044/{bin,home,xdg/{config,data,cache,state}} && cd /tmp/t044
B=https://github.com/rtk-ai/rtk/releases/download/v0.49.0
curl -fsSLO $B/rtk-x86_64-unknown-linux-musl.tar.gz && curl -fsSLO $B/checksums.txt
sha256sum -c --ignore-missing checksums.txt          # rtk-x86_64-unknown-linux-musl.tar.gz: OK
tar -xzf rtk-x86_64-unknown-linux-musl.tar.gz -C bin
git clone --depth 1 --branch v0.49.0 https://github.com/rtk-ai/rtk rtk-src
git clone --no-local <this repository> clone && git -C clone checkout d3833e7
```

**2. Create the isolation wrapper `/tmp/t044/iso`.**

```sh
#!/bin/sh
T=/tmp/t044
exec env HOME=$T/home XDG_CONFIG_HOME=$T/xdg/config XDG_DATA_HOME=$T/xdg/data \
  XDG_CACHE_HOME=$T/xdg/cache XDG_STATE_HOME=$T/xdg/state RTK_TELEMETRY_DISABLED=1 \
  GIT_CONFIG_GLOBAL=$T/home/.gitconfig GIT_PAGER=cat PAGER=cat \
  PATH=$T/bin:<directory holding uv>:/usr/local/bin:/usr/bin "$@"
```

**3. Run the comparison for each case** from `/tmp/t044/clone`:

```sh
rw=$(/tmp/t044/iso rtk rewrite "$cmd"); case $? in 0|3) rcmd=$rw ;; *) rcmd=$cmd ;; esac
/tmp/t044/iso sh -c "$cmd"  >raw.out 2>raw.err; echo "raw exit $?"
/tmp/t044/iso sh -c "$rcmd" >rtk.out 2>rtk.err; echo "rtk exit $?"
cmp -s raw.out rtk.out && echo identical || echo differs
```

- **Fixtures.** Create them first, as listed under *Method*.
- **Order.** Run p01 before adding the failing test files. Remove the syntax and import files
  before p06.
- **JSON check.** `python3 -m json.tool rtk.out` for t05 and t08.

**4. Check the hook contract.** Feed a payload to the hook directly:

```sh
printf '{"tool_name":"Bash","tool_input":{"command":"command git log -n 5"},"hook_event_name":"PreToolUse"}' \
  | /tmp/t044/iso rtk hook claude
```

**5. Check footprint and removal.** Inside the wrapper only, run:

- `rtk init -g --auto-patch </dev/null`
- `rtk init -g --opencode --auto-patch </dev/null`
- `rtk init -g --uninstall`

List `home/` and `xdg/` after each.

**6. Check exclusions.** Write `[hooks]\nexclude_commands = [...]` to
`/tmp/t044/xdg/config/rtk/config.toml` and repeat `rtk rewrite`.

**7. Guard the human's configuration.** Take MD5 digests of the files under *Isolation* before
step 1, and run `md5sum -c` after.

**8. Clean up.** `rm -rf /tmp/t044`.

## Cleanup

After the trials:

- **Removed.** `rm -rf /tmp/t044` removed the downloaded archive, the binary, the RTK source
  clone, the repository clone with its `.venv`, the throwaway home and XDG directories, and every
  output file. That was 41 MB.
- **`ls -d /tmp/t044*`:** `No such file or directory`.
- **`find / -xdev -name rtk -type f -perm -u+x`:** no results.
- **`command -v rtk`:** nothing.
- **RTK directories in the real home.** `~/.config/rtk` and `~/.local/share/rtk`: `No such file
  or directory`.
- **Checksums.** The results are under *Isolation*.
