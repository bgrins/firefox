# Independent adjudication: composition-only keyframe updates

## Verdict

**Repair warranted.** The three runtime discrepancies are observations of one implementation defect: `KeyframesEqualIgnoringComputedOffsets` omits the keyframe's specified composite operation, so `KeyframeEffect::SetKeyframes` can return before storing a valid composition-only update. A null-target getter case establishes the defect without rendering, CSS value equality, or a refresh-timing premise. The ordinary margin-left case also demonstrates the visible consequence.

This is a known-symptom area. Bug 1778407 comments 2–4 describe a related CSS keyframe composition-only mutation requiring another property change. Its DevTools INVALID resolution is not a source repair. The present direct WAAPI reproduction and source diagnosis strengthen that report; they do not establish novelty or release-browser prevalence. Root owns any bug selection and native repair.

## Normative trace

The current [WA1 setKeyframes definition](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-setkeyframes) requires successful processing to replace the effect's keyframes, while an exception preserves them. The [getKeyframes algorithm](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-getkeyframes) exposes each stored keyframe's composite operation. These rules also apply when the target is null and the keyframe has no animated property declarations. No permission exists to retain an old specified operation because a current rendering happens to be equivalent.

For rendered effects, [effect-value calculation](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect) combines each endpoint with the underlying value before interpolation, using the frame-specific operation or the effect default. Here the underlying margin is 10px and the endpoints are 20px and 40px at progress 1/2: replacement gives 30px, addition gives 40px. Changing only one endpoint operation gives 35px. Ordinary lengths make addition and one accumulation numerically equal, but their specified enum values remain separately observable.

The current draft was independently retrieved; HTML and extracted text are retained. CSSWG issue 7476 concerns defaults in CSS-generated keyframes, not replacement of explicit WAAPI composite members. Its record is closed. The scout's named-range/implicit-endpoint integration issues do not affect two explicit ordinary offsets at 0 and 1. No normative ambiguity blocks this repair.

## Independent runtime review

Historical execution is root session 40649, exit 0; receipt browser is Firefox 160.0a1, macOS, headless, build 20261018154931. Browser termination code -15 is recorded after successful result collection; it is not a page failure. The result is not a release-browser observation.

All 34 before/after input pins agree. The served page bytes match the page hash. All 32 archived source/page/tool inputs agree with the receipt; the two binary pins remain historical identities. At review capture, all live pins also matched. Future repair or rebuilds need not match those historical bytes.

The independent checker recomputes the expectations from specified records and rational arithmetic; it does not accept the page's expected values as its oracle. It checks all labels, actual values, match flags and summary membership. Its model is handwritten, not extracted native code or a Lean proof.

| Observation | Expected | Observed |
| --- | --- | --- |
| Null target, empty-property replace→add getter | add, add | replace, replace |
| Rendered composition-only getter | add, add | replace, replace |
| Rendered composition-only sample | 40px | 30px |
| Initial replacement | 30px | 30px |
| Change endpoint value to 42px while selecting add | 41px | 41px |
| Repeat that input | 41px | 41px |
| Change effect default for auto keyframes | 40px | 40px |
| Six mixed-effect update/cancellation/base/default controls | 34, 44, 29, 39, 24, 20px | all equal |
| Higher replacement / commit prefix / cancellation | 100, 24, 24px | all equal |

The getter observations are synchronous and do not rely on sampling. The rendered companion explicitly pauses and sets currentTime=500 for duration=1000, then reads computed style. No oversized tree, stack limit, compositor acceleration or scroll-driven timing is involved.

## Complete implementation boundary inspected

