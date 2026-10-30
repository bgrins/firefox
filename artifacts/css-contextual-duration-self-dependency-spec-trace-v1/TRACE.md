# Self-dependent ordinary animation duration: normative boundary

**Question:** Does CSS define a cycle break, animation-free timing basis, or one-step-per-update rule for `animation-duration:calc(1em / 16px * 1s)` when that same CSS animation animates `font-size`?

**Scenario:** An associated CSSAnimation uses the document timeline, linear replace keyframes from 0px to 32px, no delay, and retained local time 750ms. Duration remains CSS-owned; there is no `var()`, custom property, scroll/view timeline, or successful script duration override. The proposed recurrence additionally assumes a positive active duration. No candidate feedback result is used in this analysis.

## Dependency trace

1. [CSS Cascade 5 §4.4](https://drafts.csswg.org/css-cascade-5/#computed) resolves specified values and their dependencies into computed values. [CSS Values 4 §6.1.1](https://drafts.csswg.org/css-values-4/#font-relative-lengths) defines `em`:
   > Equal to the computed value of the font-size property of the element on which it is used.
   Thus the ordinary interpretation of the duration expression depends on the element's computed font size, not automatically its underlying unanimated font.
2. [CSS Animations 2 §4.1](https://drafts.csswg.org/css-animations-2/#animation-duration) supplies the effect-timing connection:
   > The animation-duration property specifies the iteration duration of the animation’s associated animation effect.
   Section [2](https://drafts.csswg.org/css-animations-2/#animations) requires animation-property changes to update the associated objects; a successful updateTiming duration override would sever this particular CSS-to-effect connection. Pausing or seeking alone does not create that duration override.
3. [Web Animations §4.7.3, step 2, nonzero branch](https://drafts.csswg.org/web-animations-1/#calculating-the-overall-progress) uses the selected duration:
   > Let overall progress be the result of calculating active time / iteration duration.
   With the stated active-phase assumptions, the linear font effect depends on that progress.
4. [CSS Animations 1 §2](https://drafts.csswg.org/css-animations-1/#animations) closes the dependency back into CSS:
   > CSS Animations affect computed property values.
   Its animation-origin rule and [Cascade 5 §6.1](https://drafts.csswg.org/css-cascade-5/#cascade-sort) mean the font effect participates in the computed font size, subject to higher-priority declarations.
5. Returning to step 1 creates a semantic dependency requiring a resolution policy. The inspected ordinary-duration and CSS-animation update provisions do not specify which previous/simultaneous font value to use, a fixed-point solver, or an iteration boundary for this self-dependent path. [CSS Animations 2 §6.2](https://drafts.csswg.org/css-animations-2/#requirements-on-pending-style-changes) requires relevant API results to reflect processed pending computed-value changes, but supplies no cycle-specific algorithm.

## Candidate barriers and their scope

| Proposed barrier | What the primary text establishes |
|---|---|
| Duration is not animatable | [Web Animations §5.2](https://drafts.csswg.org/web-animations-1/#animating-properties) excludes it from keyframe processing and transitions. Here font-size is animated; duration is an ordinary declaration with a changing dependency. Exclusion does not itself freeze that declaration. |
| Animation-free base value | [Web Animations §5.4.5, steps 1–4](https://drafts.csswg.org/web-animations-1/#applying-the-composited-result) obtains an underlying value for the animated target property, combines its effect stack, then inserts the result into the cascade. It does not direct all animation timing properties to use an animation-free context. |
| Animation taint | [CSS Variables 1 §3](https://drafts.csswg.org/css-variables-1/) replacement step 3 rejects animation-tainted custom-property results in non-animatable properties. No var() replacement occurs in this expression. |
| General substitution cycles | [CSS Values 5 Appendix A](https://drafts.csswg.org/css-values-5/) guards nested arbitrary-substitution contexts; property replacement completes substitution before other value transformations. Plain calc arithmetic and em conversion do not establish the nested var/attr/custom-function substitution cycle described there. |
| A frame is one timing update | [Web Animations §4.4](https://drafts.csswg.org/web-animations-1/#animation-frame-loop) updates timeline time and sends events; it does not assign one CSS-duration recomputation to each frame. Fixed timeline time does not imply fixed timing parameters. Its stateless discussion is informative and explicitly qualifies dynamic timing changes. |
| Scroll-animation cycle prevention | [Scroll-driven Animations §5.1](https://drafts.csswg.org/scroll-animations-1/#event-loop) explicitly bounds scroll/view timeline resampling, including an additional stale-timeline pass. These timeline guards do not match a document-timeline duration dependency. They cannot be imported as a general rule. |

CSS Values 4 also redirects font-relative units in **font-affecting properties** to parent metrics. The definition names properties affecting font size/metrics and gives non-exhaustive font-related examples. It does not explicitly classify animation-duration or say that indirect participation in a font animation dynamically makes an animation parameter font-affecting. Applying that exception here would be an additional interpretation needing clarification; this trace does not silently choose it as a cycle fix.

## Consequence for the experiment

Under an additional sequential-update interpretation, the active-branch arithmetic is Dnext=1.5/D in seconds. That is a conditional model, not a mandated update algorithm. Neither an exact two-cycle nor convergence to its positive fixed point follows as a required browser result. The existing observation/model work must retain this distinction. Exogenous ancestor-font changes have no same-element feedback edge and remain a separate case.

**Verdict: INCONCLUSIVE** — the inspected current normative chain exposes the dependency but does not establish a unique self-duration cycle policy. This supports requesting a CSSWG clarification, not declaring either frozen duration, base-font duration, fixed-point iteration, or once-per-frame iteration conforming by default. The useful question is which computed-font snapshot governs ordinary animation parameters when the associated effect contributes that font, including synchronous API observations.

No external issue or message was sent. No browser, native, model, index, application or canonical-state operation was performed. No new bug, acceptance or full native-conformance proof is claimed.
