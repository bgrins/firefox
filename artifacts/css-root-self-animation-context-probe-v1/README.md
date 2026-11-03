# Root identity during keyframe conversion

The direct primitive keyframe path in the immutable e86 source constructs an animation style builder with `is_root_element: false`, even when the animation target is the document element. No setter was found between that construction and the generated ordinary declaration conversion. This is a distinct source boundary from the missing dependency-publication investigation and from variation settings' choice of parent versus current font metrics. No browser result or repair is claimed here.

## Source route

The five complete source captures in SOURCE.json are exact `git show e86b64866cdc5e2260ba9be08c45756fd96e21bb:<path>` bytes. The existing publication review independently captures the same glue, style-builder and length-dispatch bodies.

1. `Servo_GetComputedKeyframeValues` receives the target and pseudo type. For an ordinary root target, its inheritance parent is absent. The helper `create_context_for_animation` passes the target style and optional parent style to `StyleBuilder::for_derived_style`.
2. `for_derived_style` uses the default computed values when the parent is absent, but explicitly initializes `is_root_element: false`. The target's writing mode, zoom and flags are copied separately; a copied `IS_ROOT_ELEMENT_STYLE` bit does not change this Boolean field.
3. `Context::new_for_animation` retains the supplied builder without replacing its root field. The keyframe loop calls `AnimationValue::from_declaration` using this Context. In the direct primitive arm, the generated code sets `for_non_inherited_property`, handles system fonts if applicable, and calls `to_computed_value`; it does not set root identity. The probe avoids variables, custom properties and system-font keywords.
4. The font-relative length dispatcher tests `context.builder.is_root_element` to choose root-self behavior for rem, rlh, rex, rch, rcap and ric. With false, rem/rlh use Device root values instead of the root-self branch. This is independent of the local font base selected by the property's converter.

Searchfox discovery 2ff1b6/fb7838 finds no explicit assignment that supplies root identity in this path; c27317 finds no `context.builder =` replacement. The exact captured constructors and direct conversion body, not absence of search hits alone, establish the described route. This does not audit every indirect/custom/SMIL conversion or claim that every current-root read is wrong. Other root-target animation paths need their own argument.

The existing 36-case WPT's root-self page exercises ordinary declarations. Its ordinary-root failures must not be described as animated-root coverage. The separate descendant root-animation diagnostic concerns stale inputs after root changes; this probe uses fresh frames for each underlying root style and does not depend on that invalidation mechanism.

## Calibrated, unrun diagnostic

`probe.js` creates eight cases: rem/rlh × root font-variation-settings/root font-size × underlying root23px/37px or31px/47px. Each case uses fresh standards documents, fixed horizontal axes, an explicit underlying line-height and no external resources. Sixteen observations retain first and fonts-ready/two-frame readings.

Before assigning author root fonts, each document measures initial rem and normal rlh using100-unit boxes. The initial font size and normal line-height are recorded, rather than hard-coding16px or a font-specific normal height. A separate reference document measures ordinary root `font-size:2rem` or `2rlh`, and also records ordinary root variation settings using the corresponding ratio. That variation reading is observational, since it can share the known ordinary variation defect.

On the animated root, an independent literal20→40 animation must produce30. An additional root `font-size:1em→3em` animation must produce twice the measured initial font size; this checks inherited font-base conversion separately from rem root identity. Both effects are cancelled and the configured underlying font size/line-height are verified before constructing the actual relative animation. Its first target-property getter precedes timing/keyframe getters. Root target identity, paused midpoint, parser admission, serialization and cleanup are checked.

The ordinary root font-size comparator must agree with the measured initial reference before a row is classified. A mismatch remains an explicit calibration failure, not an invented variation result. First/settled differences are preserved rather than rejected, since self-feedback may itself be relevant. Classifications say initial-reference, underlying-root, both or other; they do not identify a native cause. Variation alone cannot distinguish its current-font-base error from the missing root identity. The font-size case plus the em control is the intended discriminator.

The current Values4 font-relative exception rebases font-affecting properties on the root to initial font/line-height metrics. The preserved axis review includes the exact primary text, and the animation source review separately traces live computed-keyframe evaluation. Here axes are fixed and root line-height is explicit, while the initial normal-lh reference is measured. This does not resolve the separate parent-axis/normal-lh policy question or claim arbitrary font metrics are interchangeable.

## Validation and next step

Actual545a6d/0 passed four synthetic classification/timing paths, one uncalibrated-comparator path,12 rejecting controls and JavaScript syntax. No browser, native build, live source, app, index or canonical state was changed. The checker does not validate native font selection or the source cause.

Root can run this diagnostic on a retained original archive and preserve the complete returned object. If the font-size/em control passes but root rem/rlh follows the underlying root instead of the initial reference, trace the target/pseudo identity handoff for the narrow correction. Do not change the sealed variation candidate or globally set every derived builder to root merely from this source lead.
