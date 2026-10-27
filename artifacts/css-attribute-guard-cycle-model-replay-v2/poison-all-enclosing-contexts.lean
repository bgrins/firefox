import Examples
open AttributeGuard AttributeGuard.Examples
example : (property {} typedSelf 64 0).state.poisoned = [.attribute 0, .property 0] := by
  decide +kernel