| Boundary | Actual function/data path | Consequence or remaining provider |
| --- | --- | --- |
| Input enum/default | BaseKeyframeTypes.webidl; `CompositeOperationOrAuto`; BaseKeyframe default auto | Four distinct values; generated binding conversion is external to this static review |
| Ordinary JS entry | `KeyframeEffect::SetKeyframes(JSContext*, ...)` → `KeyframeUtils::GetKeyframesFromObject` | Processing failure returns before mutation; valid input obtains target style and timeline/range |
| Parsed sequence | `GetKeyframeListFromKeyframeSequence` → `ConvertKeyframeSequence` | The actual composite dictionary member is assigned to `mComposite`; loose offset validation and easing parsing precede commit |
| Property-indexed input | `GetKeyframeListFromPropertyIndexedKeyframe` | Composite scalar/list distributes into generated keyframes; no property values means no generated keyframes, so use an ordinary property for this form's test |
| Optimized commit | Full array overload of `SetKeyframes` | Comparator shortcut precedes move assignment, missing-offset recomputation, relevant-animation notification and style-present property update |
| Equality provider | Full `KeyframesEqualIgnoringComputedOffsets`; `PropertyValuePair::operator==`; `Servo_DeclarationBlock_Equals` | Checks array length, specified offset, timing and ordered properties; omits composite. Property identity/pointer shortcuts then Rust declaration-sequence equality explain equal reparsed px values. Empty-property witness avoids this provider entirely |
| Offset state | `ComputeMissingKeyframeOffsets` and timeline/range inputs; `MaybeUpdateKeyframeComputedOffsets` on later reads | Computed offsets are derived state, deliberately omitted by comparator; this repair must retain existing invalidation behavior and cannot claim universal timeline freshness |
| Getter | Full `KeyframeEffect::GetKeyframes` | WAAPI uses stored frames (with offset refresh); serializes `mComposite` directly. CSS-specific computed frames, variable serialization, JS allocation and error paths remain separate providers |
| Property rebuild | `UpdateProperties` → `BuildProperties` → `GetAnimationPropertiesFromKeyframes` → `BuildSegmentsFromValueEntries` | auto resolves to effect default; explicit enum is retained; segment endpoints store both operations |
| Derived comparison/restyle | `AnimationPropertySegment::operator==`; `UpdateProperties`, `EnsureBaseStyles`, `UpdateEffectSet`, `MarkCascadeNeedsUpdate`, `NotifyEffectPropertiesUpdated`, `RequestRestyle` | Segment equality already includes both composite operations. Once the initial shortcut is fixed, this path notices real segment changes, refreshes needed base values and requests restyle |
| Sampling | `EffectCompositor::ComposeSortedEffects` → `Animation::ComposeStyle` → `KeyframeEffect::ComposeStyle` → `Servo_AnimationCompose` → `compose_animation_segment` → `composite_endpoint` | Map-first underlying selection then base fallback, endpoint composition then interpolation; complete scalar value arithmetic and timing providers are not proved here |
| Other callers | `ConstructKeyframeEffect`; CSSAnimationKeyframeEffect JS setter; nsAnimationManager existing-animation update | CSS setter has override bookkeeping; style updates share the array overload. The direct API fix therefore has a broader caller impact requiring CSS controls |

`SetComposite` is a different entry path that rebuilds properties when the effect default changes; its passing control does not exercise the faulty per-frame comparison. The prior root iteration-identity repair is present in the pinned KeyframeEffect.cpp snapshot. It concerns iteration timing and is not this defect or a prerequisite for the one-condition repair.

## Minimal standalone repair and WPT proposal

Add `a.mComposite != b.mComposite` to the existing mismatch condition in `KeyframesEqualIgnoringComputedOffsets`. Keep computed offsets excluded. No enum remapping, new invalidation policy, or Rust arithmetic change is needed. Parent should review and format the final expression and execute baseline/candidate WPT before accepting it. This artifact does not modify production files.

Use one dedicated WPT testharness page beside `web-animations/interfaces/KeyframeEffect/setKeyframes.html`, or tightly scoped additions there. Suggested nonredundant cases:

1. Null target and array input with explicit offsets and empty property arrays: all old/new pairs of replace, add, accumulate and auto. Include identical input and back mutation. This detects getter regressions even where current pixels match.
2. Property-indexed input with `marginLeft: ["20px", "40px"]`: scalar composite, two-entry composite list, and repeated shorter list. Keep offsets/values fixed during the mutation.
3. Connected element with a 10px underlying margin, 20px→40px endpoints, paused at 1/2: change both operations, then only first/last, then revert; expect 40px or 35px as appropriate. Test explicit→auto under an additive effect default, auto→explicit replace, and an effect-default change that leaves explicit frames unchanged.
4. A value-changing 42px control (41px with addition), unchanged-input control, and processing-error atomicity control on an already populated effect. These exercise the fast path and error return without making their behavior new bug claims.
5. Shared-caller guard: a small CSS-generated animation whose one rule's composition changes through CSSOM while other fields remain fixed, then style flush. Its baseline status is a new gate, not an already executed result. Keep CSS default semantics explicit; do not merge a default-policy change into this repair.

Use `t.add_cleanup` for cancellation/removal, no sleep, and getter assertions alongside rendered assertions. Existing `setKeyframes.html` exercises inputs starting from an empty effect and immediate property-value changes; shared fixtures cover composite parsing, not this same-values update. Existing effect-composition and commitStyles WPT already cover much of the successful control behavior. No metadata file existed for the inspected setter/composition tests at capture; that is not a claim they were executed or all pass.

The standalone defect commit should contain only the necessary Gecko comparison and regression WPT. Any formal companion and research documentation should precede it in a separate commit, following the project's review convention.

## Proposed formal contract and complete native bridge

### Authoritative state and theorem

