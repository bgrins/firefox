# Source-first observable oracle

Written before reading probe-v2, root DESIGN, or proposed native changes. Sources are the four retained primary HTML documents, authenticated in SPEC-PINS.json; the extracted sections are retained separately. webspec-index is unavailable on this agent and root reports no known usable location, so this review reads the original HTML directly and verifies anchors there. This is a bounded normative reading, not an exhaustive automated call-graph trace.

## Required distinctions

1. CSS Properties and Values §2.4 says a universal-syntax registered property's computed value follows unregistered custom properties: substituted tokens or guaranteed-invalid value (GIV). Registration does not make GIV unrepresentable.
2. Cascade §7.3.2 makes explicit `inherit` take the parent's computed value. That value is distinct from the property's initial value, even when its registration does not ordinarily inherit. Cascade §7.3.1 makes `initial` request the initial value. Therefore an already computed inherited GIV cannot in general be replaced by an `initial` declaration when the registration has an explicit valid initial value.
3. CSS Variables §2.2 makes GIV serialize as an empty string, but an explicitly empty token value is valid and is not GIV. Serialization alone cannot distinguish them. A `var()` fallback consumer can: fallback is selected for GIV and not merely for empty valid tokens.
4. Properties and Values §2.5 animates registered values by computed value. Web Animations' by-computed-value rule falls back to discrete combination for incompatible components/types; discrete combination selects the first endpoint below 0.5 and the second at/above 0.5. A selected endpoint must retain its computed-value meaning, including GIV.
5. Web Animations §5.3.3 computes each specified keyframe property in the target's context. §5.3.4 fills a missing endpoint with the underlying computed value. These are two routes by which an actual GIV can enter the effect result. They must not be conflated with a missing effect/property that leaves underlying cascade untouched.

## Predicted browser observations

Assume a universal registered property P has explicit valid initial value I and an effect endpoint or underlying value that is demonstrably GIV. If the effect selects that GIV, getComputedStyle(target).getPropertyValue(P) must serialize empty and `width: var(P, F)` must use F (provided F is a valid width). It must not use I. If an animation supplies valid tokens V, the same consumer uses V. If P is a valid empty token stream, serialization is also empty but fallback is not selected; the consuming declaration may instead become invalid after substitution.

If a higher-priority effect publishes GIV over a lower-priority valid value, deleting/omitting the higher value is incorrect: it reveals the lower value. Publishing `initial` is also incorrect when I differs from GIV. The animation result therefore needs to survive effect composition and declaration publication as the already computed semantic GIV.

Required calibration: establish the parent's/underlying GIV and fallback before starting animation; distinguish valid initial, valid animated tokens, empty tokens and absent effect; use non-boundary sample times for discrete switches. Avoid relying solely on empty CSSOM strings. The test must ensure animation-taint restrictions are not the reason the observed consumer falls back; an animatable consumer such as width is appropriate.

This oracle does not yet establish which native route is defective or whether the supplied fixture reaches these prerequisites. Those are subsequent review stages.
