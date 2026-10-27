# Publishing active keyframe attribute dependencies

Proposed minimum: transport one conservative “queried an attribute” bit from the completed Rust keyframe computation to its owning KeyframeEffect, publish it when that computation replaces the property cache, and query the OR across currently registered effects at mutation time. Request normal semantic work for dependent targets. Do not change the attribute initial-value implementation, taint policy, custom-property interpolation architecture, or dormant replay behavior in this patch.

This is a design, not an implemented repair or browser result. SOURCE-BINDINGS separates exact installed-130 archive joins from historical supplements that still need current guards. The installed capsule records 24 landing passes and 27 installed test identities. It does not supply a mutation result. No native or index files were read or modified here; the supplementary files were read from historical Git objects.

## Transfer and publication

1. Installed `Servo_GetComputedKeyframeValues` owns one real AttributeTracker across all keyframes. Ordinary and custom-property preparation and value substitution use it. `query` allocates a reference entry before lookup, so absent, invalid and fallback-producing reads are included. Return `attribute_tracker.references.is_some()` after the complete loop (or an equivalent consumed-tracker test). Do not infer sensitivity from numeric results, taint, parser tokens, or only the last endpoint.
2. Carry a local boolean through `ServoStyleSet::GetComputedKeyframeValuesFor`, the internal KeyframeUtils computation helper, `GetAnimationPropertiesFromKeyframes`, and `KeyframeEffect::BuildProperties`. Initialize outputs on all early exits, including missing PresContext/target and empty computed arrays. The generated FFI signature must be rebuilt; this is not yet a compiled interface.
3. Prefer an explicit output/result associated with the returned properties. In `UpdateProperties`, publish the new per-effect bit for the accepted computation before any unchanged-properties return. Existing attr-taint comparison and base-style work remain intact. The bit can change false→true when an equal-valued literal is replaced with attr(), or true→false when an equal-valued attr expression is replaced by a literal.
4. Do not mutate the published bit unconditionally inside `BuildProperties`: `UpdateBaseStyle` also calls that function without replacing `mProperties`. Its temporary result must not clear the dependency metadata associated with a retained cache. A base-only call can discard the dependency output; a more conservative union would require explicit lifetime semantics. Keep publication local to the property-cache update.

A boolean deliberately overapproximates names and namespaces: any attribute change can affect an attribute-sensitive effect. This avoids Rust-owned name transport, refcount/FFI ownership, and namespace filtering in the first patch. The watch model's exact-name aggregate refines to this conservative target predicate, but that abstraction relation has not been formalized against C++.

## Aggregate and lifecycle

Compute the aggregate by scanning existing EffectSet members and asking each effect's bit. Avoid a cached aggregate in the initial patch. Then an equal-value update immediately changes the observed aggregate; AddEffect/RemoveEffect naturally include/exclude exactly that effect; cancelling one effect cannot erase another's dependency; and destruction of an empty set needs no separate watch bookkeeping. No new raw target pointers or cross-language allocated watch lists are necessary.

| Path | Required treatment |
|---|---|
| Normal property rebuild, including equal values | Replace the bit with the completed computation before the unchanged-values return. |
| Copy constructor | Copy the bit with cloned `mProperties` and keyframes. Defaulting false would lose the copied cache's dependency. |
| Changed `setKeyframes` with available style | Existing path calls UpdateProperties; publish its new bit, even if numerical endpoints are equal. |
| Identical specified keyframes early return | Retain the prior bit. It is not a justification for refreshing a stale retained cache. |
| Changed keyframes with no style | Do not clear old metadata and call the work finished. Either retain/mark conservative unknown sensitivity until a successful build, or prove the future attach/style path rebuilds before observation. This path remains an implementation gate. |
| Cancellation/removal | Existing registration removal changes the live-set OR; retain the bit on the effect object alongside its cached properties. |
| Retarget / pseudo-element change | Existing UpdateTarget removes old membership, installs the new target, registers, then obtains style and rebuilds. Retaining the bit temporarily is conservative. Missing-style paths need the same explicit deferred-build obligation. |
| Re-register retained dormant object | The bit helps admit future mutations but does not repair mutations that happened while absent. Keep the separately measured dormant freshness gap explicit; do not add recursive recomputation or restyle posting inside registration. |
| UpdateBaseStyle | Do not replace the cached-property dependency bit from a computation whose properties are not committed. |

Registration occurs in more than one call context. This proposal adds no normal-restyle request there. Existing BuildProperties copied-keyframe/reentrancy assertions remain; a result must not be published for a different generation if a future implementation adds reentrant mutation. No proof of that native generation property is supplied.

## Pseudo-element coverage is a design gate

