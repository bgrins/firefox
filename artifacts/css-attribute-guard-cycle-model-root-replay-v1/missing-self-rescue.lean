import Examples
open AttributeGuard AttributeGuard.Examples
example : (property {} missingSelf 64 0).outcome = .value [.atom 7] := by
  decide +kernel
