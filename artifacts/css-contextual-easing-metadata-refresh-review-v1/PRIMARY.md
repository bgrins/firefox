Primary sources:

- https://drafts.csswg.org/css-animations-1/#animations — existing animations reflect animation-property changes.
- https://drafts.csswg.org/css-animations-2/#animations — object updates and successful setKeyframes/updateTiming ownership. The former explicitly mentions “the resolved value of the animation-timing-function property for the target element”.
- https://drafts.csswg.org/css-animations-2/#keyframe-processing — step1 takes computed ordinary timing as default; step2.2 acquires keyframe-local computed metadata.
- https://drafts.csswg.org/css-animations-2/#animation-duration — effect iteration-duration correspondence.
- https://drafts.csswg.org/css-animations-2/#pending-style-changes — observations must reflect processed pending computed changes; not a definition of every dependency.
- https://github.com/w3c/csswg-drafts/issues/5125 — competing keyframe property dependency contexts; historical examples are not current browser measurements.
- https://github.com/w3c/csswg-drafts/issues/14246 — open proposal for element-independent script timing parsing; not a CSS metadata resolution.
- https://searchfox.org/mozilla-central/source/servo/components/style/matching.rs — current public retrieval in SOURCE-READ.json, selected excerpts retained.
- https://chromium.googlesource.com/chromium/src/+/refs/heads/main/third_party/blink/renderer/core/animation/css/css_animations.cc — current decoded-source hash in BLINK-SOURCE.json, selected excerpts retained.

Trace A: ancestor font effect → observed inherited font change → unchanged keyframe-local descriptor's context changes → [missing explicit metadata-refresh scheduling step] → keyframe processing → effect output. INCONCLUSIVE: a gap in the argument, not permission or graph-proven unreachability.

Trace B: ancestor font effect → observed changed ordinary computed animation property → Animations2 §2 update unless matching successful script override → computed default easing/duration correspondence → existing effect timing/output. Conditional update obligation REACHED once computed-property change and acquisition are established. Implementation scheduling and browser results remain separate.

Precise question for later clarification: must a CSS keyframe block's computed easing be regenerated after its inherited font dependency changes solely through an ancestor animation, absent any rule/declaration edit? Which computed context and invalidation step applies, and how does successful setKeyframes suppress it? No external question was sent.
