import Examples
open AttributeGuard AttributeGuard.Examples
example : (property {} missingSelf 0 0).outcome = .invalid := by
  decide +kernel
