# Composite-only setter companion: implementation scope

## Claims to implement

The mandatory core is specified-state and derived-state refinement, including ordered observable provider/event traces, over arbitrary finite sequences. It is not an enum-equality theorem or a full rendering theorem.

Typed specified frames retain ordered frame identity/position, optional percentage or named-range offset, easing, ordered property declarations and all four distinct composite operations. Raw declaration allocation identity and structural declaration observations are separate; a compiled pointer shortcut must agree with structural equality under the admitted declaration provider relation. Computed offsets and range-present state are derived fields, never part of specified equality.

The independent reference setter replaces the specified projection on successful processing. The optimized setter may retain equivalent raw representation only when its specified observations agree. The reference observable state is compared modulo admitted declaration/serialization equivalence, not raw allocation identity. Event behavior is specified separately: changed specified observations recompute offsets once, notify iff an animation is present and relevant, and invoke property rebuilding iff style is present. Unchanged specified observations preserve a valid cache and do not emit those update effects. This distinguishes the normative replacement observation from permissible internal no-op behavior.

Sequence actions include successful processed input, processing failure, effect-default change, and context refresh (style/timeline/range provider changes). Failure is atomic after processing and before target-style acquisition. Context refresh is represented explicitly; equality alone cannot justify stale offsets. At every unchanged-input skip, derived offsets and property/base caches must satisfy their validity relation for the relevant provider environment, or the real refresh path must have restored that relation. Include concrete admitted empty, singleton, percentage/missing-offset and named-range/unresolved states, not only a theorem over an impossible invariant.

The proof will establish specified getter retention, derived-offset/range validity, effect-default resolution without collapsing auto, consumer-property agreement and skip/update event gates. Rebuild state uses independently supplied valid computed-property/base providers, and the actual native rebuild control flow. No claim that an observer/restyle stub paints pixels or reproduces scheduler behavior.

## Mandatory compiled extraction

- Complete Keyframe record/OffsetType equality/defaults, `ComputedOffsetsAreDifferent`, `IsRangedKeyframe`.
- Complete `PropertyValuePair::operator==` and the comparator; structural declaration equality provider traced and explicitly adapted.
- Both ordinary `KeyframeEffect::SetKeyframes` overloads, including processing-error return and target-style/timeline/range acquisition.
- Complete ordinary `GetKeyframes` control flow and serialization. A typed JS boundary adapter records real dictionary/property writes and error branches; it is not a replacement projection function.
- Complete `ComputeMissingKeyframeOffsets`, ordinary distribution helper, `GetComputedOffset`, and `MaybeUpdateKeyframeComputedOffsets` control flow. Timeline geometry is an admitted input provider; actual named-range normalization is retained where tractable.
- Complete `UpdateProperties`, `BuildProperties`, actual operation resolution into segment endpoints, and segment equality. Computed CSS values, base style, effect-set publication, cumulative-change computation and external restyle/notification services remain separately logged providers. Retain segment construction where needed for the property-consumer claim; do not supply expected final properties as a provider.

Retain static source closure for actual parsing, declaration equality/serialization, CSS computed values/base style, constructors, CSSAnimationKeyframeEffect override bookkeeping and the CSS shared caller. The universal theorem covers ordinary WAAPI effects; CSS-generated keyframe augmentation and override bookkeeping are traced/WPT boundaries, not silently covered by the ordinary model.

## Native observations and corpus

Compare actual stored specified fields, derived offsets/range flag, getter dictionary/property serialization, derived consumer segments/base state and ordered provider/event traces against an independent oracle. Vary absent/present/relevant animation, style/target presence, equal/different/empty/multiple frames, all enum transitions and first/interior/last endpoints, same/different structurally equal declaration allocations, offset/easing/property changes, length/order, errors and context/default refresh. Exercise unresolved/changed range contexts and NaN-vs-NaN refresh comparison explicitly, with layout geometry providers admitted.

Compiler-successful semantic mutations must include original composite omission, other specified-field omissions, length/order or first/last-only comparison, auto collapse, dropped assignment, skipped offset recomputation, notification-gate errors and suppressed property update/restyle. Only successful semantic disagreements count as kills. Keep harmless raw derived-offset differences and numeric add/accumulate equivalence as honest controls with distinct getter observations.

## Boundaries and acceptance

JS iteration/WebIDL conversion, CSS parsing/locking/value equivalence/serialization, actual layout/timeline geometry, allocation/runtime semantics, style-system freshness and scheduling remain explicit boundary contracts unless their real implementation is extracted. Full sampling and Rust property arithmetic remain external; root WPT supplies rendered evidence. No universal C++/IEEE or all-CSS conformance claim.

Source-only replay authenticates every helper/source/toolchain input before imports, compiles complete extracted bodies, audits Lean axioms, reruns mutations, and records counts and bounded matching/update cost. Bind the final formatted root candidate snapshot before freeze. Original frozen scout, independent review and root WPT receipts supply provenance; no live code/WPT/build/browser/Git edits are performed here.
