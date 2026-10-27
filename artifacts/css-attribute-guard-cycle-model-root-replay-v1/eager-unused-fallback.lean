import Examples
open AttributeGuard AttributeGuard.Examples
example : (property {} eagerFallback 64 0).outcome = (property {} presentRaw 64 0).outcome := by
  decide +kernel
