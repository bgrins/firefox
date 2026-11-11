# V3 target isolation preparation

V2 successfully resolved the isolated lock, compiled and ran its baseline plain program. The instrumented build reused that same binary: both binary hashes were identical, both package-clean commands removed zero files, and the instrumented build completed in 0.00 seconds. The unchanged comparator rejected the missing tokenizer traces. This is failed instrumentation/build isolation, not a native/model lexical disagreement.

V3 uses a distinct initially absent Cargo target directory for each of the eight plain/instrumented labels. It derives the executable path from that label’s target and removes the ineffective package-clean calls. Command receipts include working directory and Cargo target path; binary receipts include target and executable paths. All temporary target directories remain within the owned temporary workspace and are removed on completion or exception.

`origin/runner-v3.patch` records the precise runtime delta. V2’s manifest, runner and failure receipts are retained. The dependency-resolution recipe, source/vendor/tool pins, strict model schema, unchanged comparator, mutation definitions, expected first witnesses, corpus, borrowed model rows and incremental receipt retention are preserved. No native command runs during this v3 source preparation. Root owns the full gate after source review.

The source-only checker retains the same 18 input pins, 437 source objects, 180 actual model rows, 18 schema refusals and four synthetic metadata controls. No new proof or CSS coverage claim is added. Native sensitivity remains unestablished until all pairs compile/run and the unchanged comparator rejects the three intended mutations at their exact witnesses.
