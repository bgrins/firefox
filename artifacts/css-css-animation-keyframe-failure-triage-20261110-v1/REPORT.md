# Three existing CSSAnimation.getKeyframes failures

Read-only triage, 2026-11-10. Source/test basis: `f3949d2992abdc02536b9a61e51dc7d603ce0868`. The concurrent property-input snapshot experiment does not change CSS keyframe assembly. No native changes, test changes, browser execution, or new bug count are part of this capsule.

| Existing subtest | Observed first failed assertion | Current-spec assessment | Follow-up |
|---|---|---|---|
| Multiple frames at the same time with different easing/composite | Frame 1 contains `fontSize`; expected `marginTop` and `paddingLeft` | WPT group order is supported by the current draft. Pinned implementation uses a different group order. | Revisit known bug 1778402 with the updated normative text; investigate a narrowly scoped grouping fix separately. |
| CSS variable overridden inside a keyframe | Initial frame additionally contains `--end-color` | Including the custom property is required. This failed property-inventory expectation is stale. | Correct the WPT property inventory after separately checking all returned values. |
| Only custom property in a keyframe | Initial frame additionally contains `--not-used` | Including the custom property is required even when no ordinary declaration references it. | Correct the WPT property inventory after separately checking all returned values. |

The runtime record stops at each first assertion failure. It does not establish that every later value/composite assertion would pass after adjusting an expectation. These results preserve all three baseline failures; they do not waive any change in the running snapshot experiment.

## Ordering: current expectation reached

Scenario: an ordinary CSS animation, percentage `from`/`to` offsets, no `setKeyframes()` override, with the exact authored groups in the existing WPT. Its `from` declarations occur in this order:

| Source occurrence | Group `(offset, easing, composite)` | Property |
|---|---|---|
| 1 | `(0, ease, add)` | color |
| 2 | `(0, ease, accumulate)` | margin-top |
| 3 | `(0, linear, add)` | font-size |
| 4 | `(0, ease, accumulate)` | padding-left |

All intervening `to` declarations merge into the same offset-1 group and do not affect the relative offset-0 order.

