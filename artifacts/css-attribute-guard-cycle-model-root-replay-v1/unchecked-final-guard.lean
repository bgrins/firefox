import Examples
open AttributeGuard AttributeGuard.Examples
example : (property unchecked missingSelf 64 0).outcome = (property {} missingSelf 64 0).outcome := by
  decide +kernel
