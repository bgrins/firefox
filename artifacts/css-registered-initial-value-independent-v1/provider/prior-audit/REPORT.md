# CSS-wide keyframe maps and fallback representation

## Disposition

Two mechanisms must remain separate. A skipped CSS-wide declaration leaving the seeded map unchanged is not by itself a specified-value violation: dependencies in keyframes use the target's computed values, not a simultaneous cascade of the declarations at that endpoint. A discriminating dependency probe is justified, but its likely repair is broader than replacing skipped map entries. The fallback-to-`initial` Universal wrapper is a narrower, independently justified representation lead. Neither new proposal has been run in a browser by this audit.

This is source/spec research, not formal-verifier discovery or a proof of native behavior. Existing endpoint repair evidence and all original full-proof boundaries remain unchanged.

## A. Same-effect dependencies

Scenario: register `--source` and `--sink` as non-inherited numbers, initial 10 and 0 respectively. The target's nonanimated source is 42. One replace-composition, linear animation specifies source from `initial` to 90, sink from `var(--source)` to `calc(2 * var(--source))`. Sample at half duration.

1. [Web Animations computing property values](https://drafts.csswg.org/web-animations-1/#computing-property-values) resolves a keyframe value using the element's computed dependency values. Its normative algorithm does not install the other endpoint declarations as a replacement element style. The adjacent example resolves width against the animated font-size at the current time.
2. [Calculating computed keyframes](https://drafts.csswg.org/web-animations-1/#calculating-computed-keyframes) performs that operation for each property. [Effect-value calculation](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-effect) then interpolates those computed endpoints.
3. [Properties and Values API substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) requires a registered reference to supply its computed value. Its animation behavior uses the registered numeric type.
4. Source at the midpoint is `(10 + 90)/2 = 50`. Therefore sink endpoints at that same sample are 50 and 100; the sink value is 75. With author-important `--source:42`, source remains 42 and sink must instead be 63.

Verdict: **REACHED** for these expected dependency observations under the stated simple acyclic scenario. This is not a claim that every CSS-wide map skip is erroneous. In particular, with important source 42 and constant `initial` source keyframes, retaining the actual computed 42 can be correct; overwriting it with 10 would be wrong for a dependent value.

The current source constructs `KeyframeCustomPropertiesBuilder` from `style.custom_properties()`, then cascades endpoint custom declarations into that map. `value_may_affect_style` skips non-inherited initial, inherited inherit and any unset because ordinary cascade initialization would already contain their default values. Other endpoint literals can overwrite the map. It consequently mixes a base style dependency with endpoint-local replacements. At source level, a map initially containing42 can retain42 for the initial endpoint and contain90 for the other endpoint; sink endpoint conversion then produces42 and180, whose midpoint is111. This is an explanatory prediction, not a browser measurement: actual restyle/caller sequencing determines the style supplied to each invocation. Do not treat the map snapshot assumption as a proved scheduler premise.

Replacing the first endpoint's skipped initial with10 would produce sink endpoints10 and180, midpoint95. That would still disagree with75. Therefore a local CSS-wide defaulting patch is not the supported remedy for this dependency probe. Any repair must distinguish computing the animated source endpoint itself from resolving a dependent property against the source's current computed effect, account for dependency ordering/cycles, and preserve the important cascade. That belongs with the broader animation/cascade integration work.

### Existing evidence and history

The retained `registered-var-to-registered-animating.html` already requires a registered reference to observe another animation's current computed value. It has expected-FAIL metadata; this audit does not claim a fresh result. It exercises separate animations, while the proposal below separates same-effect endpoint-local and current-computed interpretations.

The [2016 CSSWG minutes](https://lists.w3.org/Archives/Public/www-style/2016Nov/0073.html) explicitly resolve var references in keyframes against the animated custom property on the element. [Issue 5125](https://github.com/w3c/csswg-drafts/issues/5125) lays out all three competing approaches: pre-animation style, endpoint-local cascade, and animated computed dependencies. The fetched issue page is closed and links5255, but its opening proposal is not a normative decision. Fetching PR5255/comments via the available web and direct network paths failed; those failures are retained. Current normative Web Animations text and the older explicit resolution support the proposal without asserting unobserved PR contents. The broad source FIXME points to bug1883255; this is not a novelty claim.

## B. Fallback-to-initial representation

Scenario: register non-inherited number `--n`, initial10; set target base42. Animate from14 to `var(--missing, initial)` with --missing absent, sample at50%.

1. The var replacement chooses fallback `initial`.
2. [CSS Values5 property substitution](https://drafts.csswg.org/css-values-5/#substitution-in-properties) says a result consisting of one CSS-wide keyword is interpreted as if that keyword had been specified originally. There is no unresolved revert question in this `initial` case.
3. The endpoint consequently computes as the registered initial number10, just like direct `initial` or literal10. Numeric midpoint must be12.

Verdict: **REACHED** for expected12 and equality with the direct-initial control. The test has no animated cross-property dependency, so it does not rely on resolving A's scheduling question.

Source path: `substitute_references_if_needed_and_apply` substitutes the fallback, parses the resulting CSS-wide keyword, calls `remove_and_insert_initial_value`, and returns. That helper removes the existing map entry then inserts `ComputedRegisteredValue::universal(Arc::clone(initial_value))`. It does not call `compute_value`. The typed-Unparsed endpoint conversion added by the separate root repair clones this map value. `CustomAnimatedValue::animate` cannot use numeric interpolation between the number14 and that Universal representation. The anticipated midpoint is a discrete endpoint, despite a later cascade being able to compute its serialized initial text correctly. Runtime remains unconfirmed.

Direct initial conversion uses the stylist's computed initial values and is an essential disconfirming control. Missing var without fallback follows `handle_invalid_at_computed_value_time`, which explicitly computes the non-inherited initial and is another useful control. A fallback of literal10 also goes through normal typed conversion. These distinguish the wrapper path from generic missing-variable handling and from the already repaired raw endpoint parsing.

The same helper is used in other defaulting paths. A possible repair should install the correct computed initial value at the provider boundary, or explicitly normalize its Universal initial representation before exposing a typed animation endpoint. Do not merely force interpolation on arbitrary Universal values: unregistered and universal registrations legitimately retain that representation. Preserve absence/guaranteed-invalid semantics, inherited versus non-inherited lookup, root handling and attr taint. This audit proposes no native hunk because the broader helper's callers and initial-value provider need a separate repair review.

## Minimal proposed inputs

`PROPOSED-INPUTS.md` contains exact small inputs and independently calculated expectations. It is a proposal, not an installed WPT. Root should record each observed source value as well as sink value and keep important-source controls separate. A failed source calibration invalidates the sink classification instead of silently supporting one model.

For A, prioritize literal versus initial source endpoints and the important override. For B, prioritize literal initial, direct initial, fallback initial, numeric fallback and missing-var-without-fallback. Avoid expanding to revert, dynamic registration, pseudo/shadow cases or cycles before these independent mechanisms are classified.

## Closure

Full current source files and relevant existing WPT/metadata are retained with exact pins. No native/test/browser/build/Git operation was performed. The checker authenticates the closed capsule and recomputes only the elementary independent arithmetic expectations; it is not a native interpreter, compiled witness, spec validator or universal proof. Sources can subsequently change without changing this sealed historical evidence.
