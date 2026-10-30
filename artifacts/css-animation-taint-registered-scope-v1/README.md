# Registered-property scope audit

The unregistered-only producer gate is an experimental scope boundary, not an established normative exemption. The original proposal targeted the observed active unregistered gap and left registered/default/inheritance policy uncertified. Its 94 adjacent preservation cases are regression coverage; passing them cannot establish that a registered animation source should be untainted.

The frozen corrected proposal marks only when `std::ptr::eq(registration, PropertyDescriptors::unregistered())` and the winning cascade origin is Animations. The saved getter returns that singleton only if both registries miss. A registered universal `*` descriptor is a separate registration, even though its syntax is universal; typed `<custom-ident>` is also excluded. This identity test replaced the incorrect draft `syntax.is_none()` test. Identifying the engineering subset correctly did not justify its policy. Other paths may transport existing provenance through registered conversions, so exclusion of this producer does not prove every registered value is untainted. Animations origin includes script-generated effects; this diagnostic uses CSS keyframes only.

## Primary reading and limits

Variables 1 describes “any custom property” used in keyframes as animation-tainted. Its var replacement step 3 has no registration predicate; step 4 selects fallback. [Producer](https://drafts.csswg.org/css-variables-1/#animation-tainted), [replacement](https://drafts.csswg.org/css-variables-1/#replace-a-var-function).

Properties and Values API §2 retains similar behavior except for its specified changes. Sections 2.4–2.7 address computed-value typing, interpolation and serialized substitution. Universal syntax retains unregistered computed-value behavior; valid custom identifiers keep their keyword. None supplies an express taint exemption. The inference is that registration alone does not justify exclusion, not a proof from failed text search. [Registration and subsections](https://drafts.css-houdini.org/css-properties-values-api-1/#registered-custom-properties).

**Verdict: INCONCLUSIVE for an exemption/full native policy; no exemption established in the deciding sections.** The broad producer and guard wording supports testing registered inputs; sink expectations remain tentative pending matched observations and any contrary rule. Indexed query failed with the retained read-only-database error: no exhaustive graph or machine-validated anchor claim. PRIMARY.json records manual official-draft reads.

Registration selects inheritance and initial value; unregistered values inherit. That changes which value reaches a child, not automatically its taint policy. Cross-element propagation, registered invalid/default behavior, universal inherits=true, registered aliases, WAAPI and name-global keyframe taint remain outside this same-element valid-keyword diagnostic.

## Four matched modes

The single tentative WPT page has unregistered, registered `*`, registered `<custom-ident>` and literal callbacks, each in a fresh iframe. All use a CSS animation holding --scope-v:vertical-rl at750ms of2s. The noninitial var fallback is vertical-lr; parent writing-mode is horizontal-tb. Underlying input changes horizontal-tb→vertical-lr while active keyword remains fixed. The literal vertical-lr sink retains the same driver.

Registered modes call CSS.registerProperty successfully with inherits=false and initial horizontal-tb. Separate non-animated calibration elements check actual behavior: a child of a variable parent vertical-lr starts horizontal-tb for registered modes; a two-identifier declaration remains `one two` for universal/unregistered but computes to horizontal-tb for typed syntax. This catches silently ignored universal registration. Both registrations share inheritance configuration; inherited-animation provenance is not tested.

Each phase reads sink first, then three passive-frame readings, then source/timing/identity details. Complete records are published to window.registeredTaintObservations and the page pre before calibration/lifecycle/sink assertions. Setup errors may leave partial objects. Raw output does not prove internal branch choice. WPT PASS alone does not archive this object; failure messages include it, and an external observer must explicitly collect PASS trajectories.

Static validation uses genuine explicit-path subset manifest, exact harness resources, inert callback registration and path/content lint, with Git subprocess discovery denied. No browser/native execution or source/index/profile/control mutation occurred. Existing proposals and106 roster remain unchanged. A separate minimal installed-browser wrapper may collect the same page object without changing its sampling.
