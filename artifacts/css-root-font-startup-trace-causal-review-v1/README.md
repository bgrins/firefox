# Late startup: conversion succeeds before the repairing target update

The trace rules out a wholly missing post-publication normal route, EffectProperties delivery or64px keyframe conversion in the recorded cohort. Root32 publication is followed by selective handoff, normal child recascade, task4 delivery, and64px computation with propertiesChanged=true. The later target update rebuilds64px again with propertiesChanged=false. The next concrete lead is deferred animation-rule application after that successful rebuild; its queue state is not logged yet.

The closed raw log is f099833a0a36df6dcb50d95248064f269ae14fa4a23bbba994e5b8fa639a6101. Saved-only analyze.py107bb6 exit0 reproduces the sealed extractor's entire RFST output and preserves exact full lines/line numbers in TRACE-EXCERPT. It verifies the stored late46/46/46→64 projection and exact native conversion/changed sequences. Root supplied completed archive/state preservation and profile cleanup; this report performs no live preservation check. No browser, native source, build, index or canonical action occurred.

## Observed sequence

The matching cohort is root node0x10b40c7c0, device0x101c7d820, child node0x10b40c970 and child effect address0x10b130f10. The root effect address is0x10b130d40. Rust events shown here use ThreadId(6); C++ events explicitly join target node/effect/style pointers. The unique23→32 root publication, child46→64 conversions and single-late fixture support this mapping. The browser did not independently expose native node pointers. Pseudo95 is retained as its raw enum value, not decoded by guessing.

| Raw lines | Recorded event |
| --- | --- |
|11081|Root publishes23 with no prior style on device0x101c7d820.|
|11184–11206|Normal root MatchAndCascade queues/delivers mask5; its effect computes32 twice (initial changed1, second changed0). This is computation, not root32 Device publication.|
|11193–11220|Child normal MatchAndCascade queues/delivers mask5; initial and EffectProperties rebuilds use Rem basis23 and compute46 for both keyframes. Same effect address reports changed1 then0.|
|11222–11228|Explicit AnimationOnly\|ParallelTraversal root pass publishes32, returns ancestor-font work and sets the selective signal. No FinalAnimationTraversal flag is present.|
|11239–11249|Child animation-only processing still skips process_animations. The ordinary sibling Rem basis is already32.|
|11250–11264|Joined signal=true, child seeds and root normal-dirty are recorded; normal root entry succeeds. Child CascadeOnly has admitted_animation=true and queues mask0x4.|
|11270–11278|Mask4 is delivered to that child; its effect reads basis32, computes64/64 and reports changed1, then traversal joins. The requested rebuild is present.|
|11466–11486|Later child pass has AnimationOnly with RESTYLE_SELF\|RESTYLE_CSS_ANIMATIONS, then normal RESTYLE_SELF/MatchAndCascade queues0xc. Delivery12 rebuilds64/64 at the same effect address with changed0.|

The fixture stores first46, settled46, afterCalibration46, root32/plain64, then changes only the target's background class and reads64. CSSAnimation object comparisons/counts and paused progress remain stable; these are not direct KeyframeEffect identity measurements. The late record's precondition is23/11 with no animations. The later RESTYLE_SELF sequence is consistent with that class mutation; there are no native JS phase markers identifying the exact getter boundaries. Therefore this report does not place line11277 precisely before the first versus settled/calibration getter. It does distinguish the earlier cascade-only64 rebuild from the later match-and-cascade64 rebuild using explicit kinds/hints, not time proximity alone.

Same-address effect observations across the synchronous sequence are stronger than neighboring unrelated log lines, but no allocation/destruction trace proves an unrestricted lifetime claim. There is no PID field; do not generalize address/thread equality across processes/documents or later reuse. No global happens-before relation is inferred from interleaved stderr. Full lines remain the authority.

## Source implication and remaining mechanism

In sealed6d6c instrumentation, built-properties is logged after BuildProperties/EnsureBaseStyles and before the propertiesChanged return. For changed1, the exact existing KeyframeEffect::UpdateProperties path moves the new properties into mProperties, updates effect/cascade state, notifies the animation if attached and requests a Layer restyle. There is no other normal early return between this log and the assignment. Assignment itself is not separately logged. The later changed0 result, with64 conversion repeated, supports retention of the rebuilt properties; it does not establish that the sampled animation rule had been refreshed when the earlier getters returned46.

The captured e86 downstream chain supplies a specific scheduling candidate:

1. KeyframeEffect::RequestRestyle forwards only with target, pres context and mAnimation; those guards are not logged here.
2. EffectCompositor::RequestRestyle inserts/marks mElementsToRestyle and calls PostRestyleForAnimation unless its existing posted flag suppresses the call.
3. PostRestyleForAnimation intentionally returns while IsInServoTraversal or mIsInPreTraverse is true. Its comment relies on a subsequent PreTraverse to post explicit animation hints rather than posting to PresShell immediately.
4. ServoStyleSet::StyleDocument drains PreTraverse before the first traversal and once after it, then runs a second traversal and returns. It has no third drain in that function. Each Servo_TraverseSubtree may itself perform AnimationOnly followed by normal traversal.

Thus an updated64 effect produced by the selective normal handoff inside the second StyleDocument traversal can request new animation work after the final drain. With no subsequent externally scheduled style traversal, the old46 animation rule could remain until the non-font class causes another entry. This matches the observed successful conversion plus later RESTYLE_CSS_ANIMATIONS repair. It remains a candidate: this trace does not log StyleDocument pass ordinal, mElementsToRestyle insertion/suppression, PostRestyle's branch, WillComposeStyle or the installed animation rule. Do not declare the exact suppression branch or a fix proved from this trace alone. FinalAnimationTraversal and missing membership are not explanations supported by this particular normal-pass sequence.

## Smallest next discriminator

Only if root needs another native trace, retain this same one-late document and add targeted records for this effect's RequestRestyle guard/cascade level, the existing restyleEntry/skip decision and PostRestyle traversal/pretraverse branch, plus the existing PreTraverse target drain/WillComposeStyle and StyleDocument first/second pass boundaries. Reuse already-evaluated booleans and target/effect addresses; add no getter/flush or broad animation logging. This tests whether the64 rebuild leaves an undrained request after the second pass. If draining and recomposition are both observed before the stale getter, only then follow sampled-rule installation/cache invalidation. No loop/extra traversal repair is proposed or implemented here; termination and feedback policy would need separate review.
