# Keyframe group-order runtime preparation review

No blocker found for the bounded reversible experiment. Reviewed root-authored runner inputs are bound to `RUN-INPUTS.json` SHA256 `e9eb714152ef47eb67ab604acc4f207ed151428b3c3bc46ae40255d28c215317`, with execution HEAD `a4ead15121655260247a504eef4aae28ae6c22b1`.

This is an independent review of the root-authored runtime wrapper. The reviewer authored the copied native candidate and therefore does not claim independent authorship review of that candidate. No browser/build/native/Git operation was executed by this review; the executed checks authenticate inputs and run synthetic parser controls only.

`review.py` independently authenticated all 20 runtime inputs, all three before/after source roles, 32 test-source/metadata presence pins against the pinned Git revision, preserved helper origins, and retained-build source/config linkage. It reconstructed the callback inventory from the preceding snapshot baseline: 85 existing callbacks plus the new interior/logical ordering case, giving 86 assertions and nine harness records. It independently verified the exact expected baseline vector and reran 25 rejection controls. Receipts are `preparation.json` and `parser-controls.json`.

## Variant installation and retained baseline

Exactly three tracked files are installation roles. Only the WPT HTML has `install_both: true`; both native `GeckoBindings` files are candidate-only. Copied candidate bytes match the authored candidate capsule. Metadata is absent from roles and present in test pins: both modes retain the original metadata. Thus the original expected failure becoming an unexpected PASS is permitted only as an explicitly named actual-status improvement; final delivery removes its stale annotation separately.

Baseline uses the retained clip-fix browser without a rebuild. The runner checks its three binary/config hashes and a clean tracked tree/index, then snapshots the full application and configured extras. The retained receipt is authenticated and its native pins agree with execution HEAD. Root separately verified that intervening commits contain no production-source changes; this review's receipt linkage does not independently reconstruct the compiler's complete dependency graph.

Candidate mode applies the two native edits and identical WPT bytes, performs the actual bounded `mach build binaries -j6`, records build source/config/binary hashes, and samples the built application. All existing nine pages run with one WPT process, headless. The two temporary missing-pseudo fixture pages from the previous experiment are excluded; `fixtures` is empty.

## Exact comparison gate

The baseline must have exactly the frozen status vector: 75 PASS, 11 FAIL, and nine OK harness endings. Those failures include seven existing `target.html` failures, two custom-property inventory failures, the original ordering failure, and the added logical/interleaved ordering failure. Attribute dependency (12) and named-range (6) callbacks are all expected PASS.

The candidate must change exactly the two named ordering assertions from FAIL to PASS: 77 PASS, nine FAIL, and nine OK harness endings. The comparator uses `(record kind, test, subtest)` keys and rejects duplicate rows, so null-subtest assertion/harness collisions cannot overwrite observations. Unchanged assertion and harness messages must match; only the two intentional improvements may have different messages. Expected-status metadata is not substituted for actual statuses.

The strict parser checks the exact callback/page inventory, paired starts/ends, one complete suite, valid callback statuses, OK harness endings, assertion-count bounds, and duplicate JSON keys. Crash and ERROR/CRITICAL log records are rejected. WPT process exits 0 or 1 are allowed because baseline has an unannotated new failure and candidate retains the old annotation; neither allowance bypasses raw-status/lifecycle checks. Full command logs still require inspection for build/infrastructure diagnostics outside the structured WPT stream.

The draft initially compared only statuses and lacked the baseline status vector. Root added the exact vector and unchanged-message comparison before freezing. No frozen input was modified by the reviewer.

## Restoration and limitations

The unchanged process helper starts owned process groups, logs lifecycle receipts, terminates/reaps remaining group members, and requires group absence before restoration. If that cannot be established, backups remain and restoration is deferred. This does not prove absence of descendants that deliberately escape the owned process group; no such behavior is assumed for this bounded build/WPT workflow.

Source writes are recorded for either variant. Restoration checks the just-written hashes before restoring the original copied bytes, then verifies all original source hashes, HEAD/index, tracked cleanliness, test pins, and mozconfig. The full application scan covers files, links, directories, modes, and contents; extras are restored independently. Backups are removed only after verification. Filesystem inode/hardlink identity and the whole objdir are not promised to be restored. Exception, cancellation, failed build, parser failure, and comparison failure paths enter the same restoration block once the mutation transaction begins.

This remains an exclusive local transaction: no other builder, source editor, or application updater may run against the same source/app during the experiment. The capsule lock prevents duplicate instances of this runner, not every external writer. Root agreed to hold HEAD/index/native/browser state through both runs and review.

Optimized runtime evidence can support this narrow array-order repair if the gates pass. It does not establish broader performance or debug coverage, nor satisfy the separate missing-pseudo CSSOM repair's debug/freshness requirements. Actual raw results and restoration will be reviewed in a separate addendum after both runs; this preparation report makes no runtime acceptance claim.
