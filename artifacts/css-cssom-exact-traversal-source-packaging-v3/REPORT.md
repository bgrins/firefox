# Traversal v3 standalone source packaging

Status: **SOURCE_PACKAGING_PASS_NOT_NATIVE_ACCEPTANCE**.

The exact reviewed four-file native patch is combined with the unchanged four-case runtime-v3 WPT. The resulting five-file patch checks, applies and reverses cleanly against both requested immutable bases in private temporary directories:

| Base | Source result |
| --- | --- |
| Local pre-experiment99a9ca84f08370c1797720db8688bcb3747f6985 | All four native outputs exactly match proposal-v3 candidate snapshots; WPT exactly matches the runtime input. |
| October14 checkpoint5d41bc07dec206ad511c2689f4b01ab74516c308 | Same traversal patch applies without adjustment; three native files and WPT match the local candidate exactly. nsLayoutUtils.cpp retains an unrelated existing base difference. |

The October14 checkpoint is the requested local upstream snapshot. No network freshness claim is made. No full builds or browser runs against the isolated upstream source were performed here. Clean application demonstrates source independence from intervening project patches; it does not establish functional independence, performance or native acceptance.

## Exact patch and inputs

- Native proposal prefix SHA-256:2aa367b0531bf96a881ca62b8b89b9438f4bfcbe83bdc10fe2c3ef753dc1b9c1.
- Combined candidate-native-wpt.patch SHA-256:50dff765e3892ec22015c726be592aaa3d6f283913131c20789be46427cd2a33.
- Unchanged WPT SHA-256:98514c1f71bd2d0e4af78a704a82b67175b1a33479bcf440de67f3e39baeb76e.
- Authenticated proposal-v3 manifest:7f38aefc3a57825eff20508e95d183ae571514f128958bb2d0033228e134d6b6.

The native portion is preserved byte-for-byte; only a new-file WPT hunk is appended. The WPT runs two axes by two sizes, giving four tests. All calibration and exact edge assertions are unchanged. The runtime-v3 directory was an active experiment when copied; RUNTIME-PREPARATION and RUNTIME-BEFORE are source-identity receipts, not a sealed runtime outcome or acceptance claim.

| Changed file | Added lines | Removed lines |
| --- | ---: | ---: |
| layout/generic/nsIFrame.cpp |192|83|
| layout/generic/nsIFrame.h |10|1|
| layout/base/nsLayoutUtils.cpp |44|3|
| layout/base/nsLayoutUtils.h |6|1|
| testing/web-platform/tests/css/cssom-view/getBoundingClientRect-untransformed-edge-precision.html |42|0|

The five-file roster and line counts are identical for both bases. Both bases lack the test; applying creates exactly that file, and reversing removes it. Source bytes for each base were obtained using read-only git show on the named commit, with metadata/hashes recorded in GIT-READS.json. No main index or working-tree modification occurred.

## Unrelated base difference

The local nsLayoutUtils.cpp has a separate ComputeConcreteObjectSize change removing the no-intrinsic-ratio condition from its early return. The October14 version still has that condition. The traversal patch neither imports nor removes it. Both original and applied base-to-local diffs are retained under base-differences. Therefore the upstream full nsLayoutUtils.cpp is intentionally not byte-identical to the reviewed local full snapshot, while the traversal patch itself is unchanged.

## Checks and limits

NATIVE-WPT-CHECK.json records private check/apply/reverse commands, exit codes, exact before/after hashes, local-candidate comparisons, and per-file deltas. Temporary directories are automatically removed. Applied snapshots are retained for review. The first draft checker stopped before application because git show reported an absent committed test as “exists on disk, but not in” the commit; the checker had expected a different error string. That failed check is preserved in development. The final absence check uses successful git ls-tree with an empty result, independent of temporary worktree test presence.

Run the closed artifact verifier with its supplied external manifest hash. Add --replay to repeat private source-only apply/reverse checks from retained snapshots; this performs no main-tree Git operation, compilation or browser work. Source packaging does not supersede the original mathematical/provider admissions, independent review, parent-owned correctness experiment or pending timing decision.
