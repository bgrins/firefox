# Guaranteed-invalid animation publication

2026-10-19. Source-derived hypothesis, then reproduced by root: **10 failures, 6 controls pass**, with stable source/configuration/binary pins. This is a correctness defect; no security or novelty claim. This artifact contains discovery and repair design, not an implemented or formally verified repair.

## Independent expected behavior

The registration is static and explicit: syntax `*`, either inheritance flag, initial value `20px`. The parent has an unresolved variable without a fallback. For universal registrations the computed-value rule allows the guaranteed-invalid value (GIV); it does not substitute the registered initial value for this case. Existing upstream `invalid-at-computed-value-time.html` exercises this distinction for both inheritance flags. [Properties and Values §2.4](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values).

Literal `inherit` in the keyframes takes the parent's computed value, including GIV. Literal `initial` instead takes `20px`. These are distinct specified operations even though an unregistered property's initial value happens to be GIV. [Cascade explicit inheritance](https://drafts.csswg.org/css-cascade-5/#inherit), [initial](https://drafts.csswg.org/css-cascade-5/#initial).

Keyframe property values are computed in the target context. Discrete sampling chooses the first endpoint below halfway and the second at or above halfway. A missing endpoint supplies the underlying value through neutral composition. Our samples use .25 or .75, avoiding ties, endpoints and extrapolation. Thus selected GIV must remain GIV after publication. [Web Animations effect value](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect), [discrete animation](https://drafts.csswg.org/web-animations-1/#discrete).

GIV serializes as an empty string, but is distinct from a valid empty token stream. A `var()` consumer uses its fallback for GIV. The diagnostic therefore observes the custom property, a separate alias with `61px` fallback, and used width. Expected `['', '61px', '61px']`; observed `['20px', '20px', '20px']`. [Variables GIV](https://drafts.csswg.org/css-variables-2/#guaranteed-invalid), [var replacement](https://drafts.csswg.org/css-variables-2/#replace-a-var-function).

**Verdict: REACHED.** The specified computed value must survive publication; registered Initial is not an equivalent representation.

The current Properties ED and published TR differ on omitted registration descriptors. No omitted descriptor is used here. In particular, this report does not repeat the earlier frontier report's overly broad claim that an omitted initial descriptor is necessarily invalid under the current ED.

## Actual source path

Complete files are retained in `sources/` with `SOURCE-PINS.json`; Searchfox discovery is retained separately. This is a source audit, not a verified translation.

1. `Servo_GetComputedKeyframeValues` creates an animation context using the actual parent style. Literal CSS-wide declarations take the ordinary `AnimationValue::from_declaration` route; they do not depend on the substituted typed-keyframe repair.
2. `CustomAnimatedValue::from_declaration(Inherit)` reads the registration-selected inherited map. GIV is absent there. It returns outer **Some(CustomAnimatedValue { name, value: None })**. Outer `None` still means no computed animation endpoint, not GIV.
3. The neutral route uses `AnimationValue::from_computed_values` and `CustomAnimatedValue::from_computed`, preserving the same inner `None` from underlying style.
4. The selected segment result is inserted by `Servo_AnimationCompose` and later uncomputed through `AnimationValue::uncompute` / `CustomAnimatedValue::to_declaration`.
5. `to_declaration` currently converts inner `None` to `CSSWideKeyword::Initial`.
6. Recascade handles Initial using the registered initial map or its already-seeded noninherited initial state. This yields `20px`, independently of the original GIV.

The accepted identity and segment components preserve name identity and the distinction between absent endpoints and inner GIV. They deliberately did not prove this uncompute/recascade join. Their theorems are not refuted by this counterexample; the necessary publication constructor invariant was missing.

## Runtime and diagnostic isolation

`probe.html` is the exact root-run first diagnostic. Each of eight cases runs for both inheritance settings. Constant inherit, inherit-first, inherit-last, neutral-first, neutral-last fail only the final sampled array assertion. Initial, valid-parent, and unresolved-declaration controls pass. Parent, registration, nonanimated reference, active effect and exact sampled progress assertions precede the failed observation. `runtime/` retains the root receipt and raw log; no browser was run by this agent.

The original diagnostic uses a direct `inherit` reference and underlying value. For inherits=false that reference depends on earlier repair72. **`probe-v2.html` removes that test prerequisite:** target/reference receive direct unresolved-variable GIV (or literal33px for the valid-parent control); keyframes retain literal inherit. It has the same16-case expected roster. Its separate runtime evidence belongs to root; the first run is not relabeled as a v2 run.

## Upstream prerequisites

`UPSTREAM-PINS.json` binds exact files from base `976279105b2e78b8666a959eb3f25c9176cefaf8`. Upstream has the same CSS-wide inherit constructor and inner-None→Initial publication. Its glue uses the ordinary declaration iterator for all these literal keyframes. The preexisting upstream invalid-at-computed-value-time WPT supplies the direct universal GIV calibration used by v2. The three proposed production edits do not require the typed variable-keyframe, attribute metadata, token-boundary, or direct-inherit repairs. Exact patch application and upstream runtime remain root gates; source inspection is not an isolated-upstream execution result.

## Bounded negative findings and remaining work

- Registration does not change during these tests: this is not evidence of a registration-epoch invalidation defect.
- Registered initial, valid parent value and unresolved raw declaration controls retain their expected behavior.
- Typed nonuniversal GIV reachability, registration changes, root inheritance, pseudo-elements, SMIL, effect stacks and all URL/provenance paths were not exhaustively audited.
- A useful next proof is the publication round trip for optional computed custom values: preserve name, GIV, non-GIV and map lookup under explicit selected-registration and computed-provider premises. Reuse accepted map removal/history and segment components rather than restating them. An absent outer endpoint must never become a published GIV declaration.
- Build, dedicated candidate WPT, regressions, independent native review, and any formal companion remain separate repair acceptance gates.
