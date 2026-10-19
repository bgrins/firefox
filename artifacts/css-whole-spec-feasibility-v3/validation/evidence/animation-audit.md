# Animation attr-taint equality: bounded source audit

## Finding

A concrete candidate exists in replacing computed keyframe segments after `setKeyframes()`. No browser result is claimed in this capsule. The six-case proposal uses registered <string> constant endpoints and observes image-set(var(--name)); it does not rely on unsupported if() or numeric-to-string functions.

With both old endpoints equal to literal URL text A, replacing both by attr(data-image) whose value is the same text A changes required taint but not the payload comparison. The reverse update can retain old taint. Different-payload updates and fresh-effect controls discriminate this route. The test checks initial computed payload/URL behavior, newly stored raw keyframes and final computed payload before final URL behavior; paused currentTime is moved from500 to501 to force sampling. All URLs are a fixed data image; no external URL or secret is used.

## Complete source route

1. `KeyframeEffect::SetKeyframes(JSContext*,...)` parses new keyframes and gets target style; the overload checks raw keyframe equality, stores new keyframes and invokes UpdateProperties. Literal syntax and attr() syntax are different declaration payloads, so this first equality should not suppress this update.
2. `UpdateProperties` calls BuildProperties, which calls `KeyframeUtils::GetAnimationPropertiesFromKeyframes`. That computes values through Servo_GetComputedKeyframeValues, copies the resulting values into entries, and builds property segments.
3. Current project `Servo_GetComputedKeyframeValues` first computes keyframe custom properties. For typed unparsed custom declarations it copies the registration-selected computed map value into CustomAnimatedValue. This is the earlier registered keyframe substitution repair; the present audit does not relabel that repair or claim it absent upstream. Our test deliberately uses <string>, not universal syntax, so this is its route.
4. `UpdateProperties` compares old and new AnimationProperty arrays before assigning the new array. AnimationProperty compares identity and segments; AnimationPropertySegment compares offsets, endpoint AnimationValues, timing and composite operations. C++ AnimationValue equality delegates to Servo_AnimationValue_DeepEqual. Generated AnimationValue::Custom equality delegates to CustomAnimatedValue's derived equality; its Option<ComputedValue> delegates to Value<Component>::PartialEq, which compares only v and expressly ignores attr_tainted/url_data.
5. Equal payload endpoints therefore make propertiesChanged false. EnsureBaseStyles still runs, but the method returns before assigning mProperties even if it requests a restyle for changed base values. With constant replacement endpoints no underlying value is needed. A later sample continues using retained segment values.
6. `compose_animation_segment` clones the selected endpoints on discrete fallback; <string> animation is non-interpolable. Both endpoints within each effect have identical taint, so the defect does not require choosing interpolation metadata across different endpoints. `Servo_AnimationCompose` inserts the selected value; custom uncompute/to-declaration and the usual var substitution carry the retained taint to URL checking.

## Normative oracle

[Web Animations](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-setkeyframes), editor draft8October2026, defines replacement keyframes and calculation of their computed values before effect sampling. [Computing property values](https://drafts.csswg.org/web-animations-1/#computing-property-values) resolves each keyframe in the target context. [CSS Values attr security](https://drafts.csswg.org/css-values-5/#attr-security) requires taint on values produced by attr and their substituted equivalents. The computed string can remain identical while its permission for URL use changes. An equal serialized string alone is therefore not a valid cache-reuse criterion for this observer. Constant endpoints avoid any disputed rule about mixed-taint interpolation or additive composition.

## Distinctness and negative coverage

The existing map/cascade two-site repair affects ordinary custom-property insertion and cascade skip decisions; it does not alter AnimationValue equality or UpdateProperties. The earlier keyframe substitution repair changes computed-value construction and is a provider prerequisite for the exact current-tree test, not the new cache-reuse location. The earlier initial/inherit/reset flag repairs concern defaulting and recascade, not setKeyframes endpoint replacement.

Existing attr-security-animation.html has a non-interpolable string test and several numeric if() observers. The first starts with different text; it does not test same-text replacement of an existing effect. Numeric if() availability was already a limitation in the project’s earlier animation-taint probe; none of the new cases uses it. Existing transition files exercise different creation/composition routes. [Bug2033518](https://bugzilla.mozilla.org/show_bug.cgi?id=2033518) and [bug2071160](https://bugzilla.mozilla.org/show_bug.cgi?id=2071160) are WPT-sync records for related animation/transition taint behavior, resolved in Firefox152 and158. They are context, not evidence this particular Gecko route is novel or fixed.

`Value::animate` also retains the left operand’s taint after successful interpolation. That merits a separate semantic/provider audit; this capsule makes no interpolated numeric taint finding because a supported observable route and precise combination contract are still needed. CSS-wide, universal animation values, SMIL, transitions, additive composition, neutral endpoints and dynamic attribute-change scheduling are outside the bounded repro. No global PartialEq change is proposed: different consumers may need payload equality versus metadata-sensitive replacement checks.

## Next gate and repair constraint

Root should run the six exact cases on its pinned combined build. If only the two same-payload updates fail, review a narrowly metadata-aware animation-value comparison or update predicate at the retained-value boundary. Preserve numerical transition decisions and unrelated equality consumers; audit raw-keyframe equality, base-value reuse and any equality-based segment dedup separately. A new proof could state observational substitutability of retained endpoints under payload+taint equality; it must not infer a universal animation theorem from array equality alone.

## Evidence limits

Complete source snapshots are retained and hashed, including current prior-repair glue. Node syntax validation only; no build/browser/native extraction run here. Searchfox discovery was used for actual call sites; local snapshots capture project changes. No full source-memory/compiler or scheduling proof, no security exploitation or novelty claim.
