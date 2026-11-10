# Collection-local stylesheet media snapshots

Distinct stylesheet wrappers can share parsed contents while having different media conditions. The previous media-change query looked up a contents-wide result, so an always-active duplicate could make a conditional link appear already active. The page then retained stale styles after a viewport change.

The repair stores an optional prior applicability result on each stylesheet collection entry. Cache lookup refreshes every entry before selecting cached data; direct and UA rebuilds write the result before nonmatching or repeated-content early returns. New entries start unknown. A failed rebuild invalidates the whole affected collection's snapshots, and an unknown result refuses the unchanged-style fast path. Nested import/media rule keys and iteration remain unchanged.

## Specification and source review

The HTML media-attribute processing rule requires an external resource to apply when its own media value matches and the other relevant conditions hold. Equal resource URLs do not merge those conditions. The retained `spec-media.json` gives the queried passage and content hash; the WPTs also cite cascade ordering for the later competing declarations. Setup assertions check viewport size, media matching, source order, resource loading and URL identity.

Source review covered both cache rebuild branches, cache hits that skip already committed entries, direct and UA rebuilds, and both document and shadow-author query callers. `SheetCollectionFlusher` reborrowing shares the same mutable entry slice and copies its flags; it does not flush the collection again. Failed rebuilds clear snapshots rather than publishing observations against discarded data. This does not prove complete allocation-failure recovery or native memory safety.

The three-file patch was prepared in the preceding `css-shared-sheet-media-rebase-20261110-v1` commit. Its exact preimages still matched the current branch, including the root-identity and cascade rollback repairs. Installation applied it in an owned temporary directory, checked all candidate hashes, and copied only those bytes into the live files. That temporary directory was removed.

The same patch applies without fuzz to the three source files at Searchfox-indexed revision `47f2a88cbab9072c8f8f156494b92d6891e488fb`. `upstream-result.json` records source and result hashes. This is source applicability, not an isolated upstream build or runtime comparison.

## Current native comparison

The baseline browser's hashes matched the completed root-identity build. The two regression pages reproduced four failures and four passes, with both harness endings OK. Separate controls passed 39 assertions and one rendering reference test. The controls cover dynamic nested media, iframe media-query events, cross-document computed styles, and false-supports import layer order. The installed Nightly also reproduced exactly the four target failures, with executable and application hashes unchanged across its run.

The candidate build used `mach build binaries -j6` in the existing object directory and exited zero. The retained log includes the existing Mach progress reporter's `KeyError: export`; it did not prevent native build completion. Scoped Rustfmt and WPT lint exited zero. The build record pins the three source files, five regression resources and installed binary hashes.

The candidate passed all 47 assertions and the rendering reference test, with five OK harness endings and one PASS reftest ending. All 43 previously passing assertions stayed passing; the four target failures became passes. Source, test and binary hashes matched the build record after execution. See `candidate-result.json` and the raw WPT streams.

The delivery is three Rust files and five WPT resources: two runnable pages and three CSS supports. These are manifestations of one repair. They do not establish a separate bug for every failing assertion, every mutation step, or each document/shadow scope.

## Recheck saved evidence

Run `python3 -I -B check.py` from this directory. The checker authenticates retained files, joins callback identities across roles, requires preservation of every prior pass, and checks all target improvements and harness endings. It does not rerun Firefox or prove the recorded build executed the stated source. The build/test commands and their actual outputs are retained in the logs.

The older publisher is pinned to a historical ancestor and is left unchanged. This continuation uses the current source hashes, explicit staging, and signed local research commits before the native repair. No Try push or external submission is part of this work.
