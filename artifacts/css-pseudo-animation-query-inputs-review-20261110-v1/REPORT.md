# Query-input candidate independent source review

No source blocker found for a reversible real-build and ordinary-path preservation experiment on the frozen candidate. This is not acceptance of a working missing-pseudo repair: the new query path has no production caller and has not compiled or executed. The reviewer authored the two earlier prerequisites, but did not author this incremental query-input stage. The cumulative patch must replace those proposals rather than be applied on top of them.

Reviewed incremental patch: `c12aac7c0c334dc2e252db7091788c9977b3c7fc7abf0282aeee698d660da77c`; cumulative patch: `29390ea55c62ceefb36395a0a0657c26600a859991d937caa97f437a754b3757`. Source basis 3f8f7324c20de730eddcf07b224dd93e9be6694d. Source-only replay passed all 25 Git pins, prerequisite reconstruction, incremental/cumulative forward/reverse replay and deterministic copied-source formatting. No live source/app/Git mutation or native compilation occurred.

## Timing and ordinary behavior

GetHoldTimeForComposition preserves the existing pending + null-hold + non-null-start guard, wallclock timeline admission, unresolved conversion handling and playback-rate formula. Ordinary ComposeStyle still guards missing effect/unresolved timeline, captures pending, uses AutoRestore and retains its pending-state postcondition. Re-reading Pending inside the helper follows only the AutoRestore copy; under the existing synchronous non-reentrant path it observes the same state. The default timestamp is evaluated only inside the original wallclock branch, not at ordinary helper entry. The query supplies one timestamp and obtains temporary hold/current-time results without writing live hold/start/pending or triggering readiness.

Query timing normalization matches AnimationEffect::UpdateNormalizedTiming for non-monotonic timelines, including the existing non-null duration premise. Boundary and current-time reads are captured before conversion. This is source correspondence, not a floating-point theorem or arbitrary reentrancy equivalence. Strong timeline references preserve lifetime, not cached snapshot freshness.

## Ownership, identity and ordering

The helper rejects unsupported/generated pseudo targets, mismatched pres context and style pseudo types, nonempty outputs, and aliased output references. It owns the target/request and both styles. EffectSet iteration ends before conversion; strong effect references retain lifetime. The existing comparator sorts effects, then each effect/animation relationship and full target/request identity is checked. Inputs, CSS generation options, range, timeline, timing, iteration composite and cascade level are captured before conversion.

Owned offsets are refreshed before BuildPropertiesFromInputs generates endpoints. No completed endpoint array can survive that refresh. Property arrays and base-value table are local. Effects/animations are retained even though later work uses captured data, so destructors cannot remove them midway through preparation. Declaration blocks remain shared, and the exact element association of ComputedStyle cannot be authenticated from its pseudo type alone.

## Cascade and output maps

The fresh animation-level union and its two skip-set polarities mirror ComposeSortedEffects: animation-origin composition includes transitions as potential underlying values on animated properties; transition-origin composition excludes animation-level properties and includes transition effects only. No important-rule filtering is invented at this layer: a later origin-correct recascade must do that. Null-progress effects contribute no values; the fresh union follows prepared EffectSet inputs, not renderer cached property masks.

Every property in the prepared union gets a base extraction from the explicit base style; the code bypasses stored mBaseValues and missing-pseudo EnsureBaseStyle early return. Both distinct maps are allocated internally after all false-return checks. Composition reuses explicit ComposeProperties and skips null progress. Renderer UpdateProperties/cascade publication/restyle/WillComposeStyle paths are absent. Local attribute-reference output is not published; no persistent cache may rely on this discarded tracking.

## Required boundaries and gates

The helper cannot establish that endpoint/base styles, inherited parent style read by Servo, attributes/container providers and timeline caches belong to one coherent sample. It neither solves dependencies between animated providers nor detects/retries reentrant mutation. These are explicit caller premises, not consequences of RefPtr ownership. A future caller must release lazy-resolution borrows before conversion, provide raw base excluding the target's own animation/transition while retaining inherited animated context, and provide a separately justified endpoint provider style. Passing one raw style for both is not generally established.

No caller yet proves disconnected/flat-tree/printing admission, visited behavior, effect registration completeness, transient recascade, cache bypass or cancellation clearing. Those remain missing repair architecture, not waived follow-ups. The final debug transform-hint traversal gate stays open.

The next bounded experiment should compile the cumulative eight-file patch and preserve the existing 130-record ordinary baseline. Because the shared hold selector is newly factored, include focused existing pending play/pause and interrupted-pause cases, null/held/zero-rate cases and unresolved/finite-range boundaries. An ordinary-only run cannot certify the unused API: direct invocation or the reviewed CSSOM hook must later test implicit/fixed/additive endpoints, transition overlap, exact target identity, refreshed range offsets and provider-dependent values. No new broad test suite or unbounded convergence claim is needed for this source-review gate.
