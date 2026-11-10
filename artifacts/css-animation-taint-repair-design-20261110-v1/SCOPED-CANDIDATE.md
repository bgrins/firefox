# Candidate: active CSS-animation values

This candidate fixes the demonstrated intersection: a currently sampled custom
property from CSS keyframes wins on an element, and an ordinary declaration on
that element consumes it in a nonanimatable destination. It also preserves the
taint through selected custom-property references and ordinary inheritance, as
required by current text. It deliberately does not implement a global tainted-name
registry or strip inherited taint. It is an implementable partial repair, not a
claim that property-name acquisition is fully implemented.

## Origin must survive composition

A bit applied to every value in the animations cascade level would also newly
taint Web Animations API effects. It cannot isolate CSS keyframes. Further,
`EffectCompositor::GetServoAnimationRule` can include transitions while composing
the animations level, because a transition can supply an underlying value for a
missing keyframe endpoint. Therefore “not the transitions level” is not a proof
that no transition value participated.

The authenticated C++ sources expose the necessary earlier boundary:

- `ComposeSortedEffects` has each `Animation` object before composing its effect.
- `Animation::AsCSSAnimation` returns null by default; `CSSAnimation` overrides it.
- `KeyframeEffect::ComposeStyleRule` still has its animation and invokes
  `Servo_AnimationCompose` for a specific property.
- `Servo_AnimationCompose` obtains any required underlying value, calls
  `compose_animation_segment`, then inserts the result in the animation value map.

One concrete representation is an internal **sample origin** marker on
`CustomAnimatedValue`, distinct from persistent **animation taint** on the computed
custom-property value. Pass CSS-animation origin from `ComposeStyleRule` to
`Servo_AnimationCompose` before the producing object is lost. The marker travels
with the composed custom value, not in a set of all properties touched by any
effect: a later replacement can discard a lower effect, whereas additive or
underlying-value composition can consume it. Preserve provenance for participating
values and add the current effect's origin when it actually produces a result.
Do not blindly union every lower effect that happened to run.

At `PropertyDeclarationBlock::from_animation_value_map`, the actual sampled-rule
publication boundary reached by `get_animation_rule`, turn the relevant CSS
sample-origin marker into persistent custom-value taint. Keep generic
`AnimationValue::uncompute` origin-neutral: it preserves existing value taint but
does not convert a transient sample-origin marker into new taint. The separate
publication method avoids teaching CSSOM helpers and shared `commitStyles`
composition that merely converting an animation value always acquires taint.

This split needs a new internal marker plus its propagation, but avoids threading
an implicit “currently publishing styles” global through generic animation APIs.
An alternative is an explicit composition-purpose argument threaded through the
shared C++/Rust composition call chain; it has the same obligation to avoid
acquisition during non-publication calls. Do not combine these mechanisms without
a demonstrated need.

`AsCSSAnimation()` identifies an object class, not an immutable history of its
keyframe declarations. A CSSAnimation whose effect/keyframes have been replaced
by script is a required provenance control before claiming the broader
CSS-versus-Web-Animations boundary is completely handled. The minimum direct
fixture uses unmodified stylesheet-authored CSS keyframes.

## Persistent value transport and substitution

1. Add an independent animation-taint field to computed/specified custom values
   and an explicit carrier in universal token values. Preserve it through
   `to_computed_value`, `from_computed_value`, `to_declared_value`, universal
   wrapping, serialization back to token values, and declaration recascade.
2. Preserve selected-reference taint in `Substitution` and the custom-property
   resolution paths, including single-reference, concatenation, recursive,
   reference-free and parsed-value paths. Custom-property destinations accept the
   value and retain its taint. An unused fallback is not evaluated by this
   transport; the stronger question whether its syntactic reference infects the
   containing property remains an explicit unimplemented policy boundary.
3. In `substitute_one_reference`, if the current primary is tainted and the
   destination is a nonanimatable noncustom property, use the existing
   invalid-primary/fallback path. Do not mutate the stored source. Preserve
   destination identity through shorthand expansion and audit `None` separately.
4. Store taint in inherited computed custom values and preserve existing
   inheritance behavior. Do not implement issue 13933's proposed stripping.
5. Include persistent taint in custom-map semantic equality and deduplication.
   Audit sample-origin/taint-only changes at effect suppression points separately
   from payload interpolation equality. A source that changes provenance with
   equal text must still change a dependent destination's computed style.

The final publication hook applies to both universal and typed custom values,
so the registered `from_computed` construction path does not bypass acquisition
there. Registered properties must have explicit tests; lack of a typed browser
calibration is a coverage gap, not permission to exempt them. Taint during
keyframe dependency pre-resolution is a separate integration obligation.

## Minimal affected surfaces for this candidate

| Surface | Reason |
| --- | --- |
| `dom/animation/KeyframeEffect.cpp` | Supply CSS effect identity while it is still available. |
| `servo/ports/geckolib/glue.rs` | Receive that identity at `Servo_AnimationCompose`; attach and preserve per-result sample provenance. Regenerate the corresponding FFI declarations through the normal build. |
| `servo/components/style/properties_and_values/value.rs` | Separate transient sample origin from persistent custom-value taint; preserve taint through typed/universal conversions and composition. |
| `servo/components/style/properties/helpers/animated_properties.mako.rs` | Update any explicit `CustomAnimatedValue` construction/destructuring and provide an explicit publication conversion if needed. |
| `servo/components/style/properties/declaration_block.rs` | Acquire persistent taint only while turning the sampled animation map into a cascade rule. |
| `servo/components/style/custom_properties.rs` | Token carrier, selected-reference transport and destination guard. |
| `servo/components/style/custom_properties_map.rs` | Preserve semantic metadata differences through storage and equality. |

`properties/mod.rs`, `properties/cascade.rs` and existing glue constructors remain
mandatory audits for destination classification and all custom-value paths; they
may need changes once the exact representation is compiled. The list is a
reviewable starting surface, not a promise that no other initializer or FFI
declaration will require an update.

## Required acceptance and honest limits

The minimum browser acceptance is R1–R7 and R8's equal-text metadata control, plus
the inherited case I1. Include R9's registered cases before claiming the chosen
representation transports typed provenance correctly. Retain clean WAAPI-only
and transition-only controls to ensure the scoped origin mechanism does not
silently acquire taint on those sources. Run existing attribute-taint tests to
prove the new flag has not replaced or cleared the old one.

Inactive keyframes, clean important winners, arbitrary same-named properties,
removed-rule lifetime and unused-fallback infection remain outside this partial
repair's acquisition claim. Current property-name prose may require additional
behavior in these cases. Explicitly record the chosen behavior and coverage;
do not treat passing the direct fixture as proof that they conform.

No copied-source prototype is included. Source authentication and design review
are complete; native implementation and browser validation remain the next task.
