# Universal-to-typed registration transition observation

Prepared, not run. This probe targets a source-backed transition path absent from the earlier paused CSS-animation registration tests. It uses successful primary `attr(data-ticket)` values and fixed data-image URLs; it has no attr fallback, external receiver, native patch, or disclosure claim.

## Exact e86 handoff

The saved e86 `Servo_ComputedValues_ShouldTransition` extracts custom animation values directly from the before-change and after-change maps. `AnimationValue::from_computed_values` clones those values without reinterpreting the old map under the current registration. Universal versus typed `ValueInner` representations differ even when their serialized strings match. `allow-discrete` bypasses the normal interpolation rejection after the animatability/property-value checks.

`nsTransitionManager::ConsiderInitiatingTransition` passes those endpoints to `DoCreateTransition`. Crucially, `AppendKeyframe` first calls `Servo_AnimationValue_Uncompute`; `DoCreateTransition` then calls `SetKeyframes` with the **new** computed style. `SetKeyframes` immediately updates properties. Thus this is a potential registration crossing during transition construction, before the first sampled frame, rather than merely an old universal object sampled later.

For an old attribute-tainted universal endpoint, `ComputedValue::to_declared_value` preserves the taint by making the reference-free Unparsed value explicitly tainted. `KeyframeCustomPropertiesBuilder` seeds the current map, then cascades that declaration using the current stylist. In the typed case, `Cascade::value_may_affect_style` does not use its same-universal-value shortcut against an existing typed value. `cascade_custom_property` sends the reference-free declaration to `substitute_references_if_needed_and_apply`. This reaches `substitute_internal` / `do_substitute_chunk`, whose no-reference branch creates default taint rather than importing `explicitly_attr_tainted`. The earlier computed-map bypass in `Servo_GetComputedKeyframeValues` then reads the rebuilt typed value: it excludes the separate `CustomAnimatedValue::from_declaration` parser concern, but does not exclude this map-construction path.

The endpoint used for cancellation is separate. `CSSTransition::SetEffectFromStyle` stores the rebuilt segment's end value. `DoUpdateTransitions` checks it against the after-change style. Since the new typed endpoint can remain tainted and equal to that style, losing taint solely on the reconstructed start endpoint need not trigger this cancellation. On subsequent updates, equality to the end value can retain the transition. This is a source inference, not an observed transition or a proof covering every restyle interleaving.

Sampling also has a relevant split: `Value::animate` would OR endpoint taint after successful inner interpolation, but the saved `GenericValueComponent::String` is marked `animation(error)`. `compose_animation_segment` falls back from interpolation error to cloning the from endpoint below 0.5 and the to endpoint at or above 0.5. Thus an OR from the other endpoint does not automatically repair a lost string start-endpoint taint. This is why both controlled sampling times matter.

The probe must still establish that stylesheet registration replacement supplies the old universal and new typed values to this path, creates a real transition, preserves it through sampling, and produces the predicted sink difference. Source inspection alone does not establish those browser outcomes.

## Five isolated cases

Each iframe owns its own `--source`; registrations always use `inherits: false`. The initial attribute exists in the parsed document before style is first observed. All transitions have a 100-second linear duration.

1. Universal → `<string>` plus primary attribute A → B in the same unflushed change, `allow-discrete`: primary target, with distinct serialized endpoints.
2. Universal → `<string>` with unchanged primary attribute A, `allow-discrete`: isolates representation change from a token change.
3. Registration plus primary attribute A → B, `normal`: interpolation eligibility comparison.
4. Stable `<string>` registration, primary attribute A → B, `allow-discrete`: same-registration taint preservation control with distinct endpoints.
5. Universal → `<string>`, fixed literal data-image A, `allow-discrete`: public literal/sink and representation-change control.

The combined registration/attribute changes occur before any computed-style or animation query; the probe does not rely solely on equal serialized payloads producing a transition.

`probe.js` records initial and stable initial values, immediate post-change values, actual constructor/property roster, registration rule, and animation keyframes. It samples only a unique real `CSSTransition` for `--source`, with no preexisting animations. It pauses that transition and records exact progress 0.25 and 0.75, play state, current time, custom value and background image. It then cancels animations, records the unanimated after value, and removes the iframe. Getter order is custom value, background image, then the registration-control value. Each frame has a separate unanimated element declaring `--source: 17px`: universal registration must preserve 17px, while `<string>` must produce the registered initial string. Before/after and sampled controls are recorded. The expected quoted primary data-image A/B tokens and image-set syntax support are also recorded and checked; failed substitution cannot serve as a blocked-sink control. `samplePrerequisites` requires those calibrations as well as transition/timing checks; all raw observations survive a failed calibration. Timers are cleared; failures remain explicit observations.

A missing transition is an unmet sampling prerequisite, not a passing security result. The normal-behavior case can legitimately have no transition. A useful candidate result would require the target's primary-attr baseline and after-cancel values to remain blocked, the early sample to differ while the late sample remains blocked, correct sampled progress and preserved attribute-derived tokens, plus functioning same-registration and literal controls. Any unexpected control result requires investigation before attributing an effect. Computed image serialization alone is not proof of an external request or disclosure.

## Execution contract and scope

Serve this directory using root's existing isolated browser procedure and retain `await window.done` (also `window.REPORT`) with actual browser identity and source/application authority. This package does not start a server, browser or native process. It does not assert source-bound behavior for System Firefox or run against the active diagnostic application.

Only JavaScript syntax checking has run. No browser results, native checks or specification verdict are included. This experiment is deliberately different from the earlier six-phase static / paused inherit / paused var-endpoint animations; it must not be reported as a repeat or extension of their measured 18 blocked sinks per browser.