Effects use `(originating element, PseudoStyleRequest)` keys; querying `EffectSet::Get(concretePseudo, NotPseudo)` is insufficient. Archived AnimationUtils implementation maps before/after/marker/backdrop/checkmark/picker-icon nodes to their origin and maps named view-transition nodes to the document root plus named request. Its header's view-transition storage comment is inconsistent with that implementation; use the implementation, not the comment, and authenticate its current body before coding.

The installed `MaybeRecascadeForAttrFunction` visits `ForEachElementAndPseudo`, whose own comment says coverage is limited (bug 2037724). That iterator is useful for ordinary/generated/UA widget attr dependencies but is not evidence of all animation targets, especially named view-transition sets. The installed `ServoStyleSet` additionally carries the existing bug 1922095 FIXME: it sends the originating element to keyframe computation for view-transition pseudos. This proposal must preserve the current queried-owner relationship, without claiming to fix that separate owner selection.

Preferred complete discovery option: expose a read-only iteration over existing ElementAnimationData's ordinary and keyed pseudo EffectSets. For the mutated attribute owner, query every stored set's live-member OR and collect dependent target keys. Continue the existing generated/UA-widget traversal for concretely separate storage owners. Deduplicate if needed. Do not allocate EffectSets during this query. Resolve each target key to the concrete restyle element using the existing pseudo mapping conventions, then post normal work. Iteration must not invoke a flush, script, or mutate the set/hash table; post only after collecting stable targets if required.

Historical ElementAnimationData has the needed ordinary slot plus private keyed map but no public iterator. Adding such an iterator costs a small helper/API beyond the eight-file scalar transfer path. Before implementing it, bind its header/source and prove the concrete-target resolver covers named view-transition requests and UA widget storage. An absent pseudo node cannot simply be reported as refreshed: generation/attach must rebuild its properties before observation. Before/after/marker are mandatory test coverage; backdrop/checkmark/picker-icon and view-transition cases need supported-feature/generation calibrations. Unsupported highlight effects are not silently promoted to supported animations.

A smaller `ForEachElementAndPseudo` + GetElementPseudoPair implementation can be a scoped experiment, but cannot be presented as complete pseudo-element coverage. Do not accept a universally phrased fix on ordinary-element evidence alone.

## Delivery

At `AttributeWillChange`, use `PostRestyleEvent` with `RESTYLE_SELF` for effect-sensitive targets; retain the existing ordinary-style branch's behavior. The call site is already outside traversal, and PostRestyleEvent asserts that constraint, sets non-animation restyle bookkeeping, and invalidates cached style. Do not call UpdateProperties directly here or use the animation-only posting API.

A broadening of `RECASCADE_SELF` is insufficient: installed restyle-hint cleanup explicitly consumes that bit during animation-only traversal, while installed `process_animations` returns early in that traversal for styled targets. RESTYLE_SELF remains a normal obligation. In normal traversal, process_animations queues EFFECT_PROPERTIES for relevant animations (and installed fix129 also when CSS_ANIMATIONS updates); Gecko_UpdateAnimations maps the concrete target/pseudo pair, updates CSS animations first, then calls EffectCompositor::UpdateEffectProperties, which rebuilds each registered effect. Null style and disconnected/non-dynamic contexts have explicit early returns and remain lifecycle gates.

This identifies the scheduling route; it is not a same-flush liveness proof. Test cancel-plus-attribute-mutation without an intervening flush, unrelated pending animation restyles, and pseudo targets. Publication alone cannot discharge delivery, and passing ordinary effects does not establish pseudo routing.

## Required validation before accepting a repair

Preserve the exact twelve-case retained/fresh/ordinary diagnostic and its calibration rules. Add focused histories for initially absent→added attr, equal-valued literal→attr and attr-A→attr-B keyframe replacement, copied effects, two effects sharing the target with one cancellation, retarget to a different owner, and keyframe replacement while detached/unstyled followed by attachment. Include namespace changes and remove/readd, without using unrelated ordinary attr styling on the animated target to mask missing watches.

Add supported CSS and WAAPI pseudo histories with explicit generation, initial value, fixed time, and independent ordinary/literal controls; at minimum before/after/marker. Enumerate supported remaining stored pseudo kinds rather than assuming the generated-content iterator covers them. Keep dormant cancel/replay and the known custom-property context witnesses as separate held behaviors, not invented obligations that this publication patch automatically repairs. A source or unit-level check must ensure UpdateBaseStyle cannot overwrite committed dependency state; a browser trigger for that distinct branch is not yet established.

The next action is root design review plus the pending diagnostic result, then binding supplemental sources and an artifact-only candidate. No implementation, new acceptance, or canonical theorem credit is included here.
