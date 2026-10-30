# Contextual duration: scoped animation-only update experiment

This is an uncompiled, one-file scheduling proposal. It is not an accepted fix or a proof of general feedback-loop safety. Native files, application, index and canonical state were not changed.

The captured current matching.rs includes accepted 129. Its Gecko process_animations returns during an animation-only traversal with an old style, before needs_animations_update can compare computed animation lists. The normal branch already couples CSS_ANIMATIONS with EFFECT_PROPERTIES; this proposal preserves that branch exactly. The new branch compares old/new get_ui().animations_equals, queues those same two tasks only on inequality, then returns. It does not enter transition, timeline, display-change or blanket has_animations handling. Initial styling with no old values is unchanged.

Root reported the current-app duration observation while its owner was still finishing: normal inherited font mutation and updateTiming override passed; animated inherited font changed computed duration from 1s to 1.5s while effect duration remained 1000ms and opacity .75. This package does not certify that run's terminal or restoration; those belong to the root runtime receipts. The source explains why an unrelated later normal restyle need not repair it: the stored computed animation list already contains the new duration, so normal old/new equality can conceal the stale effect.

## Normative and fixture review

CSS Animations 2 explicitly connects changes to animation properties to updates of their CSSAnimation and associated objects, with per-property updateTiming overrides. The duration observer therefore has a direct ordinary-property bridge, unlike the separate unresolved keyframe-local easing metadata question. CSS Animations 1 says changes to animation properties apply to an existing animation as though present from its beginning. The computed duration and paused 750ms time yield .75 at 1000ms and .5 at 1500ms; updateTiming({duration:1250}) retains .6. No claim requires restarting the animation.

- https://drafts.csswg.org/css-animations-2/#animations
- https://drafts.csswg.org/css-animations-1/#animations
- https://drafts.csswg.org/css-values-4/#font-relative-lengths

Both sealed duration and ordinary-easing fixtures were independently read and their full manifests authenticated (fc2c5e/0). They collect all four input samples plus an unrelated-restyle sample before their result assertions. Font, computed property, animation/effect/rule/root identity, paused time, repeat reads and literal output controls are explicit. The duration fixture also checks effect timing and unchanged opacity frames. No fixture blocker found. Ordinary easing uses the resolved animation-timing-function property and setKeyframes precedence; its native parsing prerequisite remains separate from this duration experiment.

## Scheduling trace and limits

Searchfox function reads: Servo_TraverseSubtree (ff70b7/0) runs animation-only work before normal traversal; ServoStyleSet::StyleDocument (1c7571/0) permits a second traversal when EffectCompositor::PreTraverse reports pending animation work. AnimationEffect::SetSpecifiedTiming (9b9923/0) returns if timing is unchanged, otherwise normalizes timing, notifies the animation and requests a Layer restyle. Gecko_UpdateAnimations dispatches CSS animation updates before effect-property updates. UpdateOldAnimationPropertiesWithNew preserves existing animation identity and skips duration fields overridden by script.

- https://searchfox.org/firefox-main/source/servo/components/style/matching.rs
- https://searchfox.org/firefox-main/source/servo/ports/geckolib/glue.rs
- https://searchfox.org/firefox-main/source/layout/style/ServoStyleSet.cpp
- https://searchfox.org/firefox-main/source/layout/style/GeckoBindings.cpp
- https://searchfox.org/firefox-main/source/layout/style/nsAnimationManager.cpp
- https://searchfox.org/firefox-main/source/dom/animation/AnimationEffect.cpp

For the proposed parent-font/child-opacity experiment, the child's output does not affect its duration input; after the refresh the computed animation lists should become equal. This is a scoped source argument, not measured traversal convergence. EFFECT_PROPERTIES updates all effects on the selected element (Searchfox 708981/0), so this is not a CSS-effect-only refresh. The selection predicate covers all changed computed animation-list fields, not just duration.

A same-element font-size animation with duration derived from its own em can change its input again when retimed. The equality guard alone does not establish convergence, bounded flush work, or the correct self-dependency semantics. Do not remove the animation-only return globally or claim the three acyclic probes establish safety for these cases. Before acceptance, exercise self-dependent and mutually dependent timing/font cases with bounded runtime and repeated-read observations, existing restyle-count tests, and multiple unrelated effects on the selected element. If those expose repeated updates, the fix needs a deliberately chosen scheduling/dependency boundary, not an arbitrary retry cap.

Bug 1883255 remains broad animation/cascade integration prior art. Its fetched description/comments do not establish this exact duration failure as a duplicate: https://bugzilla.mozilla.org/show_bug.cgi?id=1883255 . No new bug ID or acceptance credit is assigned.

## Targeted regression selectors

First experiment: the exact three-callback duration fixture pinned in SOURCE.json. Preserve both originally passing controls and full ending/status evidence. Candidate failure is a valid experiment result; restoration remains mandatory.

Existing tests worth selecting before acceptance (not run here):

- testing/web-platform/tests/css/css-animations/AnimationEffect-updateTiming.tentative.html (including rejected updateTiming ownership)
- testing/web-platform/tests/css/css-animations/CSSAnimation-canceling.tentative.html (idle animation must not restart)
- testing/web-platform/tests/css/css-animations/animation-base-response-001.html
- testing/web-platform/tests/css/css-animations/animation-base-response-002.html
- testing/web-platform/tests/css/css-animations/animation-base-response-003.html
- testing/web-platform/tests/css/css-animations/animation-base-response-004.html
- testing/web-platform/tests/css/css-animations/parsing/animation-duration-computed.html
- testing/web-platform/tests/css/css-animations/animation-duration-infinite.html
- dom/animation/test/mozilla/test_restyles.html and its file_restyles.html support fixture

Searchfox duration/typed-calc searches (e04979/0,333791/0,0fee91/0,6098c0/0) found these adjacent tests, not an exhaustive absence proof. Existing accepted-129 reactivation coverage must also remain in the root's regression selection. No new formal model is needed to assert a three-sample arithmetic identity; the unresolved obligation is real scheduling and dependency behavior.
