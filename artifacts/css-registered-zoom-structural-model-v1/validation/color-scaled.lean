import Examples
open RegisteredZoom.Structural RegisteredZoom.Structural.Examples
example : nonLengths (wrongColor 40) = nonLengths (.color 40 : V) := by
  decide +kernel
