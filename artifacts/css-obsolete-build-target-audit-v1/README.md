# Completed review-cache cleanup audit

Twelve noncanonical Lean review caches are supported cleanup candidates, totaling 8,578,400,256 allocated file bytes (7.989 GiB). No deletion has been performed. Each exact path below has a recorded successful owner terminal, authenticated retained source archive and verification report outside the cache, and only Lean compiler-product extensions. No symlink was found in a selected target. REPORT.json records directory device/inode, file counts, allocated/apparent sizes, extensions and retained evidence hashes.

All paths have the prefix `artifacts/css-spec-lean/.lake/research-review/` and suffix `/.lake/build`.

| Review directory | Allocated file bytes | Completed session |
| --- | ---: | ---: |
| `0f1f56b` | 744,189,952 | 31963 |
| `13c41ee` | 690,012,160 | 55695 |
| `7f23946` | 773,648,384 | 56156 |
| `b818a9a` | 720,658,432 | 7918 |
| `e2ee3de` | 660,295,680 | 31934 |
| `ee116c8` | 760,369,152 | 24310 |
| `fba53c4-retry-v2` | 637,763,584 | 40134 |
| `anonymous-layer-candidate-v1` | 663,035,904 | 55434 |
| `global-condition-candidate-v2` | 693,166,080 | 41554 |
| `import-layer-candidate-v1` | 723,566,592 | 4580 |
| `rollback-layer-candidate-v1` | 747,716,608 | 76494 |
| `author-sheets-candidate-v1` | 763,977,728 | 70734 |

The five named candidate copies initially had archive-pending bindings. This audit joins each to its later accepted archive via the same producer hash and equality of every recorded verification vector, then authenticates the accepted source tar. The separate successful `fba53c4-retry-v2` cache is backed by completed session 40134 and the authenticated original source archive. The original `fba53c4/.lake/build` remains excluded exactly as before; its failed cache is not selected. The interrupted `global-condition-candidate-v1` cache (336,556,032 bytes, exit 130) also remains excluded.

Read-only audit 060c01/0 authenticated the retained evidence and measured the selected trees. Process observation dd02dc/0 found no Lean/Lake command, command targeting the review directory, or process cwd within it. This is point-in-time command/cwd evidence, not an exhaustive open-file proof; root must repeat process/open-file and identity/content checks immediately before removal. The audit process and its ancestors alone were excluded from command matching to avoid matching the search expression itself. The initial sandbox ps call was denied; public local process reads then succeeded under read-only escalation.

Canonical lakefile/manifest contain no research-review dependency references, and their hashes are retained. Canonical .lake/build, .lake/packages, toolchains, the Creusot tool build, main objdir-full, and active log runtime/backups were excluded. These twelve completed historical review caches are not current canonical dependency targets. All sources, tar archives, producer/binding/process records, verification reports and browser evidence stay outside the proposed deletion paths.

All five earlier isolated Servo targets remain absent, with TARGET-CLEANUP receipts and source/log/generated evidence retained. Their runtime 2–5 receipts record 773,038,080 allocated bytes already removed. All 198 Lean review targets from the earlier css-cache-cleanup-v1 plan also remain absent. Recent isolated model receipts report successful scratch cleanup; no further target was found there.

Root should delete only the exact eligible .lake/build paths after independent review and fresh checks. Do not delete source/verification parents or use a broad wildcard. Sizes describe allocated file blocks and do not promise an identical free-space increase on APFS. No source, Git, epoch, application or active process was mutated.
