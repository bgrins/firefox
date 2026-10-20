# Flex table-caption percentage-height cache: independent source review

## Verdict

**GO for the proposed native change and paired runtime evaluation.** No source or oracle blocker found. Candidate build, final WPT pair, regression gates and final source binding remain root-owned pending gates; baseline observations alone are not acceptance of the candidate. Full measuring/final-cache freshness and the separate F11/F12 component remain open.

Reviewed shared native patch `0c17e1c0d737d02877ac87b118ed08912cfe709fc185f282cd8a553c3fb05ffa`; candidate `dd8bf5333aca62588f3960c11a0a18763e26b815fcf101c283acecd492436105`; landing WPT `a21a6559b1bda44aa1ae81681213d4f87fd9375479767910f4e2777ec7e6d47b`.

## Oracle and fixture

Independently verified current primary [Flexbox flex-item rules](https://drafts.csswg.org/css-flexbox-1/#flex-items), [CSS2 table model](https://drafts.csswg.org/css2/#model), [Sizing percentage rules](https://drafts.csswg.org/css-sizing-3/#percentage-sizing), [CSSOM resolved values](https://drafts.csswg.org/cssom/#resolved-values), and [CSSOM View client rectangles](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects), on 2026-10-20.

The wrapper is the flex item, while height applies to the inner table. Its percentage uses the wrapper containing block, not the auto-sized wrapper. The definite 200/300px host therefore supplies 100/150px to height:50%. Content is only one 20px line and below either minimum table height. A 20px caption adds to the table/caption bounding union; CSSOM View explicitly includes table and caption boxes. Resolved height observes the table height, while the bounding rectangle observes both. This is why the WPT's 100/150px and 120/170px observations are distinct and legitimate.

The fixture fixes width, margins, borders, padding, border-spacing and flex shrink. Center and last-baseline avoid stretch. Both resize directions, auto/fixed captions, and percentage/literal heights are represented. No support skip hides a missing baseline feature. A fresh same-final-style twin supplies position and baseline expectations; the independent numeric height checks prevent fresh/warm agreement from hiding a shared sizing failure. Last-baseline marker equality alone would miss this bug.

Authenticated all 16 baseline capsule payloads using external FILES digest `d014cf40cd51273f0ed6f5911b8e102b48c85e8c049a793e4c7028bae0ec9a85`; fresh isolated verifier passes. Release/project have identical 16 rows: four auto-caption percentage mismatches and twelve controls. Initial, restore and repeat checks all calibrate. This is diagnostic evidence, not yet execution of the final landing WPT against the candidate.

## Source path and normalization

- Wrapper `ComputeAutoSize` combines inner table and caption shrink-wrap sizes. With an auto-height caption, its computed block size remains unconstrained when either component is unconstrained. The changed inner percentage basis need not appear in the wrapper computed size. A fixed-caption control can expose the size change earlier and avoid this collision.
- `CreateReflowInputForInnerTable` takes `aOuterRI.mContainingBlockSize` for the inner RI. The grid-only margin/caption deduction is not active for this flex item. Both ordinary and override/border-collapse initialization paths pass the actual basis into inner RI construction/Init.
- `ReflowInput::InitConstraints` establishes a local logical cbSize from the explicit input or containing-block computation, performs existing normalization, then saves it in `mContainingBlockSize`. The key copies this initialized value. It does not reconstruct a physical dimension from wrapper geometry, retain an RI pointer, or introduce a new sentinel interpretation. Definite/unconstrained values remain distinguishable by ordinary logical-size equality.
- `SizeItemInCrossAxis` calls `MeasureBSizeForFlexItem` when item block axis is cross axis. A clean equal-key hit returns before `SetHadMeasuringReflow`. The cached BSize then becomes the planned cross size. The original key omits the inner-table basis even when computed size, min/max, available BSize and padding stay equal.
- `NeedsFinalReflow` can subsequently take the clean non-measuring branch and accept final metrics matching that stale plan. This explains why a final-cache-only addition would be too late to repair cross-size alignment. Exact branch execution is source inference supported by controlled runtime, not an instrumented trace.
- A new-key miss runs the existing measuring callback, sets the measuring flag, updates measured payload and clears prior final metrics. Existing final gates then run against the refreshed plan. No claim is made that their providers/dirty/relative-size guards are sufficient for every subtree.

Both added logical coordinates are justified as basis inputs, not just the observed height. Writing-mode conversion happens in existing RI construction. `LogicalSize::operator==` compares its coordinate pair and asserts compatible modes in debug; release equality alone does not detect a writing-mode identity change. Existing style/dirty invalidation must still protect that lifecycle, just as for the old computed-size key.

## Minimality, preservation and cost

The entire candidate is reconstructed by exactly two additions: `const LogicalSize mContainingBlockSize;` and copying `aRI.mContainingBlockSize` in the constructor. Default equality incorporates it. Thus a candidate hit implies the old key still matches; unchanged bases preserve old key decisions. Changed bases can cause conservative misses even for literal heights or unused dimensions. No ordering, cache update, output arithmetic, callback flags or final-skip policy changes.

The earlier border/padding addition is independent. The zero-padding fixture is not relying on that repair. The standalone source has no padding-key member and receives only the two containing-block additions. I independently applied/reversed its full native+WPT patch with `/usr/bin/patch --fuzz=0` in a disposable directory, matching complete before/candidate source and exact WPT bytes. This proves packaging fidelity, not isolated upstream runtime. See SOURCE-ROUNDTRIP.json.

Cost is one additional LogicalSize stored per CachedBAxisMeasurement, copied and compared when keys are constructed/checked. There is no new allocation type, lookup or loop. Actual ABI size, padding effects and runtime performance were not measured; increased misses are real potential work and no zero-cost claim is justified. Disabling measurement caching globally or for all tables would be broader. A resize Boolean would fail to remember the prior basis value.

## Limits and next gates

1. Root must bind the formatted candidate and execute the 16-case final WPT baseline/candidate plus chosen regressions. This review will not promote inferred branch activity into instrumented proof.
2. The formal component should prove key strengthening and the measurement-hit/stale-plan/final-hit witness with fresh-provider assumptions visible. It must not assume current output equals cached output or claim all key inputs are now complete.
3. Dirty-state, frame lifetime, same-frame callbacks, arbitrary relative descendants, style-driven writing-mode changes, and skipped/non-measuring paths remain broader cache-lifecycle obligations. This change supplies one missing input, not a replacement for those invariants.
4. Percentage width, orthogonal writing modes, indefinite-to-definite transitions, caption-side changes and fragmentation are useful later coverage. They are not demonstrated defects or prerequisites invented from lack of tests here.

No shared source, WPT, browser, build or Git state was changed. No formal proof acceptance is claimed.
