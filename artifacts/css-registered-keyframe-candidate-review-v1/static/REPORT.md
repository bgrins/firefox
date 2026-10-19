# Registered keyframe endpoint substitution

## Finding and disposition

The retained six-case root browser diagnostic has four midpoint failures and two passing controls. Literal `0` to `42` and `0` to `calc(40 + 2)` produce `21`; attribute end, attribute start, attribute fallback, and variable end produce the discrete endpoint (`42`, `0`, `42`, `42`). The harness ends OK. `OBSERVATIONS.json` is reconstructed from the retained raw log. This is a browser-observed interpolation defect with a matching source explanation, not a result of a universal formal proof. This audit did not execute a browser or compile Gecko. The earlier animation-taint idea was not confirmed and is not a finding here.

Recommend a narrow typed-Unparsed endpoint conversion in `Servo_GetComputedKeyframeValues`, after its existing custom-property builder completes. Preserve all generic conversion callers and the existing CSS-wide, Parsed, universal and unregistered paths. Root owns the actual patch, paired runtime validation and acceptance.

## Independent normative trace

1. [Web Animations, computing property values](https://drafts.csswg.org/web-animations-1/#computing-property-values): keyframe values are resolved using the target element's computed dependency context. [Computed keyframes](https://drafts.csswg.org/web-animations-1/#calculating-computed-keyframes) applies that operation to each specified property before effect interpolation. Thus the raw function text is not itself the numeric endpoint.
2. [Properties and Values API, computed value behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation): registration syntax is checked at computed-value time. A successful `<number>` literal computes to the numeric value; an invalid registered value follows invalid-at-computed-value-time handling.
3. [CSS Values 5, attr substitution](https://drafts.csswg.org/css-values-5/#attr-substitution): `attr()` is replaced at computed-value time, using its typed attribute value or applicable fallback. The target contains `data-value="42"`; the missing attribute has numeric fallback `42`.
4. [Properties and Values API, animation behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior): registered values interpolate according to their computed type. Here both endpoints compute as numbers. With default linear easing and replace composition, duration 1000 and current time 500, the independent expectation is `(0 + 42)/2 = 21` in both directions.

Verdict: REACHED for the six retained static-endpoint cases. The registration, target attachment, pause, explicit sample time and literal/calc controls rule out an unsupported registration or timing explanation. This does not establish dynamic dependency invalidation, all keyframe cascades, or URL-taint correctness. The live-computed-keyframe requirement makes dynamic updates a useful separate regression gate, not something proved by these static samples. `evidence/PRIMARY-WEB.json` retains primary fetch results; the current editor drafts were consulted on 2026-10-19. The missing webspec-index tool prompted direct-primary fallback authorized by root.

## Complete source path

Full files are retained under `evidence/source`; `SOURCE-PINS.json` identifies the exact locally modified source read in this audit. Searchfox was used for discovery; its indexed source is not asserted identical to this project branch.

| Stage | Actual operation and consequence |
|---|---|
| `Servo_GetComputedKeyframeValues` | Creates one animation context, then seeds a fresh keyframe custom map from `style.custom_properties().clone()` for each keyframe. A real element AttributeTracker is passed to builder completion. |
| `PrioritizedPropertyIter`, `compare_property_priority` | Custom declarations sort before other properties. The same sorted iterator is reset between map construction and output. Equal non-shorthand categories compare equal; preserve existing order rather than introduce a new sort. |
| `KeyframeCustomPropertiesBuilder::cascade/build` | Cascades normal custom declarations, records first-seen custom names, and runs `apply_custom_and_prioritary_properties` / cycle resolution. The finished map resides in `context.builder.substitution_functions.custom_properties`. |
| `substitute_references_if_needed_and_apply` | Substitutes var/env/attr, interprets fallback CSS-wide keywords, invokes registered syntax conversion and installs the resulting computed value. Failure follows `handle_invalid_at_computed_value_time`. |
| Existing output loop | Reads the original declaration block with `to_animation_value_iter`, which skips important declarations and invokes `AnimationValue::from_declaration`. |
| `AnimationValue::from_declaration` Custom arm | Invokes `CustomAnimatedValue::from_declaration` with the original CustomDeclaration. It does not select the completed keyframe map. |
| `CustomAnimatedValue::from_declaration` Unparsed arm | Tries `SpecifiedValue::compute` directly on `value.css`. The raw attr/var text fails numeric syntax parsing and becomes `ComputedValue::universal` through the fallback. The universal path itself has an existing substitution FIXME. |
| `CustomAnimatedValue::animate` / generic value variants | Typed numeric values interpolate; mismatched/universal values cannot use numeric interpolation. Root's observed discrete endpoints agree with this path. |

`ComputedCustomProperties::get(registration, name)` chooses exactly the inherited or non-inherited map. Do not substitute `get_for_cssom` or `AnimationValue::from_computed_values`: both search inherited first and then non-inherited, and the latter explicitly records bug 1869476. `StyleBuilder::custom_properties` exposes the newly built map, not a detached clone of the initial style.

## Proposed narrow implementation contract

Within the existing non-null declaration-block branch of `Servo_GetComputedKeyframeValues`, iterate `normal_declaration_iter`. For each declaration:

- If it is Custom with `CustomDeclarationValue::Unparsed` and registration is non-universal, read `context.builder.custom_properties().get(registration, &declaration.name)` and create `AnimationValue::Custom(CustomAnimatedValue::from_computed(&declaration.name, value))`.
- Otherwise invoke the existing `AnimationValue::from_declaration` with the same context, base/default styles, and dummy AttributeTracker as the old iterator. Preserve its Option-return filtering.
- Pass any produced value through the existing `maybe_append_animation_value`. Keep property restriction, display filtering, seen-name suppression, neutral null-block handling and simulated-computation-failure handling in their current locations.

Expose the existing `from_computed` constructor narrowly (public with its existing meaning), or add a public AnimationValue constructor wrapping it. Do not serialize and reparse the map. The constructor clones both the optional computed value and declaration name; this preserves the wrapper's attr-taint field and typed representation, and retains the identity premise used by the separate animation-map proof. This is an ownership-safe clone under the existing Arc/value APIs, not a new lifetime or heap proof.

An empty or important-only block must still produce no value: do not construct an endpoint merely from the outer property's name. A missing map value means the guaranteed-invalid custom value inside `Some(AnimationValue::Custom(...))`; it is distinct from the null animation pointer used for a neutral keyframe. Preserve that distinction.

Generic `CustomAnimatedValue::from_declaration` must remain unchanged. `Servo_GetAnimationValues` builds a SMIL animation context but does not run the keyframe builder; `Servo_AnimationValue_Compute` likewise converts a first normal declaration directly. Blindly reading their context map would return an old/base value rather than compute the supplied declaration. Their unresolved-substitution behavior is a separate caller scope. The proposed branch also leaves other template callers untouched.

The existing builder already incurs the cascade/substitution work. Reusing its result replaces a second raw typed parse with a registration-selected lookup and clone. It does not add a new graph traversal, sorting phase or dependency scheduling rule. No timing benchmark or global performance claim is made.

## Defaults, invalid values and cycles

The actual invalid handler is important: for a non-universal registration it copies a non-root inherited property's parent value, or computes the registration initial value for non-inherited/root cases. Otherwise it removes the name. `substitute_all` invokes this same handler for custom-property cycles. These paths overwrite/remove the seeded base instead of retaining it. They support reading the completed map for invalid typed raw text and ordinary detected cycles, with explicit browser controls still required.

Do not generalize this result to direct CSS-wide declarations. `value_may_affect_style` returns false for inherited `inherit`, non-inherited `initial`, and any `unset`, relying on ordinary cascade initialization. The keyframe builder instead seeds the element's base computed map. For example, non-inherited `--n` with initial 0 and base 42 keeps map 42 when its direct keyframe value is `initial`; the existing direct converter selects the actual initial 0. Reading the map for all Custom variants would introduce a regression. Keeping CSS-wide conversion unchanged avoids that regression.

Two separate source leads remain unconfirmed by this audit: another keyframe property's reference to that skipped CSS-wide declaration can observe the seeded map; and a substitution fallback yielding `initial` uses `remove_and_insert_initial_value`, which stores a Universal wrapper around the registration initial text rather than a newly typed value. Neither is claimed fixed by this proposal. Direct `revert` variants retain their existing omission and bug 1533327 boundary. A registration map can also contain stale entries following registration changes; registration-aware selection avoids the known two-map lookup ambiguity but is not a proof of registration lifecycle freshness.

## Dependencies and priority boundaries

Existing builder substitution/cycle rules are reused, not replaced. Registered dependencies on font metrics, line height, color scheme and other custom properties continue through its existing graph. The keyframe builder has an empty ordinary Declarations collection; do not claim it implements the full animation cascade or all same-keyframe non-custom dependencies. Web Animations computes dependencies from the element's computed context; cross-animation ordering/invalidation remains a separate obligation. The frozen existing `registered-var-to-registered-animating.html` tests that harder case and has expected-FAIL metadata. Preserve and report its outcome rather than treating it as covered by the new six cases.

First-seen custom selection and output seen filtering use the same prioritized declarations. Switching only value conversion does not introduce a new keyframe-priority winner. Input list uniqueness, the native callback supplying declarations, pseudo restrictions, neutral endpoints, and importance filtering remain the existing providers. Do not expand scope to synthetic duplicate property lists without a reachable caller.

## Focused root validation proposal

1. Preserve the exact six existing endpoint cases; require the four failures to become numeric midpoint passes and both controls unchanged.
2. Repeat attr/var cases with inherited and non-inherited registrations, nonzero initial value and parent/base values deliberately different from each endpoint.
3. Add direct `initial`, `inherit`, `unset` controls with distinct base/parent/initial values. These disconfirm an overbroad map-read branch.
4. Invalid raw typed text, missing var without fallback, missing/invalid typed attr without fallback, and a self-cycle: check the actual expected initial/parent endpoint. Include valid explicit fallback control. Keep fallback-to-CSS-wide as a separate diagnostic if its provider remains Universal.
5. Retain unregistered and universal registration discrete controls, an empty/invalid keyframe value, and existing no-crash invalid animation coverage. Preserve neutral endpoints and important-declaration rejection where the input API admits them.
6. Run the existing cross-animation registered-var test with its retained metadata, plus relevant registered animation tests. Dynamic attribute/base mutation deserves a separate calibrated test; no claim that static endpoint conversion fixes restyle scheduling.

## Prior art and limits

[Bug 1883255](https://bugzilla.mozilla.org/show_bug.cgi?id=1883255) is an open broad cascade-integration enhancement and explicitly names this duplicated animation path. Related historical interpolation work includes bugs 1869185 and 1877383. The latter concerned missing endpoint/base typing, not proof that the present attr/var endpoint diagnostic is already fixed. This bounded search does not establish novelty or justify filing a new bug without checking those relationships. Bug 1869476 was referenced by retained source; the direct web fetch failed and its current status is not asserted.

No native patch, candidate execution, compiled extracted witness, Lean proof, full parser/cascade proof, dynamic dependency proof or final acceptance is provided here. The useful result is the independently checked static endpoint oracle, exact root raw observations, causal source trace, and a narrower conversion boundary that avoids a concrete CSS-wide regression. Original full formal milestones and refuted/open claims elsewhere are unchanged.
