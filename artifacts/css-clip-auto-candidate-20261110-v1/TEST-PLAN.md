# Bounded regression plan

No tests in this capsule have run in a browser. `proposed-tests/clip-auto-composition.html` contains nine deterministic samples, intended for `web-animations/animation-model/keyframe-effects/clip-auto-composition.html` after review. It is deliberately not installed in the live WPT tree. The duration is1000ms; iteration samples are at500ms or2500ms in three iterations, avoiding endpoints.

| Group | Sample | Expected candidate / baseline distinction |
| --- | --- | --- |
| Existing regression | effect-value-iteration-composite-operation.html, clip testcase | Existing first midpoint and third start unchanged; third midpoint becomes rect(auto,150px,150px,30px). Preserve the unrelated align-content and calc-size failures. |
| New iteration | Same rect(auto,50px,50px,10px) at both keyframes, iterationComposite accumulate,2500ms | rect(auto,150px,150px,30px); expected to differ from baseline. |
| New first iteration | Same rectangle,500ms | Original rectangle; both builds. |
| New numeric iteration | Same rect(10px,50px,50px,10px),2500ms | rect(30px,150px,150px,30px); both builds. |
| New outer-auto iteration | auto at both endpoints,2500ms | auto; both builds. |
| New effect addition / accumulation | Underlying and constant endpoint both rect(auto,50px,50px,10px) | rect(auto,100px,100px,20px), each composite mode; expected to differ from baseline. |
| New numeric addition | Underlying and endpoint rect(10px,50px,50px,10px) | rect(20px,100px,100px,20px); both builds. |
| New mismatch addition | Numeric underlying, matching-auto constant effect | Effect rectangle remains; both builds. |
| New outer-auto addition | Underlying/effect both auto | auto; both builds. |

The nine-case page is predicted to have3FAIL/6PASS on the baseline and9PASS on the candidate. These are predictions, not results. Exact callback identity and status must be retained for both runs. Do not update metadata solely to make the overall suite exit successfully.

## SMIL preservation gate

Reuse the existing from-by and from-to harnesses backed by `dom/smil/test/db_smilCSSFromBy.js` and `db_smilCSSFromTo.js`; their exact inputs are pinned in source/. Keep the current expectations. In particular include all-numeric from-by success, equal-auto/mismatched-auto noEffect, and equal-auto from-to interpolation. Run the full small harness pages to protect other properties through the renamed exports.

Add one focused SVG timing page or an existing harness case for each missing caller class:

1. Repetition: a from-to clip animation with the same auto position at both endpoints and `repeatCount=3`, comparing `accumulate=sum` with `accumulate=none` at iteration0 and iteration2 midpoints. Existing behavior must remain noncumulative for that rectangle. Include the same all-numeric pair, where accumulation must occur.
2. Sandwich addition: a constant matching-auto clip animation with `additive=sum` over a matching-auto underlying clip. Verify current replacement fallback remains; pair with an all-numeric additive sum that genuinely adds. This reaches AddForSMIL rather than the AccumulateForSMIL from-by path.
3. By-only: reuse or add matching-auto/all-numeric by-only cases to reach zero-value finalization; preserve the current failure/result. Do not mistake a noEffect assertion alone for validation of internal destination-wrapper mutation.

For the repeat control, choose lengths with distinct underlying, first-iteration and cumulative values so replacement cannot accidentally satisfy addition. Pause the SVG timeline and seek with setCurrentTime rather than wall-clock waits. Snapshot the baseline first; preserve its actual semantics rather than inventing a new SVG oracle from the unresolved spec question.

The explicit count-zero low-level case is in the source-linked model. Repetition normally calls Add only when mRepeatIteration is nonzero, so the browser repeat control cannot certify the count-zero FFI branch. If a native value/FFI test harness is readily available, include numeric count0 returning the right operand, outer Auto/Auto count0 succeeding, and matching-auto Rect count0 returning null; otherwise retain this as a documented lower-level coverage limit.

No large CSS suite or unbounded new matrix is needed before the first candidate comparison. Broaden only after a compile error, callback difference, or newly identified caller concern.