1. [CSS Animations 2, processing keyframes, step 2.2](https://drafts.csswg.org/css-animations-2/#keyframe-processing) groups matching selectors, easing and composition.
2. Step 2.3 processes groups by their earliest member. Step 4 specifies the resulting order as “document order with duplicate keyframes collapsed to the earliest position.” Percentage offsets are then stably sorted. Thus the margin/padding group precedes font-size.
3. The same section explicitly identifies computed order as the order returned by `getKeyframes()`. [Web Animations getKeyframes, step 2](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-getkeyframes) selects computed keyframes for a CSS animation whose keyframes have not been replaced. Its output loop preserves the selected frame sequence.

**Verdict: REACHED** — for this percentage-only fixture, the current specification requires the WPT's group order. This is a current-spec discrepancy in the pinned implementation, already described by an existing bug; it is not a newly counted bug.

The tool's step-only graph found no route from the API definition to CSS computed-order at depths 9 and 18. That graph absence is not a negative verdict: the deciding CSS rule is explicit prose in Sort Frames, reproduced in `css-processing.md` and independently checked against the current primary HTML in `PRIMARY-WEB.json`. This trace uses the quoted direct rule, not a claim of graph completeness.

The native chain is concrete:

- `KeyframesAnimation::from_keyframes` in `keyframes_rule.rs` stably sorts percentage steps by offset.
- `Servo_StyleSet_GetKeyframesForName` visits those steps in reverse, obtains/creates a frame for each matching tuple, and reverses the completed array.
- `GetOrCreateKeyframe` in `GeckoBindings.cpp` returns an already-created matching group without moving it; otherwise it appends one.
- Offset-0 groups are first encountered in reverse order as margin/padding, font-size, color. The final reverse yields color, font-size, margin/padding: exactly the observed mismatch.
- `CSSAnimationKeyframeEffect::GetComputedKeyframes` retains this percentage order while completing endpoints. `KeyframeEffect::GetKeyframes` serializes it.

This explains grouping order only. A future repair must preserve last-declaration precedence, logical/physical property handling, easing/composition distinction, and named-range ordering. Simply changing the traversal direction is not a supported repair design. The existing fixture uses different ordinary properties in different groups, so it demonstrates an observable API ordering discrepancy without establishing a visual rendering defect.

[Bug 1778402](https://bugzilla.mozilla.org/show_bug.cgi?id=1778402) comment 0 describes the same swapped groups and argues that Gecko matched the then-current reverse/prepend specification. Its history records RESOLVED WORKSFORME on 2026-11-03; the fetched history supplies no explanatory closing comment. That historical argument does not match today's explicit earliest-position rule. The metadata still links this bug and expects FAIL. The later [bug 2016574](https://bugzilla.mozilla.org/show_bug.cgi?id=2016574) work on range offsets and generated endpoint composites does not remove this failure; its narrowly captured commit context is in `HISTORY.json`. No regression-introduction date or reopening action is inferred here.

## Custom properties: inclusion reached

Scenario A declares `--end-color` on `:root`, then declares a different `--end-color` and `color: var(--end-color)` in the animation's `to` frame. Scenario B declares `transform` in `from` and only `--not-used` in `to`. Neither registers the custom property. Both create an ordinary CSS animation and call `getKeyframes()` without overriding its keyframes.

1. [CSS Variables 1, custom properties](https://drafts.csswg.org/css-variables-1/#defining-variables) defines their animation type as discrete. These are animatable properties even without registration or a consuming `var()` reference.
2. [CSS Animations 2, step 2.3.1](https://drafts.csswg.org/css-animations-2/#keyframe-processing) excludes properties whose animation type is not animatable. That exclusion does not apply here. The custom declaration is therefore retained in its authored endpoint and its name enters the animated-property set.
3. Step 3 supplies the property's underlying computed value at the missing initial endpoint. It does not remove the property because its value is unused by ordinary CSS declarations. The guaranteed-invalid underlying value for `--not-used` affects its value, not membership in the animated-property set.
4. [Web Animations computed-keyframe calculation, step 2.2](https://drafts.csswg.org/web-animations-1/#calculating-computed-keyframes) computes each property and retains the resulting pair. The CSSAnimation branch of [getKeyframes, step 2](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-getkeyframes) uses these computed frames; step 3.3 emits every animation property-value pair.
5. [Animation property name to IDL attribute name, step 1](https://drafts.csswg.org/web-animations-1/#animation-property-name-to-idl-attribute-name) preserves custom-property names, so the keys remain `--end-color` and `--not-used`. The indexed one-hop invocation is captured in `trace-custom.md`.

**Verdict: REACHED** — both custom properties must be included. The extra keys that trigger the two failures are supported by the current specifications. This verdict is about inclusion; it does not certify all serialized values, dependency semantics, or endpoint composites.

Native admission agrees: `PropertyDeclarationId::is_animatable()` returns true for `Custom`. `Servo_StyleSet_GetKeyframesForName` retains these declarations; `CSSAnimationKeyframeEffect::GetComputedKeyframes` collects them and completes missing endpoints. `KeyframeEffect::GetKeyframes` explicitly constructs custom names with `--` and defines enumerable properties on the returned object.

Neither custom-property metadata stanza links a dedicated bug. Blame and exact historical diffs distinguish their origins:

- The overridden-variable FAIL annotation was added by `a06a42587e6d571739fad82ab2a9e6dcce1955f7`, an upstream metadata sync under [bug 1811306](https://bugzilla.mozilla.org/show_bug.cgi?id=1811306). The sync bug documents animation-composition work, not a normative justification for excluding custom properties.
- The custom-only FAIL annotation was added by `f7058dcbbc993d326b30a6d3cb791e474b58d77d`, part of [bug 1846516](https://bugzilla.mozilla.org/show_bug.cgi?id=1846516), which implemented discrete custom-property animation. Its commit explicitly adjusted animatability checks. This provides direct historical context for the newly returned custom-property key, rather than evidence of a regression in this branch.

## Evidence boundaries and next step

The draft dates observed in primary HTML are 2026-08-18 for CSS Animations 2 and 2026-10-09 for CSS Variables 1. Indexed section digests, current primary excerpts, seven validated anchors, exact source objects, metadata history, and the three baseline failure records are frozen here. Searchfox was used for source discovery; actual reasoning uses the local pinned Git contents, because indexed upstream and this branch need not match. Available CLI versions reported updates; neither tool was changed.

The productive next native question is how to retain earliest group position while preserving reverse-cascade declaration precedence. That deserves a separate copied-source candidate and controls, not a change to the snapshot extraction. The custom cases instead need an isolated test-expectation audit with complete actual frame objects before any WPT correction. No additional browser run, new test, patch, or catalogue entry was created for this triage.

Run `python3 check.py` for frozen-file and pinned-Git authentication. It verifies evidence provenance, not the correctness of the prose interpretation or any new runtime behavior.
