# Traversal v4 standalone source packaging

**SOURCE_PACKAGING_PASS_NOT_NATIVE_ACCEPTANCE.** The reviewed four-file native proposal plus the unchanged four-case untransformed-edge WPT checks, applies and reverses on both requested immutable bases in disposable directories.

| Base | Applied result |
| --- | --- |
| Local parent `99a9ca84f08370c1797720db8688bcb3747f6985` | All four native files exactly match proposal-v4/capsule candidate snapshots; WPT matches the executed v3 input. |
| Pinned upstream `5d41bc07dec206ad511c2689f4b01ab74516c308` | The same patch applies unchanged. Three native files and WPT match the local candidate; nsLayoutUtils.cpp preserves its unrelated upstream difference. |

The upstream snapshot is the requested October checkpoint, not a claim of current upstream freshness. Source applicability does not establish isolated runtime independence, correctness, performance or native acceptance. No isolated build/browser run was performed here.

## Exact inputs

- Native patch: `f4bdac1de8d9256fe3e148e1d36a88b5d5ddb7cc17daabe5b0df4af04c88b8f9`.
- Combined candidate-native-wpt.patch: `202a8ff8772bbcdae1c9b28f0016c4e1b0929e5ba9b5c9cb6e8ef6060840e6e0`.
- Unchanged WPT: `98514c1f71bd2d0e4af78a704a82b67175b1a33479bcf440de67f3e39baeb76e`.
- Authenticated proposal-v4 FILES: `9cb90bc4e1739c482b2b20785389b002cfeb297bc958b42684e58d37fa4e4770`.

The native patch is byte-identical to the sealed producer proposal. Its four-file prefix is followed by the unchanged WPT new-file hunk retained in v3 source packaging. The WPT source is authenticated against sealed runtime-v3; it runs two axes by two sizes, four tests. The ongoing parent-owned v4 experiment is not an input to this source-only result.

| File | Added | Removed |
| --- | ---: | ---: |
| layout/generic/nsIFrame.cpp | 195 | 83 |
| layout/generic/nsIFrame.h | 10 | 1 |
| layout/base/nsLayoutUtils.cpp | 44 | 3 |
| layout/base/nsLayoutUtils.h | 6 | 1 |
| testing/web-platform/tests/css/cssom-view/getBoundingClientRect-untransformed-edge-precision.html | 42 | 0 |

There is no DOMRect or research-file change in the five-file patch. The earlier DOMRect repair's role in shared runtime evidence remains separate; omission from this source patch is not proof that runtime behavior is independent of it.

## Preserved base difference

The local nsLayoutUtils.cpp contains a separate ComputeConcreteObjectSize early-return change removing the no-intrinsic-ratio condition. The upstream base retains that condition. Both base and applied comparisons are saved under base-differences and show the same unrelated change, with only hunk locations shifting. This proposal does not import it into the upstream result.

## Verification

GIT-READS records read-only git show and ls-tree queries at the two exact commits. Both bases lack the WPT. NATIVE-WPT-CHECK records check, apply, reverse-check and reverse exit 0 on each base, per-file hashes/deltas, candidate comparisons and byte-exact reversal, including test removal. Applied snapshots are retained. Temporary directories were removed on completion.

Run `python3 -I -S verify.py --files-sha256 <external FILES hash> --replay` to authenticate the closed artifact and repeat private source-only apply/reverse checks. Replay uses retained snapshots and does not touch the main checkout or index. All producer, v3 packaging and runtime-v3 outer payloads were authenticated before use. No compiler, build, browser or main Git/index/native mutation occurred.
