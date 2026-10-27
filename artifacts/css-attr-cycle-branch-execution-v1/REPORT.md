# Local-branch attribute cycle observations

Both leads reproduce on the pinned local Nightly build. Every case row, including control values, repeated reads, expected values and mutual-cycle participants, is identical to its installed-release row. The user agent differs as expected; no source-to-binary refinement claim is implied.

| Probe | Cases | Spec disagreements | Passing controls | Observed outer exit |
|---|---:|---:|---:|---:|
| Raw nested attr | 13 | 5 | 8 | 0 |
| Used bare/unit attr fallback | 13 | 7 | 6 | 0 |

Raw cases still yield abc where the current spec predicts literal strings. Used-fallback self/mutual cases yield red, including red for both mutual participants, where the spec predicts invalid custom properties and the consuming green fallback. The sealed original audits retain full spec traces, the conflicting raw-nested WPT history and comparison with prior fixes 7822bb6 and e3ba54f. These observations establish that those prior fixes have not eliminated these cases on this branch. No accepted fix, new bug count or security classification is asserted.

Both runs used HEAD 87445004c1ae44d9c1e2873b91f01414cf75cbb2 with unchanged pinned firefox/XUL, application/platform metadata, three native source files, probe bundle and audit references. RESULT.json contains before/after identities and all raw rows. Separate FILES.json manifests seal both runtime directories. REFERENCES.json pins them and the source bundle; COMPARISON.json records the exact row comparison.

The parent authorized these two sequential browser runs after GTests completed. Raw outer session 78614 terminated with observed exit 0 (9ef74a); used outer session 79828 likewise exited 0 (5c6c03). Outer logs are raw.log and used.log. EXECUTION.json retains launch and terminal tool evidence.

Both wrappers reported stable=true, errors=[], launcher_exit=0 and profile_removed=true. Independently checked exact executable/profile parent matches are empty, and both owned profile paths are absent (CLEANUP.json). The initial independent ps check was denied in the filesystem sandbox after result inspection; the authorized read-only retry succeeded. This does not invalidate either wrapper's already successful cleanup. No claim is made about independent exits for every child process.

Browser access has been handed back to the parent. No further launch, shared build/test command, native/live-WPT edit, index/HEAD change, ledger update or canonical Lean edit occurred. WPT candidates and separate repair proposals remain artifact-only in css-attr-cycle-branch-probes-v1. Preserve the existing raw-cycle WPT oracle pending explicit adjudication.
