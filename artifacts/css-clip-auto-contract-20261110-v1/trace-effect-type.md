# trace: `WEB-ANIMATIONS-1#the-effect-value-of-a-keyframe-animation-effect` -> `WEB-ANIMATIONS-1#animation-type`

Max depth 9, kind `step`. Found 3 trace(s).

## Trace 1 (1 hop(s))

1) `WEB-ANIMATIONS-1#the-effect-value-of-a-keyframe-animation-effect` step 3 calls `WEB-ANIMATIONS-1#animation-type`
   > If animation type of the target property is not animatable abort this procedure since the effect cannot be applied.

## Trace 2 (1 hop(s))

1) `WEB-ANIMATIONS-1#the-effect-value-of-a-keyframe-animation-effect` step 3.1.3 calls `WEB-ANIMATIONS-1#animation-type`
   - under: For each keyframe in interval endpoints:
   - under: If keyframe has a composite operation that is not replace, or keyframe has no composite operation and the composite operation of this keyframe effect is not replace, then perform the following steps:
   > Replace the property value of target property on keyframe with the result of combining underlying value (Va) and value to combine (Vb) using the procedure for the composite operation to use corresponding to the target property’s animation type.

## Trace 3 (1 hop(s))

1) `WEB-ANIMATIONS-1#the-effect-value-of-a-keyframe-animation-effect` step 9 calls `WEB-ANIMATIONS-1#animation-type`
   > Return the result of applying the interpolation procedure defined by the animation type of the target property to the values of the target property specified on the two keyframes in interval endpoints, taking the first such value as Vstart and the second as Vend and using transformed distance as the interpolation parameter p.

