import Examples
open AttributeGuard AttributeGuard.Examples
example : (property {} missingMutual 64 1).outcome = .value [.atom 7] := by
  decide +kernel
