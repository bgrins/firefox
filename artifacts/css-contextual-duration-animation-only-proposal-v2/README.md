# Guarded animation-only duration proposal

This is an uncompiled artifact-only successor to proposal-v1. It adds the existing-or-specified CSS-animation filter already used by needs_animations_update. It does not change the computed animation-list inequality, queued CSS_ANIMATIONS | EFFECT_PROPERTIES tasks, retained animation-only return, no-old-style handling, or normal-traversal path. No native source or application was read or changed while the V1 experiment was restoring.

Dispatch now requires both:

1. The new computed style specifies CSS animations, or self.has_css_animations(context.shared, None) reports existing CSS animations.
2. The old and new computed animation lists differ.

This suppresses the V1 path where animation-name:none plus a changing computed duration could trigger CSS animation and all-effect-property work despite having no CSS animation. It deliberately does not use self.has_animations or relevant EffectSet membership. A CSS animation that is currently irrelevant but still specified remains eligible through specifies_animations(), preserving the accepted-129 reactivation requirement. Existing CSS animations also remain eligible when the new style no longer specifies them.

The source base is the V1 captured current matching.rs, including accepted129, pinned in SOURCE.json. native.patch applies to that base; V1-DELTA.patch contains only this filter refinement. No duplicate base source, tests, model or execution owner are added. Both sealed regression plans are referenced: V1 contains existing ownership/cancellation/reactivation cases and five new behavioral probes; V2 adds the zero-start self-font measurement, whose idealized Dnext=1.5/D map can alternate. Those observations are not fixed-point conformance oracles.

Root reported the V1 child WPT's three callbacks passing while owner97737 was still restoring. That is historical experimental evidence for V1, not execution of this V2, a completed owner receipt, or acceptance. This filter does not establish general feedback convergence, bounded flush work or cycle freedom. EFFECT_PROPERTIES still updates all effects on a selected element.

Before publication, run the exact V2 source through the broader original/candidate comparison, including original passing controls, retained failure/ending signatures, accepted-129 cases, unrelated/no-CSS effects and pseudo elements. Run the separate dom/animation/test/mozilla/test_restyles.html selector and the bounded self-feedback measurements with an external watchdog and retrieval of their JSON. Do not impose an arbitrary iteration cap as a semantic fix. No new accepted ID, formal theorem or native refinement claim is made.
