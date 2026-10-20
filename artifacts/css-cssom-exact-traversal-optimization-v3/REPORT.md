# Source-only traversal optimization recommendation

Status: **DESIGN_READY_FOR_ARTIFACT_IMPLEMENTATION; NO PERFORMANCE CLAIM**.

This checkpoint inspects the sealed v2 candidate, not a changed production tree. No compiler, browser, build, Git, or main-source operation ran. The parent owns the timing campaign. Its preliminary measurements are not treated as a final verdict. This directory contains source evidence and an implementation sketch, not a replacement native patch.

## Recommended next candidate

Retain one traversal definition and select its compile-time mode once, before the ordinary ancestor loop. The default/null-metadata instantiation must contain the original nsPoint additions, ScaleToOtherAppUnits grouping, flags, stopping conditions and matrix conversion. The metadata instantiation keeps four signed64 accumulators and checks every addition with public mozilla::SafeAdd. Use the existing recursive null-metadata restart on precisely the same arithmetic failure conditions as v2. Keep the wide carrier, all final endpoint checks, cached matrix fallback and self-identity treatment unchanged.

The common metadata caller uses empty flags and layout viewports. A third instantiation can specialize those exact runtime predicates: direct GetPosition replaces the IgnoreScrolling test, and ordinary stopping uses IsTransformed without visual-viewport or stacking-context flag checks. This specialization changes neither transform handling nor the returned ancestor. Other metadata requests take the generic wide instantiation. Do not treat this common-call restriction as the exact eligibility predicate: all existing context, SVG, parent and reached-target checks still apply.

Combine the two SVG state-mask tests into one test of NS_FRAME_IS_SVG_TEXT | NS_FRAME_SVG_LAYOUT. Cache the immutable source PresContext pointer before the loop, but retain comparison with each visited ancestor's context. These are small source simplifications; an optimizing compiler may already do them.

This is the most promising bounded experiment because it removes runtime mode decisions from the loop and makes successful checked-add state explicit. It does not remove the additions needed to preserve arbitrary signed64 cancellation. It does not replace the wide exact domain with a smaller fast domain.

## Evidence and exact equivalences

SOURCE-CHECKS.json authenticates retained v2 inputs and checks the relevant bodies. Searchfox accessor/function output is retained as indexed discovery evidence; the v2 full-source snapshots are authoritative.

| Source operation | Proposed replacement | Reason and limit |
| --- | --- | --- |
| Per-iteration if (aAppUnitTranslation) | One dispatch to a compile-time traversal mode | The pointer value is invariant during the method. Null mode preserves original arithmetic; wide mode preserves v2 arithmetic. Code generation and code-size consequences remain unmeasured. |
| CheckedInt<int64_t> += signed32 position; isValid | int64_t accumulator plus SafeAdd<int64_t>, with immediate failure restart | CheckedInt's addition itself uses SafeAdd, then carries both operands' validity. At every reached loop head v2's four accumulators are valid. SafeAdd uses __builtin_add_overflow and is a public mozilla function, not a detail helper. No claim that Clang currently retains redundant validity instructions. |
| Two !HasAnyStateBits tests for SVG | One negated mask-union test | IsInSVGTextSubtree is exactly HasAnyStateBits(NS_FRAME_IS_SVG_TEXT); HasAnyStateBits is mState & mask. Preserve the exclusion at the same source/ancestor points. |
| Repeated source PresContext() | Saved source context pointer | Getter returns mPresContext directly. Stable frame/context lifetime is the existing traversal admission. Ancestor context loads remain. |
| Empty-flags GetPositionMaybeIgnoringScrolling | GetPosition in the common-layout instantiation | Empty flags make IgnoreScrolling false. Generic and null modes retain the original flags behavior. |
| shouldStopAt under empty flags and layout target | IsTransformed in common-layout instantiation | Both the visual-root clause and stacking/display-port clause are false. The target comparison remains first, so target-own transforms stay excluded. |

