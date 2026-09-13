# T015 — Hand closed tasks off for review with a merge request link

Kind: feature · Epic: E01 · Status: plan approved

## Behaviour

Closing a task today ends with "report the branch", and opening the pull or merge request is
left to whoever reads the report. After this change, the close step prepares the review in a
fixed, configurable sequence that works on any git host:

1. **Fetch** the review remote (on by default).
2. **Rebase** the task branch onto its target — the backlog's `mainline` — using whichever of
   the local branch and the remote-tracking branch is further ahead. If they have diverged,
   stop and ask (on by default).
3. **Push** the task branch (on by default).
4. **Print the link** that opens a pull or merge request for the branch, with its title — and,
   where the host accepts it, its description — already filled in.

Because merges are squashed, the pull request title becomes the only commit that reaches the
mainline. It is therefore generated in Conventional Commits form, ready for semantic
versioning: `{type}({scope}): {subject} ({id})`, for example
`feat(taskrail): hand closed tasks off for review with a merge request link (T015)`.

The CLI owns the deterministic parts and the agent keeps the judgement:

- `taskrail review <ID> --json` fetches, and reports what to rebase onto, or that the bases
  diverged. It changes nothing else.
- The agent rebases and resolves conflicts with the rules the skill already has, then runs
  `taskrail validate`.
- `taskrail review <ID> --publish --json` pushes the branch (with a lease when it already
  exists on the remote) and returns the title, the description and the link.

### Host support

Verified against primary sources before planning:

| Provider | Link | Title and description prefilled | Source |
|---|---|---|---|
| `github` | `{web}/{repo}/compare/{base}...{head}?quick_pull=1&title=…&body=…` | yes | GitHub Docs, "Using query parameters to create a pull request" |
| `gitlab` | `{web}/{repo}/-/merge_requests/new?merge_request[source_branch]=…&merge_request[target_branch]=…&merge_request[title]=…&merge_request[description]=…` | yes | `Projects::MergeRequests::CreationsController#new` and its permitted params |
| `gitea` | `{web}/{repo}/compare/{base}...{head}?title=…&body=…` | yes | `routers/web/repo/compare.go` (`FormTrim("title")`, `FormTrim("body")`) |
| `forgejo` | `{web}/{repo}/compare/{base}...{head}` | no — the compare handler reads no such parameters | `routers/web/repo/compare.go` |
| `bitbucket` | not built in | unverified | Atlassian documentation is not readable without a browser |

GitHub answers 404 to invalid query parameters and 414 to over-long URLs, so the description
is dropped from the link when the URL would exceed 8,000 characters. `github.com`,
`gitlab.com` and `codeberg.org` are detected from the remote URL; any other host needs
`provider`, and `web_url` when the web address differs from the remote's host. A
`url_template` covers hosts without a built-in provider, such as Bitbucket.

### Configuration

```toml
[git]
push_task_branch = true       # default changes from false to true

[review]
remote = "origin"
fetch = true
rebase = true
provider = "auto"             # auto | github | gitlab | gitea | forgejo | none
web_url = ""                  # e.g. "https://git.example.com" for self-hosted hosts
url_template = ""             # placeholders: {web_url} {repo} {base} {head} {title} {body}
scope = ""                    # default Conventional Commits scope; empty omits it
```

Each core kind declares its default commit type in `kind.toml` (`commit_type`): `feature` →
`feat`, `bug` → `fix`, `chore` → `chore`, `spike` → `docs`. The agent overrides type and scope
when the content calls for it (`--type ci`, `--scope taskrail`, `--breaking` for `!`).

## Acceptance criteria

1. `review <ID>` run inside the task's branch reports the target (the backlog's `mainline`) and
   the head (the task branch); run on any other branch it exits 5 without fetching.
2. It refuses a task that is not done on this branch (exit 5), since review follows closing.
3. With `fetch` on it runs `git fetch <remote>` and reports it; with `fetch = false` or
   `--no-fetch` it does not. A failed fetch exits 2.
4. With `rebase` on, `rebase_onto` is `<remote>/<mainline>` when that is ahead of or equal to
   the local mainline, the local mainline when it is ahead, and whichever exists when only one
   does. When they have diverged, `rebase_onto` is null, `diverged` is true and it exits 5.
   With `rebase = false`, `rebase_onto` is null and the reason says so.
5. `--publish` pushes the task branch when `push_task_branch` is true: a plain push when the
   remote has no such branch, `--force-with-lease=<branch>:<remote sha>` when it does. With
   push disabled it pushes nothing and returns the push command instead. A rejected push exits
   4.
6. The title renders `{type}({scope}): {subject} ({id})`: type from the kind's `commit_type` or
   `--type`, scope from `--scope` or config and omitted with its parentheses when empty, `!`
   with `--breaking`, and the subject being the task title with its first letter lowercased
   unless the first word is all capitals.
7. The description names the task and its artifact, and ends with a `Reopens: <ID>` trailer
   for each task the branch reopened (found with `git log --grep='^Reopens: '` over the
   branch's own commits), so the trailer survives a squash merge.
8. Links for `github`, `gitlab` and `gitea` match the verified formats above with
   percent-encoded values; `forgejo` links to the compare page; `url_template` is filled from
   its placeholders; `none` or an undetected host returns no link and exit 0.
9. The remote URL forms `git@host:owner/repo.git`, `ssh://git@host[:port]/owner/repo.git` and
   `https://host/owner/repo[.git]` all yield the right web address and repository path,
   including GitLab subgroups.
10. The core skill's close and hand-off steps use `review` instead of their current manual
    fetch, rebase and push instructions, and the commit-message section states that with
    squash merges the pull request title is what reaches the mainline.

## Affected areas

- `tools/taskrail/src/taskrail/` — a new `review.py` (remote parsing, base selection, title,
  description, links), the `review` command in `cli.py`, `[review]` and the new push default in
  `config.py`, `commit_type` in `kinds.py`, the core kind descriptors, and the default config
  written by `install.py`.
- `tools/taskrail/src/taskrail/skills/taskrail/SKILL.md` — close, hand-off and commit messages;
  installed copies refreshed with `taskrail upgrade`.
- `tools/taskrail/tests/` — tests for each criterion, using a bare local remote.
- `tools/taskrail/DESIGN.md` and `README.md`.
- This repository's `CLAUDE.md` — the merge convention: squash, Conventional Commits title,
  component as scope, task ID at the end.

## Out of scope

- Creating the pull request through an API or `gh`/`glab`: the link needs no credentials.
- Labels, reviewers, draft state, GitLab push options.
- Bitbucket and Forgejo title prefill: the first is unverified, the second unsupported.
- Workspace creation's own base choice (T001 friction F2), which stays in T013.
- The merge driver (T004).

## Open questions and risks

- **Repositories installed before this change** keep whatever `push_task_branch` their config
  states. This repository states `false` explicitly, so it would still not push until changed.
- **Pushing is outward-facing.** With the new default an agent publishes the task branch at
  every close. The skill will say so in the hand-off report.
- **Squash keeps only the title and description**, so a reopen's trailer must be in the
  description; this relies on the host being set to use the pull request title and
  description as the squash commit message.

## Decisions at the plan gate

- The plan is approved as written.
- `review` requires the task to be done on its branch: reviewing follows closing.
- This repository's config switches `push_task_branch` to `true`, matching the new default.
