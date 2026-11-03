# Root-relative keyframe recomputation

The actual archived e86 diagnostic establishes stale retained animation values after the root metrics change. All three properties—variation, ordinary width and opacity—retain the original root basis through both seeks, in first and settled observations, for rem and explicit rlh and all three getter orders. Recreating the effects on the same targets, or creating fresh targets, resolves the new basis. Static and literal controls remain valid. This is broader than numeric calc metadata and is separate from the four-file variation parent-basis candidate.

The exact saved assessor replay b69d13/0 equals the frozen runtime assessment (a722f2/0). There are72 rows and216 principal scalar observations, not216 independent frames. Browser/archive/cleanup authority is the root runtime; this review ran no browser or native code. Initial root-only/first WPT assertions alone did not establish settled behavior; the later diagnostic does.

## Specification trace

Scenario: standards-mode rendered non-root targets, paused replace effects with two specified endpoints, resolved progress, unchanged target/parent font sizes, root font-size23→31px and explicit line-height37→47px. The root values and static unit references are observed after the mutation; both rem and rlh have unambiguous root bases here.

1. [Web Animations effect-value algorithm, step5](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect) obtains computed keyframes for the effect. The introductory algorithm and its final explanatory note require live computed keyframes, not an immutable snapshot from effect creation.
2. [Calculating computed keyframes, step2.2](https://drafts.csswg.org/web-animations-1/#calculating-computed-keyframes) computes each specified property with the target element as context.
3. [Computing property values](https://drafts.csswg.org/web-animations-1/#computing-property-values) resolves dependencies using the target's computed-value context, with dependencies computed first.
4. [CSS Values root font-relative lengths](https://drafts.csswg.org/css-values-4/#font-relative-lengths) makes non-root rem depend on the root font size and rlh on the root line-height. These targets are not the root and the root line-height is an explicit px length, so root self-reference and normal-line metric questions do not apply.

**Verdict: REACHED**—the specified effect calculation must use the current root basis. The persistent settled/seek observations violate this recomputation requirement. This establishes a conformance discrepancy for the recorded archive, not its novelty, release prevalence, native cause, accepted fix, or a new catalogue increment.

The step-only index trace returned zero routes because computed-keyframes is a definition link; it is not evidence of NOT REACHED. The explicit algorithm steps above were read in full. Exact outputs and spec hashes are preserved. All four anchors were verified (9ccd5f/14739f/d744db/d9a752). An initial multi-anchor exists invocation847ecf failed argument parsing; the individual checks succeeded.

## Native update path and remaining inference

SOURCE-EXCERPTS pins the actual saved sources by hash and exact text:

- matching.rs::finish_restyle updates Device root font-size/line-height and emits RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT for changed font-size/line-height.
- data.rs::needs_to_recascade_self honors that hint when the persisted computed style carries USES_FONT_OR_WM_RELATIVE_UNITS.
- matching.rs animation processing schedules EFFECT_PROPERTIES for targets with animations. EffectCompositor::UpdateEffectProperties invokes KeyframeEffect::UpdateProperties on each effect when reached; this existing route rebuilds computed animation properties.
- Servo_GetComputedKeyframeValues creates a local animation Context, converts declarations to values, and returns the attribute-tracker bit. It does not return the local builder's relative-unit flags. Device root queries also set document-level used-root state; that side effect is distinct from publishing a target-style flag.

These facts support a missing target dependency-publication hypothesis, but the browser does not log native flags or function entries. They do not prove the target skips recascade, rule out every scheduling route, or show which minimal source change is sufficient. The existing fix131 attribute publication contract does not establish font dependency publication. The companion Lean review addresses that logical separation, not this runtime attribution.

The next discriminator is a nonzero ordinary margin-left:1rem/1rlh on the same animated target, compared with an otherwise identical0px target. If only that unrelated ordinary declaration restores updates, it supports absent effect-to-persisted-style dependency transport over a generic failure inside UpdateProperties. It remains indirect evidence: the margin forces ordinary style work too. Keep the frozen72-row diagnostic unchanged and preserve observations in a separate runtime.

## Prior art

[Bug1254424 comment0](https://bugzilla.mozilla.org/show_bug.cgi?id=1254424#c0) already identified liveness of ancestor-dependent animation values. Comments1 and4 describe Stylo's fix and retirement of the old style system. [Bug1350754 comment0](https://bugzilla.mozilla.org/show_bug.cgi?id=1350754#c0) explains the UpdateEffectProperties hook for changed target style, and its patch series landed. Bug1338944 concerns the old deferred-composition machinery and was closed after that engine's removal. Exact MCP bug records are retained.

This is relevant architecture/history, not proof that today's root-only case is a duplicate or a regression of those patches. The bounded search found no exact prior root-only rem/rlh report; absence from that search is not novelty proof. A minimal WPT should exercise root mutations while keeping the target font fixed, include ordinary-width and static controls, and require current values after a settled sample. Preserve the original36 suite; do not reinterpret the parent-basis patch as a fix for this independent failure.
