# Inactive but specified CSS animation: animated-input probe

This isolated one-callback probe targets the eligibility distinction in guarded duration proposal V2. It is separate from the sealed twelve-page broader suite and has not run in a browser. No native, application, Git/index or canonical state changed.

The parent has a paused WAAPI font-size animation sampled at 16→48→16→48px. Its child retains animation-name:retained, linear opacity keyframes0→1, fill:none, paused currentTime750ms and animation-duration:calc(1em / 32px * 1s). The dimension ratio is a number; multiplication by1s produces a duration. This is the same typed-arithmetic grammar as the already exercised1em/16px duration probe with a different positive divisor. This new fixture checks declaration retention and CSS.supports itself; no new browser parse result is claimed here.

At16px the computed duration is500ms. At paused750ms the effect is after its active interval with fill:none: progress is null, target.getAnimations() omits it, and the underlying opacity0.2 applies. The fixture acquires the CSSAnimation before setting750ms and keeps that handle. At48px the duration becomes1500ms, so the same local time is halfway through the active interval: progress0.5, opacity0.5 and the same CSSAnimation returns to the relevant list. Returning to16px and then48px checks both directions again. The driver alone changes time; there is no child style/rule mutation during these four samples.

Literal paused WAAPI reference effects independently calibrate the inactive500ms/opacity0.2 and active1500ms/opacity0.5 outputs. The four observations are collected before expected-result assertions. They retain computed CSS duration/name/fill, effect duration/progress/local time, animation time/state/startTime/pending, relevant membership, effect/target/root/rule identities and exact opacity keyframes. The callback does not reacquire a replacement CSS animation when the original is absent from getAnimations().

The normative bridge is ordinary animation-property updating, not keyframe-local contextual easing. CSS Animations2 requires animation-property changes to update the CSSAnimation and associated objects, subject to script overrides. This probe never calls updateTiming or replaces keyframes/effect. CSS Animations1 specifies live property updates with preserved playback time and fill:none's absence of contribution outside execution. Web Animations distinguishes relevance from the continuing animation object and applies effect values according to phase and fill. The expected inactive/active outputs follow that combination; no restart or newly created animation is allowed by the intended oracle.

- https://drafts.csswg.org/css-animations-2/#animations
- https://drafts.csswg.org/css-animations-1/#animations
- https://drafts.csswg.org/css-animations-1/#animation-fill-mode
- https://drafts.csswg.org/web-animations-1/#relevant-animations
- https://drafts.csswg.org/web-animations-1/#fill-behavior

Source review of the sealed V2 candidate (decaee/0) confirms its eligibility is specifies_animations() OR has_css_animations(...), followed by computed-list inequality. Consequently this still-specified animation is eligible even while no relevant effect is returned by getAnimations(). Replacing that predicate with relevant-effect membership would risk dropping the reactivation update. A passing browser result will test this observable consequence, not prove the exact native predicate used without instrumentation.

Accepted fix129's unchanged six-case landing test covers reactivation after a normal CSS duration mutation, including recomputation of contextual keyframe values. This new case holds plain opacity keyframes fixed and changes duration through animated inherited font while the retained animation is irrelevant. It is not a new accepted fix, an ownership model theorem or a duplicate of the original active-duration probe. It does not cover pseudo elements, cancellation, feedback cycles or timing override acquisition.

Static check454f9e/0 passed: one exact name registered without invoking its callback, genuine WPT manifest registration, exact two support resources and zero WPT lint errors. The scratch-directory Git-detection diagnostic is retained; no Git repository or index was created. Actual original/candidate observation remains required before any repair or regression claim. The broader suite was not edited.
