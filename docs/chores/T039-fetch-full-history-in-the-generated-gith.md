# T039 — Fetch full history in the generated GitHub workflow

Kind: chore · Epic: E02 · Status: scoped

## Goal

The workflow `taskrail init --github-workflow` writes must give `taskrail validate` the git
history its reopen check (T012, DESIGN §7 "Reopens in history") reads.

Today the template in `install.workflow()` uses `actions/checkout` with its defaults, which fetch
a single commit (`fetch-depth: 1`). In such a clone the only commit has no parents, so it
reopens nothing, and the check examines one commit and never warns. Reproduction in a throwaway
repository (a task marked done, then reopened in a commit without a `Reopens:` trailer, then three
unrelated commits), cloned with `--depth 1` and in full:

```text
$ git log --oneline
17267ec unrelated 3
700d251 unrelated 2
b15c363 unrelated 1
6b28e10 reopen T001 without trailer
cbc944e done T001
f889442 init
--- shallow clone: taskrail validate
history: shallow clone; examined 1 commit(s), so older reopens are not checked
1 task(s) in 1 backlog(s): 0 error(s), 0 warning(s)
history: {'examined': 1, 'limit': 500, 'truncated': False, 'shallow': True, 'skipped': None}
issues: []
--- full clone: taskrail validate
TODO.md:13: warning: T001 went from ✅ done to ⬜ pending in 6b28e10 ("reopen T001 without trailer") without a `Reopens: T001` trailer; ... [reopen-untraced]
1 task(s) in 1 backlog(s): 0 error(s), 1 warning(s)
history: {'examined': 3, 'limit': 500, 'truncated': False, 'shallow': False, 'skipped': None}
```

## Change set

1. `tools/taskrail/src/taskrail/install.py` — in `workflow()`, give the checkout step
   `with: fetch-depth: 0`:

   ```yaml
         - uses: actions/checkout@v7
           with:
             fetch-depth: 0
   ```

   Nothing else in the template changes; `validate` keeps running without flags.
2. `tools/taskrail/tests/test_install.py` — two tests:
   - the generated workflow's checkout step requests full history (`fetch-depth: 0` in the
     `with:` block directly under `actions/checkout`);
   - `upgrade` rewrites a workflow an earlier template wrote and nobody edited: the test writes
     the previous template's text and records its digest in `installed.json`, as an older
     install would have, runs `upgrade`, and checks the file is reported `updated` and now
     requests full history. (A locally edited workflow is skipped — existing managed-file
     behaviour, already covered for skills; not re-tested here.)
3. `tools/taskrail/DESIGN.md` §9, *Extras* bullet — say the workflow checks out full history,
   because `validate`'s reopen check (§7) sees nothing past a shallow clone's boundary.
4. `tools/taskrail/README.md` — the `--github-workflow` bullet: runs `validate` with full git
   history, so the reopen check sees every commit. (It also runs on pushes to the mainlines;
   the bullet says only "on pull requests" — fix that in the same sentence.)
5. `tools/taskrail/CHANGELOG.md` — one bullet at the end of `## Unreleased`: the generated
   workflow fetches full history; `upgrade` updates an existing, unedited workflow, and one
   edited locally is reported as skipped (add `fetch-depth: 0` by hand or pass `--force`).
6. This document, and its row in `docs/chores/README.md`.

## Decisions needed

1. **`fetch-depth: 0` or a bounded depth?** Recommendation: `0`. A bounded depth cannot be matched
   to `--history-limit`: the limit counts commits that *change backlog files*, while
   `fetch-depth` counts all commits, so any finite depth can still cut the window short and turn
   a reopen's parent into a shallow boundary (which then reopens nothing, silently). The cost of
   full history is one larger fetch; the check itself stays bounded by `--history-limit`.
   Alternative: a large fixed depth such as `fetch-depth: 1000`, cheaper on huge repositories but
   still incomplete by construction.
2. **Should `validate` in the workflow pass any flag?** Recommendation: no. The default limit
   (500) applies to CI as it does locally; `--no-history` would defeat the change. The
   `reopen-untraced` warning does not change the exit code, so the job still passes and the
   warning shows in its log. Alternative: `--history-limit N` — rejected, it would hard-code a
   policy the repository can already choose by editing (and then owning) the workflow.
3. **`upgrade` and existing workflows.** No code change needed: the workflow is a *managed*
   file (digest in `installed.json`, extra remembered in `extras.github_workflow`), so `upgrade`
   rewrites an unedited one and reports an edited one as skipped. Recommendation: rely on that,
   pin it with the test in change 2, and state it in the changelog bullet. Alternative: drop the
   upgrade test and keep only the template test.

## Out of scope

- Adding a workflow to this repository (explicitly excluded).
- Surfacing `reopen-untraced` as a GitHub annotation, or failing the job on warnings.
- Pinning or bumping the action versions (`actions/checkout@v7`, `astral-sh/setup-uv@v10`).
- The pre-commit hook (local clones already have their history) and anything in `install()`'s
  extras or `cli.py` (T004 touches those).
- Any change to `history.py` or `validate`.

## Verification

- `uv run --directory tools/taskrail pytest -q` — all tests, including the two new ones, pass.
- In a throwaway repository under a temporary directory: `init --github-workflow` with the
  current `main` code writes the old template; `upgrade` with this branch's code reports
  `.github/workflows/taskrail.yml` updated and the file contains `fetch-depth: 0`; a second
  repository whose workflow was edited locally reports it skipped.
- Repeat the reproduction above: a `--depth 1` clone reports `shallow: true` and no warning, a
  full clone (what `fetch-depth: 0` produces) reports the `reopen-untraced` warning. GitHub
  Actions itself is not run.
- `.taskrail/bin/taskrail validate` in this worktree.
