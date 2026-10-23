# Hidden-query cost: source interpretation

Status: source-only assessment of the root-reported timing signal. No runtime, compiler, browser, build, native or Git action. The active experiment owns the final measurements; the reported 0→9ms principal and 1→8ms OOF medians are inputs to this assessment, not independently recounted results here.

## What is being timed

The benchmark has 256 branches, each with three nested levels. Every recovery iteration changes subject width between160px and168px, flushes the outer subject, then times four **different** sampled leaf queries together. Sixteen iterations are summed into one row. Seven measured rows follow two warmups. There is no same-leaf immediate-repeat measurement, no first-query split, and no position calibration. A reported zero is timer-resolution-limited, not proof that the operation costs nothing.

Two distinctions matter:

1. Principal branches are fixed8px, flex:none, flex-start. Width changes do not apparently change their leaf size or position in this restricted fixture. Marking these branches is conservative work; the repair does not prove that every marked box changed.
2. OOF branches are also8px but are centered in a relative flex container. Their expected horizontal origin changes from `(160−8)/2=76px` to `(168−8)/2=80px`. All sampled widths/heights can remain8×8 while stale positions are wrong. Thus this OOF case is not an unchanged-geometry control. Exact position expectations should be visibly calibrated before drawing a correctness/performance comparison.

## Why work moves into the query

The principal repair marks principal child subtrees precisely when `ReflowChildren` skips final child reflow and placement. The OOF repair marks its subtree before hidden child reflow. A later query passes the selected frame to the hidden-content forcing machinery. `UpdateHiddenContentInForcedLayout` rejects clean targets; eligible targets cause hidden ancestors to be inserted in the forcing set and the topmost such ancestor to be queued dirty.

`ReflowForHiddenContentIfNeeded` flushes layout while that forcing set is still populated, then clears it. `HidesContentForLayout` returns false for a member of the forcing set. With ordinary successful completion, hidden early exits are therefore bypassed and normal `DidReflow` clears direct/descendant dirty flags. The next unchanged leaf query should then fail the initial dirty guard and avoid another forced pass. This is a source-conditional expectation, not a proof that every callback, continuation or child follows it.

Consequently the observed aggregate increase is compatible with **one real subtree recovery per width mutation**, amortized across the four reads. It is not evidence that four complete recoveries occur per mutation. For256 branches, a full recovery can visit far more frames than the four sampled leaves.

The initial mutation-only loop never queries hidden leaves. Once branches are dirty, subsequent marks can stop at already-dirty roots. The recovery loop instead alternates dirtying and forced completion. Similar mutation/outer-flush totals therefore do not imply similar work at the subsequent query or isolate marking cost itself.

## Do not narrow the repair to cache misses

The prior authenticated four-phase result has34 principal improvements (retained identities in PRINCIPAL-34.json):

- 16 fixed-size direct-query failures, across initial visibility, single/column formatting and four geometry APIs.
- 8 shrink cases: four item-zero and four stale-descendant observations, append/prepend and bounding/offset.
- 10 skipped-placement cases: four item/leaf insertion cases, four parent margin/padding/width/height mutations, and two anonymous-text insertion cases.

The last group is especially important: geometry can have correct sizes but stale placement without a new zero-output measurement. A miss-only mark or a test for returned zero dimensions does not cover these source paths. A proposed selective optimization would need a readiness predicate covering final placement, nested query targets, parent-relative offsets, anonymous text and all prior test identities—not just measuring-key equality. No such predicate is derived here, and no production rewrite is recommended.

## Bounded follow-up measurement

Keep the same source variants,256-branch fixture,16 mutations and visible controls. After each mutation and outer flush, record separately:

1. First sampled leaf query.
2. Immediate repeat of that same leaf, without any intervening mutation or outer query.
3. The other three distinct sampled leaves.
4. A second pass over all four leaves, still with no mutation.

Accumulate these buckets across the batch and retain every full rectangle. Add a no-change batch that repeats reads after one completed recovery, with no class toggle. Calibrate full rectangles against a separately visible peer (especially OOF x76/x80), not only sizes. Keep calibration failure separate from speed comparisons. Avoid adding layout-affecting work between query buckets.

If only the first-query bucket scales with subtree size, this supports conservative once-per-mutation recovery. If same-leaf repeats or the no-change batch repeatedly incur comparable cost, investigate forcing-set lifetime and dirty-bit producers using a separate diagnostic trace before changing code. Distinct-leaf cost alone could instead indicate incomplete subtree coverage/completion; it does not prove redundant work on the same target. Timer quantization and additional measurement overhead should be reported, with the original aggregate benchmark retained for comparison.

## Source/evidence boundaries

INPUT-PINS.json identifies exact benchmark and retained native inputs. Hidden forcing/lookup definitions were discovered via Searchfox; prior frozen query/mark/DidReflow slices are retained. This report reasons about those selected bodies, not a complete synchronous-layout callgraph. The root's running candidate/combined timings remain separate, and no final timing receipt has been asserted to exist or pass by this review.
