# Base-value metadata scheduling audit

## Status

Concrete source-supported hypothesis, UNCONFIRMED in a browser. The eight-case probe is UNEXECUTED. No native patch is proposed for landing. Root owns runtime adjudication. This audit does not alter the endpoint repair. Sources were copied from the current checkout during its build: UpdateProperties includes the endpoint-only candidate; EnsureBaseStyles is unchanged. SOURCE-PINS identifies complete retained files, not an upstream revision claim.

## Candidate and exact path

EnsureBaseStyles unconditionally reconstructs mBaseValues. When asked to report changes, it moves the old map aside and compares each new value using AnimationValue inequality. That comparator delegates to payload-only Servo equality, so an outer attr_tainted change with equal payload is invisible to aBaseStylesChanged. If explicit endpoints also compare unchanged, UpdateProperties returns without RequestRestyle. The endpoint candidate's extra check does not inspect the base map.

A concrete admitted effect has one explicit CSS-wide initial keyframe at offset1 and an implicit underlying endpoint at0. Registration is noninherited <string>, initial stringB; the element's own base is distinct stringA. At paused25% the implicit underlying endpoint is selected. Changing the normal declaration literalA to attr(data-image) producing the sameA changes the underlying taint without changing either stored endpoint. Reverse direction and missing-final endpoint at75% are symmetric. The fixed initialB differs from both A and changed-controlC, avoiding an interpolation equality shortcut. BuildSegmentsFromValueEntries calls HandleMissingInitialKeyframe/HandleMissingFinalKeyframe; the resulting null endpoint causes HasReplaceableValues to fail and EnsureBaseStyle to request the base.

EnsureBaseStyle → ServoStyleSet::GetBaseContextForElement → Servo_StyleSet_GetBaseComputedValuesForElement removes animation rules and resolves normal rules in the current element context. It then extracts a fresh animation value into mBaseValues. Servo_AnimationCompose requests the underlying value for a null endpoint and, in the absence of a lower effect, retrieves this map. composite_endpoint clones the underlying value for a null endpoint. The registered String component is noninterpolable; compose_animation_segment selects the appropriate endpoint on interpolation failure. Thus forced recomposition should use the new taint if base reconstruction succeeded.

## Why an already-delivered restyle may not suffice

A normal style-attribute replacement in matching::replace_rules_internal replaces author style nodes but retains the animation rule. process_animations queues EFFECT_PROPERTIES for an existing effect on a normal traversal. Gecko_UpdateAnimations calls EffectCompositor::UpdateEffectProperties, which marks cascade state dirty and invokes UpdateProperties. Marking cascade dirty alone does not enqueue animation resampling. UpdateCascadeResults requests animation restyles only for changed compositor-important overrides or changed transition/animation property membership; neither is changed by this single custom-property fixture. Custom properties are not compositor-animatable in that code.

ServoStyleSet::StyleDocument performs the extra animation traversal only when EffectCompositor::PreTraverse finds queued animation restyles. PreTraverse consumes mElementsToRestyle and posts animation replacement hints. A paused effect has unchanged computed progress, so NotifyAnimationTimingUpdated need not enqueue another sample. Advancing currentTime by1ms changes progress and provides a discriminating explicit resample control.

This is a conditional call-chain argument: no exhaustive proof excludes every other dirty-style trigger, initial pending animation task or rule-resolution route. A browser pass may show one of those already supplies the necessary scheduling. Do not infer a bug solely because the local comparator ignores metadata.

## Probe and independent oracle

probe.html has eight synchronous WPT cases: neutral-start both directions with same/different payload; neutral-end both directions with same payload; two explicit replacement controls. Each uses a nonanimated twin with identical base declarations, literal image-set calibration, initial effect observation, captured immediate result, then forced time seek within the same discrete half. It checks the twin and forced-resample results before the captured immediate result. This separates failure to compute/publish a tainted base from failure to resample it. The target result is captured before the twin/reference flushes. No setKeyframes call occurs during the mutation, so this does not exercise the endpoint retention repair itself.

Predicted discriminator, not an observed result: four same-payload implicit-endpoint cases fail only Immediate effect URL taint; different-payload and explicit-replacement controls pass; forced resampling passes throughout. If forced resample fails, the base provider/publication or interpolation premise is not established and the scheduling diagnosis must not be asserted. Tests do not rely on network loading, if(), parent inheritance or an attr() keyframe provider. They do rely on current registration/normal attr computation and metadata-preserving map publication; standalone independence from earlier fixes has not been demonstrated.

## Negative findings and boundaries

mBaseValues is rebuilt even when the change flag is false: the candidate is stale composed output/scheduling, not necessarily stale cached base storage. Effects with two explicit replace endpoints need no base and should ignore the mutation. A changed payload normally sets baseStylesChanged and requests restyle. A running animation or explicit time change may mask missing scheduling. Other effects, changed property membership, transitions or compositor overrides can independently enqueue work; the probe excludes them.

Do not generalize to additive strings: their addition is unsupported and may fall back to the explicit endpoint, so they are not a suitable oracle. Numeric additive cases would introduce separate interpolation-taint and observable-conversion questions. Neutral string endpoints provide the narrower test. Base-map removal detection, arbitrary metadata such as URL data, inherited base changes, full dirty-bit propagation and all public animation histories are unproved/uninspected beyond the named paths.

If runtime confirms the predicted discriminator, a candidate repair boundary is metadata-aware comparison inside EnsureBaseStyles, using the endpoint accessor while retaining ordinary value equality. Before proposing a patch, test whether it must inspect only custom entries, confirm null/missing entries and changed-map shape, and verify that requesting the existing Layer restyle is sufficient. No change to global equality is justified by this audit alone.

## Primary specification readings

Read current primary drafts with the web tool on2026-10-19 (Web Animations draft dated8October2026):

- https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect : implicit endpoint0/1 takes the underlying value; no frozen old-base exception.
- https://drafts.csswg.org/web-animations-1/#animating-properties : registered properties use computed-type animation; incompatible discrete components select endpoints at half progress.
- https://drafts.csswg.org/css-values-5/#attr-security : registered substitution preserves attribute provenance and a tainted URL makes the declaration invalid at computed-value time.

The expected immediate result follows from the current underlying value, not from the native comparator. These are linked current readings, not archived full-spec bytes. Searchfox discovery covered EnsureBaseStyles, UpdateProperties callers, EFFECT_PROPERTIES, PreTraverse, UpdateCascadeResults, base resolution and composition. Exact local complete files are retained because the endpoint candidate is not indexed.
