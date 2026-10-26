# Hidden ordinary-block and column query cost fixture

**Source-only benchmark proposal. Not browser-calibrated or native acceptance.** Root owns any browser/build execution. This measures the new skipped-block marking and table-provider query gate, independent of hidden flex items and hidden absolute-positioned targets. A visible absolute fixture host supplies stable page coordinates only.

## Work and exact default roster

Three observers (`block` nested percentage leaf, first `td`, first `col`) × visible/hidden × 1/32/128 ordinary block siblings give 18 configurations. One warmup round is excluded; five measured rounds produce 90 rows. Configuration order rotates each round. The complete acknowledged progress roster has 220 events. Each batch uses a fresh fixture; no browser or source variant is inferred from a label.

The fixture derives from the retained ordinary-block diagnostic. Each branch is 32px tall, with two equal fixed-layout table columns or a 50%-width ordinary leaf. At outer width160/168, the expected selected rectangle is `[10, 10 + 32*index, width/2, 32]`. Tables have no borders, spacing or padding. All targets are visibly calibrated at160→168→160 before hiding. No percentage height, transform, zoom, flex, hidden OOF target or extreme coordinate is involved. Root must treat any actual visible-calibration failure as an invalid fixture/run, not a candidate defect.

Recovery phase: hide if selected, alternate the outer width 16 times, and read only the outer rectangle to flush parent layout. Then read the last branch first and immediately repeat the same target. Full rectangles and exact bucket/iteration/index/width identities are retained for both reads. Mutation+outer-flush timing is separate from first/repeat timing. Restoring visibility and width must recover every target's full rectangle. Choosing the last root also avoids measuring only the first line child.

Hot phase: build a separate fresh fixture at fixed160px, visibly calibrate every target, hide if selected, and calibrate every target again before timing. No subsequent style/DOM write or event-loop yield occurs during either hot batch. `hotSame` repeats the last target; `hotCycle` cycles every target. Each batch executes16,384 getBoundingClientRect calls, checks all four values and contributes all four to a deterministic checksum. Both modes are checked again afterwards. The default measured total is2,952,000 timed geometry calls:2,880 recovery reads and2,949,120 hot reads. Calibration/outer reads are additional untimed work.

Hot timing includes ordinary JS loop, comparisons, checksum and DOMRect allocation overhead, held identical between variants. It does not isolate the C++ predicate. Several milliseconds per batch are expected at this call count, but no timing is asserted in advance; zero/near-quantum results remain unresolved. Geometry correctness is a gate for clean setup and is also observed per hot read. A baseline that returns stale recovery geometry is doing different work: its smaller first-query time must not be interpreted as a speed advantage for correct layout. Recovery mismatch counts are retained rather than converted to PASS.

## Bounded controls and knobs

CONFIG.json explicitly pins sizes, iterations, hot read count and rounds. The validator permits at most3 distinct sizes in1…256,0…2warmups,1…5measured rounds,1…32recovery iterations and4,096…65,536hot reads, with at most300progress events and45seconds fixture deadline. Default90 measured rows and18 groups stay small. Change configuration only in a newly pinned reviewed copy; no unrecorded URL override is accepted. There is no adaptive stopping that would give different work to different source variants.

Visible block/td/col groups measure ordinary clean query controls. Hidden hot groups are mutation-free, clean, full-geometry controls. Hidden recovery groups distinguish conservative marking cost from already-incorrect baseline publication. First/repeat samples are individual coarse measurements summed across16rounds; hot samples time whole fixed batches, reducing quantization loss. Fixed browser-phase order, warmup, local scheduling, headless execution and timer quantization still limit comparisons. This is a bounded local diagnostic, not CI performance proof or a general no-regression claim.

## Runner and source ownership

run.py and cleanup.py derive from sealed cost-v4 FILES `f979247dcb21cbe442ef246792fed70c24840cd919faf2afc482d2adce792d98`. Cleanup is byte-identical. Runner process ownership, fresh profile, original POSIX group/session authentication, bounded TERM/KILL handling, profile removal, terminal/no-live-group receipts, loopback server, source/binary pinning and early startup environment are unchanged. No preference is added. MOZ_DISABLE_SAFE_MODE_KEY and MOZ_DISABLE_UPDATE_PROCESSING remain1; inherited MOZ_SAFE_MODE_RESTART is removed and recorded.

The small runner delta adds an external manifest/closed-roster check before behavior, bounded config validation before launch, and exact persisted progress validation before summary acceptance. REQUESTS, SPAWN, STARTUP-ENV, RESULT, logs and cleanup details are retained on failure. Parent experiments must additionally join source pins to their own expected variant and reject integrity/cleanup ambiguity; runner exit0 is not native acceptance. Escaped processes outside the original group/session remain outside the cleanup claim, as in v4.

Root-only command after review, using the external FILES hash and a fresh output outside this directory:

`python3 -I -S artifacts/css-hidden-query-cost-v1/run.py --manifest-sha FILES_SHA --binary ABSOLUTE_FIREFOX_BINARY --output ABSENT_OUTPUT --label baseline --pin ABSOLUTE_NATIVE_SOURCE`

Repeat `--pin` for each source owned by the parent campaign. The runner also pins Firefox, colocated XUL and its six execution inputs. It does not install source, build, stage or commit anything. The original75-second runner deadline remains; missing or partial observations must not be called a native hang.

## Static validation

Node syntax checking and Python AST parsing pass. Synthetic validation exercises the exact90-row/default call roster and eight corruptions: wrong identity, calibration, query order/count, hot checksum/read count, negative timer and missing clean calibration. An intentionally wrong recovery rectangle is accepted as retained mismatch evidence. These tests verify receipt handling, not browser geometry or performance. No browser/build/compiler/Git or live native/test mutation was performed.
