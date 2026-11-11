# Independent composition extraction review

Verdict: **no blocking source-level finding; suitable to proceed to the stated compilation and debug/runtime gate.** This is acceptance of a prerequisite refactor for testing, not acceptance of the missing-pseudo CSSOM repair or an unexecuted regression gate.

Reviewed patch SHA-256: `7e155ea1320673a0dd0f999cdc59ad4f85b77d5ee8b82c1d08b9b773198b0eee`. `REVIEWED.json` pins the patch, both candidate files, six source files and supporting report/checker inputs. `ORIGINS.json` independently authenticates all six source files against Git revision `7bc1ed9cde2a3f3f6e8c615125a7cf75c7964f16`.

## Ordinary behavior

`ComposeProperties` is a meaningful extraction: the ordinary `KeyframeEffect::ComposeStyle` immediately delegates to it. It does not introduce a second implementation waiting for a future caller. `GetComputedTiming(nullptr, aEndpointBehavior)` remains in ComposeStyle, with the same null-progress early return. The overflow synchronization block remains after composition, including for an empty or entirely skipped property list. Null progress still returns before that bookkeeping.

The property order, skip membership, selected segment, coincident-offset behavior, last segment and computed timing operands are unchanged. The new helper directly calls the same `Servo_AnimationCompose` previously reached through `ComposeStyleRule`. The new entry assertion only repeats a condition guaranteed by the ordinary caller's existing guard. It does not add release-mode validation for future callers.

The original assertions index segment zero and the final segment before the later non-empty assertion and before the property skip. This pre-existing ordering remains unchanged. The new public helper's contract therefore requires every supplied property's segment array to be valid and nonempty, including skipped properties in assertion-enabled builds. It is not a general validator of arbitrary prepared arrays. Future preparation code must satisfy that premise rather than use skip membership to excuse invalid segments.

`Animation::ComposeStyle` is untouched: unresolved timeline rejection, temporary pending hold-time adjustment/restoration and the post-compose pending-state assertion stay in place. `WillComposeStyle` and last-progress/iteration bookkeeping are untouched. `EffectCompositor` still sorts effects, builds masks and dispatches through Animation. This extraction does not alter cascade masks, compositor flags, target registration or base-value preparation.

## FFI and hoisted inputs

The const base table is consistent with the pinned Rust signature `base_values: &RawServoAnimationValueTable`. `Gecko_AnimationGetBaseStyle` already takes a const opaque pointer, reinterprets it as a const hashtable and performs `GetWeak`. The extracted helper preserves the existing table representation and address; it does not cast away const or introduce a second table. The output value map remains mutable. Generated-header signature compatibility and actual C++ access/type checking still require compilation.

The base-table address and iteration-composite option are now supplied once per call instead of read through the effect for each selected property. The address change is a stable reference to the same live table object. The option change relies on stable effect/options throughout synchronous composition. The header already describes avoiding effect-state mutation during potentially parallel composition. The inspected direct callbacks only read base values, supplied timing and segment easing; they do not receive an effect or DOM target or flush style. The Rust segment path operates on animation values and writes the output map.

This is adequate supporting source evidence for the existing composition contract, not a whole-program reentrancy or purity proof. Transitive interpolation, allocation, reference management and concurrent lifetime rules were not formally verified. Discovering a callback that changes iteration options during composition would require revisiting this equivalence; the same broader mutation would also threaten stable segment/property references already held by the original loop.

Moving `BaseValuesHashmap` into the public C++ section changes accessibility, not object layout or WebIDL. Its member retains the same type and location. The new static helper accesses no effect instance; future callers own the prepared properties, base values and timing and must keep them alive and stable through the call. A const reference alone does not prove those lifetime/concurrency obligations.

## Claims and gate

The author's report correctly calls this output-map composition rather than mathematical purity. It does not claim fresh CSSOM properties, fresh effect masks, correct nonexistent-pseudo base styles, query-safe timing/preparation, cache bypass, a transient recascade, or a fix for bug 1615083. The existing missing-pseudo failures should remain for this extraction. A future CSSOM caller must preserve endpoint policy and pending/unresolved behavior deliberately; obtaining an arbitrary timing object and invoking this helper is not sufficient by itself.

The proposed runtime gate covers ordinary WAAPI value/timing composition, CSS animations/transitions, commitStyles endpoint behavior, pending timing, throttling/overflow, and pseudo generation transitions. Its debug requirement matters because the source premises are assertion-sensitive. Baseline-matched execution must distinguish existing failures from regressions. This review executed no build, formatter, browser or sanitizer, and does not certify those proposed suites have run.

## Independent validation

The six exact source objects were checked independently against Git. The author's source checker was inspected and replayed read-only: deterministic candidate generation, scratch forward/reverse application, exact ordinary timing/guard/overflow preservation and normalized segment-loop correspondence passed. `SOURCE-CHECK.json` and `source-check.log` retain the receipt. The checker is useful source evidence, not a compiler or a native behavioral equivalence proof. Manual review additionally covered the input-hoisting contract, const callbacks, public alias and caller bookkeeping.

No source, WPT, build tree, browser, Git index or history was changed by this review. If formatting changes the frozen patch, the formatted bytes need a hash update and a semantic/format-only comparison before this review is cited for them.
