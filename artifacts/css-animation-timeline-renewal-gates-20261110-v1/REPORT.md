# Timeline renewal gates and animation-taint calibration

The direct animated-variable route is forbidden by the current Variables Level 1 substitution algorithm, but the inspected local implementation does not expose the required animation-taint gate. The artifact fixture tests that hypothesis first. No browser result, confirmed defect, recurrence proof, fix, or security claim is supplied by this capsule.

## Specification gate and history

The [current Variables Level 1 replacement algorithm](https://drafts.csswg.org/css-variables-1/#replace-a-var-function) makes an animation-tainted custom property unavailable when substituted into a nonanimatable property, then applies a supplied fallback. Unregistered `--name` therefore gives `--fallback` in this fixture's timeline declarations, even while the custom property's computed value remains `--live`.

This is not a newly introduced Level 2 requirement. The [December 2015 Level 1 CR](https://www.w3.org/TR/2015/CR-css-variables-1-20151203/#using-variables) limited the gate to animation properties. The [November 2021 Level 1 CRD](https://www.w3.org/TR/2021/CRD-css-variables-1-20211111/#using-variables) and [June 2022 Level 1 CR](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#using-variables) already broaden it to nonanimatable properties and retain fallback substitution. These dated snapshots bound the change; this audit does not establish the exact CSSWG change date. `SPEC-SNAPSHOTS.json` authenticates downloaded primary HTML. The dated webspec-index calls failed and their receipts are retained; direct primary snapshots supplied the historical comparison.

## Local source gate

`SOURCES.json` pins complete files at local revision `4cda7885b649deba826da5566940cb32833c9f14`; `EXCERPTS.json` provides exact named-path excerpts with line coordinates and hashes. Searchfox was discovery only: its newer indexed implementation is not substituted for these local bytes.

* `properties/longhands.toml` marks both `scroll-timeline-name` and `timeline-scope` with `animation_type = "none"` and the scroll-driven-animation preference. `get_animated_properties` filters nonanimatable declarations when collecting animated properties. Custom property IDs are animatable, so that filter does not establish the required indirect `var()` gate.
* `properties_and_values/value.rs` stores value, URL data, and attribute-taint in `Value<Component>`; conversion and interpolation preserve/combine attribute-taint. `custom_properties_map.rs` stores these values, including parent lookup and deduplication. Its separate taint equality check is also attribute-taint. `VariableValue` is only one part of this inspection, not the basis of a repository-wide absence claim.
* `cascade_custom_property` uses cascade priority for inclusion, seen/revert handling and custom value selection. Its inspected unparsed/parsed/inherited branches insert computed values without recording animation provenance. `substitute_one_reference` obtains a variable from the computed substitution map and recursively resolves it or serializes its value. The inspected Var branch neither checks animation provenance nor tests destination animatability.
* `VariableDeclaration::substitute_variables` receives destination metadata, invokes this substitution path, then reparses the ordinary destination property. Its invalid-property and parse-failure gates are present; neither is an observed implementation of the animation-taint rule. `substitute_variables_if_needed` also has no observed such gate.

This makes missing animation-taint handling a concrete source hypothesis. The browser calibration remains necessary: an uninspected producer or earlier filtering path could defeat the prediction. Attribute-taint is a separate mechanism and is not evidence that animation-taint works or fails.

## Separate registry hypothesis

The parent reports that the preceding named-timeline native experiment observed initial provider management (task bit 32) request animation work on an outside ancestor during call 13, iteration 1; the subsequent provider recascade had an old style and emitted no second timeline task. This audit does not independently reclassify or generalize that runtime.

The pinned `process_animations` returns early for animation-only traversal when the element has an old primary style. `finish_restyle` then installs the newly computed style with `data.set_styles(new_styles)`. Normal timeline-management tasks are subsequently selected by comparing the old installed timeline values against the next new values. `Gecko_UpdateAnimations` only calls timeline managers for their corresponding task bits; an effect-properties task alone does not rebuild the registry.

Consequently, if animation-only recascade can change a provider's computed timeline name from `--t` to `--off`, it can install `--off` without running timeline management. A later normal recascade computing `--off` again would see equality and would not recover the lost timeline delta merely by revisiting that element. A local font animation can make the element eligible for a later normal font-related recascade; that eligibility alone does not force a timeline task. These are conditional source deductions, not a reproduced stale registry or infinite drain.

The proposed inherited-variable feedback would require all of the following observations: an outside animation actually supplies the name; rebinding makes that animation's value disappear; the provider receives animation-only recascade; its computed name changes while timeline management is skipped; and a later normal visit fails to repair the registry. The current taint rule blocks this route in a conforming implementation. Do not implement the feedback experiment until the small calibration is measured.

A style query selecting a literal timeline declaration is a distinct possible route that does not substitute the tainted value into that declaration. `restyle_kind_for_animation` does not perform selector matching; custom-property changes can produce style-query hints for a later normal traversal. That route therefore needs its own matching/handoff evidence. It is not established by the direct-variable source analysis, and it is outside this fixture.

## Calibration and decision

`animation-tainted-timeline-calibration.html` is prepared for temporary WPT path `css/css-variables/animation-tainted-timeline-calibration.html`. Four callbacks test direct scroll-name substitution, direct scope substitution, a separate never-animated variable, and inherited taint with an `animation-name` control. Constant keyframes, negative delay, paused playback and fill-both establish an active `--live` value distinct from the underlying `--base`; the source's computed progress must be 0.5. The child control has a fixed parent animation name, avoiding self-selection of the source animation.

Use explicit `layout.css.scroll-driven-animations.enabled=true` and `layout.css.display-animations.enabled=false`. The former enables the tested timeline properties; the latter does not resolve or suppress the custom-property question. This is an artifact-only preparation, with no live test installation or browser run by this agent.

`check_wpt.py check2` passed with actual exit 0: JavaScript syntax, four inertly registered callback names, real WPT lint and a one-page WPT manifest. `check1` is retained preparation history under the earlier filename; `check2` is authoritative. These checks do not execute test assertions.

If all taint assertions pass, stop the direct-variable route. If the active-value and ordinary-variable controls pass but nonanimatable destinations receive `--live`, retain the result as a separate Variables conformance candidate before investigating registry consequences. An inherited `animation-name` failure would additionally implicate the older, narrower restriction. No outcome alone proves a recurring backedge or universal traversal bound.
