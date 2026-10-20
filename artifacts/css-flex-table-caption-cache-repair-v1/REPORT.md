# Caption percentage-height cache proposal

Status: source-reviewed proposal, not compiled or browser-tested. Root owns integration/runtime. Original F1–F16, full F11/F12, and general cache freshness remain open.

## Reproduction and oracle

Authenticated all 16 root runtime payloads against FILES d014cf40cd51273f0ed6f5911b8e102b48c85e8c049a793e4c7028bae0ec9a85; independently replayed verify.py under isolated, nonoptimized Python. Release and project have exactly the same 16 observations: four stale auto-caption/percentage cases; twelve controls pass. Every initial, restoration and repetition calibration passes.

The fixed-width horizontal flex container changes height 200↔300. Its table uses height:50%, a one-line 20px auto-height caption and either center or last-baseline alignment. Fresh inner table height is 100↔150 and combined caption/table extent is 120↔170. Warm layout retains the old values. In the last-baseline cases both marker positions can agree while the table height is wrong: marker equality is insufficient.

Primary sources inspected 2026-10-20: [Flexbox §4](https://drafts.csswg.org/css-flexbox-1/#flex-items) makes the wrapper the flex item, while height applies to the table; [CSS2 §17.4](https://drafts.csswg.org/css2/#model) resolves table percentages against the wrapper's containing block; [Sizing §4.1](https://drafts.csswg.org/css-sizing-3/#percentage-sizing) resolves percentages against the containing block. The container has a definite height, zero border/padding, no stretch, and no cyclic height dependency. Caption and cell are single 20px lines, below both requested table heights. **REACHED:** changing the definite percentage basis must change the table height. The same final DOM/style fresh-layout reference additionally checks placement without hardcoding platform font ascent. webspec-index could not write its database; primary web retrieval was used instead.

## Source chain and affected caches

Full sources are copied from the runtime-pinned source, not Searchfox tip. Native patch changes only CachedBAxisMeasurement::Key.

1. nsTableWrapperFrame::ComputeAutoSize calls InnerTableShrinkWrapSize and CaptionShrinkWrapSize. With an auto-height caption it returns unconstrained BSize unless both contributions are constrained; a fixed-height caption instead exposes the changed inner height in the wrapper computed size.
2. CreateReflowInputForInnerTable passes aOuterRI.mContainingBlockSize to the actual inner RI. This basis is an input to inner percentage sizing even when the wrapper computed size is unchanged. The grid adjustment does not apply to this flex fixture.
3. SizeItemInCrossAxis calls MeasureBSizeForFlexItem, then copies measurement.BSize into the item cross size. The cached measurement Key currently stores computed size, actual logical border/padding, computed min/max BSize and available BSize, but not that containing-block size.
4. A clean equal-key cache hit returns before SetHadMeasuringReflow. Thus the final gate takes its non-measuring branch. If prior final metrics match the stale plan, padding, and definiteness, NeedsFinalReflow returns false. This gate does not separately compare the outer containing-block size.
5. Rejecting the measurement hit reflows the wrapper and its inner table using the new basis, marks HadMeasuringReflow and replaces the measuring payload, clearing old final metrics. The actual measured result now supplies the plan. NeedsFinalReflow then either reflows for content-size/relative-BSize dependency or caches equivalent measuring results under its existing guards. The proposal does not modify that policy or assert those guards universally sufficient.

The precise executed cache branch is inferred from complete source plus controlled runtime, not an instrumented branch trace. Candidate runtime remains required. This is not a claim that measuring-key equality alone proves arbitrary subtree freshness.

## Narrow repair

Add actual aRI.mContainingBlockSize (LogicalSize) to the measurement Key and its defaulted equality. Both logical components are retained because inner table sizing can consume either basis; no synthetic reconstruction from wrapper size is used. Preserve the accepted border/padding key and every other field.

Using only a transient resize Boolean would not record the old input. Disabling all table measurement reuse would be broader. Adding this input to final metrics alone would not repair the stale cross-size plan already consumed by alignment. The two-line proposal rejects the earliest unsound reuse in this reproduced measured path. It does not close non-measuring callers or all containing-block lifecycle invariants.

Cost: one additional LogicalSize per cached measurement, plus its equality comparison. Actual ABI size and performance have not been measured; no neutrality claim. Conservative invalidation for a changed but unused basis is possible.

## Test and packaging

Artifact-only table-caption-percentage-height-resize.html contains 16 tests: four repros, fixed-caption and literal-height controls, grow/shrink, center/last baseline. Each asserts initial, fresh, resized, restored and repeated inner/combined heights, then relative table and marker positions. No support skip, diagnostic-only success, or expected-failure annotation. Root must run this new WPT baseline and candidate; the diagnostic execution is not execution of this final WPT.

native.patch is based on the exact project runtime snapshot and adds only the containing-block field/initializer. An independently applicable upstream variant must likewise add only these two lines, preserving that base's existing fields (without importing the separate padding-key fix or other pending flex repairs). No Git applicability check or isolated upstream runtime was performed here.

## Formal follow-up

Prove old-key equality can coexist with a changed containing-block size and unequal independently specified table output; new-key equality implies both basis components agree, with old decisions preserved for equal bases. Model the measurement-hit → stale-plan → final-hit masking separately, retaining dirty/continuation/fragmentation/definiteness and successful fresh provider assumptions. Do not assume the desired current geometry as a cache validity premise.
