# Stepped-function consumer audit

The two simplification guards address a real zero-basis calculation issue, but are not a complete independently landable change while current easing consumers require context-free resolution. No native changes, compilation, browser execution, acceptance, or fix count occurs in this audit.

## Current consumer contracts

| Consumer | Current representation and boundary | Consequence of retaining contextual Round/ModRem |
|---|---|---|
| Ordinary integer properties | Specified Integer owns calc; computed conversion has Context and rounds/clamps | Contextual evaluation is supported; zero/NaN and range expectations still require exact tests |
| steps() | Generic Steps(Integer, StepPosition); parser rejects Integer.resolve()==None | Previously admitted folded expressions become parse failures until contextual conversion and invalidation are completed |
| cubic-bezier() | Generic four Number fields can retain AST, but parser requires all four resolve() values | Same admission regression; needs contextual coefficient conversion and range handling |
| linear() | Specified alias already contains computed PiecewiseLinearFunction with scalar x/y entries | Need specified owned stop AST plus computed builder; parser cannot simply retain existing representation |
| subgrid name-repeat | Current branch has accepted contextual fix 127 and cache prerequisite 122 | Old upstream resolve-none rejection is absent here; do not report it as a current-branch regression |
| Context-free descriptors | Counter bounds/pad, font palette and font-face consumers retain resolution checks | Their context policies remain separate; no blanket deferral activation |

The extra current-native second-percentage unwrap route is detailed in LINEAR-TRACE.md; it is a source prediction independent of the stepped proposal.

## Necessary dataflow work

For Steps/Bezier, retain specified Integer/Number and resolve them with the actual CSS computation context, preserving count/range/clamping semantics and serialization. For linear(), introduce specified stops owning output Number and optional start/end Percentage. Keep the existing computed scalar piecewise representation and apply the builder's nondecreasing-coordinate/omitted-position algorithm only after contextual conversion. Account for size traits, shared-memory representation, animation/FFI conversion and serialization rather than changing the computed ABI casually.

`Servo_ParseEasing` currently invokes `to_computed_value_without_context` with no element argument. Generic WAAPI easing parsing cannot silently borrow the CSS property's context policy. CSSWG issue 14246 remains the explicit open API-policy boundary in the prior handoff research. CSS property and keyframe conversion additionally require owning-style dependency publication, effect invalidation, declaration scope and animated-style ordering; normal-only conversion metadata is insufficient. Existing held Steps groundwork is not a complete Bezier/Linear or WAAPI implementation.

Do not retain incorrect stepped folding selectively for easing to preserve admission. A complete experiment must test all affected consumers and distinguish current supported element integer paths from descriptor/API contexts. The sealed consumer probe keeps easing rows diagnostic; its z-index zero expectation is 0 because enclosing NaN is censored at the top-level calculation, unlike sign-only zero yielding 1.

## Deferred arithmetic prerequisite

The parallel sealed knowledge review (css-relative-stepped-knowledge-review-v1) identifies another existing prerequisite: CalcNumeric maps contextual leaves then calls runtime resolve, without re-running simplification. Deferral can therefore select the known Round binary32 quotient path rather than the remainder-based simplifier. The review's opacity/sign expression is an unexecuted exposure hypothesis, not a new observed bug. Full readiness guards plus consumer representation are insufficient until this already-known arithmetic discrepancy is reconciled on the exact base. Preserve NaN priority, signed zero and percentage-stage controls; do not equate unchanged source bodies with equivalent newly selected evaluation paths.

## Evidence and limits

Primary captures equal the explicit current HEAD; local changes relative to Searchfox are recorded, notably contextual subgrid and integer/easing range work. Searchfox captures are content-pinned, not represented as immutable upstream revision attestations. ADDITIONAL-SOURCE-EXCERPTS.json records the scalar linear representation and FFI helpers. Searchfox discovery covered these named consumers, not all CSS grammar call paths. Existing fix 120 remains held; fix 127/122 prerequisites matter for export onto a clean upstream baseline.

Primary rules consulted: CSS Values 4 stepped functions and calculation simplification/range rules (https://drafts.csswg.org/css-values-4/), CSS Easing 2 (https://drafts.csswg.org/css-easing-2/). Zero step/divisor yields NaN; final calculation censorship and destination range rules are distinct stages. The generic easing context policy is not resolved by the separate range-offset discussion. The webspec-index executable was unavailable; this audit used primary document browsing and existing pinned traces, without claiming an exhaustive indexed algorithm graph.
