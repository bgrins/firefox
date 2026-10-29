Disabled acceptance/signing adaptation plan; no ID, HEAD, epoch or acceptance is allocated. No signing or staging code is executed by this package. Current counts remain 145 accepted /146 tracked, with held120 excluded.

| Existing component | Minimal adaptation |
| --- | --- |
| V49 commit.py | Reuse exact helper unchanged. Supply an authenticated combined five-path patch; files has all five paths, source_pins only the four extant postimages. The helper already verifies exact staged/committed names, tree, signature and post-commit epoch. |
| V49 init.py | Preserve all16 current accepted payloads and all historical markers/transitions, including current145 source over historical144 and accepted146. Permit only held provider +three modified C++ files +tracked metadata deletion; exactly one newly untracked landing WPT. Add explicit deletion checks before generic init. |
| V49 finish.py | Preserve the research→validation→native signed chain. Add deleted-parent-blob/committed-absence assertions and five-path status check. Publish the new transition/ledger only after actual final acceptance and native receipt. Keep only held provider dirty afterward and restore563 expected untracked names. |
| V49 render_checkpoint.py and readout-v6 renderer | Replace two-file assumptions with four writes plus one deletion; authenticate source blobs separately from deletion. Append one root-authorized record only after real receipts; preserve every old145 accepted row and held120 exclusion. |

The deleted metadata path cannot appear in source_pins with null: unchanged commit.py hashes every source_pins file. Put its exact preimage in deleted_preimages, include it in files and the combined patch, and validate absence explicitly in init, final acceptance and finish. Native status must be precisely three modifications, one landing-file addition, and one metadata deletion. Before signing verify the deleted blob from the parent commit equals the sealed62fbc4d0 preimage; after signing require no tree entry or working file. Preserve the same-inode archived .ini and local recovery control preimages until the checkpoint succeeds; hash-index these without copying full epochs into research.

The promotion owns metadata absence as an explicit null pin with its installed identity/OWNED row removed. The pending epoch therefore records metadata deletion among modified native paths (this framework means non-artifact tracked changes), alongside the three C++ modifications and held provider. The source_path list itself remains the three C++ files. After the native commit only held provider remains dirty. The accepted marker must keep four current file hashes separate from removed-path/preimage history so future claim helpers never hash a deleted file.

Root execution map, after exact future bindings and approval:

```text
python -I -S -B <signing>/init.py
python -I -S -B <signing>/commit.py <signing>/research-selection.json
python -I -S -B <signing>/commit.py <signing>/validation-selection.json
python -I -S -B <signing>/commit.py <signing>/native-selection.json
python -I -S -B <signing>/finish.py
```

Use exclusive per-step logs and stop on any failure; do not automatically retry signing. Research/proof/tooling is committed before the standalone native commit. Validation holds the actual install/build/lint/final-WPT records, independent review and root-authorized acceptance. Newly completed research after V51 can be included without copying already committed packages; runtime app/binary backups and full epoch preimages stay outside commits.

Typed owns css-move-before-promotion-v1. Its concrete command interfaces are install.py <manifest> <epoch>, build.py <label> <epoch> <manifest>, and final.py <manifest> <epoch> <binding-path> <binding-hash>. Those must remain disabled until their own actual bindings. Final evidence must join saved build EPOCH/current controls/application metadata, live landing body, absent seven-FAIL .ini and full original/candidate raw replay. Required final result is70PASS/12OK/exit0, including51 named targets and19 strict controls;21 observed repairs are within one removal-invalidation workstream, not21 fixes. Historical paired child exit1 from seven unexpectedPASS remains unchanged.

The eventual message uses one reviewer list, r?#firefox-style-system-reviewers,#layout-reviewers, with a root-approved terse subject and actual newline. WPT sync bug2080017 is not a native defect-tracking ID. Shared held-provider/configured-pref limits and formal-model limits remain explicit. The separate shadow-context family remains unaccepted and outside this five-path native payload.
