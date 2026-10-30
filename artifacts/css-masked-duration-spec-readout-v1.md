# Masked font change: specification evidence

Observed 2026-10-30. After the authored change, underlying and animated font sizes are both 32px, so either investigated timing interpretation gives calc(1em / 16px * 1s) = 2s. Firefox retains a 1000ms effect duration and opacity .75 through the first read, three frames, and a subsequent getAnimations() call. Chrome and the literal control use 2000ms and .375. A standalone WPT should avoid asserting an initial timing policy.

Scenario: two CSS animations retain their element and effects; names and keyframes do not change; both are paused at 750ms; no updateTiming(), setKeyframes(), effect replacement, or script-owned duration is involved. Only authored font size changes from 16px to 32px. The opacity animation has linear endpoints 0 and 1.

1. [CSS Values 4, em](https://drafts.csswg.org/css-values-4/#em) defines the local unit using the element's computed font size. The final equal-input state gives 32px and hence 2s. This inference does not select an earlier unequal-input policy.
2. [CSS Animations 2, duration](https://drafts.csswg.org/css-animations-2/#animation-duration) ties the property to the associated effect: “specifies the iteration duration”. [Animation update rules](https://drafts.csswg.org/css-animations-2/#animations) preserve explicit API overrides; none apply here.
3. [Pending style changes](https://drafts.csswg.org/css-animations-2/#requirements-on-pending-style-changes) requires animation API results to reflect pending computed-value changes. The later getAnimations() check distinguishes this observation from merely deferring a style query.
4. [Web Animations, model liveness](https://drafts.csswg.org/web-animations-1/#model-liveness) says: “Changes made to any part of the model cause the entire timing model to be updated and any dependent style.” Its subsequent computed-style example is explicitly non-normative, so it is corroboration rather than a separate normative step.

Verdict: INCONCLUSIVE for a complete normative first-getter algorithm trace. These clauses support the final 2s expectation, but the CSS-to-animation timing-input selection and style-change update chain have not been traced end to end here. This does not resolve initial same-element policy or negate the reproduced cross-engine and literal-control difference.

All linked anchors were verified against fetched official HTML in css-masked-duration-spec-anchors-v1.json. webspec-index is absent; no graph enumeration was performed. Bootstrap help was inspected; installation is deferred until the native build finishes to preserve its toolchain. Current official drafts were read directly. No exhaustive NOT REACHED claim is made.
