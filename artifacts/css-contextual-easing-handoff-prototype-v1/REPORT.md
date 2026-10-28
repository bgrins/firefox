# Contextual easing handoff integration

Compile-preparation only: six source paths rebased onto signed a1f28b1578df604a67c45e2d23ab54f246941561 and canonical84f502af. All parser resolve guards stay closed. The combined source has not been typechecked or executed; this package is not contextual-syntax activation or a complete lifecycle fix.

Five prior handoff base files equal the current signed and actual source byte-for-byte, so their candidates are reused exactly from css-contextual-steps-dependencies-prototype-v1. Only specified/easing.rs changed since that base, due to accepted143; it uses the sealed representation prototype based on the current file, with the temporary infallible wrapper removed. SOURCE-ROLES provides explicit repository-relative base/candidate captures and hashes for all six paths. The generic/computed easing representations remain unchanged, and generic calc df7e (accepted145 atop144) is outside the patch.

## Concrete integrated behavior

Gecko keyframe extraction constructs its existing animation Context from the actual element, base/parent styles, container query and tree-counting cache, then computes the selected timing function there. Servo threads parent style and a corresponding Context through generation of IntermediateComputedKeyframe. Servo_ParseEasing remains fallible and writes output only after successful context-free conversion. Both easing keyframe callers no longer call an infallible context-free wrapper; the wrapper itself is absent. Unrelated range and filter conversion helpers are unchanged.

The prior has_contextual_timing_function classifier now covers Steps, Bezier and Linear through their common fallible helper. Its real unvisited cascade handoff evaluates unresolved timing values before owning-style build, temporarily sets and restores for_non_inherited_property, and marks rule caching uncacheable while recording conversion effects. Existing matching hooks request keyframe reconstruction on normal style changes. These are the exact prior handoff mechanisms, not a newly claimed exhaustive invalidation system.

Resolved Linear functions retain the old canonical piecewise builder/equality/serialization; contextual stops own output and both percentage ASTs and build scalar entries after context conversion. Steps count and Bezier x clamping are preserved. The representation's detailed compatibility argument and unmeasured allocation caveat remain in its pinned package; no runtime serialization or performance equivalence is asserted here.

## Concrete activation blockers

Selected keyframe declaration scope is not yet threaded. Context::new_for_animation selects same-tree author scope; the late cascade pass inherits its current declaration scope. lookup_keyframes returns only the animation, losing the declaring scope. Tree-counting consults current_scope.shadow_order and can return the containing-tree default, so shadow/slotted declarations can differ between computation and dependency publication. Both phases need the same selected rule scope before activation. Closed parser guards keep this first compile experiment from admitting those unresolved trees.

Selected-step winner handling, owning-effect publication, style sharing, all dependency invalidation, and animated-style ordering still require review and runtime coverage. Repeated evaluation in a temporary animation Context alone is insufficient. Preserve the earlier self-font cycle/iteration limitation rather than implementing guessed animation-only iteration. Servo-only paths require their own feature compilation; a successful Gecko check will not prove them.

Context-free Web Animations policy remains unresolved under open CSSWG14246. No arbitrary default context is introduced. API rejection of unresolved input is fallible safety behavior, not a claim of completed API syntax semantics.

The same consumer work also blocks broader relative Round/ModRem canonical-readiness changes. Accepted145 now supplies deferred finite arithmetic, but neither generic guard proposal is activated here. Preserve144/145 and avoid overlapping repair counts when choosing final patch boundaries.

## Checks and limits

All six current base bodies were authenticated against signed Git objects; both source packages' manifests authenticated. Private forward/reverse/reapply transport is exact without offsets/fuzz, and Rustfmt parses all six candidates. Invariant checks confirm the retained parser guards, both migrated keyframe calls and wrapper removal. No live source, app, index, build, runtime or canonical control changed. Root owns the configured Gecko check and restoration. Earlier handoff checking is historical evidence only, not compilation of this combination.

Searchfox discovery was attempted this turn but failed DNS; existing sealed Searchfox caller discoveries and unchanged source joins are reused. No missing-tool/bootstrap or new upstream revision claim is made. No new proof package or coverage count was created.
