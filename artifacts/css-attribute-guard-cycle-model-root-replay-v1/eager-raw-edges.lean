import Examples
open AttributeGuard AttributeGuard.Examples
example : (property eagerRaw nestedRaw 64 0).outcome = (property {} nestedRaw 64 0).outcome := by
  decide +kernel
