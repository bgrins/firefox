import Defaults
open ProviderDefaults
open AttributeGuard (Key)
example : Key.property 2 ∈ (property true mutualEnv 12 2).state.poisoned := by
  decide +kernel
