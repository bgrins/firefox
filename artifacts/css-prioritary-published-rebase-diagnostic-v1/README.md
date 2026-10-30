# Published-baseline rebase and interrupted-verification diagnosis

The interrupted V4 run does not establish which index field changed. The frozen traceback locates the failure inside `verify_intermediate`, comparing its root `after` and `before` snapshots. This happens after the forced-colors lane, before the next lane starts; it is not the outer `phases.run` comparison or a CSS assertion.

`index_state` returns five fields: HEAD, staged-entry digest, cached-diff digest, working-diff digest, and raw-index hash. It samples them through separate Git commands, so it is not an atomic snapshot. The working-diff digest covers the whole tracked checkout, including tracked artifacts, rather than only native files. The separate native-path set check does not narrow that digest. All six retained successful snapshots, from the completed build through forced-colors POST, are equal. The failing pair was not retained. The nested repository's final comparison was not reached. The subsequent restoration raw-index change cannot identify the earlier differing field. A concurrent writer, a raw-index change, or a working-tree difference remains a hypothesis, not a finding. The helper already sets `GIT_OPTIONAL_LOCKS=0` and disables fsmonitor for its Git commands; those settings do not prove absence of external writes.

The run built successfully and retained ordinary 61 PASS / 7 FAIL / 8 OK and forced-colors 2 PASS / 1 FAIL / 2 OK. Both completed lane comparison gates passed. Appearance was unstarted. Independent review verified restoration; root separately removed the retained backup. This is partial experimental evidence, not a complete 77-case result or accepted native repair.

## Minimal diagnostics

`intermediate.py` and `INTERMEDIATE-DELTA.patch` add an optional failure recorder before the existing root and nested equality assertions. They retain both complete snapshots and the exact differing field names. Equality remains mandatory, including raw-index equality. There is no retry, normalization, or automatic epoch refresh. Successful return values and checks remain unchanged.

`OWNER-INSTRUMENTATION.patch` illustrates the only runner change needed: pass a recorder that exclusively writes `INTERMEDIATE-INDEX-MISMATCH.json`, including the verification-call ordinal. It applies to the frozen retry owner for review; it is not a current-state-admitted execution recipe. The normal traceback remains necessary to identify the caller. A recorder I/O error also fails the run; it cannot admit a mismatch. This diagnostic identifies changed observations, not the process responsible. Further process or command-level instrumentation should follow evidence, rather than guessing the cause now.

## Cascade-only proposal

The three currently published source files were read without modification and matched the sealed narrow combined postimages:

| Role | Published preimage | Proposed postimage |
| --- | --- | --- |
| custom_properties.rs | bb13b61a… | unchanged |
| properties/cascade.rs | 5b7204f8… | a6f4e611… |
| properties_and_values/value.rs | 6624c2a5… | unchanged |

`native.patch` applies the experimental selected-declaration traversal above that published baseline. It changes only `cascade.rs`. Construction is exact: apply all five previously published image-enablement hunks to the frozen V4 cascade. `V4-IMAGE-DELTA.patch` exposes that relation. The COLOR-or-IMAGE deferral, both selected-value/default eligibility hooks, and the image component classification are retained. V4's reached rollback handling, Appearance self-gate exclusion, ForcedColorAdjust dependency and prepared-priority/SCC handling are otherwise unchanged. This composition is source-checked, not a proof of combined runtime semantics.

Forward/reverse patch replay with zero fuzz and the pinned Rust formatter passed in owned removable scratch. Ten field-level mismatch controls retain diagnostics and reject; another ten reject without a recorder. A consumed-input mutation still rejects before equality, and successful snapshots are unchanged. No compiler, browser, Git command, source write, index operation, epoch change, or current-state guard was executed by this package's checker.

## Next controlled experiment

Build and observe the published baseline first, then this cascade candidate with the same frozen 77 cases and real Zoom capture. The old original77 build predates the published color/image repairs; it is historical comparison evidence, not a current-HEAD baseline. Recompute the original-PASS preservation set and target transitions from the new baseline. Keep all ordinary FAILs and partial-lane evidence. Also retain the exact registered image/font cases already in the suite and compare their full signatures; preservation of code hunks alone is not runtime preservation.

Restore the published three source preimages and the actually admitted pretrial application, whose published role is `built:false`. Do not restore the retired held-provider overlay or claim the old restored application was rebuilt from current HEAD. A new owner needs fresh current source identities, control hashes, application/backup inventory, consumed-input closure and publication-aware admission; the old whole-file restoration and held-provider assumptions are invalid now. Reuse the existing lifecycle with these bounded changes, not another recursive historical owner chain.

Root reported 29,096,604 KiB available. Against the historical 1,008,605,176-byte backup, this is 204,711,928 bytes below the unchanged 27 GiB post-backup floor. Re-measure current free space and actual backup size before launch, allowing additional build growth; do not reduce the floor. Any cleanup must be separately authorized and limited to proven unused owned caches. This package performs no cleanup and binds no future runtime or current epoch.
