# Ordinary-element transition routing probe

Open `standalone.html` in a browser and press Run. The same source can be called as `await runTransitionRoutingCase(mode)` for `transition-only`, `active-overlap`, or `current-no-fill`. Run the cases sequentially. Retain the full returned JSON and browser version, including failed setup checks; `predictionMatches` alone is not an acceptance result.

The WPT-shaped wrapper is `transition-current-not-in-effect-priority.html`, intended for `web-animations/animation-model/combining-effects/`, with its relative resources file. It has three callbacks: two controls and one interpretation probe. The standalone wrapper needs no WPT environment. Both use the exact shared helper. Successful WPT observations remain in `window.transitionRoutingResults`; value failures include the full row collection.

| Mode | Before | During / two frames | After cancel |
| --- | --- | --- | --- |
| Transition only | 0.5 | 0.5 | 0.5 |
| Active overlapping WAAPI effect | 0.5 | 0.8 | 0.5 |
| Current before-phase, fill:none WAAPI effect | 0.5 | Probe: 0.5 | 0.5 |

Each case generates a real CSS opacity transition from important 0.2 to important 0.8 on the observed ordinary element. It pauses that original transition at half duration. The WAAPI effect, when present, is also paused, uses opacity endpoints 0.1/0.3, and is either sampled halfway or held before its delayed active interval without fill. No transition is retargeted. Four observations each take three style reads, then record timing and object identity. Registration, exact target, original transition survival, paused/pending state and resolved/null effect progress are checked separately from the predicted style.

The fixture constructs the owning transition relationship through CSS on the same element and verifies that the original object remains registered and targets that element after style flushes. The web API does not expose the native owning-element field; this is stronger construction evidence than a retargeted CSSTransition, not a direct observation of that private field. JS pause/currentTime operations intentionally alter fixture animations. Cleanup removes all owned effects, elements and styles.

## Contract and uncertainty

[Applying the composited result](https://drafts.csswg.org/web-animations-1/#applying-the-composited-result) chooses the insertion origin from the highest-order effect in a property's stack. [Transition composite order](https://drafts.csswg.org/css-transitions-2/#animation-composite-order) places transitions before ordinary WAAPI animations, while [transition cascade level](https://drafts.csswg.org/css-transitions-2/#animation-cascade-level) assigns Transition origin to a transition retaining its owning element. Thus transition-only beats important author declarations; active overlap selects Animation origin and the important author value wins.

For the null-progress case, [the effect-value algorithm](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-effect) aborts without a sample when iteration progress is unresolved. Inferring that this non-sampling effect cannot select the stack's origin needs the surrounding application algorithm; the stack-order text does not itself explicitly state that filter. The combining-effects introduction is non-normative and is not used as a binding premise. Therefore the final row is an interpretation probe, not a settled conformance oracle. Its failure, even with valid setup, does not establish a new bug or authorize a production change. CSSWG clarification may be necessary.

The adjacent copied-helper investigation is `css-pseudo-animation-composed-recascade-20261110-v1`. Its source trace finds a property union formed before null-progress sampling is skipped, in both the proposed query helper and existing renderer machinery. This ordinary-element fixture tests renderer-visible behavior independently of that helper and its retargeted-transition setup. It does not depend on the temporary privileged driver, any copied native patch, pseudo elements, provider recascade, custom properties or layout-relative endpoints. No claim of novelty or equivalence to bug 1606176 is made.

## Validation and handoff

`python3 -I -B check.py` passes genuine WPT lint and manifest classification, JavaScript syntax, and inert registration of the exact three callback names. Temporary staging is removed. No browser was run by the author; all predictions remain unmeasured in this capsule. The WPT path and wrapper are a proposal, not installed or committed tests. The existing native transaction and frozen combined capsule remain untouched.

Root can run the standalone page in the separate System Firefox 158 connector during the objdir build, recording that browser identity. A result there is evidence for that release browser, not for the active candidate or a cross-browser specification verdict.
