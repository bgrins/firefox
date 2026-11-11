# Relative-value provider oracles

The ordinary-element endpoint oracle is **45px**. The explicit unanimated-base algorithm yields **50px** for the additive case, not 70px. These are different computations: an authored animation endpoint uses current target dependencies; the initial underlying value has a separate base-value rule. The pseudo endpoint oracle cannot safely be promoted from the element case because current Web Animations text explicitly passes the originating element as dependency context. See the separate verdicts below.

These traces describe the captured current drafts, not a renderer-derived specification. They do not establish broad provider correctness, public CSSOM repair acceptance, or cross-engine agreement. No browser was executed. Root's separate composed runtime has only fixed-value providers and does not settle these relative-value cases.

## Exact scenario

Use a connected non-replaced HTML block, horizontal writing mode, no important declarations/transitions/other effects, no font-size-adjust or zoom, and authored `font-size:20px`. All animations have linear easing, two explicit offsets 0 and 1, one normal iteration and resolved progress 0.5; await readiness before seeking. There are two separate effects, not a single combined declaration block.

A: replace `font-size:20px→40px`, independently replace `margin-left:1em→2em`.

B: authored `margin-left:2em`, replace `font-size:20px→40px`, and independently add constant `margin-left:10px` at both endpoints. The explicit two endpoints avoid CSS-generated/WAAPI implicit endpoint distinctions.

For pseudo comparisons, the originating element has an explicit different font (`12px`), the pseudo has authored `20px`, and the animations target that pseudo. Generated and absent-box cases differ only in `content:""` versus `content:none`. The ordinary control has its own `20px` font. This makes accidentally using the origin observable.

## A: ordinary-element margin 45px — REACHED

