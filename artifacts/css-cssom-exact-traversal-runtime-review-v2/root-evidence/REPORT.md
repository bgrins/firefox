# Existing-traversal rectangle experiment

**HOLD the native repair on local performance. The finite browser correctness gate passes.** No integer-translation patch remains installed, and no new native fix is counted.

The baseline includes signed DOMRect fix102. This experiment rebuilt that baseline before testing; it did not reuse the earlier pre-fix binary. The final reviewed four-file traversal proposal and scripts were pinned before mutation. The temporary untransformed-edge WPT passed lint. Actual-source clang-format checking passed with zero errors or warnings. Baseline, candidate and restoration builds all exited0. Mach's progress reporter emitted export-tier KeyErrors while the underlying builds completed; those logs are retained. Candidate/restoration builds reported21 suppressed warnings in unchanged platform/media files; no new layout compiler warning was reported.

## Actual correctness

The23-file suite completed74 unique subtests and the same22 OK plus1 PASS file outcomes. Baseline70 PASS/4 FAIL becomes candidate72 PASS/2 expected FAIL. Only horizontal/vertical139808.125px untransformed-edge cases change from FAIL to PASS; all four cases in that new WPT pass. The other70 subtests are unchanged, including the expected rotated-SVG-text and surrogate-indexing failures. Baseline rows and file outcomes also exactly match the earlier standalone DOM-only calibration. These are successor-v2 browser results, not borrowed v1 execution.

## Performance decision

Six fresh-profile headless runs validate36 case calibrations and252 timed batches, totaling5.04 million measured calls. Geometry, checksums, order, visibility and contemporaneous source/binary pins remain stable within each run.

| Case | Baseline before (ns/call) | Candidate | Restored baseline |
| --- | --- | --- | --- |
| ordinary depth128 |350,350|400,400|300,300|
| transform near root depth128 |350,400|450,450|400,350|
| transform near leaf depth128 |350,400|450,400|400,350|
| ordinary depth8 |150,150|150,150|150,150|

The candidate exceeds all four baseline process medians in the deep ordinary and near-root cases. This warrants another optimization before native acceptance. The timer is quantized to1ms, equivalent to50ns/call for these20000-call batches, with observed batch lengths2–13ms. Variant order is fixed, only two processes are measured per phase, and builds occur between phases. These observations do not establish statistical significance, a precise population percentage or a browser-wide regression. Restored-baseline drift is retained rather than averaged away. Direct comparison with v1 timing values would also mix a different baseline DOMRect implementation.

## Restoration and replay

All four source files were restored byte-for-byte, the temporary WPT removed, and the original-source build completed successfully. Other native inputs, HEAD and index were unchanged. Restored binaries have different hashes from the initial build; this is source/build restoration, not byte-identical binary restoration. Six temporary browser profiles were removed by the runner; the active objdir is preserved.

The original analyze.py authenticated the live restored inputs and generated the timing comparison. The additive analyze-retained.py reproduces the same comparison using retained WPT/source snapshots for main-tree inputs, so later native edits do not invalidate historical evidence. Its first attempt exposed a missing per-WPT DOMRect snapshot: DOMRect was already committed and absent from the changed-file roster. The failed parser/log are preserved. EXTRA-INPUT-PROVENANCE records copying that body from the frozen pre-experiment proposal; initial live-source joins, fixed-source receipts and every benchmark's DOMRect hash already bind those bytes. It is not described as a new contemporaneous WPT capture. The corrected retained analyzer passes. Immutable sibling research capsules named in INPUTS remain replay dependencies; historical binaries are identified by receipts and are not archived.

The external independent runtime review additionally reconstructs outcomes directly from raw events. Full graphics/native provenance and the original safe-origin/allocation/lifetime obligations remain open. The next artifact-only optimization must preserve both v1-domain inclusion and v2's deliberately expanded exact domain, old-defined matrix grouping, excluded-route behavior and the cached fallback.
