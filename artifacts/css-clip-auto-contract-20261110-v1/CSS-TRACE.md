# CSS clip with equal auto components

**Question:** Must CSS Web Animations combine the numeric components of equal-auto clip rectangles for Add and iteration Accumulate?

**Scenario:** A connected absolutely positioned HTML element; finite valid durations; explicit two-endpoint keyframes; replace effect composition for the iteration case; resolved progress0.5 and current iteration2; A=`rect(10px,50px,50px,10px)`, E=`rect(auto,50px,50px,10px)`. No SMIL animation, unsupported pseudo, missing endpoint or named timeline.

1. [Web Animations Level2 effect value, step12.2](https://drafts.csswg.org/web-animations-2/#the-effect-value-of-a-keyframe-animation-effect) amends Level1's per-endpoint composition. With iterationComposite=accumulate, combine final-keyframe value Va with each endpoint Vb twice. The deciding instruction is:

   > apply the following step current iteration times

   The tool finds one untruncated direct step route to CSS Values accumulation; see trace-accumulation.md. Level1 alone does not define this iteration amendment.

2. [CSS Masking, clip appendix](https://drafts.csswg.org/css-masking-1/#clip-property) gives clip the animation type:

   > by computed value

   This applies to four rectangle components, each a length or auto. Used border-box meanings of auto do not convert it into a numeric computed value for this combination.

3. [Web Animations Level1, animating properties](https://drafts.csswg.org/web-animations-1/#animating-properties) combines corresponding components. Its whole-property discrete fallback for discrete components requires:

   > and the two corresponding values do not match

   A versus E meets that mismatch; E versus E does not. Equal auto is not a reason to reject the other three components.

4. [CSS Values, combining values](https://drafts.csswg.org/css-values-4/#combining-values) defaults an undefined addition operation to the second operand and undefined accumulation to addition:

   > its accumulation operation is identical to addition.

   Thus equal-auto component combination keeps auto. [Combination of dimensions](https://drafts.csswg.org/css-values-4/#combine-dimensions) supplies numeric addition for the matching px lengths. Repeated E/E combination yields `(auto,150px,150px,30px)`.

5. Return to Level1's [effect-value interpolation step](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect). The accumulated start endpoint remains A because its mismatch makes whole-property addition discrete, while the end becomes3E. At midpoint, discrete interpolation selects the end. This is the existing WPT's expected150px result.

For ordinary CSS composite:add, Level1's same per-endpoint algorithm first combines the supplied underlying value and endpoint using the property's animation type. Equal-auto underlying/endpoint rectangles therefore preserve auto and add their numeric components too. Fixing only iterationComposite would leave that companion CSS operation unresolved.

**Verdict: REACHED** — the CSS/Web Animations chain requires componentwise numeric combination for matching auto rectangles; the observed native whole-rectangle rejection prevents it. This verdict concerns CSS animation semantics, not SVG/SMIL admission or a new-bug count.

| Rejected interpretation | Reason |
| --- | --- |
| Any auto component makes the whole rectangle discrete | Level1's deciding mismatch condition is false for equal auto. |
| Missing accumulation defaults to rejecting the property | CSS Values defaults to addition, then to the second component operand where needed. |
| SVG keyword prohibition applies to this HTML WAAPI scenario | No SVG animation element is in this scenario's caller chain. |
| Level1 alone supplies iterationComposite | The governing amendment is in Level2. |

All seven CSS/WA anchors used here passed webspec-index exists. Receipts include snapshot hashes. Numbering follows the Level2 amendment explicitly; Level1's rendered markdown restarts a numbered list after a note, so its composition/interpolation steps are identified by function as well as anchor rather than inventing stable numeric labels.
