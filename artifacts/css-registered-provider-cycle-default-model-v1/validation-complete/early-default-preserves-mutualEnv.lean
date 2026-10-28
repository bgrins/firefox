import Defaults
open ProviderDefaults
open AttributeGuard (Key)
example : (property false mutualEnv 12 0).outcome = (property true mutualEnv 12 0).outcome := by
  decide +kernel
