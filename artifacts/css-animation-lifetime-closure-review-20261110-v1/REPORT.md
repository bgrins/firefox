# Animation drain: lifetime closure review

## Result

The observed initial-style admission does not establish recurring same-target renewal. Its four initial admissions and later task masks 5/4 fit the finite font-chain experiment. A separate, source-backed escape from the strictly descending producer relation exists in named-timeline management: initializing a descendant timeline can synchronously rebind and request animation work on an ancestor or sibling. This is a concrete next coverage target, not a demonstrated infinite loop or new browser defect.

No browser/build/IPC, production edits, tests or Git mutations were performed. Searchfox discovery preceded exact source reads; initial sandbox DNS failures and successful network retries are retained. Searchfox and local source differ in some implementations, so the conclusions use the local immutable revision `bc8b09c8d72292354b4adbe0cbf91a9f0f110a1d` and the held repair's semantic capsule, not Searchfox line positions. `SOURCES.json`, `HELD-SOURCES.json`, and `EXCERPTS.json` identify the exact bytes.

## Narrow lifetime exclusion

`recalc_style_at` computes the target's new style, then calls `clear_descendant_data` for display:none. That helper clears data only on traversal children and their descendants; the target retains its primary style. The hidden root also suppresses child traversal. Therefore this operation alone cannot turn the same hiding target into an initially unstyled target on its next application. Reinitializing a cleared node requires a strict ancestor's later reveal. Conditionally, with a stable finite traversal tree and a finite number of ancestor hide/reveal changes, each descendant has only finitely many such recreated lifetimes. This is not a proof that all native ancestor changes are finite.

The display-animation preference is insufficient to exclude this path. `KeyframeUtils::IsAnimatableProperty` rejects the direct display property while disabled. Custom properties remain animatable (`PropertyId::is_animatable`), and `VariableDeclaration::substitute_variables` can feed ordinary display declarations. Thus an animated custom property used by `display:var(--d)` is outside that direct-property filter. No animation-taint or keyframe-display restriction was assumed to prohibit it.

Custom-property changes can also emit child hints for style queries in `accumulate_damage_for`. Ordinary `traverse_container` begins at the parent; its explicit originating-element-style case permits evaluation at the supplied element for pseudo styling. The ordinary element case supplies a downward cause, but a proof must distinguish originating element and pseudo identities. It cannot silently count every query as a strict DOM ancestor relation.

`process_animations` returns on animation-only traversal when the old primary style exists. Initial styling is the exception. Ordinary management after a descendant handoff can still update animations on that descendant. The source exclusion here concerns repeated initial admission of the same hiding target; it does not exclude all normal management, every producer, or pseudo/frame recreation outside the inspected traversal path.

## What the measured masks cover

`ServoTypes.h` defines CSSAnimations=1, EffectProperties=4, ScrollTimelines=32, ViewTimelines=64 and TimelineScopes=128. The inherited analyzer records ten tasks in each animated callback, exclusively masks 5 and 4, with four initial animation-only tasks in the SMIL callback. The literal callback records no tasks. This excludes the named-timeline task branches for those recorded targets/events; it does not assert that every event in the document was traced.

The held `StyleDocument` calls full `ServoStyleSet::PreTraverse` once, then repeats `EffectCompositor::PreTraverse` and subtree traversal. Full PreTraverse includes SMIL posting; the repeated drain does not call that SMIL hook or sample SMIL. The one paused seek therefore supplies initial stimulus. No SMIL clock advance or repeated SMIL sampling inside this inspected loop is established.

## Named-timeline producer: exact request gates

The following source chain can cross tree rank:

1. `matching.rs::process_animations` can create TimelineScopes, ScrollTimelines or ViewTimelines tasks during initial styling, including the animation-only initial exception.
2. `Gecko_UpdateAnimations` processes timeline definitions before CSS animation/effect work. TimelineScopes calls `UpdateTimelineScopes` then `UpdateAllNamedTimelineAnimations`; ScrollTimelines/ViewTimelines call `UpdateTimelines` then `UpdateNamedTimelineAnimations(affectedNames)`.
3. `nsAnimationManager` iterates the document's animation map, not the defining target's descendants. `UpdateNamedTimelineAnimation` resolves the affected CSS animation's own target/name. Equal old/new timeline returns. Missing or `UnresolvedTimeline` results are deferred; a different concrete timeline goes immediately to `SetTimelineNoUpdate`.
4. `Animation::SetTimelineNoUpdate` can return for a JS timeline override or identical pointer. Otherwise it ends with `UpdateTiming(NoSeek, Async)`, which calls `UpdateEffect(IfNeeded)` and `KeyframeEffect::NotifyAnimationTimingUpdated`.
5. A restyle request requires an animation, nonempty properties and `HasComputedTimingChanged()`. Its type is Standard or Throttled according to `CanThrottle`. `KeyframeEffect::RequestRestyle` uses the affected animation target/pseudo and its cascade level. These are CSS animations, at the Animations level, not normal-restyle or transition hints.
6. `EffectCompositor::RequestRestyle` inserts that target in the corresponding queue; non-throttled requests set the eligible bit. A later PreTraverse of this same StyleDocument call can consume it. Throttled-only entries need the existing flush conditions and are not automatically evidence of another drain iteration.

Thus a global update call alone is not request injection. The candidate causal edge is **N(provider) → A(outside target)**, including an ancestor target. A subsequent normal descendant handoff may then revisit the provider. No recurrence has been shown.

A concrete ScrollTimeline/ViewTimeline with unresolved current time is distinct from the `UnresolvedTimeline` sentinel class: only the latter is tested by the named-update deferral branch. New concrete definitions can therefore rebind immediately even before frame creation, though a timing change and an eligible request still need measurement. Conversely, removing the last matching definition can take the deferred branch, which is processed by `UpdateDeferredTimelineChanges`; the Searchfox call-site discovery identifies the viewport/resize-observer phase in Document, not this repeated drain.

The traced path calls timing/effect updates synchronously and contains no direct recursive StyleDocument invocation. That establishes potential same-call queue injection, not a universal no-reentrancy theorem over every callee, promise/event path or embedding hook.

## Next discriminator

See `NEXT-PROBE.md`. The scroll variant tests the non-descendant edge with one existing outside animation and one newly admitted provider. Scope-only and missing-name controls distinguish a global visit, immediate rebind and deferred removal. A separate view variant exercises its distinct task bit. No fixture has been implemented or run.

The current proof remains conditional on causal closure. The new source edge shows why tree descent alone cannot be generalized across timeline management. Keep the present finite font-only trace accepted at its actual scope; first measure this edge before introducing a broader ranking model.