1. [CSS Fonts 4, font-size](https://drafts.csswg.org/css-fonts-4/#font-size-prop) and [CSS Box 3, physical margins](https://drafts.csswg.org/css-box-3/#margin-physical) supply computed length animation types. [CSS Values 4, dimensions](https://drafts.csswg.org/css-values-4/#combine-dimensions) supplies the numeric interpolation/addition operations.
2. [Web Animations, computed keyframes](https://drafts.csswg.org/web-animations-1/#calculating-computed-keyframes), step 2.2, sends each authored property to [compute a property value](https://drafts.csswg.org/web-animations-1/#computing-property-values), using the target element. The dependency context is its computed values, and dependency values must be calculated first.
3. The font effect therefore yields `(20+40)/2 = 30px`. [The em definition](https://drafts.csswg.org/css-values-4/#em) makes the margin endpoints 30px and 60px.
4. [Effect-value calculation](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect) chooses those two explicit endpoints, uses replace, and interpolates them at 0.5: `(30+60)/2 = 45px`. The computed-keyframe liveness paragraph reinforces use of current dependencies.

There is no per-endpoint overlay of the font animation's own 20px/40px endpoints. That would produce margin endpoints 20px/80px and 50px, which is not the traced algorithm. Using static authored font20 throughout would produce 30px and also contradict the current dependency step. Separate disjoint property effects do not become a joint keyframe provider merely because they share offsets.

## B: ordinary-element margin 50px — REACHED under the written base rule

1. [Applying the composited result](https://drafts.csswg.org/web-animations-1/#applying-the-composited-result), step 1, defines the initial property base by finding its computed value **“in the absence of animations”**. With explicitly authored font20 and no inherited animated dependencies, the authored margin2em has base `2×20 = 40px`.
2. Its steps 2–3 establish the margin property stack and supply that base as the first underlying value. The separate font effect is not another margin-stack entry.
3. [Effect composition](https://drafts.csswg.org/web-animations-1/#effect-composition) and the effect-value algorithm combine the 10px endpoint with 40px by add; both endpoint sums are 50px. Interpolation therefore remains 50px. The final font is independently30px.

This verdict deliberately follows the unqualified absence-of-animations text. A result of70px requires the additional premise that only animations of the evaluated property are suppressed while other same-target animations remain in its base dependency context. The captured base-value step does not state that exception. If interoperability or another normative clause requires that interpretation, it needs a separate explicit reconciliation; this report does not silently substitute it. In particular, no implementation bug should be filed solely from a future50/70 discrepancy before recording that scope question. A result obtained by mixing endpoint/provider overlays would likewise need its own trace.

## CSS ownership and origins

[CSS Animations 2 processing](https://drafts.csswg.org/css-animations-2/#keyframe-processing) constructs the authored keyframes; our explicit endpoints avoid its generated endpoint branch. [Animation composition](https://drafts.csswg.org/css-animations-2/#animation-composition) supplies CSS replace/add choices. The Web Animations algorithms then apply to the resulting effects. A plain WAAPI effect and an owning CSSAnimation use Animation origin in these scenarios. CSSAnimation list order and plain Animation ordering differ, but the two effects touch disjoint properties here; neither order supplies the other effect's per-keyframe declarations. There are no CSS transitions, so Transition origin cannot be inferred from a manually paused CSSAnimation or from calling WAAPI methods on it. Final cascade winners matter: an important winning font would change A's dependency context, and an important margin would mask the final result; both are excluded.

## Pseudo endpoint 45px — INCONCLUSIVE as an intended conformance oracle

The pseudo is not interchangeable with its originating Element in this draft. [Keyframe effects](https://drafts.csswg.org/web-animations-1/#effect-target-target-element) defines the target element of a pseudo effect as its originating element; computed-keyframe step2.2 nevertheless passes that target element to the value-computation algorithm. In contrast, logical mapping explicitly refers to the effect target. With the origin fixed at12px, literal substitution through that call gives margin18px, although the pseudo font effect is30px. CSS Values describes em in terms of the element where it is used, and the pseudo is fully styleable. Those texts do not explicitly repair the algorithm's Element/pseudo context handoff.

Thus the ordinary45px conclusion is established, but a pseudo45px WPT must not be presented as mechanically derived without resolving this wording. The literal18px consequence is a useful discriminator, not a recommended implementation policy. CSS Animations2's target-(pseudo-)element variable is explicit during keyframe generation, but it does not replace Web Animations' later argument. No broad absence-of-search result is claimed as proof that no clarification exists.

[CSS Pseudo4](https://drafts.csswg.org/css-pseudo-4/#generated-content) ties box generation to content and makes before/after fully styleable. [CSSOM getComputedStyle](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle) selects the pseudo object and reads its resolved properties when the connection/context guards hold. Neither supplies a separate relative-unit algorithm for a missing box. Accordingly, once a pseudo effect exists, merely generating a box cannot justify switching dependency providers. CSS-created animation existence on an absent-box pseudo is a separate precondition; the diagnostic records effect inventories rather than manufacturing an expected CSSAnimation.

B's explicit pixel animation endpoints do not encounter the pseudo em-keyframe argument mismatch. Its written base-rule arithmetic is still40+10 conditional on a styleable pseudo with authored font20/margin2em and an actual additive effect. That does not resolve A's provider issue or the general base suppression scope question.

## Acquisition and limitations

`PRIMARY-SOURCES.json` pins seven freshly fetched primary HTML documents with URLs, times and hashes. `ANCHORS.json` authenticates every recorded anchor against those exact bytes; section HTML/text excerpts are retained. `webspec-index` could not query its local readonly database; stderr and help are preserved and no database was changed. Fresh primary HTML was used as the fallback. Public CSSWG issue searches are retained, including issue66 on base-value liveness: that discussion concerns live recomputation/keyframe generation and does not settle suppression of other animated properties or the pseudo argument mismatch.

Next useful experiment is observational: run A/B on ordinary/generated-before/absent-before, using CSSAnimation and plain WAAPI and reversing creation/list order. Record authored baseline, font/margin, content, actual effect identity/type/target/pseudo, progress, pending status, and a second read after unrelated invalidation. Do not let absence of a CSS effect or a failed font prerequisite masquerade as a relative-unit result. Do not add guessed pseudo or70px assertions. Parent/child animated inheritance, custom-property overlays, attr(), currentColor, and logical mapping need their own normative traces before a general provider API is accepted.

`provider-comparison.html` is an unexecuted standalone observational fixture for the24 combinations. It awaits readiness, seeks both effects to half, records sync/invalidation/next-frame reads, and includes actual effect inventories. It has no numerical conformance assertions. Reads can flush styles and are not atomic engine snapshots; a missing CSS animation remains visible as an empty inventory. Its output must first be checked for two matching effects and resolved half progress before interpreting an animated-value row.
