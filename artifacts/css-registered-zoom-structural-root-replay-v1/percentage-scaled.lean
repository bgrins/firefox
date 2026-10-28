import Examples
open RegisteredZoom.Structural RegisteredZoom.Structural.Examples
example : nonLengths (wrongPercentage 10 25) = nonLengths (.lengthPercentage 10 25 : V) := by
  decide +kernel
