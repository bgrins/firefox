import Defaults
open ProviderDefaults
open AttributeGuard (Key)
example : (publish 3 (.property 0) ⟨.pending, {}⟩).outcome = .value 3 := by
  decide +kernel
