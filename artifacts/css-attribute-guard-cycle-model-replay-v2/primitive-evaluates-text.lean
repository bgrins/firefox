import Examples
open AttributeGuard AttributeGuard.Examples
example : (property {} validPrimitive 64 0).outcome = .invalid := by
  decide +kernel
