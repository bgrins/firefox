import Examples
open AttributeGuard AttributeGuard.Examples
example : (property {} missingMutual 64 2).outcome = .invalid := by
  decide +kernel
