# T016 — Bump taskrail on main to 0.2.0.dev0 after the 0.1.0 tag

Kind: chore · Epic: E01 · Status: scope

## Goal

`taskrail-v0.1.0` is published on `2f8122d`. While `main` still reads `0.1.0`, any change merged
afterwards produces a build that reports itself as the release, and a consumer's wrapper would
accept it as `taskrail-v0.1.0`. Moving `main` to `0.2.0.dev0` makes every build after the tag
distinguishable from it, as the README's releasing steps require.

## Change set

| File | Change |
|---|---|
| `tools/taskrail/pyproject.toml` | `version = "0.2.0.dev0"`. |
| `tools/taskrail/uv.lock` | Regenerated with `uv lock`. |
| `tools/taskrail/tests/test_version.py` | `test_the_release_tag_matches_the_version` expects the tag of the version **without** its development suffix. Today it compares against the full version, so it would fail for `0.2.0.dev0`, although `release_tag()` drops the suffix on purpose. |
| `tools/taskrail/CHANGELOG.md` | An `## Unreleased` section above `## 0.1.0`, where the next release's entries accumulate. |

## Decisions needed

1. **`## Unreleased` section in the changelog.** Recommended: each pull request that changes
   taskrail adds its line there, so preparing the next release is moving that section under a
   version heading. Alternative: write the whole entry when the release is prepared.

## Out of scope

- What `init` pins when run from a development build. With `0.2.0.dev0`, `init` writes
  `version = "taskrail-v0.2.0"`, a tag that does not exist until that release, so a repository
  initialised from a build of `main` has a wrapper that can only run with `TASKRAIL_BIN` or a
  matching install. It affects only installs from `main`, not from a tag, and not this repository
  (pinned to `local:tools/taskrail`). Worth a follow-up if installs from `main` become common.
- Branch slugs cut mid-word at 40 characters (this task's branch ends in `-afte`). Cosmetic, and
  unrelated to the version.

## Verification

- `uv run --directory tools/taskrail pytest -q`.
- `uv run --directory tools/taskrail taskrail --version` prints `taskrail 0.2.0.dev0`.
- `.taskrail/bin/taskrail --version` in this repository prints `taskrail 0.2.0.dev0` (local pin).
- `uv build` produces `taskrail-0.2.0.dev0-py3-none-any.whl`.
