# T027 — autopilot decisions

Decisions the orchestrator took on the human's behalf while this task ran in an autopilot lane.
Each is recorded before it is given to the lane.

## diagnose gate

Reviewed: `docs/bugs/T027-stop-init-and-upgrade-on-an-unreadable-i.md` (commit `27c132f`) — the
real merge conflict reproduced, seven kinds of broken manifest, and the root cause in
`install.py` `read_manifest` treating unreadable and missing alike.

| # | Question | Options | Decision | Reason |
|---|---|---|---|---|
| 1 | Confirm the diagnosis | confirm · rethink | **confirm** | Reproduced end to end, including that no files are deleted and only the recorded state is lost; every observed outcome follows from the one function. |
| 2 | Which broken manifests refuse with exit 2 | all read failures · JSON syntax only | **all**: syntax errors (conflict markers, empty file), non-object values, non-UTF-8 bytes and read errors | Same function, same missing check; leaving tracebacks would fix half the defect. |
| 3 | `upgrade --force` on a broken manifest | refuse · reinstall from nothing | **refuse** | `--force` overwrites managed files; with the digests lost it would overwrite copies it can no longer tell apart from local edits. |
| 4 | A readable `{}` | keep current behaviour · new message | **keep** | taskrail never writes it and there is no state to lose. |