Use a specified-keyframe record with optional specified offset (including a distinct named-range form if supported), timing/easing, ordered property declarations, and the full four-value composite enum. Keep derived computed offsets in separate state. Give effects, targets, timelines and declaration blocks distinct nominal identities with explicit relations for legitimate sharing. Do not collapse auto into its currently resolved operation: default changes and the getter distinguish it.

Define successful input processing independently from update optimization. The reference update replaces specified keyframes; the optimized update may skip only under the corrected comparison. Prove, for arbitrary finite frame arrays and arbitrary finite sequences of successful updates and processing failures, equality of specified-keyframe getter observations, error atomicity, and equivalence of update-vs-skip decisions to the full specified-record relation. Include per-frame order and length; duplicate offsets and equal declaration blocks with different allocation identities must not be silently discarded.

For derived output, state the necessary provider relation explicitly: equal specified records in the same effect-default/style/timing environment produce equivalent property definitions, and the computed-offset cache is valid for that environment or refreshed by the real invalidation path. A general cache-freshness theorem is not supplied by record equality. Under that relation prove optimized updates preserve evaluations for every subsequent default change and provider refresh. Do not supply the expected composite/getter/state result as a provider.

### Extracted path, providers, and obligations

The mandatory native core is the complete equality helper, PropertyValuePair equality, both ordinary SetKeyframes overloads, complete GetKeyframes, and the real array update state. Retain the parsed-frame struct/defaults and offset recomputation call, notification gate, style-present gate, getter serialization and failure branches. Exercise absent target/style, animation absent/present/relevant, unequal lengths, all fields independently changed, same/different declaration identities, all four composites, and first/interior/last frame changes. A two-enum truth table or a handwritten replacement setter is insufficient.

For claims covering actual property rebuild/restyle, additionally extract the complete `UpdateProperties`, `BuildProperties`, `GetAnimationPropertiesFromKeyframes`, segment construction and segment equality, with the actual computed-value and base-style providers traced. Trace the actual `RequestRestyle`, cascade-dirty and observer/property-updated effects. Required offset providers include complete ordinary missing-offset distribution and a declared named-range boundary; do not model a range resolver by passing in its expected final answer. CSS-generated getter/constructor paths and CSSAnimationKeyframeEffect bookkeeping need native trace/WPT controls; either include their full functions or explicitly limit the universal theorem to ordinary WAAPI effects.

JS iteration/conversion, CSS parsing/declaration locking and serialization, allocation failure, target style acquisition, timeline geometry, scheduling, compositor publication and actual restyle execution remain external unless separately modeled/extracted. Existing immutable source snapshots must bind every included function and provider; an adapter must distinguish supplied style/enum/timing inputs from externally expected outputs. The no-property/null-target witness can close the decisive state/getter case without assuming CSS declaration equality.

The rendering contract, if added, must include the complete C++ sampling consumer and Rust `Servo_AnimationCompose`, `compose_animation_segment` and `composite_endpoint`, plus actual property-type arithmetic/default resolution. A rational length specialization can verify this witness, not all CSS animation value types. Keep prior iteration-identity behavior unchanged; iteration index/timing and unrelated unsupported arithmetic remain declared limits.

Recommended executable mutants: omit composite (the original bug), compare only first/last frame, collapse auto to replace, compare the resolved operation instead of specified enum, move the skip after observable mutation, drop assignment, suppress style-present update, suppress notification/restyle, or make array length/order irrelevant. Keep genuine no-ops separate: add and accumulate coincide numerically for these lengths but are not getter-equivalent. Require successful compiled semantic mutant executions, universal Lean sequence theorem audits, independent provider-derived expectations, full source-only replay and pre-import authentication.

Cost is low for the universal specified-record/update theorem, medium for full setter/getter state extraction with honest JS/style providers, and medium-to-high for the complete rebuild/sampling bridge. Scope approval should distinguish those claims before implementation. This review performs none of that proof or extraction execution.

## Negative coverage and history

No discrepancy was found in the six tested ordered-fold controls or three commit-prefix controls. Those finite observations do not certify arbitrary effect stacks, transformations, iteration accumulation, transitions, cross-target ordering, custom properties or accelerated animation. Named ranges, implicit CSS endpoints, procedural macros and general IEEE arithmetic remain outside this adjudication.

Bounded history checked current bug 1778407 and its comments, retained prior source history, shared WPT fixture coverage, and CSSWG issue 7476 plus the scout's prior integration issues. Search queries also surfaced older implementation bugs 1216844 and 1291468; neither is evidence of a repair to this equality omission. The search was not exhaustive. Current source discovery used Searchfox; the installed CLI rejects `--permalink`, so exact source bytes and command output are retained instead of a fabricated revision link. No live source, WPT, browser/build, Git, or external publication was changed by this review.
