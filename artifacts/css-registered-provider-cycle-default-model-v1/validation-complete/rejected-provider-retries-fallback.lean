import Defaults
open ProviderDefaults
open AttributeGuard (Key)
example : (property true rejection 12 1).outcome = .value 11 := by
  decide +kernel
