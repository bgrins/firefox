import ZeroBasis
open Atan2ZeroBasis
example : resolvedRotation 0 false false = coefficientRotation false false := by
  decide +kernel
