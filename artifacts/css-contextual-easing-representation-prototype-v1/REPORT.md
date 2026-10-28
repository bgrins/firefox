# Contextual easing representation groundwork

This inactive two-source prototype extends existing Steps work to Bezier and Linear. It is not a complete consumer repair and activates no generic calculation guard. All unresolved-value parser guards remain, including accepted143's check of both Linear percentage positions. No live source, index, epoch, browser or build was changed. Configured compilation remains required.

## Reuse and next slice

The reusable six-source handoff is css-contextual-steps-dependencies-prototype-v1/native.patch, following the keyframe/prerequisite prototypes. It supplies Steps contextual conversion, fallible API conversion, Gecko/Servo keyframe context threading, normal-style keyframe reconstruction and late conversion-effect publication into the owning computed style. Its separate typecheck artifact reports successful Gecko configured checking, not this successor or Servo-only paths. These artifacts are pinned rather than copied or recounted.

The new patch changes specified/easing.rs and Servo_ParseEasing in glue.rs over authenticated HEAD70c3349f. It reuses earlier Steps/clamp and API-output atomicity logic, adds contextual Bezier conversion with x clamping, and supplies specified Linear stop storage. Generic/computed easing and PiecewiseLinearFunction are unchanged: computed ABI remains scalar. New specified storage/layout still requires native/cbindgen integration validation.

## Linear ownership and computation

Resolved stores the existing canonical PiecewiseLinearFunction. Contextual owns an OwnedSlice of LinearStop records: Number output and both optional Percentage expressions. Parse still requires two authored stops, regardless of two-position expansion. Known values use the same builder and preserve canonical equality, serialization and shared entry storage. Unknown values can retain ASTs without borrowing parser/context state once activation is authorized. Contextual serialization emits retained expressions; computation maps them through actual Context before using the unchanged builder for omitted positions, duplicate outputs and nondecreasing coordinates.

The new types derive owned allocation accounting and shared-memory/serialization traits. Resolved retains the old Arc accounting contract; Contextual owns its slice and nested boxed ASTs. No Context pointer, element handle or numeric-result cache is stored. Trait/layout correctness remains uncompiled. The context-free fast path preserves existing scalar computation; otherwise standard Integer/Number/Percentage conversion handles all three forms. Range, infinity, normalization and mixed-context behavior require real tests.

Servo_ParseEasing writes output only after fallible conversion succeeds. The compatibility to_computed_value_without_context().expect wrapper is TEMPORARY. The two existing keyframe callers remain safe only under retained parser guards; migrate every caller to the prior real-context handoff and remove this wrapper before activation. It is not an acceptable fallback for newly admitted contextual values.

## Activation obligations

Rebase the prior Gecko/Servo keyframe handoff and owning-style publication over current source. Establish selected declaration scope, including current_scope for tree-counting; the old late handoff does not yet prove it. Publish actual conversion effects on owning styles/effects, account for style sharing, and recompute on font/root/container/viewport/tree/scope changes. Extend the classifier through the new fallible helper for all three forms. Normal-property conversion is not complete lifecycle support.

Preserve CSS/script keyframe ownership, pseudo-element parent context and animated-style ordering. The prior self-font two-state witness rules out naive animation-only iteration; it is not a conformance oracle. Compile Gecko and Servo, run existing easing syntax/output/serialization/range tests and the prior six lifecycle WPTs. Current local constant-result admission baseline passed8/8 with32 calibrated snapshots; the generic infinite-value guard is still uninstalled, so its regression remains a source prediction.

CSSWG14246 remains Open on fresh review. Its element-dependent Web Animations proposal is not a CSS-property restriction or authority to invent a default context. Fallible API conversion is a safety boundary, not full conformance or preservation of all formerly admitted syntax.

The broader finite same-relative-unit Round/ModRem canonical-readiness work remains pending. Accepted145 supplies the deferred arithmetic prerequisite; preserve its generic source and accepted144 opposite guard in future integration. Reassess shared patch boundaries after consumers are ready. No new fix count, proof coverage, native acceptance or clean-upstream landing claim is made.
