# trace: `WEB-ANIMATIONS-2#the-effect-value-of-a-keyframe-animation-effect` -> `CSS-VALUES-4#accumulation`

Max depth 9, kind `step`. Found 1 trace(s).

## Trace 1 (1 hop(s))

1) `WEB-ANIMATIONS-2#the-effect-value-of-a-keyframe-animation-effect` step 12.2 calls `CSS-VALUES-4#accumulation`
   - under: For each keyframe in interval endpoints:
   > If this keyframe effect has an iteration composite operation of accumulate, apply the following step current iteration times: replace the property value of target property on keyframe with the result of combining the property value on the final keyframe in property-specific keyframes (Va) with the property value on keyframe (Vb) using the accumulation procedure defined for target property.

