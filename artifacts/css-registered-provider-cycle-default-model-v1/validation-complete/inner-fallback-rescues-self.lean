import Defaults
open ProviderDefaults
open AttributeGuard (Key)
example : (property true self 12 0).outcome = .value 12 := by
  decide +kernel
