import ZeroBasis
open Atan2ZeroBasis
example : resolvedRotation 0 true true = coefficientRotation true true := by
  decide +kernel
