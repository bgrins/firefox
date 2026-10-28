# Registered-number source transitions

Prepared transition tool; no transition has been executed during preparation. The parent owns execution after each required build/WPT phase is terminal. Keep paired HEAD `55dddb9d59e287e4fe2c1433a952fbfed5e19680` fixed through the comparison. The older captured native HEAD is authenticated separately; the tool checks every captured native HEAD blob at execution.

Run with isolated Python and an externally recorded tool manifest digest, current epoch digest, and evidence RESULT digest:

```text
python3 -I -S -B artifacts/css-registered-number-source-transition-v2/transition.py TOOL_MANIFEST_SHA head-candidate CURRENT_EPOCH_SHA /Users/bgrins/code/firefox/artifacts/css-registered-number-wpt-runtime-original-1 ORIGINAL_RESULT_SHA head-candidate-1
python3 -I -S -B artifacts/css-registered-number-source-transition-v2/transition.py TOOL_MANIFEST_SHA prototype-live CURRENT_EPOCH_SHA /Users/bgrins/code/firefox/artifacts/css-registered-number-wpt-runtime-candidate-1 CANDIDATE_RESULT_SHA prototype-live-1
python3 -I -S -B artifacts/css-registered-number-source-transition-v2/transition.py TOOL_MANIFEST_SHA pending-tests CURRENT_EPOCH_SHA /Users/bgrins/code/firefox/artifacts/css-registered-number-native-runtime-v1/prototype-live-1 RESTORATION_RESULT_SHA pending-tests-1
```

Replace all digest placeholders with independently recorded values and use the actual WPT output directory. Each output label must be new. Do not compute an expected digest from a file inside the transition itself. No command here has been run against the checkout.

`head-candidate` requires compiled, unaccepted committed-HEAD original sources, a complete preserved original WPT observation from the sealed v2 capsule, and absent owned build/WPT process groups. It installs the exact three native candidate bodies and acquires ownership of originally-clean `properties_and_values/value.rs` after verifying its HEAD bytes and epoch pin. Existing ownership records must agree with the current source role.

`prototype-live` requires compiled committed-HEAD candidate sources and complete preserved candidate WPT execution from the same capsule. It restores all 50 parked prototype bodies and applies the exact three-file live candidate, leaving 51 owned paths. A complete, preserved candidate run with failing assertions may authorize restoration; this tool grants no bug acceptance. Incomplete execution or preservation failure blocks restoration.

`pending-tests` requires the exact successful, uncompiled `prototype-live` transition receipt and epoch. Run it before rebuilding the restored prototype. It changes only `TestKeyframePresentation.cpp` to the sealed overlay, verifies the original prefix, and keeps all other 50 owned bodies unchanged. The original 20 GTests remain, with two added tests and 12 added pending-resolver calls. The intended totals of 22 tests and 34 calls are prepared inventory, not execution results.

Every mode authenticates six source/evidence packages and fourteen helper/provenance references, checks 140 preserved source pins through parked or live bodies as applicable, verifies the existing full epoch before/after, and rechecks native bytes and inode ownership before each write. ROOT/nested HEAD, entries, cached diff, index flags, nested index, untracked paths, and all unrelated pinned resources remain guarded by the existing preservation checker. Source changes update overlapping pin maps, installed identities, the native modified list/count, OWNED, ROLE and CURRENT-EPOCH. Every successful transition marks compilation and acceptance false. A build is required before the next browser/GTest validation.

The existing runtime build publisher reconstructs `registered_number_transition` and may omit the added `pending_gtest_overlay_installed` field. ROLE retains its overlay marker. A subsequent validation runner must bind the actual overlay source hash and ROLE, or preserve that field explicitly; it must not infer execution from a prepared inventory.

Writes use existing owned regular-file inodes. The tool acquires an exclusive transition lock, records preimages/plan and each completed source write, and attempts owned rollback on exceptions or handled SIGTERM/SIGINT. Rollback requires the complete original preservation snapshot and root/nested flags to match. Ownership drift blocks destructive recovery and is recorded for manual handling. SIGKILL, machine failure, or storage failure can leave a partial transition: inspect the journal and recorded ownership before recovery, never bypass a stale lock or epoch mismatch blindly.

The transition lock coordinates this tool's invocations; it is not a general build-service lock. The parent must keep builds, WPT, signing, source edits, and other epoch publishers quiescent during execution. Process and receipt checks add fail-closed guards; they do not authorize concurrent writers.

Validation: 19 original and 14 successor rejecting scratch controls, same-inode write/rollback, real sealed role inventories, Python parsing, all six package manifests and fourteen helper/provenance hashes. Scratch was removed. Main, live Git/index/binary reads, source mutations, browsers and builds were not executed during preparation. Independent review found and confirmed fixes for initially unbound ROLE/OWNED bytes and incomplete rollback flag checks. This is a prepared operational tool, not native compilation, browser evidence, or formal correspondence proof.

## Authorized signing successors

Version 1 correctly rejected the two ledger bodies updated by the signed v14 checkpoint, because they no longer matched the earlier v8 snapshot. No runtime mutation was attempted. Version 2 permits only `artifacts/stylo-bloom-tools/CURRENT-COMMITS.json` and `artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md` to use the exact successor hashes from v14 `ROADMAP-UPDATE.json`.

For each ledger, the roadmap before hash must match both its v8 source pin and committed preimage. The after hash must match the checkpoint selection. The pinned checkpoint receipt and final verification must bind signed HEAD `55dddb9d59e287e4fe2c1433a952fbfed5e19680` and preserved work. At execution, the tool additionally checks the actual live ledger, every corresponding current epoch pin, and the HEAD blob against that exact after hash. The committed roadmap, preimages, checkpoint note and finish script are verified against HEAD blobs too. Checkpoint selection, receipt and final verification are pinned continuation evidence; they were written after their referenced checkpoint's file selection and are not assumed to be blobs in that same commit.

The other 138 v8 source checks retain the original behavior, including parked prototype and originally-clean value.rs handling. The two ledgers are never written by this tool. No arbitrary successor, future HEAD, extra ledger, unpinned ledger, divergent overlapping epoch pin or altered preimage is accepted. Preparation consulted only signed/captured artifacts; actual live ledger/HEAD checks are deferred to parent execution. The recorded signing checks are authenticated evidence, not a new signature verification performed during this artifact-only preparation.