### Checked-add invariant

Each of the four initial values is a signed32 coordinate converted exactly to signed64. A loop iteration consumes only valid accumulator state. In v2 both doc additions are immediately checked before any value(), context work or next iteration. Cross-document additions have the same immediate check. addDocOffset checks both offset sums before returning success. Reset writes zero to both doc components. Therefore no invalid CheckedInt state reaches another operation in the accepted continuation of the method.

Replacing these objects with raw signed64 values plus SafeAdd preserves every successful mathematical sum and overflow outcome. A failed check returns to the same original null-metadata method before any accumulator can be published. SafeAdd may write an overflow result into its output parameter; the sketch uses temporaries and never consumes those values after failure. Short-circuiting the second pure local addition when the first fails does not skip a frame/provider operation. For mixed APD, retain the signed32 narrowing check and the original ScaleToOtherAppUnits call with exactly the same operands. No handwritten scale or float conversion is proposed.

This reasoning also covers v2's expanded domain, not just v1 inclusion. In particular x=1,000,000,000 with frame positions +1,500,000,000 and -2,000,000,000 must still return exact500,000,000. The two original wide witnesses remain required: docOffset2,800,000,000 with final800,000,000, and translation2,500,000,000 with rect.x=-2,000,000,000 yielding500,000,000. There is no signed32 intermediate rectangle filter and no depth threshold.

### Traversal-mode invariant

All three modes share the traversal statement order, cross-document/APD flushes, ancestor assignments and fallback calls. Compile-time branches choose only the arithmetic representation and invariant flag checks. The transformed/source zoom early path stays outside specialization. Exact metadata resets at entry, remains cleared across multi-segment transforms, and cannot recover from invalid arithmetic. Default callers do not acquire checked64 math or new context/state checks in their instantiated loop.

A shared definition is preferable to copied hand-maintained loops, which could drift on a future boundary fix. A local templated lambda is one implementation option and requires no additional public API or header template. Whether the compiler outlines it, duplicates substantial setup, or increases instruction-cache pressure remains a real performance risk.

## Guard removals not justified

SetParent asserts that parent and child PresShell agree. That is not a proof of all mParent construction/mutation paths, nor a complete derivation that equal shell implies the exact stored context-pointer identity used here. This checkpoint therefore does not remove per-ancestor context checks. Source/target context equality alone is insufficient for arbitrary frame graphs.

Do not infer SVG eligibility from the leaf alone. Do not replace IsTransformed by the MAY_BE_TRANSFORMED state bit: its implementation uses that bit only as a fast negative test and otherwise evaluates CSS and SVG transforms. Do not turn a rejected exact route into an unchecked fallback coordinate. Do not drop checked64 overflow tests based on a guessed tree-depth, memory-size or practical layout limit.

Avoid an independent pre-scan to discover a transformed ancestor, which reintroduces the known duplicate-walk cost. Avoid clamping accumulator state, including on paths whose final position returns in range. Avoid finishing the matrix with a differently grouped cross-document sum. No new transform, perspective, APZ, SVG or scaling provider semantics are introduced.

## Remaining gates

The source sketch is deliberately uncompiled while the parent's timing hold is active. After release, an artifact-only implementation should reuse the existing v2 extracted replay and its independent challenges, including null callers, APD transitions, default and nonempty flags, both wide witnesses, expanded-domain case, self identity and the intentionally failing legacy restart. The same ordinary/transformed depth cases should compare entry counts and matrix/provider operation traces. These are existing acceptance requirements, not a request for a new broad test campaign.

Then the parent can decide whether to run a reversible full build, the already established browser correctness gate and the focused performance campaign. Removing source branches is not proof of faster machine code. No speedup, native acceptance, full graphics proof or universal arithmetic safety is claimed here. Legacy restart UB outside the old-defined/v2 exact domains remains the existing explicit limitation.
